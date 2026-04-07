"""Timesheet routes"""
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/timesheets", tags=["Timesheets"])

def get_db():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

@router.get("")
async def list_timesheets(employee_id: str = None, week: str = None, project_id: str = None):
    db = get_db()
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if week:
        query["week"] = week
    if project_id:
        query["entries.project_id"] = project_id
    timesheets = await db.timesheets.find(query, {"_id": 0}).sort("week_start", 1).to_list(500)
    return timesheets

@router.post("")
async def create_timesheet(body: dict):
    db = get_db()
    body["id"] = str(uuid.uuid4())
    body["created_at"] = datetime.now(timezone.utc).isoformat()
    body["status"] = body.get("status", "Submitted")
    await db.timesheets.insert_one(body)
    result = await db.timesheets.find_one({"id": body["id"]}, {"_id": 0})
    return result

@router.put("/{timesheet_id}/approve")
async def approve_timesheet(timesheet_id: str):
    db = get_db()
    ts = await db.timesheets.find_one({"id": timesheet_id}, {"_id": 0})
    result = await db.timesheets.update_one(
        {"id": timesheet_id},
        {"$set": {"status": "Approved", "approved_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    # Event: Timesheet approved → Billing queue + Notification
    if ts:
        import module_events
        await module_events.on_timesheet_approved(ts)
    return {"status": "approved"}

@router.put("/{timesheet_id}/reject")
async def reject_timesheet(timesheet_id: str, body: dict = None):
    db = get_db()
    update = {"status": "Rejected", "rejected_at": datetime.now(timezone.utc).isoformat()}
    if body and "reason" in body:
        update["rejection_reason"] = body["reason"]
    result = await db.timesheets.update_one({"id": timesheet_id}, {"$set": update})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return {"status": "rejected"}

@router.get("/utilization")
async def utilization_report():
    db = get_db()
    employees = await db.employees.find({"billable": True}, {"_id": 0}).to_list(50)
    timesheets = await db.timesheets.find({}, {"_id": 0}).to_list(500)
    
    emp_hours = {}
    for ts in timesheets:
        eid = ts.get("employee_id")
        if eid not in emp_hours:
            emp_hours[eid] = {"billable": 0, "non_billable": 0, "total": 0, "leave": 0}
        for entry in ts.get("entries", []):
            hours = entry.get("hours", 0)
            emp_hours[eid]["total"] += hours
            if entry.get("billable"):
                emp_hours[eid]["billable"] += hours
            else:
                emp_hours[eid]["non_billable"] += hours
        emp_hours[eid]["leave"] += ts.get("leave_hours", 0)
    
    result = []
    for emp in employees:
        eid = emp["id"]
        hours = emp_hours.get(eid, {"billable": 0, "non_billable": 0, "total": 0, "leave": 0})
        available = hours["total"] + hours["leave"] if hours["total"] > 0 else 160
        utilization = (hours["billable"] / available * 100) if available > 0 else 0
        result.append({
            "employee_id": eid,
            "name": emp["name"],
            "role": emp["role"],
            "dept": emp["dept"],
            "location": emp.get("location", ""),
            "billable_hours": hours["billable"],
            "non_billable_hours": hours["non_billable"],
            "total_hours": hours["total"],
            "leave_hours": hours["leave"],
            "utilization_pct": round(utilization, 1),
            "target_pct": 80,
            "status": "On Track" if utilization >= 75 else ("At Risk" if utilization >= 50 else "Below Target"),
        })
    result.sort(key=lambda x: x["utilization_pct"], reverse=True)
    
    total_billable = sum(r["billable_hours"] for r in result)
    total_available = sum(r["total_hours"] + r["leave_hours"] for r in result)
    avg_util = (total_billable / total_available * 100) if total_available > 0 else 0
    
    return {
        "employees": result,
        "summary": {
            "total_billable": total_billable,
            "total_available": total_available,
            "avg_utilization": round(avg_util, 1),
            "target": 75,
            "headcount": len(result),
        }
    }

@router.get("/consolidation")
async def monthly_consolidation():
    db = get_db()
    timesheets = await db.timesheets.find({}, {"_id": 0}).to_list(500)
    projects = await db.projects.find({}, {"_id": 0}).to_list(20)
    project_map = {p["id"]: p for p in projects}
    
    project_hours = {}
    for ts in timesheets:
        for entry in ts.get("entries", []):
            pid = entry.get("project_id", "")
            if pid not in project_hours:
                proj = project_map.get(pid, {})
                project_hours[pid] = {
                    "project_id": pid,
                    "project_name": proj.get("name", pid),
                    "client": proj.get("client", ""),
                    "type": proj.get("type", ""),
                    "currency": proj.get("currency", "INR"),
                    "billable_hours": 0,
                    "non_billable_hours": 0,
                    "employees": set(),
                }
            hours = entry.get("hours", 0)
            if entry.get("billable"):
                project_hours[pid]["billable_hours"] += hours
            else:
                project_hours[pid]["non_billable_hours"] += hours
            project_hours[pid]["employees"].add(ts.get("employee_name", ""))
    
    result = []
    for pid, data in project_hours.items():
        data["employees"] = list(data["employees"])
        data["total_hours"] = data["billable_hours"] + data["non_billable_hours"]
        result.append(data)
    
    result.sort(key=lambda x: x["billable_hours"], reverse=True)
    return result

@router.get("/employees")
async def list_employees():
    db = get_db()
    employees = await db.employees.find({}, {"_id": 0}).to_list(50)
    return employees
