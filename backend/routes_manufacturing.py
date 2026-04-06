# Kairos Accounting - Manufacturing Module
# Work Order lifecycle: Open → Material Issue → Production → Close → FG Receipt

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional
import uuid

router = APIRouter(prefix="/manufacturing", tags=["manufacturing"])
db = None

def set_db(database):
    global db
    db = database

async def auto_post_journal_entries(entries, narration, cost_center="Manufacturing", ref_doc_type="", ref_doc_id=""):
    entry = {
        "id": str(uuid.uuid4()),
        "entry_type": "Auto Generated",
        "posting_date": datetime.now(timezone.utc).date().isoformat(),
        "cost_center": cost_center,
        "journal_entries": entries,
        "narration": narration,
        "ref_doc_type": ref_doc_type,
        "ref_doc_id": ref_doc_id,
        "voucher_type": "Journal Entry",
        "status": "Posted",
        "user_id": "system",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "posted_at": datetime.now(timezone.utc).isoformat()
    }
    await db.manual_journal_entries.insert_one(entry)
    for je in entries:
        journal_doc = {
            "id": str(uuid.uuid4()),
            "transaction_id": entry["id"],
            "account": je["account"],
            "debit": je.get("debit", 0),
            "credit": je.get("credit", 0),
            "description": je.get("description", ""),
            "posting_date": entry["posting_date"],
            "cost_center": cost_center,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.journal_entries.insert_one(journal_doc)
        net = je.get("debit", 0) - je.get("credit", 0)
        await db.chart_of_accounts.update_one(
            {"ledger_name": je["account"]},
            {"$inc": {"current_balance": net}},
            upsert=False
        )
    return entry["id"]


# ═══════════════════════════════════════════════════════
# WORK ORDERS
# ═══════════════════════════════════════════════════════
@router.post("/work-orders")
async def create_work_order(data: dict):
    bom_items = data.get("bom_items", [])
    total_rm_cost = sum(i.get("qty", 0) * i.get("rate", 0) for i in bom_items)

    wo = {
        "id": str(uuid.uuid4()),
        "wo_number": data.get("wo_number", f"WO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"),
        "production_item": data.get("production_item"),
        "production_item_name": data.get("production_item_name", ""),
        "qty_to_produce": data.get("qty_to_produce", 0),
        "qty_produced": 0,
        "qty_rejected": 0,
        "bom_items": bom_items,
        "total_rm_cost": round(total_rm_cost, 2),
        "additional_costs": data.get("additional_costs", 0),
        "cost_per_unit": round((total_rm_cost + data.get("additional_costs", 0)) / max(data.get("qty_to_produce", 1), 1), 2),
        "planned_start": data.get("planned_start"),
        "planned_end": data.get("planned_end"),
        "actual_start": None,
        "actual_end": None,
        "cost_center": data.get("cost_center", "Manufacturing"),
        "status": "Draft",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.work_orders.insert_one(wo)
    del wo["_id"]
    return wo

@router.get("/work-orders")
async def list_work_orders(status: Optional[str] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    return await db.work_orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)

@router.get("/work-orders/{wo_id}")
async def get_work_order(wo_id: str):
    wo = await db.work_orders.find_one({"id": wo_id}, {"_id": 0})
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    return wo


# ═══════════════════════════════════════════════════════
# WORK ORDER ACTIONS
# ═══════════════════════════════════════════════════════
@router.post("/work-orders/{wo_id}/start")
async def start_work_order(wo_id: str):
    """Start production - issues raw materials from inventory to WIP"""
    wo = await db.work_orders.find_one({"id": wo_id}, {"_id": 0})
    if not wo:
        raise HTTPException(status_code=404, detail="WO not found")
    if wo["status"] not in ["Draft", "Submitted"]:
        raise HTTPException(status_code=400, detail=f"Cannot start WO in {wo['status']} status")

    # Material Issue: DR WIP, CR Raw Material
    total_rm = wo["total_rm_cost"]
    if total_rm > 0:
        je_entries = [
            {"account": "WIP Inventory", "debit": total_rm, "credit": 0,
             "description": f"RM issued for {wo['wo_number']}"},
            {"account": "Raw Material Inventory", "debit": 0, "credit": total_rm,
             "description": f"RM consumed by {wo['wo_number']}"}
        ]
        je_id = await auto_post_journal_entries(
            je_entries,
            f"Material Issue for {wo['wo_number']}: {wo['production_item']}",
            wo["cost_center"],
            "Work Order", wo_id
        )

        # Update stock levels
        for item in wo.get("bom_items", []):
            await db.items.update_one(
                {"item_code": item.get("item_code", item.get("item", ""))},
                {"$inc": {"current_stock": -item.get("qty", 0)}}
            )

    await db.work_orders.update_one(
        {"id": wo_id},
        {"$set": {"status": "In Progress", "actual_start": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "WO started, materials issued", "id": wo_id}


@router.post("/work-orders/{wo_id}/complete")
async def complete_work_order(wo_id: str, data: dict = None):
    """Complete WO - transfer FG from WIP, handle scrap"""
    if data is None:
        data = {}
    wo = await db.work_orders.find_one({"id": wo_id}, {"_id": 0})
    if not wo:
        raise HTTPException(status_code=404, detail="WO not found")
    if wo["status"] != "In Progress":
        raise HTTPException(status_code=400, detail="WO must be In Progress")

    qty_produced = data.get("qty_produced", wo["qty_to_produce"])
    qty_rejected = data.get("qty_rejected", 0)
    scrap_reason = data.get("scrap_reason", "")

    # Get FG item valuation
    fg_item = await db.items.find_one({"item_code": wo["production_item"]}, {"_id": 0})
    fg_rate = fg_item.get("valuation_rate", wo["cost_per_unit"]) if fg_item else wo["cost_per_unit"]
    fg_value = round(qty_produced * fg_rate, 2)
    scrap_value = round(qty_rejected * fg_rate, 2)

    je_entries = []
    # FG Receipt: DR Finished Goods, CR WIP
    if fg_value > 0:
        je_entries.extend([
            {"account": "Finished Goods Inventory", "debit": fg_value, "credit": 0,
             "description": f"FG receipt: {qty_produced} {wo['production_item']}"},
            {"account": "WIP Inventory", "debit": 0, "credit": fg_value,
             "description": f"WIP to FG: {wo['wo_number']}"}
        ])
    # Scrap: DR Scrap/Loss, CR WIP
    if scrap_value > 0:
        je_entries.extend([
            {"account": "Scrap/Loss", "debit": scrap_value, "credit": 0,
             "description": f"Scrap: {qty_rejected} units - {scrap_reason}"},
            {"account": "WIP Inventory", "debit": 0, "credit": scrap_value,
             "description": f"WIP write-off: {wo['wo_number']}"}
        ])

    if je_entries:
        await auto_post_journal_entries(
            je_entries,
            f"WO Completion {wo['wo_number']}: {qty_produced} produced, {qty_rejected} rejected",
            wo["cost_center"],
            "Work Order", wo_id
        )

    # Update FG stock
    if qty_produced > 0:
        await db.items.update_one(
            {"item_code": wo["production_item"]},
            {"$inc": {"current_stock": qty_produced}}
        )

    await db.work_orders.update_one(
        {"id": wo_id},
        {"$set": {
            "status": "Completed",
            "qty_produced": qty_produced,
            "qty_rejected": qty_rejected,
            "actual_end": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"message": f"WO completed. Produced: {qty_produced}, Scrap: {qty_rejected}", "id": wo_id}


@router.post("/work-orders/{wo_id}/cancel")
async def cancel_work_order(wo_id: str):
    wo = await db.work_orders.find_one({"id": wo_id}, {"_id": 0})
    if not wo:
        raise HTTPException(status_code=404, detail="WO not found")
    await db.work_orders.update_one({"id": wo_id}, {"$set": {"status": "Cancelled"}})
    return {"message": "WO cancelled", "id": wo_id}
