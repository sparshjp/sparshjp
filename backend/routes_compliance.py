"""Audit & Compliance Dashboard — SOC2/ISO readiness, data access logs."""
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import uuid

router = APIRouter(prefix="/compliance")
db = None

def set_db(database):
    global db
    db = database

FRAMEWORKS = {
    "soc2": {
        "name": "SOC 2 Type II",
        "controls": [
            {"id": "CC1.1", "category": "Control Environment", "title": "Integrity and Ethical Values", "status": "compliant"},
            {"id": "CC2.1", "category": "Communication", "title": "Internal Communication", "status": "partial"},
            {"id": "CC3.1", "category": "Risk Assessment", "title": "Risk Identification", "status": "compliant"},
            {"id": "CC5.1", "category": "Control Activities", "title": "Access Controls", "status": "compliant"},
            {"id": "CC6.1", "category": "Logical Access", "title": "Authentication", "status": "compliant"},
            {"id": "CC6.2", "category": "Logical Access", "title": "Authorization", "status": "compliant"},
            {"id": "CC6.3", "category": "Logical Access", "title": "Role-Based Access", "status": "compliant"},
            {"id": "CC7.1", "category": "System Operations", "title": "Change Management", "status": "partial"},
            {"id": "CC8.1", "category": "Change Mgmt", "title": "Change Authorization", "status": "partial"},
            {"id": "CC9.1", "category": "Risk Mitigation", "title": "Vendor Management", "status": "non_compliant"},
        ]
    },
    "iso27001": {
        "name": "ISO 27001:2022",
        "controls": [
            {"id": "A.5.1", "category": "Policies", "title": "Information Security Policy", "status": "partial"},
            {"id": "A.6.1", "category": "Organization", "title": "Security Roles", "status": "compliant"},
            {"id": "A.7.1", "category": "HR Security", "title": "Background Checks", "status": "non_compliant"},
            {"id": "A.8.1", "category": "Asset Mgmt", "title": "Asset Inventory", "status": "compliant"},
            {"id": "A.8.2", "category": "Asset Mgmt", "title": "Data Classification", "status": "partial"},
            {"id": "A.9.1", "category": "Access Control", "title": "Access Policy", "status": "compliant"},
            {"id": "A.9.2", "category": "Access Control", "title": "User Registration", "status": "compliant"},
            {"id": "A.12.1", "category": "Operations", "title": "Operational Procedures", "status": "partial"},
            {"id": "A.12.4", "category": "Operations", "title": "Logging & Monitoring", "status": "compliant"},
            {"id": "A.18.1", "category": "Compliance", "title": "Legal Requirements", "status": "partial"},
        ]
    }
}

@router.get("/frameworks")
async def list_frameworks():
    result = {}
    for fw_id, fw in FRAMEWORKS.items():
        controls = fw["controls"]
        saved = await db.compliance_controls.find({"framework": fw_id}, {"_id": 0}).to_list(100)
        saved_map = {s["control_id"]: s for s in saved}
        merged = []
        for c in controls:
            s = saved_map.get(c["id"], {})
            merged.append({**c, "status": s.get("status", c["status"]), "notes": s.get("notes", ""), "evidence": s.get("evidence", ""), "last_reviewed": s.get("last_reviewed", "")})
        compliant = sum(1 for c in merged if c["status"] == "compliant")
        result[fw_id] = {"name": fw["name"], "total_controls": len(merged), "compliant": compliant, "partial": sum(1 for c in merged if c["status"] == "partial"), "non_compliant": sum(1 for c in merged if c["status"] == "non_compliant"), "readiness_pct": round(compliant / len(merged) * 100) if merged else 0, "controls": merged}
    return result

@router.put("/controls/{framework}/{control_id}")
async def update_control(framework: str, control_id: str, body: dict):
    update = {"framework": framework, "control_id": control_id, "status": body.get("status", "partial"), "notes": body.get("notes", ""), "evidence": body.get("evidence", ""), "last_reviewed": datetime.now(timezone.utc).isoformat(), "reviewed_by": body.get("reviewed_by", "")}
    await db.compliance_controls.update_one({"framework": framework, "control_id": control_id}, {"$set": update}, upsert=True)
    return update

@router.get("/access-logs")
async def get_access_logs(limit: int = 100):
    return await db.access_logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(min(limit, 500))

@router.post("/access-logs")
async def log_access(body: dict):
    log = {"id": str(uuid.uuid4()), "user_id": body.get("user_id", ""), "user_name": body.get("user_name", ""), "action": body.get("action", ""), "resource": body.get("resource", ""), "ip_address": body.get("ip_address", ""), "timestamp": datetime.now(timezone.utc).isoformat(), "details": body.get("details", "")}
    await db.access_logs.insert_one(log)
    log.pop("_id", None)
    return log

@router.get("/dashboard")
async def compliance_dashboard():
    frameworks = await list_frameworks()
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    recent_logs = await db.access_logs.count_documents({"timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}})
    pending_approvals = await db.approval_requests.count_documents({"status": "pending"})
    return {
        "frameworks": {fw_id: {"name": fw["name"], "readiness_pct": fw["readiness_pct"], "compliant": fw["compliant"], "total": fw["total_controls"]} for fw_id, fw in frameworks.items()},
        "user_stats": {"total": total_users, "active": active_users},
        "activity": {"access_logs_7d": recent_logs, "pending_approvals": pending_approvals},
        "rbac_enabled": True,
        "encryption_at_rest": False,
        "audit_trail_enabled": True,
    }
