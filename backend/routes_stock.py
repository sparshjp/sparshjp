# Kairos Accounting - API Routes for Stock/Inventory Module
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/stock", tags=["Stock"])

db = None
ai_orchestrator = None

def set_db(database):
    global db
    db = database

def set_ai_orchestrator(orchestrator):
    global ai_orchestrator
    ai_orchestrator = orchestrator

# ==================== ITEMS ====================
@router.post("/items")
async def create_item(data: dict):
    item = {
        "id": str(uuid.uuid4()),
        "item_code": data.get("item_code"),
        "item_name": data.get("item_name"),
        "item_group": data.get("item_group", "Products"),
        "stock_uom": data.get("stock_uom", "Nos"),
        "is_stock_item": data.get("is_stock_item", True),
        "is_sales_item": data.get("is_sales_item", True),
        "is_purchase_item": data.get("is_purchase_item", True),
        "has_serial_no": data.get("has_serial_no", False),
        "has_batch_no": data.get("has_batch_no", False),
        "opening_stock": data.get("opening_stock", 0.0),
        "valuation_rate": data.get("valuation_rate", 0.0),
        "standard_rate": data.get("standard_rate", 0.0),
        "hsn_code": data.get("hsn_code"),
        "gst_rate": data.get("gst_rate", 18.0),
        "reorder_level": data.get("reorder_level", 0.0),
        "reorder_qty": data.get("reorder_qty", 0.0),
        "warehouse": data.get("warehouse", "Main Warehouse"),
        "description": data.get("description"),
        "current_stock": data.get("opening_stock", 0.0),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.items.insert_one(item)
    return {**item, "_id": None}

@router.get("/items")
async def get_items(limit: int = 100):
    items = await db.items.find({}, {"_id": 0}).sort("item_name", 1).to_list(limit)
    return items

@router.get("/items/{item_id}")
async def get_item(item_id: str):
    item = await db.items.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/items/check-reorder")
async def check_reorder_items():
    """Check items below reorder level and suggest PO"""
    items = await db.items.find({"is_stock_item": True}, {"_id": 0}).to_list(1000)
    
    reorder_items = []
    for item in items:
        current = item.get("current_stock", 0)
        reorder_level = item.get("reorder_level", 0)
        if current <= reorder_level:
            reorder_items.append({
                "item_code": item.get("item_code"),
                "item_name": item.get("item_name"),
                "current_stock": current,
                "reorder_level": reorder_level,
                "suggested_qty": item.get("reorder_qty", 10)
            })
    
    return {"reorder_required": len(reorder_items), "items": reorder_items}

# ==================== STOCK ENTRIES ====================
@router.post("/stock-entries")
async def create_stock_entry(data: dict):
    entry = {
        "id": str(uuid.uuid4()),
        "stock_entry_type": data.get("stock_entry_type"),
        "posting_date": data.get("posting_date", datetime.now(timezone.utc).date().isoformat()),
        "posting_time": data.get("posting_time", datetime.now(timezone.utc).time().isoformat()),
        "from_warehouse": data.get("from_warehouse"),
        "to_warehouse": data.get("to_warehouse"),
        "items": data.get("items", []),
        "total_amount": sum(item.get("qty", 0) * item.get("rate", 0) for item in data.get("items", [])),
        "status": "Draft",
        "created_from_image": data.get("created_from_image", False),
        "image_url": data.get("image_url"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.stock_entries.insert_one(entry)
    return {**entry, "_id": None}

@router.get("/stock-entries")
async def get_stock_entries(entry_type: Optional[str] = None, limit: int = 50):
    query = {}
    if entry_type:
        query["stock_entry_type"] = entry_type
    entries = await db.stock_entries.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return entries

@router.put("/stock-entries/{entry_id}/submit")
async def submit_stock_entry(entry_id: str):
    entry = await db.stock_entries.find_one({"id": entry_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Stock entry not found")
    
    # Update stock levels
    entry_type = entry.get("stock_entry_type")
    items = entry.get("items", [])
    
    for item_data in items:
        item_code = item_data.get("item")
        qty = item_data.get("qty", 0)
        
        if entry_type == "Material Receipt":
            await db.items.update_one({"item_code": item_code}, {"$inc": {"current_stock": qty}})
        elif entry_type == "Material Issue":
            await db.items.update_one({"item_code": item_code}, {"$inc": {"current_stock": -qty}})
        elif entry_type == "Material Transfer":
            # In real implementation, handle warehouse-wise stock
            pass
    
    await db.stock_entries.update_one({"id": entry_id}, {"$set": {"status": "Submitted"}})
    return {"message": "Stock entry submitted and stock updated"}

# ==================== STOCK RECONCILIATION ====================
@router.post("/stock-reconciliation")
async def create_stock_reconciliation(data: dict):
    recon = {
        "id": str(uuid.uuid4()),
        "posting_date": data.get("posting_date", datetime.now(timezone.utc).date().isoformat()),
        "posting_time": data.get("posting_time", datetime.now(timezone.utc).time().isoformat()),
        "purpose": "Stock Reconciliation",
        "items": data.get("items", []),
        "expense_account": "Stock Adjustment - KA",
        "difference_amount": 0.0,
        "ai_reconciled": data.get("ai_reconciled", False),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Calculate difference
    total_diff = 0
    for item in recon["items"]:
        system_qty = item.get("system_qty", 0)
        physical_qty = item.get("physical_qty", 0)
        rate = item.get("rate", 0)
        total_diff += (physical_qty - system_qty) * rate
    
    recon["difference_amount"] = total_diff
    await db.stock_reconciliation.insert_one(recon)
    return {**recon, "_id": None}

@router.get("/stock-reconciliation")
async def get_stock_reconciliations(limit: int = 50):
    recons = await db.stock_reconciliation.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return recons