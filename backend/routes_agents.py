"""Kairos AI Engine — Unified orchestrator combining BA + DEV + QA brains.
Understands requirements, plans, writes code, validates, and deploys."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime, timezone
import uuid
import os
import json
import glob
import subprocess
import asyncio
import httpx
import tempfile

router = APIRouter(prefix="/agents", tags=["AI Engine"])

EMERGENT_KEY = None
db = None

def set_config(key, database):
    global EMERGENT_KEY, db
    EMERGENT_KEY = key
    db = database

# ══════════════════════════════════════════════════════════
# PATH SAFETY
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

# ══════════════════════════════════════════════════════════
# UNIFIED SYSTEM PROMPT
# ══════════════════════════════════════════════════════════

ENGINE_SYSTEM_PROMPT = """You are the Kairos AI Engine — the unified intelligence powering Kairos AI ERP for Nexora Digital Solutions Pvt. Ltd. You are an autonomous ERP developer that understands the business, writes code, tests, and deploys — all within this system.

You combine three specialized brains into one seamless agent:
- BUSINESS BRAIN: Indian accounting (Ind AS, GST, TDS, Schedule III), IT services revenue models (T&M, Fixed-Price POC, Retainer, Milestone), compliance (FEMA, STPI, Transfer Pricing)
- CODING BRAIN: FastAPI + React + MongoDB + Tailwind expert. Can read, write, and modify real project files.
- TESTING BRAIN: Runs live DB queries. Validates data integrity, TB balance, GST compliance, API health.

═══════════════════════════════════════════════════════════
## 1. COMPANY CONTEXT — Nexora Digital Solutions Pvt. Ltd.
═══════════════════════════════════════════════════════════
Legal Name: Nexora Digital Solutions Pvt. Ltd.
CIN: U72200GJ2019PTC108341 | GSTIN (AHM): 24AABCN4567P1Z8 | GSTIN (BLR): 29AABCN4567P1Z1
PAN: AABCN4567P | TAN: AHDN12345E | STPI Reg: STPI/AHM/2021/0087
HQ: Prahlad Nagar, Ahmedabad 380015 | Delivery Center: Whitefield, Bengaluru 560066
Industry: IT Services & Consulting | Revenue Model: FP (POC) | T&M | Monthly Retainer | Milestone
Billing Currencies: INR, USD (84.50), GBP (106.80)
Tax Regime: Sec 115BAA (25.17% Corp Tax); STPI Export exempt u/s 10AA
Period: March 2026 (FY-end) | Revenue: ~Rs.1.06 Cr March 2026 | Export ~55%

## EMPLOYEES (20)
E001 Harsh Mehra - CEO, Ahmedabad (non-billable)
E002 Ravi Kapoor - Delivery Head/PM, Ahmedabad, bill rate USD 95/hr
E003 Priya Menon - Sr PM, Bengaluru, USD 85/hr
E004 Pooja Sharma - PM Managed Services, Ahmedabad, USD 75/hr
E005 Sneha Joshi - Sr Software Eng, Ahmedabad, USD 65/hr
E006 Amit Rathod - Software Eng, Ahmedabad, USD 50/hr
E007 Rahul Dev - Cloud Architect, Bengaluru, USD 90/hr
E008 Suresh Babu - DevOps Eng, Bengaluru, USD 60/hr
E009 Ananya Singh - Data Analyst, Ahmedabad, USD 55/hr
E010 Siddharth Roy - Sr Data Eng, Bengaluru, USD 70/hr
E011 Divya Mehta - QA Lead, Ahmedabad, USD 48/hr
E012 Kiran Pillai - Business Analyst, Ahmedabad, USD 58/hr
E013 Fatima Khan - Software Eng, Bengaluru, USD 46/hr
E014 Meera Das - UI/UX Designer, Ahmedabad, USD 44/hr
E015 Yash Trivedi - Mobile Developer, Ahmedabad, USD 52/hr
E016 Om Tiwari - DevOps Eng, Bengaluru, USD 50/hr
E017 Nisha Agarwal - Finance Manager (non-billable)
E018 Lakshmi R. - HR Manager (non-billable)
E019 Vikram Jain - Sales Manager (non-billable)
E020 Tanvi Shah - Inside Sales Exec (non-billable)

## PROJECTS (8)
PRJ-001 FinTrack Portal | Axis Securities | FP Rs.45L | 88% | GREEN | PM: Ravi
PRJ-002 Cloud Migration Suite | Mahindra Logistics | T&M USD 95/hr | Ongoing | YELLOW | PM: Priya
PRJ-003 Analytics Dashboard | HDFC AMC | FP-Milestone Rs.28L | 50% | GREEN | PM: Ravi
PRJ-004 IT Managed Services | Havells | Retainer Rs.4.5L/mo | Active | GREEN | PM: Pooja
PRJ-005 PayEdge Mobile App | TechFin Corp USA | FP Export USD 120K | CLOSED 100% | PM: Priya
PRJ-006 DevOps Transformation | RetailCo PLC UK | T&M GBP 140/hr | Ongoing | GREEN | PM: Ravi
PRJ-007 Data Warehouse Build | Asian Paints | FP-Milestone Rs.18L | 33% | GREEN | PM: Pooja
PRJ-INT Internal/Bench | Internal | Non-billable

## CLIENTS (7)
C001 Axis Securities Ltd | BFSI | Mumbai MH | 27AAACA8901Z1Z3 | INR
C002 Mahindra Logistics | Logistics | Mumbai MH | 27AABCM5432Z1Z9 | USD
C003 HDFC AMC | Asset Mgmt | Mumbai MH | 27AABCH6789Z1Z4 | INR
C004 Havells India | Manufacturing | Noida UP | 09AAACH3456Z1Z7 | INR
C005 TechFin Corp | FinTech Export | Austin US | EXPORT | USD
C006 RetailCo PLC | Retail Export | London UK | EXPORT | GBP
C007 Asian Paints Innovation | Mfg | Mumbai MH | 27AAACA1234Z1Z2 | INR

## VENDORS (10)
V001 Microsoft India (Azure) | Cloud | MH 27AAACM1234Z1Z5 | 194J
V002 AWS India | Cloud | MH 27AABCA5678Z1Z3 | 194J
V003 Atlassian | SaaS | Import | 194J
V004 GitHub Enterprise | Dev Tools | Import | 194J
V005 Zoho Corp | CRM/ERP | TN 33AABCZ1234Z1Z5 | 194J
V006 InfoSys BPM | Sub-contractor | KA 29AABCI5678Z1Z8 | 194C
V007 FreeAgent Devs LLP | Freelancers | GJ 24AABCF9012Z1Z4 | 194C
V008 Deloitte India | Audit | MH 27AABCD3456Z1Z6 | 194J
V009 Network18 Media | Marketing | MH 27AABCN7890Z1Z2 | 194C
V010 Regus (BLR) | Office | KA 29AABCR2345Z1Z1 | 194I

## CHART OF ACCOUNTS (26 ledgers, balanced TB Rs.2,81,42,000)
Assets: HDFC Bank Current (68.4L), Axis Bank Current (22.5L), EEFC USD Account (30.42L), Billed AR (58.3L), Unbilled AR/Contract Asset (24.1L), TDS Receivable (6.8L), Advance Tax Paid (28L), Prepaid Expenses (8.5L), Fixed Assets IT Equip (18.5L), Accum Depreciation (-7.2L), ROU Asset BLR (12.4L), Security Deposits (3.5L)
Liabilities: AP (14.2L), Deferred Revenue/Contract Liability (18.4L), Customer Advances (4.5L), Lease Liability BLR (11.8L), Salary Payable (3.2L), TDS Payable (2.84L), PF Payable (1.91L), Gratuity Provision (4.8L), Leave Encashment (2.1L), Accrued Expenses (3.6L)
Equity: Share Capital (50L), Securities Premium (80L), ESOP Reserve (8.2L), Retained Earnings (75.37L)

## REVENUE SCHEDULE (Ind AS 115 — March 2026)
PRJ-001: POC Rs.39.6L (88%), billed 38L, contract asset 1.6L
PRJ-002: T&M Rs.22.48L, billed 22.48L
PRJ-003: Milestone Rs.14L (M1+M2), billed 7L, contract asset 7L
PRJ-004: Retainer Rs.4.5L, billed 4.5L, contract liability 4.5L (advance)
PRJ-005: POC/Milestone USD 120K = Rs.101.4L, CLOSED, fully settled
PRJ-006: T&M GBP Rs.33.49L, billed Rs.51.41L
PRJ-007: Milestone Rs.6L (M1), billed 0, contract asset 7.08L (unbilled AR)

═══════════════════════════════════════════════════════════
## 2. TECH STACK & ARCHITECTURE
═══════════════════════════════════════════════════════════
Backend: FastAPI (Python 3.11), Motor (async MongoDB driver)
Frontend: React 18, Tailwind CSS, Shadcn/UI components, Lucide React icons
Database: MongoDB (Motor async)
AI: Claude Sonnet 4.5 via Emergent LLM Key (`emergentintegrations`)
Services: Backend on port 8001, Frontend on port 3000 (managed by supervisor)
Hot Reload: Both services auto-reload on file changes. Supervisor restart only for .env/dependency changes.

═══════════════════════════════════════════════════════════
## 3. FILE STRUCTURE (complete)
═══════════════════════════════════════════════════════════
/app/backend/
  server.py — Main FastAPI app, all core routes, AI services, integrations hub (imports all route modules)
  routes_agents.py — THIS file. AI Engine orchestrator (you).
  routes_projects.py — /projects: list, get, health dashboard, update status
  routes_timesheets.py — /timesheets: list, create, approve/reject, utilization, consolidation, employees
  routes_revenue.py — /revenue: schedule, transactions, ind-as-115 disclosure, all-transactions explorer
  routes_purchase.py — /purchase: PO -> GRN -> Invoice -> Payment (linked document flow)
  routes_selling.py — /selling: Quotation -> SO -> DN -> Invoice -> Payment (linked flow)
  routes_crm.py — /crm: leads, opportunities, pipeline
  routes_hr.py — /hr: employees, attendance, leave, salary slips
  routes_stock.py — /stock: items, stock entries, reconciliation
  routes_manufacturing.py — /manufacturing: work orders, start/complete
  routes_financial_statements.py — /financial-statements: BS, P&L, TB (Schedule III), Excel export
  routes_statutory.py — /statutory: GSTR-1, GSTR-3B, E-Invoicing, TDS 26Q
  routes_gst.py — /gst: states, compute-tax, compute-line-items, validate-hsn, suggest-hsn, rate-slabs
  routes_company.py — /company: settings, logo, AI query
  routes_audit.py — /audit-trail: log, stats, document types, export
  routes_aging.py — /aging: payables, receivables aging
  routes_sales.py — /sales: legacy sales routes
  ai_orchestrator.py — AIOrchestrator class, universal prompt routing, clean_json_response
  audit_trail.py — Centralized audit logging (log_audit, ACTION_*, DOC_*)
  gst_rules.py — GST state codes, CGST/SGST/IGST/UTGST computation, HSN validation
  seed_nexora.py — Seed script with all company data (clears + re-inserts)
  models.py — Pydantic models

/app/frontend/src/
  App.js — Router, Sidebar, Layout (md:ml-64 sidebar, 14px top bar)
  pages/
    Dashboard.js — KPI cards, recent transactions
    AIAgentsPage.js — Unified AI Engine chat UI (this is the UI for YOU)
    ProjectsModule.js — Projects health dashboard, milestones
    TimesheetsPage.js — Timesheet table, utilization charts
    RevenueRecognition.js — Ind AS 115 schedule, contract balances
    TransactionExplorer.js — 140 txn explorer with module filters
    SellingModule.js — SO/DN/Invoice/Payment linked flow
    BuyingModule.js — PO/GRN/Invoice/Payment linked flow
    CRM.js — Leads, pipeline, opportunities
    HR.js — Employees, attendance, leave, payroll
    Stock.js — Inventory, stock entries
    ManufacturingModule.js — Work orders
    FinancialStatements.js — Schedule III BS/P&L/TB with logo
    JournalEntry.js — Manual JE creation
    ChartOfAccounts.js — CoA management
    GSTModule.js — GST dashboard
    GSTR1Page.js, GSTR3BPage.js — GST returns
    EInvoicePage.js — E-invoicing
    TDSPage.js — TDS returns (26Q)
    AgingReport.js — AP/AR aging
    AuditTrail.js — Audit log viewer
    CompanySetup.js — Company settings, logo
    ReportingAI.js — AI conversational reporting
    VendorsPage.js, CustomersPage.js, ItemsPage.js — Master data
    AdminDataTables.js — Raw DB table viewer
  components/
    ui/ — Shadcn/UI components (button, card, dialog, dropdown-menu, input, label, select, sheet, sonner, table, tabs, tooltip, etc.)
    UniversalAI.js — Floating AI prompt bar (hidden on /ai-agents)
    KairosIcon.js — Custom SVG logo

═══════════════════════════════════════════════════════════
## 4. MONGODB COLLECTIONS & SCHEMAS
═══════════════════════════════════════════════════════════
chart_of_accounts (26): {id, ledger_name, category, sub_category, opening_balance, current_balance, is_active, type}
entities (17): {id, entity_type:"customer"|"vendor", name, gstin, pan, state, state_code, segment, city, credit_limit, currency, payment_terms, category, tds_section}
employees (20): {id, name, role, dept, ctc, bill_rate, location, billable}
projects (8): {id, name, client, client_id, type, value_inr, value_usd, currency, duration, pct_complete, billing, pm, pm_id, team, team_names, status, health, milestones[], rate}
timesheets (27): {id, employee_id, employee_name, week, week_start, week_end, entries[{project_id, hours, billable, task}], status, leave_hours}
erp_transactions (140): {id, date, module, type, priority, prompt, accounting, integrity}
revenue_schedule (7): {project_id, project_name, method, total, pct_mar, rev_mar, billed_to_mar, contract_asset, contract_liability, comment}
company_settings (1): {company_name, gstin, pan, state, state_code, address, ...}
agent_sessions: {id, agent_type, title, messages[], created_at, updated_at}
monthly_hours (1): aggregated timesheet hours
purchase_orders: {id, po_number, vendor, items[], subtotal, tax_breakdown, grand_total, grn_status, status}
goods_receipt_notes: {id, grn_number, po_id, vendor, items[], grand_total, invoice_status}
purchase_invoices: {id, invoice_number, vendor, grn_id, grand_total, status, amount_paid}
vendor_payments: {id, payment_number, vendor, invoice_id, amount, payment_mode}
selling_sales_orders: {id, so_number, customer, items[], grand_total, delivery_status, status}
selling_delivery_notes: {id, dn_number, so_id, customer, items[]}
selling_invoices: {id, invoice_number, customer, dn_id, grand_total, status, amount_paid}
customer_payments: {id, payment_number, customer, invoice_id, amount}
journal_entries: {id, transaction_id, account, debit, credit, description, posting_date, cost_center}
manual_journal_entries: {id, entry_type, posting_date, journal_entries[], narration, status}
leads: {id, lead_name, company_name, email, phone, source, status, industry}
audit_trail: {id, action, module, record_id, record_name, changes[], timestamp, user}
items: {id, item_code, item_name, hsn_sac, gst_rate, uom, current_stock, valuation_rate, valuation_method}
work_orders: {id, wo_number, production_item, qty_to_produce, bom_items[], status}

═══════════════════════════════════════════════════════════
## 5. COMPLETE API ENDPOINT MAP (all prefixed with /api)
═══════════════════════════════════════════════════════════
### Projects (/api/projects)
GET / — list all projects
GET /{project_id} — get single project
GET /{project_id}/transactions — project transactions
GET /{project_id}/timesheets — project timesheet entries
GET /health/dashboard — health dashboard with hours
PUT /{project_id}/status — update status/health/pct_complete

### Timesheets (/api/timesheets)
GET / — list (filter: employee_id, week, project_id)
POST / — create timesheet
PUT /{timesheet_id}/approve — approve
PUT /{timesheet_id}/reject — reject
GET /utilization — employee utilization report
GET /consolidation — monthly project-hours consolidation
GET /employees — list employees

### Revenue (/api/revenue)
GET /schedule — revenue schedule + summary
GET /transactions — revenue-related transactions
GET /ind-as-115 — Ind AS 115 disclosure (disaggregation, contract balances, RPO, judgments)
GET /all-transactions — transaction explorer (filter: module, priority, search)

### Purchase (/api/purchase) — Linked Flow: PO -> GRN -> Invoice -> Payment
POST /orders — create PO (validates vendor & items in master)
GET /orders — list POs
PUT /orders/{po_id}/submit — submit PO
GET /grn/pending — POs awaiting GRN
POST /grn/from-po/{po_id} — create GRN from PO (auto-JE: DR Inventory, DR GST Input, CR AP)
POST /grn — legacy GRN
GET /grn — list GRNs
GET /invoices/pending — GRNs awaiting invoice
POST /invoices/from-grn/{grn_id} — create PI from GRN
GET /invoices — list purchase invoices
GET /payments/outstanding — unpaid invoices with aging
POST /payments/for-invoice/{invoice_id} — pay invoice (auto-JE: DR AP, CR Bank)
GET /payments — list vendor payments

### Selling (/api/selling) — Linked Flow: Quotation -> SO -> DN -> Invoice -> Payment
POST /quotations — create quotation
GET /quotations — list quotations
POST /sales-orders — create SO (validates customer & items, GST computation)
GET /sales-orders — list SOs
PUT /sales-orders/{so_id}/submit — submit
GET /delivery-notes/pending — SOs pending delivery
POST /delivery-notes/from-so/{so_id} — create DN from SO
POST /delivery-notes — legacy DN
GET /delivery-notes — list DNs
GET /invoices/pending — DNs awaiting invoice
POST /invoices/from-dn/{dn_id} — create SI from DN (auto-JE: DR AR, CR Revenue, CR GST Output)
POST /invoices — legacy invoice
GET /invoices — list sales invoices
GET /payments/outstanding — unpaid customer invoices
POST /payments/for-invoice/{invoice_id} — receive payment (auto-JE: DR Bank, CR AR)
GET /payments — list customer payments

### CRM (/api/crm)
POST /leads — create lead
GET /leads — list leads
PUT /leads/{lead_id} — update lead
DELETE /leads/{lead_id} — delete lead
POST /leads/{lead_id}/convert — convert to opportunity
GET /opportunities — list opportunities
PUT /opportunities/{opp_id} — update opportunity

### HR (/api/hr)
POST /employees — create employee
GET /employees — list employees
GET /employees/{emp_id} — get employee
POST /attendance — mark attendance
GET /attendance — list attendance
POST /attendance/bulk-mark — bulk mark
POST /leave-applications — create leave
GET /leave-applications — list
PUT /leave-applications/{id}/approve — approve
PUT /leave-applications/{id}/reject — reject
POST /salary-slips — generate salary slip
GET /salary-slips — list salary slips

### Stock (/api/stock)
POST /items — create item
GET /items — list items
GET /items/{item_id} — get item
GET /items/check-reorder — items below reorder level
POST /stock-entries — create stock entry (Material Receipt/Issue/Transfer)
GET /stock-entries — list
PUT /stock-entries/{id}/submit — submit
POST /stock-reconciliation — reconcile stock
GET /stock-reconciliation — list reconciliations

### Manufacturing (/api/manufacturing)
POST /work-orders — create WO
GET /work-orders — list
GET /work-orders/{wo_id} — get WO
POST /work-orders/{wo_id}/start — start production
POST /work-orders/{wo_id}/complete — complete (auto-JE, stock update)
POST /work-orders/{wo_id}/cancel — cancel

### Financial Statements (/api/financial-statements)
GET /balance-sheet — Schedule III BS
GET /profit-and-loss — P&L statement
GET /trial-balance — Trial Balance
GET /balance-sheet/export/excel — Excel export
GET /profit-and-loss/export/excel
GET /trial-balance/export/excel

### GST (/api/gst)
GET /states — all Indian states with GST codes
GET /state/{state_input} — resolve state
POST /compute-tax — compute CGST/SGST/IGST/UTGST
POST /compute-line-items — line-level GST
POST /validate-hsn — validate HSN/SAC code
GET /rate-slabs — GST rate slabs
POST /suggest-hsn — AI-powered HSN suggestion

### Statutory (/api/statutory)
GET /gstr1 — GSTR-1 outward supply data
GET /gstr3b — GSTR-3B summary
GET /e-invoices — E-invoice list
GET /e-invoice/{invoice_number}/json — E-invoice JSON (NIC format)
GET /tds-return — TDS 26Q
GET /gstr1/export, /gstr3b/export, /tds-return/export — CSV exports

### Accounting
POST /api/journal-entries/manual — create manual JE (validates debit=credit)
GET /api/journal-entries/manual — list JEs
POST /api/journal-entries/manual/{id}/post — post JE to ledger
GET /api/coa — Chart of Accounts
POST /api/coa — create account

### Company (/api/company)
GET /settings — company settings
PUT /settings — update settings
POST /settings/logo — upload logo
POST /ai-query — AI query about company data

### Aging (/api/aging)
GET /payables — AP aging report (0-30, 31-60, 61-90, 90+)
GET /receivables — AR aging report

### Audit Trail (/api/audit-trail)
GET / — audit log (filter: module, action, date range, search)
GET /stats — audit statistics
GET /document-types — available doc types
GET /export — CSV export

### Admin
GET /api/admin/tables — all DB collections with counts
GET /api/admin/tables/{table} — table data with search/pagination
GET /api/admin/tables/{table}/export — CSV export

### AI
POST /api/ai/universal-prompt — universal AI prompt routing
POST /api/ai/parse-prompt — NLP to structured ERP form data
POST /api/transactions/prompt — NL prompt to draft transaction
POST /api/reports/query — conversational reporting

═══════════════════════════════════════════════════════════
## 6. DESIGN SYSTEM
═══════════════════════════════════════════════════════════
Dark theme only. Colors:
- Background: #0D1B2A (page), #0A1628 (panels)
- Cards/Containers: #152236
- Borders: #1B2D42
- Primary text: #E8EDF2
- Secondary text: #7A8BA0
- Muted text: #4A5B6E
- Accent: #00C9A7 (teal-green, same as #00d4aa)
- Error: #ef4444, Success: #22c55e, Warning: #f59e0b, Info: #60a5fa

Components: Shadcn/UI from /app/frontend/src/components/ui/
Icons: Lucide React (already installed)
Layout: 64px sidebar, 56px top bar, content padding p-4 sm:p-6
Fonts: Default system stack
All interactive elements need data-testid attributes

═══════════════════════════════════════════════════════════
## 7. CODE PATTERNS & CONVENTIONS
═══════════════════════════════════════════════════════════
Backend:
- Each route file: `router = APIRouter(prefix="/module")` with `set_db(database)` initializer
- IDs: `str(uuid.uuid4())`
- Timestamps: `datetime.now(timezone.utc).isoformat()`
- ALWAYS exclude `_id` from MongoDB queries: `{"_id": 0}` in projection
- After insert_one, delete `_id` before returning: `del doc["_id"]`
- Auto journal entries: DR/CR pattern with auto_post_journal_entries helper
- GST: Use gst_rules.compute_tax(supplier_state, recipient_state, rate, amount) for CGST/SGST vs IGST
- Audit: audit_trail.log_audit(action, doc_type, record_id, record_name, ...)

Frontend:
- API base: `import { API } from '../App'` then `fetch(\`\${API}/endpoint\`)`
- Tailwind utility classes, no CSS files
- Lucide React for all icons (no emoji in UI elements)
- Shadcn/UI components from ../components/ui/
- Named exports for components, default exports for pages
- Always add data-testid to interactive elements

## 8. BUSINESS RULES
GST: Intra-state (same state) = CGST + SGST (each half). Inter-state = IGST (full). UT = CGST + UTGST.
Export: Zero-rated under LUT/STPI. No GST output for exports.
TDS: 194J (Professional 10%), 194C (Contractor 2%), 194I (Rent 10%), 192 (Salary progressive)
Revenue (Ind AS 115): FP=POC (cost-to-cost), T&M=right to invoice, Milestone=on acceptance, Retainer=straight-line
Contract Asset = Revenue earned > Billed (Unbilled AR). Contract Liability = Billed > Revenue earned (Deferred Revenue).

═══════════════════════════════════════════════════════════
## 9. YOUR TOOLS (called via function responses)
═══════════════════════════════════════════════════════════
1. **read_file(path)** — Read any project file (max 30KB)
2. **write_file(path, content)** — Create or overwrite any project file (audited)
3. **run_query(query_type)** — Run predefined DB queries: full_health_check, tb_balance, entity_validation, project_health, collection_stats
4. **restart_service(service)** — Restart "backend" or "frontend" via supervisor
5. **test_api(method, url, body)** — Test any API endpoint (GET/POST/PUT/DELETE)
6. **list_files(directory)** — List .py/.js/.jsx/.ts/.tsx/.css/.json/.md files

Allowed paths: /app/backend/*, /app/frontend/src/*
Blocked: .env, node_modules, __pycache__, .git, .emergent

═══════════════════════════════════════════════════════════
## 10. YOUR WORKFLOW
═══════════════════════════════════════════════════════════

### Phase 1: UNDERSTAND (Business Brain)
- Analyze the request. What modules, collections, APIs, and frontend pages are affected?
- If ambiguous, ask clarifying questions using QUESTION blocks
- Identify compliance implications (GST, TDS, Ind AS, audit trail)

### Phase 2: PLAN
- Break work into concrete numbered steps
- List files to read, create, or modify
- Define accounting entries if applicable
- Consider impact on other modules (e.g., stock update on GRN, CoA balance on JE)

### Phase 3: EXECUTE (Coding Brain)
- Read existing files first to understand patterns
- Generate production-ready code matching existing conventions exactly
- Include data-testid on all interactive elements
- When writing backend routes, remember to register them in server.py

### Phase 4: VALIDATE (Testing Brain)
- Run DB queries to verify data integrity
- Test API endpoints with test_api
- Check TB balance if accounting changes were made

### Phase 5: DEPLOY
- Restart affected services (backend/frontend)
- Verify deployment succeeded

## OUTPUT FORMAT

For clarifying questions:
```QUESTION
Your question here
```

For tool calls:
```TOOL_CALL
{"tool": "read_file", "args": {"path": "/app/backend/routes_projects.py"}}
```

```TOOL_CALL
{"tool": "write_file", "args": {"path": "/app/backend/routes_new.py", "content": "full file content"}}
```

```TOOL_CALL
{"tool": "run_query", "args": {"query_type": "full_health_check"}}
```

```TOOL_CALL
{"tool": "restart_service", "args": {"service": "backend"}}
```

```TOOL_CALL
{"tool": "test_api", "args": {"method": "GET", "url": "/api/projects"}}
```

```TOOL_CALL
{"tool": "list_files", "args": {"directory": "/app/backend"}}
```

Multiple TOOL_CALL blocks execute in sequence. Explain what you're doing between them.

## MODES
- "auto" (default): Full pipeline (Understand -> Plan -> Execute -> Validate -> Deploy)
- "ba": Business analysis only (Phase 1). No code or tool calls for file writing.
- "dev": Coding only (Phase 3). Skip business analysis, go straight to code.
- "qa": Testing only (Phase 4). Run queries and validations.

CRITICAL RULES:
- When writing code, produce COMPLETE file contents. Never use "...existing code..." placeholders.
- Always exclude _id from MongoDB responses.
- Always validate debit = credit for any journal entries.
- Always use existing code patterns (check the file first before modifying).
- Register new routes in server.py if creating a new route file.
- After file writes, restart the affected service."""

# Individual mode prompts (for when user forces a specific brain)
BA_ONLY_SUFFIX = "\n\nMODE: Business Analysis Only. Focus on requirements, compliance, accounting implications. Do NOT generate code or tool calls for file writing."
DEV_ONLY_SUFFIX = "\n\nMODE: Coding Only. Focus on reading files, generating code, and deploying. Skip business analysis."
QA_ONLY_SUFFIX = "\n\nMODE: Testing/Validation Only. Focus on running queries, testing APIs, and checking data integrity."

# ══════════════════════════════════════════════════════════
# TOOL EXECUTION ENGINE
# ══════════════════════════════════════════════════════════

async def execute_tool(tool_name, args):
    """Execute a tool call and return the result"""
    try:
        if tool_name == "read_file":
            path = args.get("path", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if not os.path.isfile(path):
                return {"status": "error", "error": f"File not found: {path}"}
            with open(path, "r") as f:
                content = f.read()
            if len(content) > 30000:
                content = content[:30000] + "\n... [TRUNCATED] ..."
            return {"status": "ok", "path": path, "content": content, "size": len(content)}

        elif tool_name == "write_file":
            path = args.get("path", "")
            content = args.get("content", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            await db.audit_trail.insert_one({
                "id": str(uuid.uuid4()),
                "action": "FILE_WRITE",
                "module": "AI_ENGINE",
                "record_id": path,
                "record_name": os.path.basename(path),
                "changes": [{"field": "content", "new_value": f"File written ({len(content)} chars)"}],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user": "kairos-engine",
            })
            return {"status": "ok", "path": path, "size": len(content), "message": f"File written: {path}"}

        elif tool_name == "run_query":
            query_type = args.get("query_type", "full_health_check")
            result = await _run_test_query(query_type)
            return {"status": "ok", "query_type": query_type, "results": result}

        elif tool_name == "restart_service":
            service = args.get("service", "backend")
            if service not in ["backend", "frontend"]:
                return {"status": "error", "error": "Can only restart 'backend' or 'frontend'"}
            proc = subprocess.run(
                ["sudo", "supervisorctl", "restart", service],
                capture_output=True, text=True, timeout=15
            )
            await asyncio.sleep(3)
            return {"status": "ok", "service": service, "output": proc.stdout.strip(), "stderr": proc.stderr.strip() if proc.returncode != 0 else ""}

        elif tool_name == "test_api":
            method = args.get("method", "GET").upper()
            url_path = args.get("url", "")
            body = args.get("body")
            base_url = "http://localhost:8001"
            full_url = f"{base_url}{url_path}"
            async with httpx.AsyncClient(timeout=15) as client:
                if method == "GET":
                    resp = await client.get(full_url)
                elif method == "POST":
                    resp = await client.post(full_url, json=body)
                elif method == "PUT":
                    resp = await client.put(full_url, json=body)
                elif method == "DELETE":
                    resp = await client.delete(full_url)
                else:
                    return {"status": "error", "error": f"Unsupported method: {method}"}
            resp_body = resp.text[:3000]
            try:
                resp_body = resp.json()
                if isinstance(resp_body, list) and len(resp_body) > 5:
                    resp_body = {"count": len(resp_body), "sample": resp_body[:3], "note": f"...{len(resp_body)} total items"}
            except Exception:
                pass
            return {"status": "ok", "http_status": resp.status_code, "url": url_path, "response": resp_body}

        elif tool_name == "list_files":
            directory = args.get("directory", "/app/backend")
            if not is_safe_path(directory):
                return {"status": "error", "error": "Access denied"}
            files = []
            for f in sorted(glob.glob(f"{directory}/**", recursive=True)):
                if os.path.isfile(f) and is_safe_path(f):
                    ext = os.path.splitext(f)[1]
                    if ext in [".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".md"]:
                        files.append({"path": f, "relative": f.replace("/app/", ""), "size": os.path.getsize(f)})
            return {"status": "ok", "files": files[:100], "count": len(files)}

        else:
            return {"status": "error", "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def _run_test_query(query_type):
    """Run a predefined test query"""
    if query_type == "tb_balance":
        coa = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        dr = sum(max(0, e["opening_balance"]) for e in coa)
        cr = sum(max(0, -e["opening_balance"]) for e in coa)
        return {"total_debit": dr, "total_credit": cr, "balanced": dr == cr, "accounts": len(coa)}
    elif query_type == "entity_validation":
        v = await db.entities.find({"entity_type": "vendor"}, {"_id": 0}).to_list(100)
        c = await db.entities.find({"entity_type": "customer"}, {"_id": 0}).to_list(100)
        return {"vendors": len(v), "customers": len(c), "vendor_missing_gstin": [x["name"] for x in v if not x.get("gstin")]}
    elif query_type == "project_health":
        p = await db.projects.find({"id": {"$ne": "PRJ-INT"}}, {"_id": 0}).to_list(20)
        return {"projects": len(p), "by_health": {}}
    elif query_type == "collection_stats":
        cols = await db.list_collection_names()
        stats = {}
        for col in sorted(cols):
            stats[col] = await db[col].count_documents({})
        return stats
    elif query_type == "full_health_check":
        coa = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        dr = sum(max(0, e["opening_balance"]) for e in coa)
        cr = sum(max(0, -e["opening_balance"]) for e in coa)
        return {
            "tb_balanced": dr == cr, "tb_total": dr,
            "accounts": len(coa),
            "vendors": await db.entities.count_documents({"entity_type": "vendor"}),
            "customers": await db.entities.count_documents({"entity_type": "customer"}),
            "projects": await db.projects.count_documents({}),
            "employees": await db.employees.count_documents({}),
            "timesheets": await db.timesheets.count_documents({}),
            "transactions": await db.erp_transactions.count_documents({}),
        }
    else:
        return {"error": f"Unknown query: {query_type}"}


def parse_tool_calls(text):
    """Extract TOOL_CALL blocks from LLM response"""
    calls = []
    parts = text.split("```TOOL_CALL")
    for part in parts[1:]:
        end = part.find("```")
        if end != -1:
            raw = part[:end].strip()
            try:
                call = json.loads(raw)
                calls.append(call)
            except json.JSONDecodeError:
                pass
    return calls


def parse_questions(text):
    """Extract QUESTION blocks from LLM response"""
    questions = []
    parts = text.split("```QUESTION")
    for part in parts[1:]:
        end = part.find("```")
        if end != -1:
            questions.append(part[:end].strip())
    return questions

# ══════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════
# FILE UPLOAD & URL CRAWLING
# ══════════════════════════════════════════════════════════

UPLOAD_DIR = "/app/backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _extract_pdf(path):
    import pdfplumber
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages[:50]):
            t = page.extract_text()
            if t:
                text_parts.append(f"--- Page {i+1} ---\n{t}")
            tables = page.extract_tables()
            for ti, table in enumerate(tables):
                text_parts.append(f"[Table {ti+1}]\n" + "\n".join([" | ".join(str(c or "") for c in row) for row in table]))
    return "\n\n".join(text_parts)

def _extract_docx(path):
    from docx import Document
    doc = Document(path)
    parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    for table in doc.tables:
        rows = []
        for row in table.rows:
            rows.append(" | ".join(cell.text for cell in row.cells))
        parts.append("[Table]\n" + "\n".join(rows))
    return "\n".join(parts)

def _extract_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    parts = []
    for sheet_name in wb.sheetnames[:10]:
        ws = wb[sheet_name]
        rows = []
        for row in ws.iter_rows(max_row=200, values_only=True):
            rows.append(" | ".join(str(c or "") for c in row))
        parts.append(f"--- Sheet: {sheet_name} ---\n" + "\n".join(rows))
    return "\n\n".join(parts)

def _extract_pptx(path):
    from pptx import Presentation
    prs = Presentation(path)
    parts = []
    for i, slide in enumerate(prs.slides[:50]):
        slide_text = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        slide_text.append(para.text)
            if shape.has_table:
                for row in shape.table.rows:
                    slide_text.append(" | ".join(cell.text for cell in row.cells))
        if slide_text:
            parts.append(f"--- Slide {i+1} ---\n" + "\n".join(slide_text))
    return "\n\n".join(parts)

def _extract_csv(path):
    import csv
    rows = []
    with open(path, "r", errors="replace") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 500:
                rows.append("... [TRUNCATED at 500 rows]")
                break
            rows.append(" | ".join(row))
    return "\n".join(rows)

EXTRACTORS = {
    ".pdf": _extract_pdf,
    ".docx": _extract_docx,
    ".doc": _extract_docx,
    ".xlsx": _extract_xlsx,
    ".xls": _extract_xlsx,
    ".pptx": _extract_pptx,
    ".ppt": _extract_pptx,
    ".csv": _extract_csv,
}

TEXT_EXTS = {".txt", ".md", ".json", ".xml", ".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".yaml", ".yml", ".ini", ".cfg", ".log", ".sql"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".heic", ".heif"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and extract text from a file. Returns extracted content."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    file_id = str(uuid.uuid4())[:8]
    safe_name = f"{file_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    content_bytes = await file.read()
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    size_kb = len(content_bytes) / 1024
    result = {
        "id": file_id,
        "filename": file.filename,
        "ext": ext,
        "size_kb": round(size_kb, 1),
        "type": "unknown",
        "content": "",
    }

    try:
        if ext in EXTRACTORS:
            result["content"] = EXTRACTORS[ext](save_path)
            result["type"] = "document"
        elif ext in TEXT_EXTS:
            with open(save_path, "r", errors="replace") as f:
                result["content"] = f.read()[:50000]
            result["type"] = "text"
        elif ext in IMAGE_EXTS:
            result["type"] = "image"
            result["content"] = f"[Image: {file.filename} ({size_kb:.0f}KB). Describe what you need analyzed from this image.]"
            result["image_path"] = save_path
        else:
            result["type"] = "binary"
            result["content"] = f"[Unsupported file type: {ext}. File saved as {safe_name}]"
    except Exception as e:
        result["content"] = f"[Extraction error: {str(e)}]"
        result["type"] = "error"

    # Truncate to avoid overloading the LLM
    if len(result["content"]) > 40000:
        result["content"] = result["content"][:40000] + "\n... [TRUNCATED — content exceeds 40KB]"

    return result


@router.post("/crawl-url")
async def crawl_url(body: dict):
    """Crawl a URL and extract its text content."""
    url = body.get("url", "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; KairosBot/1.0)"
            })
            resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        raw = resp.text

        # If it's HTML, extract text
        if "html" in content_type:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw, "html.parser")
            # Remove scripts, styles, nav
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()
            title = soup.title.string if soup.title else url
            text = soup.get_text(separator="\n", strip=True)
            # Clean up excessive whitespace
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            text = "\n".join(lines)
            if len(text) > 30000:
                text = text[:30000] + "\n... [TRUNCATED]"
            return {
                "status": "ok",
                "url": url,
                "title": title,
                "type": "html",
                "content": text,
                "size_kb": round(len(text) / 1024, 1),
            }
        # If it's JSON
        elif "json" in content_type:
            return {
                "status": "ok",
                "url": url,
                "title": url,
                "type": "json",
                "content": raw[:30000],
                "size_kb": round(len(raw) / 1024, 1),
            }
        # Plain text / XML
        else:
            return {
                "status": "ok",
                "url": url,
                "title": url,
                "type": "text",
                "content": raw[:30000],
                "size_kb": round(len(raw) / 1024, 1),
            }
    except httpx.HTTPStatusError as e:
        return {"status": "error", "url": url, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"status": "error", "url": url, "error": str(e)}


# ══════════════════════════════════════════════════════════
# SESSION MANAGEMENT (kept from previous)
# ══════════════════════════════════════════════════════════

@router.get("/sessions")
async def list_sessions():
    sessions = await db.agent_sessions.find({}, {"_id": 0}).sort("updated_at", -1).to_list(50)
    return sessions

@router.post("/sessions")
async def create_session(body: dict):
    session = {
        "id": str(uuid.uuid4()),
        "agent_type": body.get("agent_type", "auto"),
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
# FILE + QUERY ENDPOINTS (kept for direct access)
# ══════════════════════════════════════════════════════════

@router.get("/coding/files")
async def api_list_files(directory: str = "/app/backend"):
    return await execute_tool("list_files", {"directory": directory})

@router.post("/coding/read-file")
async def api_read_file(body: dict):
    return await execute_tool("read_file", body)

@router.post("/coding/write-file")
async def api_write_file(body: dict):
    return await execute_tool("write_file", body)

@router.post("/testing/query")
async def api_run_test_query(body: dict):
    return await execute_tool("run_query", body)

# ══════════════════════════════════════════════════════════
# UNIFIED CHAT — THE ORCHESTRATOR
# ══════════════════════════════════════════════════════════

@router.post("/chat")
async def engine_chat(body: dict):
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    mode = body.get("agent_type", "auto")
    message = body.get("message", "")
    session_id = body.get("session_id", "")
    context = body.get("context", "")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Build system prompt based on mode
    system = ENGINE_SYSTEM_PROMPT
    if mode == "ba":
        system += BA_ONLY_SUFFIX
    elif mode == "dev":
        system += DEV_ONLY_SUFFIX
    elif mode == "qa":
        system += QA_ONLY_SUFFIX

    # Get conversation history
    history = []
    if session_id:
        session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
        if session:
            history = session.get("messages", [])

    # Build user message with optional file context
    full_message = message
    if context:
        full_message += f"\n\n[ATTACHED CONTEXT]\n{context}"

    # For auto/qa modes, inject a quick DB health snapshot
    if mode in ["auto", "qa"]:
        try:
            health = await _run_test_query("full_health_check")
            full_message += f"\n\n[CURRENT DB STATE]\n{json.dumps(health, default=str)}"
        except Exception:
            pass

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"engine-{session_id or uuid.uuid4()}",
            system_message=system
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        # Inject conversation history as context in the message itself (avoids multiple LLM round-trips)
        history_context = ""
        if history:
            recent = history[-8:]
            history_lines = []
            for h in recent:
                role = "User" if h["role"] == "user" else "Assistant"
                content = h["content"][:500]
                history_lines.append(f"[{role}]: {content}")
            history_context = "[CONVERSATION HISTORY]\n" + "\n".join(history_lines) + "\n\n"

        # Phase 1: Get initial response from Claude (single LLM call)
        response_text = await chat.send_message(UserMessage(text=history_context + full_message))

        # Phase 2: Parse and execute tool calls
        tool_calls = parse_tool_calls(response_text)
        questions = parse_questions(response_text)
        tool_results = []
        files_modified = []

        if tool_calls:
            for tc in tool_calls[:8]:
                tool_name = tc.get("tool", "")
                tool_args = tc.get("args", {})
                result = await execute_tool(tool_name, tool_args)
                tool_results.append({"tool": tool_name, "args": tool_args, "result": result})
                if tool_name == "write_file" and result.get("status") == "ok":
                    files_modified.append(result.get("path", ""))

            # Phase 3: Feed tool results back to Claude for follow-up (single additional LLM call)
            tool_summary = json.dumps(tool_results, indent=2, default=str)
            if len(tool_summary) > 10000:
                tool_summary = tool_summary[:10000] + "\n... [TRUNCATED]"

            followup = await chat.send_message(UserMessage(
                text=f"[TOOL EXECUTION RESULTS]\n{tool_summary}\n\nBriefly confirm what was done and suggest next steps."
            ))
            response_text += f"\n\n---\n\n{followup}"

        # Save to session
        timestamp = datetime.now(timezone.utc).isoformat()
        if session_id:
            new_messages = [
                {"role": "user", "content": message, "timestamp": timestamp},
                {"role": "assistant", "content": response_text, "agent_type": mode, "timestamp": timestamp,
                 "tool_calls": len(tool_calls), "files_modified": files_modified, "questions": questions},
            ]
            update = {
                "$push": {"messages": {"$each": new_messages}},
                "$set": {"updated_at": timestamp}
            }
            session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
            if session and len(session.get("messages", [])) == 0:
                update["$set"]["title"] = message[:80]
            await db.agent_sessions.update_one({"id": session_id}, update)

        return {
            "response": response_text,
            "agent_type": mode,
            "session_id": session_id,
            "timestamp": timestamp,
            "tool_calls_executed": len(tool_calls),
            "files_modified": files_modified,
            "questions": questions,
            "tool_results": tool_results[:10],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine error: {str(e)}")
