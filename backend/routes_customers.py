"""Auto-generated module: Customers"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/customers", tags=["Customers"])

db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_customers():
    items = await db.customers.find({}, {"_id": 0}).to_list(1000)
    return {"count": len(items), "customers": items}

@router.post("")
async def create_customer(body: dict):
    body["id"] = str(uuid.uuid4())
    body["entity_type"] = "customer"
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.customers.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}

@router.put("/{customer_id}")
async def update_customer(customer_id: str, body: dict):
    result = await db.customers.update_one({"id": customer_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"status": "updated", "id": customer_id}

@router.delete("/{customer_id}")
async def delete_customer(customer_id: str):
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"status": "deleted", "id": customer_id}
