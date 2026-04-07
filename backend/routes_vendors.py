"""Auto-generated module: Vendors"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/vendors", tags=["Vendors"])

db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_vendors():
    items = await db.vendors.find({}, {"_id": 0}).to_list(1000)
    return {"count": len(items), "vendors": items}

@router.post("")
async def create_vendor(body: dict):
    body["id"] = str(uuid.uuid4())
    body["entity_type"] = "vendor"
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.vendors.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}

@router.put("/{vendor_id}")
async def update_vendor(vendor_id: str, body: dict):
    result = await db.vendors.update_one({"id": vendor_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"status": "updated", "id": vendor_id}

@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: str):
    result = await db.vendors.delete_one({"id": vendor_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"status": "deleted", "id": vendor_id}
