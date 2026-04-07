"""Notifications — Invoice reminders, approval requests, due date alerts."""
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import uuid

router = APIRouter(prefix="/notifications")
db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_notifications(user_id: str = None, read: bool = None):
    query = {}
    if user_id:
        query["user_id"] = user_id
    if read is not None:
        query["read"] = read
    return await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)

@router.post("")
async def create_notification(body: dict):
    notif = {
        "id": str(uuid.uuid4()),
        "type": body.get("type", "info"),
        "title": body.get("title", ""),
        "message": body.get("message", ""),
        "user_id": body.get("user_id", ""),
        "role": body.get("role", ""),
        "entity_type": body.get("entity_type", ""),
        "entity_id": body.get("entity_id", ""),
        "action_url": body.get("action_url", ""),
        "priority": body.get("priority", "normal"),
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.notifications.insert_one(notif)
    notif.pop("_id", None)
    return notif

@router.put("/{notif_id}/read")
async def mark_read(notif_id: str):
    await db.notifications.update_one({"id": notif_id}, {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}})
    return {"status": "ok"}

@router.put("/read-all")
async def mark_all_read(body: dict = {}):
    user_id = body.get("user_id", "")
    query = {"read": False}
    if user_id:
        query["user_id"] = user_id
    result = await db.notifications.update_many(query, {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}})
    return {"status": "ok", "marked": result.modified_count}

@router.get("/unread-count")
async def unread_count(user_id: str = None, role: str = None):
    query = {"read": False}
    if user_id:
        query["$or"] = [{"user_id": user_id}, {"role": role}] if role else [{"user_id": user_id}]
    count = await db.notifications.count_documents(query)
    return {"unread": count}

@router.post("/generate-reminders")
async def generate_reminders():
    generated = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    upcoming = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")
    overdue_invoices = await db.invoices.find({"status": {"$in": ["unpaid", "draft"]}, "due_date": {"$lte": today}}, {"_id": 0}).to_list(50)
    for inv in overdue_invoices:
        existing = await db.notifications.find_one({"entity_type": "invoice", "entity_id": inv.get("id", ""), "type": "overdue"})
        if not existing:
            n = {"id": str(uuid.uuid4()), "type": "overdue", "priority": "high", "title": f"Overdue Invoice: {inv.get('invoice_number', '')}", "message": f"Invoice {inv.get('invoice_number', '')} for {inv.get('client', '')} is past due date {inv.get('due_date', '')}", "entity_type": "invoice", "entity_id": inv.get("id", ""), "role": "finance_manager", "read": False, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.notifications.insert_one(n)
            n.pop("_id", None)
            generated.append(n)
    pending_approvals = await db.approval_requests.find({"status": "pending"}, {"_id": 0}).to_list(50)
    for req in pending_approvals:
        created = req.get("created_at", "")
        if created and created[:10] < today:
            step = req["steps"][req["current_step"]] if req["current_step"] < len(req["steps"]) else {}
            existing = await db.notifications.find_one({"entity_type": "approval", "entity_id": req["id"], "type": "reminder"})
            if not existing:
                n = {"id": str(uuid.uuid4()), "type": "reminder", "priority": "medium", "title": f"Pending Approval: {req.get('reference_name', '')}", "message": f"Approval request for {req.get('type', '')} ({req.get('reference_name', '')}) awaiting {step.get('label', 'approval')}", "entity_type": "approval", "entity_id": req["id"], "role": step.get("role", "admin"), "read": False, "created_at": datetime.now(timezone.utc).isoformat()}
                await db.notifications.insert_one(n)
                n.pop("_id", None)
                generated.append(n)
    contracts = await db.contracts.find({"status": "active", "end_date": {"$lte": upcoming}}, {"_id": 0}).to_list(20)
    for c in contracts:
        existing = await db.notifications.find_one({"entity_type": "contract", "entity_id": c["id"], "type": "expiring"})
        if not existing:
            n = {"id": str(uuid.uuid4()), "type": "expiring", "priority": "high", "title": f"Contract Expiring: {c.get('title', '')}", "message": f"Contract with {c.get('client_name', '')} expires on {c.get('end_date', '')}", "entity_type": "contract", "entity_id": c["id"], "role": "admin", "read": False, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.notifications.insert_one(n)
            n.pop("_id", None)
            generated.append(n)
    return {"generated": len(generated), "notifications": generated}

@router.delete("/{notif_id}")
async def delete_notification(notif_id: str):
    await db.notifications.delete_one({"id": notif_id})
    return {"status": "ok"}
