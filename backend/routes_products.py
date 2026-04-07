from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/products")
db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_products():
    items = await db.products.find({}, {"_id": 0}).to_list(500)
    return {"count": len(items), "products": items}

@router.post("")
async def create_product(body: dict):
    body["sku"] = body.get("sku") or str(uuid.uuid4())
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.products.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}

@router.get("/{sku}")
async def get_product(sku: str):
    product = await db.products.find_one({"sku": sku}, {"_id": 0})
    if not product:
        raise HTTPException(404, "Product not found")
    return product

@router.put("/{sku}")
async def update_product(sku: str, body: dict):
    result = await db.products.update_one({"sku": sku}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(404, "Product not found")
    return {"message": "Product updated", "sku": sku}

@router.delete("/{sku}")
async def delete_product(sku: str):
    result = await db.products.delete_one({"sku": sku})
    if result.deleted_count == 0:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted", "sku": sku}
