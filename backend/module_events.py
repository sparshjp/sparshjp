"""Inter-module event triggers for cross-module linking.
Called by individual route modules when significant events occur."""
from datetime import datetime, timezone
import uuid

db = None

def set_db(database):
    global db
    db = database


async def on_contract_created(contract: dict):
    """Contract signed → Auto-create a Project."""
    if db is None:
        return
    project_id = f"PRJ-{str(uuid.uuid4())[:6].upper()}"
    project = {
        "id": project_id,
        "name": contract.get("title", ""),
        "client": contract.get("client_name", ""),
        "type": {"fixed": "Fixed-Price", "tm": "T&M", "retainer": "Monthly Retainer"}.get(contract.get("billing_type", ""), "T&M"),
        "pm": "",
        "status": "ACTIVE",
        "health": "GREEN",
        "pct_complete": 0,
        "value_inr": contract.get("value", 0) if contract.get("currency", "INR") == "INR" else 0,
        "value_usd": contract.get("value", 0) if contract.get("currency") == "USD" else 0,
        "currency": contract.get("currency", "INR"),
        "billing": contract.get("billing_type", "Monthly"),
        "duration": f"{contract.get('start_date', '')} to {contract.get('end_date', '')}",
        "team_names": [],
        "milestones": [
            {"id": ms.get("id", f"MS-{str(uuid.uuid4())[:4].upper()}"), "name": ms.get("name", ""), "value": ms.get("amount", 0), "currency": contract.get("currency", "INR"), "status": "Pending", "date": ms.get("due_date", "")}
            for ms in contract.get("milestones", [])
        ],
        "source_contract_id": contract.get("id"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.projects.insert_one(project)
    await _notify(f"Project {project_id} auto-created from contract {contract.get('contract_number', '')}", "info", "normal", ["creator", "admin", "project_manager"])
    return project_id


async def on_milestone_completed(contract: dict, milestone: dict):
    """Milestone completed → Create draft billing invoice + Notification."""
    if db is None:
        return
    invoice = {
        "id": f"INV-{str(uuid.uuid4())[:8].upper()}",
        "project_id": contract.get("source_project_id", ""),
        "project_name": contract.get("title", ""),
        "client": contract.get("client_name", ""),
        "contract_id": contract.get("id"),
        "period": datetime.now(timezone.utc).strftime("%Y-%m"),
        "entries": [{"description": f"Milestone: {milestone.get('name', '')}", "amount": milestone.get("amount", 0)}],
        "total_amount": milestone.get("amount", 0),
        "currency": contract.get("currency", "INR"),
        "status": "draft",
        "source": "milestone",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.invoices.insert_one(invoice)
    # Mark milestone as invoiced in contract
    await db.contracts.update_one(
        {"id": contract.get("id"), "milestones.id": milestone.get("id")},
        {"$set": {"milestones.$.invoiced": True}}
    )
    await _notify(
        f"Milestone '{milestone.get('name', '')}' completed on {contract.get('title', '')} — Draft invoice {invoice['id']} created ({invoice['total_amount']:,.0f} {invoice['currency']})",
        "reminder", "high", ["creator", "admin", "finance_manager"]
    )
    # Forex: if non-INR, create forex transaction
    if contract.get("currency", "INR") != "INR":
        await on_non_inr_invoice(invoice, contract)
    return invoice["id"]


async def on_timesheet_approved(timesheet: dict):
    """Timesheet approved → Mark entries billing-ready + Notification."""
    if db is None:
        return
    await db.timesheets.update_one(
        {"id": timesheet.get("id")},
        {"$set": {"invoiceable": True}}
    )
    total_hours = sum(e.get("hours", 0) for e in timesheet.get("entries", []) if e.get("billable"))
    await _notify(
        f"Timesheet approved for {timesheet.get('employee_name', '')} (Week {timesheet.get('week', '')}) — {total_hours}h billable ready for invoicing",
        "info", "normal", ["creator", "admin", "finance_manager"]
    )


async def on_budget_threshold(budget: dict, usage_pct: float):
    """Budget >80% → Approval request + Alert notification."""
    if db is None:
        return
    if usage_pct >= 80:
        severity = "critical" if usage_pct >= 100 else "warning"
        # Create approval request for budget override
        req = {
            "id": str(uuid.uuid4()),
            "type": "budget_override",
            "reference_name": f"Budget Override: {budget.get('name', '')}",
            "amount": sum(li.get("amount", 0) for li in budget.get("line_items", [])),
            "requester_name": "System",
            "status": "pending",
            "steps": [{"role": "admin", "label": "Admin Approval", "status": "pending"}],
            "comments": f"Auto-generated: Budget {budget.get('name', '')} at {usage_pct:.0f}% utilization",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.approval_requests.insert_one(req)
        await _notify(
            f"Budget '{budget.get('name', '')}' at {usage_pct:.0f}% — Approval required for continued spending",
            "overdue" if severity == "critical" else "reminder", "high", ["creator", "admin", "finance_manager"]
        )


async def on_approval_actioned(request: dict, action: str, by: str):
    """Approval approved/rejected → Notification to requester."""
    if db is None:
        return
    status_text = "APPROVED" if action == "approve" else "REJECTED"
    await _notify(
        f"Your request '{request.get('reference_name', '')}' has been {status_text} by {by}",
        "info", "high" if action == "reject" else "normal",
        ["creator", "admin", "finance_manager", "project_manager"]
    )


async def on_resource_allocated(allocation: dict):
    """Resource allocated → Update project team_names."""
    if db is None:
        return
    project_name = allocation.get("project_name", "")
    employee_name = allocation.get("employee_name", "")
    if project_name and employee_name:
        await db.projects.update_one(
            {"name": {"$regex": f"^{project_name}$", "$options": "i"}},
            {"$addToSet": {"team_names": employee_name}}
        )


async def on_non_inr_invoice(invoice: dict, contract: dict):
    """Non-INR invoice → Auto-create forex transaction."""
    if db is None:
        return
    rates = await db.forex_rates.find_one({"base_currency": "INR"}, {"_id": 0})
    currency = invoice.get("currency") or contract.get("currency", "USD")
    rate = (rates or {}).get("rates", {}).get(currency, 84.5)
    txn = {
        "id": str(uuid.uuid4()),
        "type": "invoice",
        "reference_name": f"Invoice {invoice.get('id', '')} — {contract.get('client_name', '')}",
        "currency": currency,
        "foreign_amount": invoice.get("total_amount", 0),
        "booking_rate": rate,
        "booking_inr": round(invoice.get("total_amount", 0) * rate, 2),
        "settled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.forex_transactions.insert_one(txn)


async def on_document_uploaded(doc: dict, user_name: str = "system"):
    """Document uploaded → Compliance access log."""
    if db is None:
        return
    log = {
        "id": str(uuid.uuid4()),
        "user_name": user_name,
        "user_id": user_name,
        "action": "document_upload",
        "resource": f"document/{doc.get('id', '')} — {doc.get('filename', '')}",
        "ip_address": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.compliance_access_logs.insert_one(log)


async def _notify(message: str, ntype: str = "info", priority: str = "normal", target_roles: list = None):
    """Internal helper to create a notification."""
    if db is None:
        return
    notif = {
        "id": str(uuid.uuid4()),
        "title": message[:80],
        "message": message,
        "type": ntype,
        "priority": priority,
        "read": False,
        "target_roles": target_roles or ["creator", "admin"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.notifications.insert_one(notif)
