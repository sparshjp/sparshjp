from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

router = APIRouter(prefix="/bulk")
db = None

def set_db(database):
    global db
    db = database

@router.post("/employees")
async def bulk_import_employees(body: dict):
    records = body.get("records", [])
    if not records:
        raise HTTPException(400, "No records provided")
    for rec in records:
        if "created_at" not in rec:
            rec["created_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.employees.insert_many(records)
    return {"imported": len(result.inserted_ids), "count": len(records)}

@router.post("/vendors")
async def bulk_import_vendors(body: dict):
    records = body.get("records", [])
    if not records:
        raise HTTPException(400, "No records provided")
    for rec in records:
        if "created_at" not in rec:
            rec["created_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.vendors.insert_many(records)
    return {"imported": len(result.inserted_ids), "count": len(records)}

@router.post("/clients")
async def bulk_import_clients(body: dict):
    records = body.get("records", [])
    if not records:
        raise HTTPException(400, "No records provided")
    for rec in records:
        if "created_at" not in rec:
            rec["created_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.clients.insert_many(records)
    return {"imported": len(result.inserted_ids), "count": len(records)}

@router.post("/products")
async def bulk_import_products(body: dict):
    records = body.get("records", [])
    if not records:
        raise HTTPException(400, "No records provided")
    for rec in records:
        if "created_at" not in rec:
            rec["created_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.products.insert_many(records)
    return {"imported": len(result.inserted_ids), "count": len(records)}
