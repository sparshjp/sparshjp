"""Approval Workflows — Configurable approval chains for PO, invoices, expenses."""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/approvals")
db = None

def set_db(database):
    global db
    db = database

WORKFLOW_TYPES = ["purchase_order", "sales_invoice", "expense", "journal_entry", "leave_request", "timesheet"]

@router.get("/workflows")
async def list_workflows():
    items = await db.approval_workflows.find({}, {"_id": 0}).to_list(100)
    return items

@router.post("/workflows")
async def create_workflow(body: dict):
    wf = {
        "id": str(uuid.uuid4()),
        "name": body.get("name", ""),
        "type": body.get("type", "purchase_order"),
        "steps": body.get("steps", []),
        "threshold_amount": body.get("threshold_amount", 0),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if wf["type"] not in WORKFLOW_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid type. Use: {WORKFLOW_TYPES}")
    await db.approval_workflows.insert_one(wf)
    wf.pop("_id", None)
    return wf

@router.put("/workflows/{wf_id}")
async def update_workflow(wf_id: str, body: dict):
    update = {k: v for k, v in body.items() if k in ("name", "steps", "threshold_amount", "is_active")}
    await db.approval_workflows.update_one({"id": wf_id}, {"$set": update})
    wf = await db.approval_workflows.find_one({"id": wf_id}, {"_id": 0})
    return wf

@router.delete("/workflows/{wf_id}")
async def delete_workflow(wf_id: str):
    await db.approval_workflows.delete_one({"id": wf_id})
    return {"status": "ok"}

@router.get("/requests")
async def list_requests(status: str = None, type: str = None):
    query = {}
    if status:
        query["status"] = status
    if type:
        query["type"] = type
    items = await db.approval_requests.find(query, {"_id": 0}).sort("created_at", -1).to_list(200)
    return items

@router.post("/requests")
async def create_request(body: dict):
    wf_type = body.get("type", "purchase_order")
    amount = body.get("amount", 0)
    workflows = await db.approval_workflows.find({"type": wf_type, "is_active": True}, {"_id": 0}).to_list(10)
    matched_wf = None
    for wf in sorted(workflows, key=lambda w: w.get("threshold_amount", 0), reverse=True):
        if amount >= wf.get("threshold_amount", 0):
            matched_wf = wf
            break
    if not matched_wf and workflows:
        matched_wf = workflows[0]
    steps = matched_wf.get("steps", []) if matched_wf else [{"role": "admin", "label": "Admin Approval"}]
    req = {
        "id": str(uuid.uuid4()),
        "type": wf_type,
        "reference_id": body.get("reference_id", ""),
        "reference_name": body.get("reference_name", ""),
        "amount": amount,
        "requester": body.get("requester", ""),
        "requester_name": body.get("requester_name", ""),
        "workflow_id": matched_wf["id"] if matched_wf else None,
        "steps": [{"role": s.get("role", "admin"), "label": s.get("label", ""), "status": "pending", "approved_by": None, "approved_at": None, "comments": ""} for s in steps],
        "current_step": 0,
        "status": "pending",
        "comments": body.get("comments", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.approval_requests.insert_one(req)
    req.pop("_id", None)
    return req

@router.post("/requests/{req_id}/approve")
async def approve_request(req_id: str, body: dict):
    req = await db.approval_requests.find_one({"id": req_id}, {"_id": 0})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")
    step_idx = req["current_step"]
    if step_idx >= len(req["steps"]):
        raise HTTPException(status_code=400, detail="No pending steps")
    req["steps"][step_idx]["status"] = "approved"
    req["steps"][step_idx]["approved_by"] = body.get("approved_by", "")
    req["steps"][step_idx]["approved_at"] = datetime.now(timezone.utc).isoformat()
    req["steps"][step_idx]["comments"] = body.get("comments", "")
    if step_idx + 1 >= len(req["steps"]):
        req["status"] = "approved"
    else:
        req["current_step"] = step_idx + 1
    await db.approval_requests.update_one({"id": req_id}, {"$set": {"steps": req["steps"], "current_step": req["current_step"], "status": req["status"]}})
    # Event: Approval actioned → Notification
    import module_events
    await module_events.on_approval_actioned(req, "approve", body.get("approved_by", "admin"))
    return req

@router.post("/requests/{req_id}/reject")
async def reject_request(req_id: str, body: dict):
    req = await db.approval_requests.find_one({"id": req_id}, {"_id": 0})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    step_idx = req["current_step"]
    if step_idx < len(req["steps"]):
        req["steps"][step_idx]["status"] = "rejected"
        req["steps"][step_idx]["approved_by"] = body.get("rejected_by", "")
        req["steps"][step_idx]["approved_at"] = datetime.now(timezone.utc).isoformat()
        req["steps"][step_idx]["comments"] = body.get("comments", "")
    req["status"] = "rejected"
    await db.approval_requests.update_one({"id": req_id}, {"$set": {"steps": req["steps"], "status": "rejected"}})
    # Event: Rejection → Notification
    import module_events
    await module_events.on_approval_actioned(req, "reject", body.get("rejected_by", "admin"))
    return req

@router.get("/pending/{role}")
async def get_pending_for_role(role: str):
    reqs = await db.approval_requests.find({"status": "pending"}, {"_id": 0}).to_list(200)
    result = []
    for r in reqs:
        idx = r.get("current_step", 0)
        if idx < len(r.get("steps", [])) and r["steps"][idx].get("role") == role:
            result.append(r)
    return result

@router.get("/stats")
async def approval_stats():
    pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}, "total_amount": {"$sum": "$amount"}}}]
    stats = await db.approval_requests.aggregate(pipeline).to_list(10)
    return {s["_id"]: {"count": s["count"], "total_amount": s["total_amount"]} for s in stats if s["_id"]}
