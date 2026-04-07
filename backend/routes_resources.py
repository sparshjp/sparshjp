"""Resource Planning — Bench management, skill matrix, project staffing forecast."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/resources")
db = None

def set_db(database):
    global db
    db = database

@router.get("/allocations")
async def list_allocations(employee_id: str = None, project_id: str = None):
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if project_id:
        query["project_id"] = project_id
    return await db.resource_allocations.find(query, {"_id": 0}).to_list(500)

@router.post("/allocations")
async def create_allocation(body: dict):
    alloc = {
        "id": str(uuid.uuid4()),
        "employee_id": body.get("employee_id", ""),
        "employee_name": body.get("employee_name", ""),
        "project_id": body.get("project_id", ""),
        "project_name": body.get("project_name", ""),
        "role": body.get("role", ""),
        "allocation_pct": body.get("allocation_pct", 100),
        "start_date": body.get("start_date", ""),
        "end_date": body.get("end_date", ""),
        "billable": body.get("billable", True),
        "bill_rate": body.get("bill_rate", 0),
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.resource_allocations.insert_one(alloc)
    alloc.pop("_id", None)
    # Event: Resource allocated → Update project team
    import module_events
    await module_events.on_resource_allocated(alloc)
    return alloc

@router.put("/allocations/{alloc_id}")
async def update_allocation(alloc_id: str, body: dict):
    allowed = {"allocation_pct", "end_date", "role", "billable", "bill_rate", "status"}
    update = {k: v for k, v in body.items() if k in allowed}
    await db.resource_allocations.update_one({"id": alloc_id}, {"$set": update})
    return await db.resource_allocations.find_one({"id": alloc_id}, {"_id": 0})

@router.delete("/allocations/{alloc_id}")
async def delete_allocation(alloc_id: str):
    await db.resource_allocations.delete_one({"id": alloc_id})
    return {"status": "ok"}

@router.get("/skills")
async def list_skills():
    return await db.employee_skills.find({}, {"_id": 0}).to_list(500)

@router.post("/skills")
async def upsert_skills(body: dict):
    emp_id = body.get("employee_id", "")
    skills = body.get("skills", [])
    record = {
        "employee_id": emp_id,
        "employee_name": body.get("employee_name", ""),
        "skills": skills,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.employee_skills.update_one({"employee_id": emp_id}, {"$set": record}, upsert=True)
    return await db.employee_skills.find_one({"employee_id": emp_id}, {"_id": 0})

@router.get("/bench")
async def get_bench():
    allocs = await db.resource_allocations.find({"status": "active"}, {"_id": 0}).to_list(1000)
    emp_alloc = {}
    for a in allocs:
        eid = a["employee_id"]
        emp_alloc.setdefault(eid, {"name": a["employee_name"], "total_pct": 0, "projects": []})
        emp_alloc[eid]["total_pct"] += a.get("allocation_pct", 0)
        emp_alloc[eid]["projects"].append({"project": a["project_name"], "pct": a.get("allocation_pct", 0)})
    employees = await db.employees.find({}, {"_id": 0}).to_list(500)
    bench = []
    for emp in employees:
        eid = emp.get("id", "")
        alloc_info = emp_alloc.get(eid, {"total_pct": 0, "projects": []})
        available_pct = max(0, 100 - alloc_info["total_pct"])
        if available_pct > 0:
            skills = await db.employee_skills.find_one({"employee_id": eid}, {"_id": 0})
            bench.append({
                "employee_id": eid, "name": emp.get("name", ""),
                "department": emp.get("department", ""), "designation": emp.get("designation", ""),
                "allocated_pct": alloc_info["total_pct"], "available_pct": available_pct,
                "projects": alloc_info["projects"],
                "skills": skills.get("skills", []) if skills else [],
            })
    return sorted(bench, key=lambda b: b["available_pct"], reverse=True)

@router.get("/forecast")
async def staffing_forecast():
    projects = await db.projects.find({"status": {"$in": ["active", "planned"]}}, {"_id": 0}).to_list(100)
    allocs = await db.resource_allocations.find({"status": "active"}, {"_id": 0}).to_list(500)
    proj_allocs = {}
    for a in allocs:
        proj_allocs.setdefault(a["project_id"], []).append(a)
    forecast = []
    for p in projects:
        pid = p.get("id", "")
        team = proj_allocs.get(pid, [])
        total_allocation = sum(a.get("allocation_pct", 0) for a in team) / 100
        forecast.append({
            "project_id": pid, "project_name": p.get("name", ""),
            "status": p.get("status", ""), "end_date": p.get("end_date", ""),
            "team_size": len(team), "total_fte": round(total_allocation, 1),
            "billable_fte": round(sum(a.get("allocation_pct", 0) for a in team if a.get("billable")) / 100, 1),
        })
    return forecast

@router.get("/utilization")
async def resource_utilization():
    allocs = await db.resource_allocations.find({"status": "active"}, {"_id": 0}).to_list(1000)
    total_employees = await db.employees.count_documents({})
    allocated_employees = len(set(a["employee_id"] for a in allocs))
    total_pct = sum(a.get("allocation_pct", 0) for a in allocs)
    avg_util = (total_pct / (total_employees * 100) * 100) if total_employees else 0
    billable_pct = sum(a.get("allocation_pct", 0) for a in allocs if a.get("billable"))
    billable_ratio = (billable_pct / total_pct * 100) if total_pct else 0
    return {
        "total_employees": total_employees, "allocated": allocated_employees,
        "on_bench": total_employees - allocated_employees,
        "avg_utilization": round(avg_util, 1), "billable_ratio": round(billable_ratio, 1),
    }
