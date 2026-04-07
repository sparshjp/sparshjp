"""Client Portal — External client access to project status, invoices, timesheets."""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
import jwt
import os

router = APIRouter(prefix="/portal")
db = None

def set_db(database):
    global db
    db = database

async def _get_portal_user(request: Request):
    token = request.headers.get("X-Portal-Token", "")
    if not token:
        raise HTTPException(status_code=401, detail="Portal token required")
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
        if payload.get("type") != "portal":
            raise HTTPException(status_code=401, detail="Invalid portal token")
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid portal token")

@router.get("/clients")
async def list_portal_clients():
    return await db.portal_clients.find({}, {"_id": 0}).to_list(100)

@router.post("/clients")
async def create_portal_client(body: dict):
    client = {
        "id": str(uuid.uuid4()),
        "client_id": body.get("client_id", ""),
        "client_name": body.get("client_name", ""),
        "contact_name": body.get("contact_name", ""),
        "email": body.get("email", ""),
        "is_active": True,
        "projects": body.get("projects", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    token = jwt.encode({"sub": client["id"], "client_id": client["client_id"], "type": "portal", "email": client["email"]}, os.environ["JWT_SECRET"], algorithm="HS256")
    client["portal_token"] = token
    await db.portal_clients.insert_one(client)
    client.pop("_id", None)
    return client

@router.put("/clients/{client_id}")
async def update_portal_client(client_id: str, body: dict):
    allowed = {"contact_name", "email", "is_active", "projects"}
    update = {k: v for k, v in body.items() if k in allowed}
    await db.portal_clients.update_one({"id": client_id}, {"$set": update})
    return await db.portal_clients.find_one({"id": client_id}, {"_id": 0})

@router.delete("/clients/{client_id}")
async def delete_portal_client(client_id: str):
    await db.portal_clients.delete_one({"id": client_id})
    return {"status": "ok"}

@router.get("/my/projects")
async def portal_my_projects(request: Request):
    user = await _get_portal_user(request)
    client_id = user.get("client_id", "")
    projects = await db.projects.find({"client_id": client_id}, {"_id": 0}).to_list(50)
    return [{"id": p.get("id"), "name": p.get("name"), "status": p.get("status"), "progress": p.get("progress", 0), "billing_type": p.get("billing_type"), "start_date": p.get("start_date"), "end_date": p.get("end_date"), "health": p.get("health")} for p in projects]

@router.get("/my/invoices")
async def portal_my_invoices(request: Request):
    user = await _get_portal_user(request)
    client_id = user.get("client_id", "")
    invoices = await db.invoices.find({"client_id": client_id}, {"_id": 0}).to_list(100)
    projects = await db.projects.find({"client_id": client_id}, {"_id": 0}).to_list(50)
    proj_ids = [p["id"] for p in projects]
    if not invoices:
        invoices = await db.invoices.find({"project_id": {"$in": proj_ids}}, {"_id": 0}).to_list(100)
    return [{"id": i.get("id"), "invoice_number": i.get("invoice_number"), "total": i.get("total", i.get("grand_total", 0)), "status": i.get("status"), "date": i.get("date", i.get("created_at", "")[:10]), "due_date": i.get("due_date")} for i in invoices]

@router.get("/my/timesheets")
async def portal_my_timesheets(request: Request):
    user = await _get_portal_user(request)
    client_id = user.get("client_id", "")
    projects = await db.projects.find({"client_id": client_id}, {"_id": 0}).to_list(50)
    proj_ids = [p["id"] for p in projects]
    timesheets = await db.timesheets.find({"project_id": {"$in": proj_ids}}, {"_id": 0}).to_list(200)
    summary = {}
    for ts in timesheets:
        for entry in ts.get("entries", []):
            pid = entry.get("project_id", ts.get("project_id", ""))
            summary.setdefault(pid, {"project_id": pid, "total_hours": 0, "billable_hours": 0})
            summary[pid]["total_hours"] += entry.get("hours", 0)
            if entry.get("billable"):
                summary[pid]["billable_hours"] += entry.get("hours", 0)
    return list(summary.values())

@router.get("/my/dashboard")
async def portal_dashboard(request: Request):
    user = await _get_portal_user(request)
    client_id = user.get("client_id", "")
    projects = await db.projects.find({"client_id": client_id}, {"_id": 0}).to_list(50)
    invoices = await db.invoices.find({"project_id": {"$in": [p["id"] for p in projects]}}, {"_id": 0}).to_list(100)
    total_invoice_amount = sum(i.get("total", i.get("grand_total", 0)) for i in invoices)
    return {
        "client_name": user.get("client_name", ""),
        "active_projects": sum(1 for p in projects if p.get("status") == "active"),
        "total_projects": len(projects),
        "total_invoiced": total_invoice_amount,
        "pending_invoices": sum(1 for i in invoices if i.get("status") in ("draft", "unpaid")),
    }
