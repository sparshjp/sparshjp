"""Auto-generated module: Leave Management"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/leave-mgmt", tags=["Leave Management"])

db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_leave_requests():
    items = await db.leave_requests.find({}, {"_id": 0}).to_list(500)
    return items

@router.post("")
async def create_leave_request(body: dict):
    import uuid
    from datetime import datetime, timezone
    
    body["id"] = str(uuid.uuid4())
    body["status"] = "pending"
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.leave_requests.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}
