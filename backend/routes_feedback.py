"""Auto-generated module: Feedback"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/feedback", tags=["Feedback"])

db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_feedback():
    items = await db.feedback.find({}, {"_id": 0}).to_list(500)
    return items

@router.post("")
async def create_feedback(body: dict):
    body["id"] = str(uuid.uuid4())
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    if not 1 <= body["rating"] <= 5:
        return {"error": "Rating must be between 1 and 5"}
    await db.feedback.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}
