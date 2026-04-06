"""Auto-generated module: Expense Management (polished by E1)"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/expenses", tags=["Expense Management"])

db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_expenses():
    items = await db.expenses.find({}, {"_id": 0}).to_list(500)
    return items

@router.post("")
async def create_expense(body: dict):
    body["id"] = str(uuid.uuid4())
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    if not body.get("currency"):
        body["currency"] = "INR"
    if not body.get("status"):
        body["status"] = "pending"
    if not body.get("submitted_date"):
        body["submitted_date"] = datetime.now(timezone.utc).isoformat()
    await db.expenses.insert_one(body)
    return {k: v for k, v in body.items() if k != "_id"}

@router.put("/{expense_id}/approve")
async def approve_expense(expense_id: str, body: dict):
    update_data = {
        "status": "approved",
        "approved_by": body.get("approved_by", "Admin"),
        "approved_date": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.expenses.update_one({"id": expense_id}, {"$set": update_data})
    if result.matched_count == 0:
        return {"error": "Expense not found", "expense_id": expense_id}
    return {"status": "approved", "expense_id": expense_id, "modified": result.modified_count}

@router.put("/{expense_id}/reject")
async def reject_expense(expense_id: str, body: dict):
    update_data = {
        "status": "rejected",
        "rejection_reason": body.get("rejection_reason", ""),
    }
    result = await db.expenses.update_one({"id": expense_id}, {"$set": update_data})
    if result.matched_count == 0:
        return {"error": "Expense not found", "expense_id": expense_id}
    return {"status": "rejected", "expense_id": expense_id, "modified": result.modified_count}

@router.get("/summary")
async def get_expense_summary():
    by_category = await db.expenses.aggregate([
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]).to_list(100)
    by_status = await db.expenses.aggregate([
        {"$group": {"_id": "$status", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]).to_list(100)

    pending = await db.expenses.find({"status": "pending"}, {"_id": 0, "amount": 1}).to_list(500)
    approved = await db.expenses.find({"status": "approved"}, {"_id": 0, "amount": 1}).to_list(500)

    return {
        "total_by_category": [{"category": item["_id"], "total": item["total"], "count": item["count"]} for item in by_category],
        "total_by_status": [{"status": item["_id"], "total": item["total"], "count": item["count"]} for item in by_status],
        "total_pending_amount": sum(e.get("amount", 0) for e in pending),
        "total_approved_amount": sum(e.get("amount", 0) for e in approved),
        "total_expenses": await db.expenses.count_documents({}),
    }

@router.get("/by-employee/{employee_id}")
async def get_expenses_by_employee(employee_id: str):
    items = await db.expenses.find({"employee_id": employee_id}, {"_id": 0}).to_list(500)
    return items
