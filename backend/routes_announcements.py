"""Auto-generated module: Announcements"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/announcements", tags=["Announcements"])

db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_announcements():
    items = await db.announcements.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return items

@router.post("")
async def create_announcement(body: dict):
    body["id"] = str(uuid.uuid4())
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.announcements.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}

@router.get("/{announcement_id}")
async def get_announcement(announcement_id: str):
    item = await db.announcements.find_one({"id": announcement_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return item

@router.put("/{announcement_id}")
async def update_announcement(announcement_id: str, body: dict):
    body["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.announcements.update_one({"id": announcement_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    updated = await db.announcements.find_one({"id": announcement_id}, {"_id": 0})
    return updated

@router.delete("/{announcement_id}")
async def delete_announcement(announcement_id: str):
    result = await db.announcements.delete_one({"id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted", "id": announcement_id}
