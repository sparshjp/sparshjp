# Kairos Accounting - API Routes for HR Module
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/hr", tags=["HR"])

db = None

def set_db(database):
    global db
    db = database

# ==================== EMPLOYEES ====================
@router.post("/employees")
async def create_employee(data: dict):
    emp = {
        "id": str(uuid.uuid4()),
        "employee_name": data.get("employee_name"),
        "employee_number": data.get("employee_number"),
        "gender": data.get("gender"),
        "date_of_birth": data.get("date_of_birth"),
        "date_of_joining": data.get("date_of_joining"),
        "department": data.get("department"),
        "designation": data.get("designation"),
        "employment_type": data.get("employment_type", "Full-time"),
        "status": "Active",
        "attendance_device_id": data.get("attendance_device_id"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.employees.insert_one(emp)
    del emp["_id"]
    return emp

@router.get("/employees")
async def get_employees(status: Optional[str] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    else:
        query["status"] = "Active"
    emps = await db.employees.find(query, {"_id": 0}).sort("employee_name", 1).to_list(limit)
    return emps

@router.get("/employees/{emp_id}")
async def get_employee(emp_id: str):
    emp = await db.employees.find_one({"id": emp_id}, {"_id": 0})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

# ==================== ATTENDANCE ====================
@router.post("/attendance")
async def mark_attendance(data: dict):
    att = {
        "id": str(uuid.uuid4()),
        "employee": data.get("employee"),
        "attendance_date": data.get("attendance_date", datetime.now(timezone.utc).date().isoformat()),
        "status": data.get("status", "Present"),
        "shift": data.get("shift"),
        "in_time": data.get("in_time"),
        "out_time": data.get("out_time"),
        "working_hours": data.get("working_hours", 0.0),
        "late_entry": data.get("late_entry", False),
        "early_exit": data.get("early_exit", False),
        "marked_by_ai": data.get("marked_by_ai", False),
        "image_ref": data.get("image_ref"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.attendance.insert_one(att)
    del att["_id"]
    return att

@router.get("/attendance")
async def get_attendance(employee: Optional[str] = None, date: Optional[str] = None, limit: int = 100):
    query = {}
    if employee:
        query["employee"] = employee
    if date:
        query["attendance_date"] = date
    att = await db.attendance.find(query, {"_id": 0}).sort("attendance_date", -1).to_list(limit)
    return att

@router.post("/attendance/bulk-mark")
async def bulk_mark_attendance(data: dict):
    """Mark attendance for multiple employees (AI-based)"""
    employees = data.get("employees", [])
    date = data.get("date", datetime.now(timezone.utc).date().isoformat())
    
    result = {"marked": 0, "failed": []}
    for emp_data in employees:
        try:
            att = {
                "id": str(uuid.uuid4()),
                "employee": emp_data.get("employee_name"),
                "attendance_date": date,
                "status": emp_data.get("status", "Present"),
                "marked_by_ai": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.attendance.insert_one(att)
            result["marked"] += 1
        except Exception as e:
            result["failed"].append({"employee": emp_data.get("employee_name"), "error": str(e)})
    
    return result

# ==================== LEAVE APPLICATIONS ====================
@router.post("/leave-applications")
async def create_leave_application(data: dict):
    leave = {
        "id": str(uuid.uuid4()),
        "employee": data.get("employee"),
        "leave_type": data.get("leave_type"),
        "from_date": data.get("from_date"),
        "to_date": data.get("to_date"),
        "total_leave_days": data.get("total_leave_days", 1.0),
        "leave_balance": data.get("leave_balance", 0.0),
        "reason": data.get("reason"),
        "status": "Draft",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.leave_applications.insert_one(leave)
    del leave["_id"]
    return leave

@router.get("/leave-applications")
async def get_leave_applications(employee: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    query = {}
    if employee:
        query["employee"] = employee
    if status:
        query["status"] = status
    leaves = await db.leave_applications.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return leaves

@router.put("/leave-applications/{leave_id}/approve")
async def approve_leave(leave_id: str):
    result = await db.leave_applications.update_one({"id": leave_id}, {"$set": {"status": "Approved"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Leave application not found")
    return {"message": "Leave approved"}

@router.put("/leave-applications/{leave_id}/reject")
async def reject_leave(leave_id: str):
    result = await db.leave_applications.update_one({"id": leave_id}, {"$set": {"status": "Rejected"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Leave application not found")
    return {"message": "Leave rejected"}

# ==================== SALARY SLIPS ====================
@router.post("/salary-slips")
async def create_salary_slip(data: dict):
    slip = {
        "id": str(uuid.uuid4()),
        "employee": data.get("employee"),
        "salary_month": data.get("salary_month"),
        "earnings": data.get("earnings", []),
        "deductions": data.get("deductions", []),
        "gross_pay": sum(e.get("amount", 0) for e in data.get("earnings", [])),
        "total_deduction": sum(d.get("amount", 0) for d in data.get("deductions", [])),
        "net_pay": 0.0,
        "tds": data.get("tds", 0.0),
        "payment_days": data.get("payment_days", 30.0),
        "status": "Draft",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    slip["net_pay"] = slip["gross_pay"] - slip["total_deduction"]
    await db.salary_slips.insert_one(slip)
    del slip["_id"]
    return slip

@router.get("/salary-slips")
async def get_salary_slips(employee: Optional[str] = None, month: Optional[str] = None, limit: int = 50):
    query = {}
    if employee:
        query["employee"] = employee
    if month:
        query["salary_month"] = month
    slips = await db.salary_slips.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return slips