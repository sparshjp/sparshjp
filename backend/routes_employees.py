from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/employees")
db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_employees():
    items = await db.employees.find({}, {"_id": 0}).to_list(500)
    return {"count": len(items), "employees": items}

@router.post("")
async def create_employee(body: dict):
    body["id"] = body.get("id") or str(uuid.uuid4())
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.employees.insert_one(body)
    return {k:v for k,v in body.items() if k != "_id"}

@router.get("/{emp_id}")
async def get_employee(emp_id: str):
    emp = await db.employees.find_one({"id": emp_id}, {"_id": 0})
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp

@router.put("/{emp_id}")
async def update_employee(emp_id: str, body: dict):
    result = await db.employees.update_one({"id": emp_id}, {"$set": body})
    if result.matched_count == 0:
        raise HTTPException(404, "Employee not found")
    return {"message": "Employee updated", "id": emp_id}

@router.delete("/{emp_id}")
async def delete_employee(emp_id: str):
    result = await db.employees.delete_one({"id": emp_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Employee not found")
    return {"message": "Employee deleted", "id": emp_id}
