"""Employee Analytics — Utilization Summary & Top Performers"""
from fastapi import APIRouter

router = APIRouter(prefix="/employee-analytics", tags=["Employee Analytics"])

db = None

def set_db(database):
    global db
    db = database

@router.get("/utilization-summary")
async def utilization_summary():
    timesheets = await db.timesheets.find({}, {"_id": 0}).to_list(500)
    emp_data = {}
    for ts in timesheets:
        eid = ts.get("employee_id", "")
        name = ts.get("employee_name", eid)
        if eid not in emp_data:
            emp_data[eid] = {"employee_id": eid, "name": name, "total_hours": 0, "billable_hours": 0}
        for entry in ts.get("entries", []):
            hours = entry.get("hours", 0)
            emp_data[eid]["total_hours"] += hours
            if entry.get("billable"):
                emp_data[eid]["billable_hours"] += hours
    result = []
    for e in emp_data.values():
        e["utilization_pct"] = round((e["billable_hours"] / e["total_hours"] * 100) if e["total_hours"] > 0 else 0, 1)
        result.append(e)
    result.sort(key=lambda x: x["utilization_pct"], reverse=True)
    return result

@router.get("/top-performers")
async def top_performers():
    summary = await utilization_summary()
    return summary[:5]
