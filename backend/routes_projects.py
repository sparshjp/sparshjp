"""Project Management routes"""
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/projects", tags=["Projects"])

def get_db():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

@router.get("")
async def list_projects():
    db = get_db()
    projects = await db.projects.find({}, {"_id": 0}).to_list(100)
    return projects

@router.get("/{project_id}")
async def get_project(project_id: str):
    db = get_db()
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/transactions")
async def get_project_transactions(project_id: str):
    db = get_db()
    txns = await db.erp_transactions.find(
        {"$or": [
            {"prompt": {"$regex": project_id, "$options": "i"}},
            {"module": "Projects", "type": {"$regex": project_id, "$options": "i"}}
        ]},
        {"_id": 0}
    ).to_list(500)
    return txns

@router.get("/{project_id}/timesheets")
async def get_project_timesheets(project_id: str):
    db = get_db()
    timesheets = await db.timesheets.find(
        {"entries.project_id": project_id},
        {"_id": 0}
    ).to_list(500)
    result = []
    for ts in timesheets:
        proj_hours = sum(e["hours"] for e in ts.get("entries", []) if e.get("project_id") == project_id)
        billable_hours = sum(e["hours"] for e in ts.get("entries", []) if e.get("project_id") == project_id and e.get("billable"))
        result.append({
            "employee_id": ts.get("employee_id"),
            "employee_name": ts.get("employee_name"),
            "week": ts.get("week"),
            "week_start": ts.get("week_start"),
            "week_end": ts.get("week_end"),
            "total_project_hours": proj_hours,
            "billable_hours": billable_hours,
            "status": ts.get("status"),
        })
    return result

@router.get("/health/dashboard")
async def project_health_dashboard():
    db = get_db()
    projects = await db.projects.find({"id": {"$ne": "PRJ-INT"}}, {"_id": 0}).to_list(20)
    
    # Get timesheet hours per project
    timesheets = await db.timesheets.find({}, {"_id": 0}).to_list(500)
    project_hours = {}
    for ts in timesheets:
        for entry in ts.get("entries", []):
            pid = entry.get("project_id", "")
            if pid.startswith("PRJ-"):
                if pid not in project_hours:
                    project_hours[pid] = {"billable": 0, "non_billable": 0}
                if entry.get("billable"):
                    project_hours[pid]["billable"] += entry.get("hours", 0)
                else:
                    project_hours[pid]["non_billable"] += entry.get("hours", 0)
    
    result = []
    for p in projects:
        pid = p["id"]
        hours = project_hours.get(pid, {"billable": 0, "non_billable": 0})
        result.append({
            "id": pid,
            "name": p["name"],
            "client": p["client"],
            "type": p["type"],
            "health": p.get("health", "GREEN"),
            "status": p.get("status", ""),
            "pct_complete": p.get("pct_complete"),
            "currency": p.get("currency", "INR"),
            "value_inr": p.get("value_inr"),
            "value_usd": p.get("value_usd"),
            "billable_hours": hours["billable"],
            "non_billable_hours": hours["non_billable"],
            "team_count": len(p.get("team_names", [])),
            "pm": p.get("pm", ""),
        })
    return result

@router.put("/{project_id}/status")
async def update_project_status(project_id: str, body: dict):
    db = get_db()
    update_fields = {}
    for key in ["status", "health", "pct_complete"]:
        if key in body:
            update_fields[key] = body[key]
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.projects.update_one({"id": project_id}, {"$set": update_fields})
    return {"status": "updated"}
