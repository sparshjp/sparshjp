from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/clients")
db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_clients():
    items = await db.clients.find({}, {"_id": 0}).to_list(500)
    return {"count": len(items), "clients": items}

@router.post("")
async def create_client(body: dict):
    body["id"] = body.get("id") or str(uuid.uuid4())
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.clients.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}

@router.get("/{client_id}")
async def get_client(client_id: str):
    client = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not client:
        raise HTTPException(404, "Client not found")
    return client

@router.put("/{client_id}")
async def update_client(client_id: str, body: dict):
    result = await db.clients.update_one({"id": client_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(404, "Client not found")
    return {"message": "Client updated", "id": client_id}

@router.delete("/{client_id}")
async def delete_client(client_id: str):
    result = await db.clients.delete_one({"id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Client not found")
    return {"message": "Client deleted", "id": client_id}
