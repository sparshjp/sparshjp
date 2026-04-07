"""Budget Management — Department/project budgets, actuals vs budget, overspend alerts."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/budgets")
db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_budgets(fiscal_year: str = None):
    query = {}
    if fiscal_year:
        query["fiscal_year"] = fiscal_year
    items = await db.budgets.find(query, {"_id": 0}).to_list(200)
    return items

@router.post("")
async def create_budget(body: dict):
    budget = {
        "id": str(uuid.uuid4()),
        "name": body.get("name", ""),
        "type": body.get("type", "department"),
        "department": body.get("department", ""),
        "project_id": body.get("project_id", ""),
        "fiscal_year": body.get("fiscal_year", "2025-26"),
        "line_items": body.get("line_items", []),
        "total_budget": sum(li.get("amount", 0) for li in body.get("line_items", [])),
        "total_actual": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.budgets.insert_one(budget)
    budget.pop("_id", None)
    return budget

@router.put("/{budget_id}")
async def update_budget(budget_id: str, body: dict):
    update = {}
    for k in ("name", "line_items", "status", "department", "project_id"):
        if k in body:
            update[k] = body[k]
    if "line_items" in update:
        update["total_budget"] = sum(li.get("amount", 0) for li in update["line_items"])
    await db.budgets.update_one({"id": budget_id}, {"$set": update})
    return await db.budgets.find_one({"id": budget_id}, {"_id": 0})

@router.delete("/{budget_id}")
async def delete_budget(budget_id: str):
    await db.budgets.delete_one({"id": budget_id})
    return {"status": "ok"}

@router.post("/{budget_id}/record-expense")
async def record_expense(budget_id: str, body: dict):
    budget = await db.budgets.find_one({"id": budget_id}, {"_id": 0})
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    category = body.get("category", "")
    amount = body.get("amount", 0)
    for li in budget.get("line_items", []):
        if li.get("category") == category:
            li["actual"] = li.get("actual", 0) + amount
    total_actual = sum(li.get("actual", 0) for li in budget.get("line_items", []))
    await db.budgets.update_one({"id": budget_id}, {"$set": {"line_items": budget["line_items"], "total_actual": total_actual}})
    return await db.budgets.find_one({"id": budget_id}, {"_id": 0})

@router.get("/variance")
async def budget_variance(fiscal_year: str = "2025-26"):
    budgets = await db.budgets.find({"fiscal_year": fiscal_year}, {"_id": 0}).to_list(100)
    result = []
    for b in budgets:
        total_budget = b.get("total_budget", 0)
        total_actual = b.get("total_actual", 0)
        variance = total_budget - total_actual
        variance_pct = (variance / total_budget * 100) if total_budget else 0
        alert = "over_budget" if variance < 0 else ("warning" if variance_pct < 10 else "on_track")
        result.append({
            "id": b["id"], "name": b["name"], "type": b["type"],
            "department": b.get("department", ""), "project_id": b.get("project_id", ""),
            "total_budget": total_budget, "total_actual": total_actual,
            "variance": variance, "variance_pct": round(variance_pct, 1), "alert": alert,
            "line_items": [{**li, "variance": li.get("amount", 0) - li.get("actual", 0)} for li in b.get("line_items", [])],
        })
    return result

@router.get("/alerts")
async def budget_alerts():
    budgets = await db.budgets.find({"status": "active"}, {"_id": 0}).to_list(100)
    alerts = []
    for b in budgets:
        total = b.get("total_budget", 0)
        actual = b.get("total_actual", 0)
        if total > 0:
            usage = (actual / total) * 100
            if usage >= 100:
                alerts.append({"budget_id": b["id"], "name": b["name"], "severity": "critical", "message": f"Budget exceeded by {round(actual - total):,}", "usage_pct": round(usage, 1)})
            elif usage >= 80:
                alerts.append({"budget_id": b["id"], "name": b["name"], "severity": "warning", "message": f"{round(usage)}% of budget consumed", "usage_pct": round(usage, 1)})
    return sorted(alerts, key=lambda a: a["usage_pct"], reverse=True)
