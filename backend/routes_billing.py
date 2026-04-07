"""Billing Automation — Auto-generate invoices from timesheets and milestones."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/billing")
db = None

def set_db(database):
    global db
    db = database

@router.get("/unbilled")
async def get_unbilled():
    unbilled_ts = await db.timesheets.find({"billing_status": {"$ne": "invoiced"}}, {"_id": 0}).to_list(500)
    projects = await db.projects.find({}, {"_id": 0}).to_list(100)
    proj_map = {p["id"]: p for p in projects}
    grouped = {}
    for ts in unbilled_ts:
        pid = ts.get("project_id", "")
        proj = proj_map.get(pid, {})
        grouped.setdefault(pid, {"project_id": pid, "project_name": proj.get("name", pid), "client": proj.get("client", ""), "billing_type": proj.get("billing_type", "T&M"), "entries": [], "total_hours": 0, "total_amount": 0})
        for entry in ts.get("entries", []):
            if entry.get("billable"):
                rate = entry.get("bill_rate", proj.get("hourly_rate", 0))
                amount = entry.get("hours", 0) * rate
                grouped[pid]["entries"].append({**entry, "employee": ts.get("employee_name", ""), "week": ts.get("week", ""), "rate": rate, "amount": amount})
                grouped[pid]["total_hours"] += entry.get("hours", 0)
                grouped[pid]["total_amount"] += amount
    return list(grouped.values())

@router.post("/generate-invoice")
async def generate_invoice(body: dict):
    project_id = body.get("project_id", "")
    entries = body.get("entries", [])
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    total = sum(e.get("amount", 0) for e in entries)
    invoice = {
        "id": str(uuid.uuid4()),
        "invoice_number": f"INV-{str(uuid.uuid4())[:6].upper()}",
        "type": "sales",
        "project_id": project_id,
        "project_name": project.get("name", ""),
        "client": project.get("client", ""),
        "billing_type": body.get("billing_type", "T&M"),
        "period": body.get("period", ""),
        "line_items": entries,
        "subtotal": total,
        "tax_rate": body.get("tax_rate", 18),
        "tax_amount": round(total * body.get("tax_rate", 18) / 100, 2),
        "total": round(total * (1 + body.get("tax_rate", 18) / 100), 2),
        "currency": project.get("currency", "INR"),
        "status": "draft",
        "generated_from": "billing_automation",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.invoices.insert_one(invoice)
    invoice.pop("_id", None)
    ts_ids = list(set(e.get("timesheet_id", "") for e in entries if e.get("timesheet_id")))
    if ts_ids:
        await db.timesheets.update_many({"id": {"$in": ts_ids}}, {"$set": {"billing_status": "invoiced", "invoice_id": invoice["id"]}})
    return invoice

@router.get("/milestone-invoices")
async def get_milestone_invoices():
    contracts = await db.contracts.find({"status": "active"}, {"_id": 0}).to_list(100)
    invoiceable = []
    for c in contracts:
        for m in c.get("milestones", []):
            if m.get("status") == "completed" and not m.get("invoiced"):
                invoiceable.append({
                    "contract_id": c["id"], "contract_title": c["title"],
                    "client_name": c.get("client_name", ""),
                    "milestone_id": m["id"], "milestone_name": m.get("name", ""),
                    "amount": m.get("amount", 0), "currency": c.get("currency", "INR"),
                    "completed_at": m.get("completed_at", ""),
                })
    return invoiceable

@router.post("/milestone-invoice")
async def create_milestone_invoice(body: dict):
    contract_id = body.get("contract_id", "")
    milestone_id = body.get("milestone_id", "")
    contract = await db.contracts.find_one({"id": contract_id}, {"_id": 0})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    milestone = next((m for m in contract.get("milestones", []) if m["id"] == milestone_id), None)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    invoice = {
        "id": str(uuid.uuid4()),
        "invoice_number": f"INV-{str(uuid.uuid4())[:6].upper()}",
        "type": "milestone",
        "contract_id": contract_id, "contract_title": contract["title"],
        "client": contract.get("client_name", ""),
        "milestone_name": milestone.get("name", ""),
        "subtotal": milestone.get("amount", 0),
        "tax_rate": body.get("tax_rate", 18),
        "tax_amount": round(milestone.get("amount", 0) * body.get("tax_rate", 18) / 100, 2),
        "total": round(milestone.get("amount", 0) * (1 + body.get("tax_rate", 18) / 100), 2),
        "currency": contract.get("currency", "INR"),
        "status": "draft",
        "generated_from": "milestone_billing",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.invoices.insert_one(invoice)
    invoice.pop("_id", None)
    milestone["invoiced"] = True
    milestone["invoice_id"] = invoice["id"]
    await db.contracts.update_one({"id": contract_id}, {"$set": {"milestones": contract["milestones"]}})
    return invoice

@router.get("/stats")
async def billing_stats():
    unbilled = await db.timesheets.count_documents({"billing_status": {"$ne": "invoiced"}})
    invoiced = await db.timesheets.count_documents({"billing_status": "invoiced"})
    draft_invoices = await db.invoices.count_documents({"status": "draft", "generated_from": {"$in": ["billing_automation", "milestone_billing"]}})
    return {"unbilled_timesheets": unbilled, "invoiced_timesheets": invoiced, "draft_invoices": draft_invoices}
