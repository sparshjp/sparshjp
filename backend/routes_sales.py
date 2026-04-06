# Kairos Accounting - API Routes for Sales Module
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/sales", tags=["Sales"])

db = None
ai_orchestrator = None

def set_db(database):
    global db
    db = database

def set_ai_orchestrator(orchestrator):
    global ai_orchestrator
    ai_orchestrator = orchestrator

# ==================== QUOTATIONS ====================
@router.post("/quotations")
async def create_quotation(data: dict):
    quot = {
        "id": str(uuid.uuid4()),
        "customer_name": data.get("customer_name"),
        "quotation_to": data.get("quotation_to", "Customer"),
        "order_type": data.get("order_type", "Sales"),
        "transaction_date": data.get("transaction_date", datetime.now(timezone.utc).date().isoformat()),
        "valid_till": data.get("valid_till"),
        "items": data.get("items", []),
        "total_qty": sum(item.get("qty", 0) for item in data.get("items", [])),
        "total": sum(item.get("amount", 0) for item in data.get("items", [])),
        "taxes": data.get("taxes", []),
        "grand_total": data.get("grand_total", 0),
        "terms": data.get("terms"),
        "status": "Draft",
        "created_from_prompt": data.get("created_from_prompt", False),
        "prompt_text": data.get("prompt_text"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.quotations.insert_one(quot)
    del quot["_id"]
    return quot

@router.get("/quotations")
async def get_quotations(status: Optional[str] = None, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    quots = await db.quotations.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return quots

@router.put("/quotations/{quot_id}/submit")
async def submit_quotation(quot_id: str):
    result = await db.quotations.update_one({"id": quot_id}, {"$set": {"status": "Submitted"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"message": "Quotation submitted"}

@router.post("/quotations/{quot_id}/convert-to-sales-order")
async def convert_to_sales_order(quot_id: str):
    quot = await db.quotations.find_one({"id": quot_id}, {"_id": 0})
    if not quot:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    so = {
        "id": str(uuid.uuid4()),
        "customer": quot["customer_name"],
        "order_type": quot["order_type"],
        "transaction_date": datetime.now(timezone.utc).date().isoformat(),
        "delivery_date": None,
        "items": quot["items"],
        "total_qty": quot["total_qty"],
        "total": quot["total"],
        "taxes": quot["taxes"],
        "grand_total": quot["grand_total"],
        "status": "Draft",
        "per_delivered": 0.0,
        "per_billed": 0.0,
        "quotation_ref": quot_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.sales_orders.insert_one(so)
    await db.quotations.update_one({"id": quot_id}, {"$set": {"status": "Ordered"}})
    del so["_id"]
    return so

# ==================== SALES ORDERS ====================
@router.post("/sales-orders")
async def create_sales_order(data: dict):
    so = {
        "id": str(uuid.uuid4()),
        "customer": data.get("customer"),
        "order_type": data.get("order_type", "Sales"),
        "transaction_date": data.get("transaction_date", datetime.now(timezone.utc).date().isoformat()),
        "delivery_date": data.get("delivery_date"),
        "po_no": data.get("po_no"),
        "items": data.get("items", []),
        "total_qty": sum(item.get("qty", 0) for item in data.get("items", [])),
        "total": sum(item.get("amount", 0) for item in data.get("items", [])),
        "taxes": data.get("taxes", []),
        "grand_total": data.get("grand_total", 0),
        "advance_paid": data.get("advance_paid", 0.0),
        "status": "Draft",
        "per_delivered": 0.0,
        "per_billed": 0.0,
        "quotation_ref": data.get("quotation_ref"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.sales_orders.insert_one(so)
    return {**so, "_id": None}

@router.get("/sales-orders")
async def get_sales_orders(status: Optional[str] = None, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    orders = await db.sales_orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return orders

@router.put("/sales-orders/{so_id}/submit")
async def submit_sales_order(so_id: str):
    result = await db.sales_orders.update_one({"id": so_id}, {"$set": {"status": "To Deliver"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sales Order not found")
    return {"message": "Sales Order submitted"}

# ==================== DELIVERY NOTES ====================
@router.post("/delivery-notes")
async def create_delivery_note(data: dict):
    dn = {
        "id": str(uuid.uuid4()),
        "customer": data.get("customer"),
        "posting_date": data.get("posting_date", datetime.now(timezone.utc).date().isoformat()),
        "posting_time": data.get("posting_time", datetime.now(timezone.utc).time().isoformat()),
        "sales_order_ref": data.get("sales_order_ref"),
        "items": data.get("items", []),
        "total_qty": sum(item.get("qty", 0) for item in data.get("items", [])),
        "lr_no": data.get("lr_no"),
        "transporter": data.get("transporter"),
        "vehicle_no": data.get("vehicle_no"),
        "status": "Draft",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.delivery_notes.insert_one(dn)
    
    # Update SO delivery percentage
    if data.get("sales_order_ref"):
        so = await db.sales_orders.find_one({"id": data["sales_order_ref"]}, {"_id": 0})
        if so:
            delivered_qty = sum(item.get("qty", 0) for item in data.get("items", []))
            total_qty = so.get("total_qty", 1)
            per_delivered = (delivered_qty / total_qty) * 100
            await db.sales_orders.update_one(
                {"id": data["sales_order_ref"]},
                {"$set": {"per_delivered": per_delivered}}
            )
    
    del dn["_id"]
    return dn

@router.get("/delivery-notes")
async def get_delivery_notes(status: Optional[str] = None, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    notes = await db.delivery_notes.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return notes