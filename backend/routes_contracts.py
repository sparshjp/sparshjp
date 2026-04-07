"""Contract Management — SOW/MSA tracking, renewals, billing milestones."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
import uuid

router = APIRouter(prefix="/contracts")
db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_contracts(status: str = None, client_id: str = None):
    query = {}
    if status:
        query["status"] = status
    if client_id:
        query["client_id"] = client_id
    return await db.contracts.find(query, {"_id": 0}).sort("end_date", 1).to_list(200)

@router.post("")
async def create_contract(body: dict):
    contract = {
        "id": str(uuid.uuid4()),
        "contract_number": body.get("contract_number", f"CTR-{str(uuid.uuid4())[:6].upper()}"),
        "type": body.get("type", "msa"),
        "title": body.get("title", ""),
        "client_id": body.get("client_id", ""),
        "client_name": body.get("client_name", ""),
        "project_id": body.get("project_id", ""),
        "start_date": body.get("start_date", ""),
        "end_date": body.get("end_date", ""),
        "value": body.get("value", 0),
        "currency": body.get("currency", "INR"),
        "billing_type": body.get("billing_type", "fixed"),
        "milestones": body.get("milestones", []),
        "auto_renew": body.get("auto_renew", False),
        "renewal_period_months": body.get("renewal_period_months", 12),
        "notice_period_days": body.get("notice_period_days", 30),
        "terms": body.get("terms", ""),
        "status": "active",
        "documents": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    for i, m in enumerate(contract["milestones"]):
        m["id"] = m.get("id", str(uuid.uuid4())[:8])
        m["status"] = m.get("status", "pending")
        m["invoiced"] = m.get("invoiced", False)
    await db.contracts.insert_one(contract)
    contract.pop("_id", None)
    return contract

@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    c = await db.contracts.find_one({"id": contract_id}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail="Contract not found")
    return c

@router.put("/{contract_id}")
async def update_contract(contract_id: str, body: dict):
    allowed = {"title", "end_date", "value", "milestones", "auto_renew", "renewal_period_months", "notice_period_days", "terms", "status"}
    update = {k: v for k, v in body.items() if k in allowed}
    await db.contracts.update_one({"id": contract_id}, {"$set": update})
    return await db.contracts.find_one({"id": contract_id}, {"_id": 0})

@router.post("/{contract_id}/milestones/{ms_id}/complete")
async def complete_milestone(contract_id: str, ms_id: str, body: dict):
    c = await db.contracts.find_one({"id": contract_id}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail="Contract not found")
    for m in c.get("milestones", []):
        if m["id"] == ms_id:
            m["status"] = "completed"
            m["completed_at"] = datetime.now(timezone.utc).isoformat()
            m["completed_by"] = body.get("completed_by", "")
    await db.contracts.update_one({"id": contract_id}, {"$set": {"milestones": c["milestones"]}})
    return c

@router.get("/alerts/renewals")
async def renewal_alerts():
    cutoff = (datetime.now(timezone.utc) + timedelta(days=60)).strftime("%Y-%m-%d")
    contracts = await db.contracts.find({"status": "active", "end_date": {"$lte": cutoff}}, {"_id": 0}).to_list(50)
    alerts = []
    for c in contracts:
        try:
            end = datetime.strptime(c["end_date"], "%Y-%m-%d")
            days_left = (end - datetime.now()).days
            alerts.append({
                "contract_id": c["id"], "title": c["title"], "client_name": c.get("client_name", ""),
                "end_date": c["end_date"], "days_remaining": days_left,
                "auto_renew": c.get("auto_renew", False),
                "severity": "critical" if days_left <= 7 else ("warning" if days_left <= 30 else "info"),
            })
        except (ValueError, KeyError):
            pass
    return sorted(alerts, key=lambda a: a["days_remaining"])

@router.get("/stats/summary")
async def contract_stats():
    pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}, "total_value": {"$sum": "$value"}}}]
    stats = await db.contracts.aggregate(pipeline).to_list(10)
    return {s["_id"]: {"count": s["count"], "total_value": s["total_value"]} for s in stats if s["_id"]}
