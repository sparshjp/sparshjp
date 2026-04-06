"""AI Agents Module - Business Agent, Coding Agent, Testing Agent
Each agent uses Claude Sonnet 4.5 via Emergent LLM Key with specialized system prompts.
"""
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
import os
import json
import glob

router = APIRouter(prefix="/agents", tags=["AI Agents"])

EMERGENT_KEY = None
db = None

def set_config(key, database):
    global EMERGENT_KEY, db
    EMERGENT_KEY = key
    db = database

# ══════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════

BUSINESS_AGENT_PROMPT = """You are the Business Analysis Agent for Kairos AI ERP — an AI-native ERP for Nexora Digital Solutions Pvt. Ltd., an IT services company based in Ahmedabad, Gujarat.

## Your Expertise
- Indian Accounting Standards (Ind AS), Schedule III Companies Act 2013
- GST compliance: CGST/SGST/IGST computation, GSTR-1, GSTR-3B, E-Invoicing, RCM
- TDS sections: 194C (Contractors), 194J (Professional/Technical), 194I (Rent), 192 (Salary)
- Revenue Recognition (Ind AS 115): POC (cost-to-cost), T&M actuals, Milestone, Retainer straight-line
- Contract Assets (Unbilled AR) vs Contract Liabilities (Deferred Revenue)
- IT Services business: Fixed-price projects, T&M billing, Retainers, Export under LUT/STPI
- FEMA compliance for export collections (EEFC, SOFTEX, BRC)
- Transfer Pricing, STPI/STP exemptions, Section 10AA

## Company Context
- Nexora Digital Solutions Pvt. Ltd. | CIN: U72200GJ2019PTC108341 | GSTIN: 24AABCN4567P1Z8
- 8 Projects: FinTrack Portal (FP), Cloud Migration (T&M USD), Analytics Dashboard (Milestone), IT Managed Services (Retainer), PayEdge App (Export USD), DevOps Transformation (Export GBP), Data Warehouse (Milestone), Internal
- 21 Employees, 7 Clients (domestic + export USD/GBP), 10 Vendors
- Revenue: ~₹1.06 Cr March 2026, Export 55%

## ERP Modules Available
CRM, Selling (Invoices/Credit Notes), Buying (PO→GRN→Invoice→Payment), Stock & Manufacturing, HR & Payroll, Project Management, Timesheets & Utilization, Revenue Recognition (Ind AS 115), Journal Entries, Chart of Accounts, Financial Statements (BS/P&L/TB), AP/AR Aging, Audit Trail, GST (GSTR-1/3B), E-Invoicing, TDS Returns

## MongoDB Collections
entities (vendors/customers with GSTIN), employees, projects (with milestones), timesheets, erp_transactions (140 transactions), revenue_schedule, chart_of_accounts (26 accounts, TB balanced ₹2.81Cr), purchase_orders, selling_invoices, journal_entries, audit_trail, company_settings

## Your Role
1. Understand business requirements from the user in plain English
2. Analyze impact on accounting, compliance, and existing modules
3. Translate into structured technical specifications that the Coding Agent can implement
4. Flag compliance risks, Ind AS implications, and edge cases
5. Suggest the correct ERP workflow and document flow

When producing technical specs, output them in this format:
```
TECHNICAL SPEC:
- Module: [which ERP module]
- Collection(s): [MongoDB collections affected]
- API Route(s): [endpoints needed]
- Frontend Component: [page/component]
- Business Logic: [step by step]
- Accounting Entries: [Dr/Cr journal entries]
- Compliance Notes: [GST, TDS, Ind AS implications]
```

Always think from the perspective of a Chartered Accountant + Business Analyst."""

CODING_AGENT_PROMPT = """You are the Coding Agent for Kairos AI ERP — an AI-native ERP built with:

## Tech Stack
- **Backend**: FastAPI (Python), Motor (async MongoDB), uvicorn
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI components, Lucide React icons
- **Database**: MongoDB (collections listed below)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (Emergent LLM Key)
- **Routing**: All backend routes prefixed with /api, FastAPI APIRouter pattern
- **State**: React useState/useEffect, axios for API calls

## Project Structure
```
/app/backend/
  server.py              — Main FastAPI app, includes all routers
  ai_orchestrator.py     — AI prompt processing for all modules
  gst_rules.py           — GST state codes, tax computation
  audit_trail.py         — Companies Act 2013 audit logging
  routes_purchase.py     — PO → GRN → Invoice → Payment flow
  routes_selling.py      — SO → Invoice → Collection flow
  routes_stock.py        — Inventory, BOM, work orders
  routes_company.py      — Company settings, Reporting AI
  routes_statutory.py    — GSTR-1, GSTR-3B, E-Invoice, TDS
  routes_audit.py        — Audit trail queries
  routes_gst.py          — GST computation, HSN validation
  routes_aging.py        — AP/AR aging buckets
  routes_projects.py     — Project management, health dashboard
  routes_timesheets.py   — Timesheets, utilization, consolidation
  routes_revenue.py      — Revenue recognition, Ind AS 115

/app/frontend/src/
  App.js                 — Main router, sidebar, layout
  pages/
    Dashboard.js, CompanySetup.js, VendorsPage.js, CustomersPage.js, ItemsPage.js
    ProjectsModule.js, TimesheetsPage.js, RevenueRecognition.js, TransactionExplorer.js
    FinancialStatements.js, AgingReport.js, AuditTrail.js
    GSTR1Page.js, GSTR3BPage.js, EInvoicingPage.js, TDSPage.js
  components/
    ui/  (Shadcn components: button, card, dialog, input, select, table, tabs, etc.)
    AISmartEntry.js, KairosIcon.js
```

## Key Patterns
- Routes: `router = APIRouter(prefix="/module", tags=["module"])`
- DB access: `db = None; def set_db(database): global db; db = database`
- MongoDB: Always exclude `_id` from responses: `find({}, {"_id": 0})`
- IDs: `str(uuid.uuid4())` for all document IDs
- Timestamps: `datetime.now(timezone.utc).isoformat()`
- Frontend API: `const API = process.env.REACT_APP_BACKEND_URL + '/api'`
- Components: Shadcn UI from `../components/ui/[name]`
- Styling: Dark theme (#0A1628 bg, #152236 cards, #1B2D42 borders, #E8EDF2 text, #00d4aa accent)
- Audit: `await audit_trail.log_audit(action, doc_type, doc_id, doc_name, ...)`

## MongoDB Collections & Schemas
- `entities`: {id, entity_type, name, gstin, state, state_code, payment_terms, credit_limit}
- `employees`: {id, name, role, dept, ctc, bill_rate, location, billable}
- `projects`: {id, name, client, type, value_inr, currency, milestones, health, pct_complete, pm, team}
- `timesheets`: {id, employee_id, employee_name, week, week_start, entries: [{project_id, hours, billable}]}
- `erp_transactions`: {id, date, module, type, priority, prompt, accounting, integrity}
- `revenue_schedule`: {project_id, method, total, rev_mar, billed_to_mar, contract_asset, contract_liability}
- `chart_of_accounts`: {id, ledger_name, category, sub_category, opening_balance, current_balance}
- `purchase_orders`: {id, po_number, vendor, items, grand_total, status, grn_status}
- `selling_invoices`: {id, invoice_number, customer, items, grand_total, status}
- `journal_entries`: {id, account, debit, credit, posting_date}
- `audit_trail`: {id, action, module, record_id, changes, timestamp}
- `company_settings`: {company_name, gstin, cin, state, logo_url}

## Your Role
1. Receive technical specs (from Business Agent or user directly)
2. Generate production-ready Python (backend) and React (frontend) code
3. Follow existing patterns exactly — match code style, naming, structure
4. Handle edge cases: MongoDB ObjectId serialization, GST computation, audit logging
5. Output complete, runnable code — not pseudocode

When generating code, always specify:
- **File path**: Exact path where code should go
- **Action**: CREATE new file / MODIFY existing file (with before/after)
- **Dependencies**: Any new packages needed

You can also READ existing files to understand current implementation before suggesting changes."""

TESTING_AGENT_PROMPT = """You are the Testing Agent for Kairos AI ERP. You have READ-ONLY access to the MongoDB database and can run validation queries.

## Your Capabilities
1. **Data Integrity Checks**: Verify TB balance, AR/AP aging accuracy, GST computation
2. **Schema Validation**: Check all documents have required fields
3. **Business Rule Validation**: Ensure linked document flows (PO→GRN→Invoice→Payment)
4. **Compliance Checks**: GST state codes, TDS sections, Ind AS 115 contract balances
5. **Cross-Collection Consistency**: Revenue schedule vs project milestones, timesheets vs billing

## Company Context
- Nexora Digital Solutions Pvt. Ltd., IT Services
- Opening TB: Dr = Cr = ₹2,81,42,000
- 8 Projects, 21 Employees, 7 Clients, 10 Vendors, 140 Transactions, 27 Timesheets

## MongoDB Collections Available
entities, employees, projects, timesheets, erp_transactions, revenue_schedule, chart_of_accounts, purchase_orders, selling_invoices, journal_entries, audit_trail, company_settings, monthly_hours

## Test Categories You Can Run
- **TB Balance**: Sum all debit balances = sum all credit balances
- **Entity Validation**: All vendors/customers have GSTIN, state_code
- **Project Health**: All projects have required fields, milestones sum to project value
- **Timesheet Integrity**: Hours per week ≤ 40 (or flagged OT), all entries have project_id
- **Revenue Schedule**: Contract assets + liabilities reconcile, methods are valid
- **Transaction Coverage**: All 8 modules represented, all have prompt/accounting/integrity
- **GST Compliance**: Company GSTIN format valid, state codes match GSTIN prefix
- **Aging Accuracy**: AP/AR aging buckets compute correctly from invoice dates

When asked to test, run the relevant queries and report:
```
TEST REPORT:
✅ PASS: [test name] — [details]
❌ FAIL: [test name] — [expected] vs [actual]
⚠️ WARNING: [observation]
Summary: X/Y tests passed
```

You should also suggest additional tests based on what you find. Be thorough and flag even minor inconsistencies."""

# ══════════════════════════════════════════════════════════
# CONVERSATION STORAGE
# ══════════════════════════════════════════════════════════

@router.get("/sessions")
async def list_sessions():
    sessions = await db.agent_sessions.find({}, {"_id": 0}).sort("updated_at", -1).to_list(50)
    return sessions

@router.post("/sessions")
async def create_session(body: dict):
    session = {
        "id": str(uuid.uuid4()),
        "agent_type": body.get("agent_type", "business"),
        "title": body.get("title", "New Session"),
        "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_sessions.insert_one(session)
    return {k: v for k, v in session.items() if k != "_id"}

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    await db.agent_sessions.delete_one({"id": session_id})
    return {"status": "deleted"}

# ══════════════════════════════════════════════════════════
# CODING AGENT — FILE ACCESS
# ══════════════════════════════════════════════════════════

ALLOWED_DIRS = ["/app/backend", "/app/frontend/src"]
BLOCKED_PATTERNS = [".env", "node_modules", "__pycache__", ".git", ".emergent"]

def is_safe_path(path):
    for blocked in BLOCKED_PATTERNS:
        if blocked in path:
            return False
    for allowed in ALLOWED_DIRS:
        if path.startswith(allowed):
            return True
    return False

@router.get("/coding/files")
async def list_files(directory: str = "/app/backend"):
    if not is_safe_path(directory):
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        files = []
        for f in sorted(glob.glob(f"{directory}/**", recursive=True)):
            if os.path.isfile(f) and is_safe_path(f):
                rel = f.replace("/app/", "")
                ext = os.path.splitext(f)[1]
                if ext in [".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".md"]:
                    files.append({"path": f, "relative": rel, "size": os.path.getsize(f), "ext": ext})
        return files[:200]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coding/read-file")
async def read_file(body: dict):
    path = body.get("path", "")
    if not is_safe_path(path):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(path, "r") as f:
            content = f.read()
        if len(content) > 50000:
            content = content[:50000] + "\n\n... [TRUNCATED — file too large] ..."
        return {"path": path, "content": content, "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coding/write-file")
async def write_file(body: dict):
    path = body.get("path", "")
    content = body.get("content", "")
    if not is_safe_path(path):
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        # Log to audit trail
        await db.audit_trail.insert_one({
            "id": str(uuid.uuid4()),
            "action": "FILE_WRITE",
            "module": "AI_CODING_AGENT",
            "record_id": path,
            "record_name": os.path.basename(path),
            "changes": [{"field": "content", "new_value": f"File written ({len(content)} chars)"}],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": "coding-agent",
        })
        return {"status": "written", "path": path, "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════════════════
# TESTING AGENT — DB QUERIES
# ══════════════════════════════════════════════════════════

@router.post("/testing/query")
async def run_test_query(body: dict):
    """Run a predefined test query against MongoDB"""
    query_type = body.get("query_type", "")
    results = {}

    if query_type == "tb_balance":
        coa = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        total_dr = sum(max(0, e["opening_balance"]) for e in coa)
        total_cr = sum(max(0, -e["opening_balance"]) for e in coa)
        results = {"total_debit": total_dr, "total_credit": total_cr, "balanced": total_dr == total_cr, "difference": total_dr - total_cr, "accounts_count": len(coa)}

    elif query_type == "entity_validation":
        vendors = await db.entities.find({"entity_type": "vendor"}, {"_id": 0}).to_list(100)
        customers = await db.entities.find({"entity_type": "customer"}, {"_id": 0}).to_list(100)
        vendor_issues = [v["name"] for v in vendors if not v.get("gstin") or not v.get("state_code")]
        customer_issues = [c["name"] for c in customers if not c.get("gstin") or not c.get("state_code")]
        results = {"vendors": len(vendors), "customers": len(customers), "vendor_issues": vendor_issues, "customer_issues": customer_issues}

    elif query_type == "project_health":
        projects = await db.projects.find({"id": {"$ne": "PRJ-INT"}}, {"_id": 0}).to_list(20)
        issues = []
        for p in projects:
            if not p.get("name"): issues.append(f"{p['id']}: missing name")
            if not p.get("client"): issues.append(f"{p['id']}: missing client")
            if p.get("milestones"):
                ms_total = sum(m.get("value", 0) for m in p["milestones"])
                if p.get("value_inr") and abs(ms_total - p["value_inr"]) > 1:
                    issues.append(f"{p['id']}: milestones sum {ms_total} != project value {p['value_inr']}")
        results = {"projects": len(projects), "issues": issues}

    elif query_type == "timesheet_integrity":
        timesheets = await db.timesheets.find({}, {"_id": 0}).to_list(500)
        issues = []
        for ts in timesheets:
            if ts["total_hours"] > 45:
                issues.append(f"{ts['employee_name']} {ts['week']}: {ts['total_hours']}h (>45h)")
            for entry in ts.get("entries", []):
                if not entry.get("project_id"):
                    issues.append(f"{ts['employee_name']} {ts['week']}: entry missing project_id")
        results = {"timesheets": len(timesheets), "issues": issues}

    elif query_type == "revenue_schedule":
        schedule = await db.revenue_schedule.find({}, {"_id": 0}).to_list(20)
        total_assets = sum(s.get("contract_asset", 0) or 0 for s in schedule)
        total_liabilities = sum(s.get("contract_liability", 0) or 0 for s in schedule)
        total_rev = sum(s.get("rev_mar", 0) or 0 for s in schedule)
        results = {"entries": len(schedule), "total_revenue_march": total_rev, "contract_assets": total_assets, "contract_liabilities": total_liabilities}

    elif query_type == "transaction_coverage":
        txns = await db.erp_transactions.find({}, {"_id": 0, "module": 1, "priority": 1}).to_list(500)
        mod_counts = {}
        pri_counts = {}
        for t in txns:
            m = t.get("module", "Unknown")
            p = t.get("priority", "Unknown")
            mod_counts[m] = mod_counts.get(m, 0) + 1
            pri_counts[p] = pri_counts.get(p, 0) + 1
        missing_fields = sum(1 for t in txns if not t.get("module"))
        results = {"total": len(txns), "by_module": mod_counts, "by_priority": pri_counts, "missing_module": missing_fields}

    elif query_type == "gst_compliance":
        company = await db.company_settings.find_one({}, {"_id": 0})
        gstin = company.get("gstin", "")
        state_code = company.get("state_code", "")
        gstin_valid = len(gstin) == 15 and gstin[:2] == state_code
        vendors = await db.entities.find({"entity_type": "vendor"}, {"_id": 0}).to_list(100)
        invalid_gstin = [v["name"] for v in vendors if v.get("gstin") not in ["IMPORT", "EXPORT"] and v.get("gstin_valid") is False]
        results = {"company_gstin": gstin, "gstin_format_valid": gstin_valid, "invalid_vendor_gstin": invalid_gstin}

    elif query_type == "collection_stats":
        collections = await db.list_collection_names()
        stats = {}
        for col in sorted(collections):
            if col != "agent_sessions":
                count = await db[col].count_documents({})
                stats[col] = count
        results = {"collections": stats, "total_collections": len(stats)}

    elif query_type == "full_health_check":
        # Run all checks
        coa = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        total_dr = sum(max(0, e["opening_balance"]) for e in coa)
        total_cr = sum(max(0, -e["opening_balance"]) for e in coa)

        vendors = await db.entities.find({"entity_type": "vendor"}, {"_id": 0}).to_list(100)
        customers = await db.entities.find({"entity_type": "customer"}, {"_id": 0}).to_list(100)
        projects = await db.projects.find({}, {"_id": 0}).to_list(20)
        timesheets = await db.timesheets.find({}, {"_id": 0}).to_list(500)
        txns = await db.erp_transactions.find({}, {"_id": 0}).to_list(500)
        schedule = await db.revenue_schedule.find({}, {"_id": 0}).to_list(20)
        employees = await db.employees.find({}, {"_id": 0}).to_list(50)

        results = {
            "tb_balanced": total_dr == total_cr,
            "tb_total": total_dr,
            "accounts": len(coa),
            "vendors": len(vendors),
            "customers": len(customers),
            "projects": len(projects),
            "employees": len(employees),
            "timesheets": len(timesheets),
            "transactions": len(txns),
            "revenue_entries": len(schedule),
        }
    else:
        results = {"error": f"Unknown query type: {query_type}", "available": [
            "tb_balance", "entity_validation", "project_health", "timesheet_integrity",
            "revenue_schedule", "transaction_coverage", "gst_compliance", "collection_stats", "full_health_check"
        ]}

    return {"query_type": query_type, "results": results, "timestamp": datetime.now(timezone.utc).isoformat()}

# ══════════════════════════════════════════════════════════
# MAIN CHAT ENDPOINT
# ══════════════════════════════════════════════════════════

@router.post("/chat")
async def agent_chat(body: dict):
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    agent_type = body.get("agent_type", "business")
    message = body.get("message", "")
    session_id = body.get("session_id", "")
    context = body.get("context", "")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Select system prompt
    if agent_type == "business":
        system_prompt = BUSINESS_AGENT_PROMPT
    elif agent_type == "coding":
        system_prompt = CODING_AGENT_PROMPT
    elif agent_type == "testing":
        system_prompt = TESTING_AGENT_PROMPT
    else:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

    # Get conversation history
    history = []
    if session_id:
        session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
        if session:
            history = session.get("messages", [])

    # For testing agent — auto-run relevant queries and inject context
    test_context = ""
    if agent_type == "testing":
        msg_lower = message.lower()
        queries_to_run = []
        if any(w in msg_lower for w in ["tb", "trial balance", "balance", "all", "full", "health", "everything"]):
            queries_to_run.append("tb_balance")
        if any(w in msg_lower for w in ["vendor", "customer", "entity", "gstin", "all", "full", "health"]):
            queries_to_run.append("entity_validation")
        if any(w in msg_lower for w in ["project", "milestone", "all", "full", "health"]):
            queries_to_run.append("project_health")
        if any(w in msg_lower for w in ["timesheet", "hours", "utilization", "all", "full", "health"]):
            queries_to_run.append("timesheet_integrity")
        if any(w in msg_lower for w in ["revenue", "ind as", "contract", "all", "full", "health"]):
            queries_to_run.append("revenue_schedule")
        if any(w in msg_lower for w in ["transaction", "coverage", "all", "full", "health"]):
            queries_to_run.append("transaction_coverage")
        if any(w in msg_lower for w in ["gst", "compliance", "all", "full", "health"]):
            queries_to_run.append("gst_compliance")
        if any(w in msg_lower for w in ["collection", "stats", "count", "all", "full", "health"]):
            queries_to_run.append("collection_stats")
        if not queries_to_run:
            queries_to_run = ["full_health_check"]

        test_results = []
        for qt in queries_to_run:
            r = await run_test_query({"query_type": qt})
            test_results.append(r)
        test_context = f"\n\n[LIVE DATABASE QUERY RESULTS]\n{json.dumps(test_results, indent=2, default=str)}"

    # For coding agent — inject file context if requested
    code_context = ""
    if agent_type == "coding" and context:
        code_context = f"\n\n[FILE CONTEXT PROVIDED]\n{context}"

    # Build message with context
    full_message = message
    if test_context:
        full_message += test_context
    if code_context:
        full_message += code_context

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"agent-{agent_type}-{session_id or uuid.uuid4()}",
            system_message=system_prompt
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        # Send history for context
        for h in history[-10:]:
            if h["role"] == "user":
                await chat.send_message(UserMessage(text=h["content"]))
            # Assistant messages are implicitly in the session

        response = await chat.send_message(UserMessage(text=full_message))

        # Save to session
        if session_id:
            new_messages = [
                {"role": "user", "content": message, "timestamp": datetime.now(timezone.utc).isoformat()},
                {"role": "assistant", "content": response, "agent_type": agent_type, "timestamp": datetime.now(timezone.utc).isoformat()},
            ]
            # Auto-title from first message
            update = {
                "$push": {"messages": {"$each": new_messages}},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
            session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
            if session and len(session.get("messages", [])) == 0:
                update["$set"]["title"] = message[:80]
            await db.agent_sessions.update_one({"id": session_id}, update)

        return {
            "response": response,
            "agent_type": agent_type,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
