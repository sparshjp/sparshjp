# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules: Project Management, Timesheets, Revenue Accrual, JWT RBAC Auth, and 10 Advanced Enterprise features.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Shadcn UI, dark theme
- **Auth**: JWT-based RBAC (roles: creator, admin, finance_manager, project_manager, hr_manager, ap_clerk, ar_clerk, tax_compliance, viewer)
- **AI**: Kairos AI Engine v4 (autonomous execution, multi-file editing, custom API keys)

## What's Been Implemented (Complete)

### Phase 1 — Core ERP (Done)
- Dashboard with module summaries
- CRM (Leads, Customers)
- Selling (Sales Orders, Invoices)
- Buying (Purchase Orders)
- Stock & Manufacturing (Inventory, Manufacturing, Quality)
- HR (Employees, Payroll)
- Delivery / Projects / Timesheets
- Accounting (Journal Entries, Revenue Recognition IndAS 115, Financial Statements, AP/AR Aging, Bank Reconciliation, Expense Management, Audit Trail)
- GST (GSTR-1, GSTR-3B, GST Returns)
- TDS (TDS Entries, TDS Returns)
- Reporting AI (Ask Kairos)
- Company Setup, Admin Settings

### Phase 2 — Kairos AI Engine (Done)
- Autonomous tool execution (create/edit files, run commands, analyze)
- Multi-file editing support
- Custom API key support (OpenAI, Anthropic, Groq, OpenRouter)
- Emergent LLM Key fallback
- Security hardened (no shell=True, no exec())

### Phase 3 — JWT Auth & RBAC (Done)
- JWT email/password login
- Role-based sidebar and API access
- User Management (admin/creator can manage roles)
- Seed credentials: kairoserp / ¢re@tor@AIengine

### Phase 4 — 10 Advanced Enterprise Modules (Done — April 7, 2026)
All backend CRUD APIs + React frontend pages + RBAC sidebar integration:
1. **Approval Workflows** — Configurable approval chains, approve/reject, stats
2. **Budget Management** — Department/project budgets, variance tracking, overspend alerts
3. **Contract Management** — SOW/MSA/NDA tracking, milestones, renewal alerts
4. **Resource Planning** — Allocations, bench view, utilization, staffing forecast
5. **Forex Management** — Exchange rates, forex gain/loss, mark-to-market revaluation
6. **Billing Automation** — Auto-invoice from timesheets & milestone completions
7. **Document Management** — Upload/attach files, categorized, download
8. **Notifications Center** — Reminders for overdue/expiring, mark read, filters
9. **Compliance Dashboard** — SOC 2 & ISO 27001 control status, readiness %, access logs
10. **Client Portal** — Manage portal clients, JWT tokens, client-facing endpoints

## Prioritized Backlog

### P2
- E-Way Bill generation module
- Mobile Responsiveness

### P3
- Refactor `routes_agents.py` monolithic `execute_tool` into `kairos_tools.py`
- Split large React components further

## Key Endpoints (New Modules)
- `/api/approvals/*` — Workflows, Requests, Stats
- `/api/budgets/*` — CRUD, Variance, Alerts
- `/api/contracts/*` — CRUD, Milestones, Renewals
- `/api/resources/*` — Allocations, Bench, Utilization, Forecast
- `/api/forex/*` — Rates, Transactions, Revaluation
- `/api/billing/*` — Stats, Unbilled, Generate Invoice, Milestone Invoice
- `/api/documents/*` — CRUD, Upload, Download, Categories
- `/api/notifications/*` — CRUD, Generate Reminders, Read/Unread
- `/api/compliance/*` — Frameworks, Dashboard, Controls, Access Logs
- `/api/portal/*` — Clients, Portal Token Access (my/projects, my/invoices)

## DB Collections (New)
- approval_workflows, approval_requests
- budgets
- contracts
- resource_allocations
- forex_rates, forex_transactions
- billing_invoices
- erp_documents
- notifications
- compliance_controls, compliance_access_logs
- portal_clients

## Test Reports
- Iteration 31: Direct API keys feature (PASS)
- Iteration 32: Security and hook fixes (PASS)
- Iteration 33: JWT Auth implementation (PASS)
- Iteration 34: 10 Enterprise modules — 42/42 backend, 10/10 frontend (PASS)
