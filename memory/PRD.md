# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules: Project Management, Timesheets, Revenue Accrual, JWT RBAC Auth, and 10 Advanced Enterprise features with full inter-module linking.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Tailwind + Shadcn UI, dark theme (#0D1B2A bg, #00C9A7 accent)
- **Auth**: JWT-based RBAC (roles: creator, admin, finance_manager, project_manager, hr_manager, ap_clerk, ar_clerk, tax_compliance, viewer)
- **AI**: Kairos AI Engine v4 (autonomous execution, multi-file editing, custom API keys, full module knowledge)
- **Event System**: `module_events.py` — cross-module triggers (Contract→Project, Milestone→Billing+Forex, Timesheet→Billing, etc.)

## What's Been Implemented

### Phase 1 — Core ERP (Done)
Dashboard, CRM, Selling, Buying, Stock, Manufacturing, HR, Delivery, Projects, Timesheets, Accounting, GST, TDS, Reporting AI, Settings

### Phase 2 — Kairos AI Engine (Done)
Autonomous tool execution, multi-file editing, custom API keys, Emergent LLM Key fallback, security hardened

### Phase 3 — JWT Auth & RBAC (Done)
JWT login, role-based sidebar/API access, User Management, seed credentials

### Phase 4 — 10 Advanced Enterprise Modules (Done — April 7, 2026)
Approvals, Budgets, Contracts, Resources, Forex, Billing, Documents, Notifications, Compliance, Client Portal

### Phase 5 — Inter-Module Linking & UI Gaps Fixed (Done — April 7, 2026)
1. **Project CRUD** — Added POST/PUT/DELETE endpoints + "New Project" form with milestones, team, currency
2. **Timesheet CRUD** — Added "New Timesheet" form with project entries, approve/reject buttons
3. **Inter-Module Event System** (`module_events.py`):
   - Contract Created → Auto-create Project + Notification
   - Milestone Completed → Draft Billing Invoice + Forex Transaction (if non-INR) + Notification
   - Timesheet Approved → Mark billing-ready + Notification
   - Approval Actioned → Notification to requester
   - Resource Allocated → Update Project team_names
   - Document Uploaded → Compliance access log
4. **Kairos AI Knowledge** — Updated system prompt with all 22 module endpoints, DB schemas, and inter-module linking rules

## Prioritized Backlog

### P2
- E-Way Bill generation module
- Mobile Responsiveness

### P3
- Refactor `routes_agents.py` monolithic `execute_tool` into `kairos_tools.py`

## Key Files
- `/app/backend/module_events.py` — Central event trigger system
- `/app/backend/routes_projects.py` — Project CRUD with POST/PUT/DELETE
- `/app/backend/routes_agents.py` — Kairos AI with full module knowledge
- `/app/frontend/src/pages/ProjectsModule.js` — New Project form
- `/app/frontend/src/pages/TimesheetsPage.js` — New Timesheet form + approve/reject

## Test Reports
- Iteration 34: 10 Enterprise modules — 42/42 backend, 10/10 frontend (PASS)
- Iteration 35: Inter-module linking + Project/Timesheet CRUD — 17/17 backend, 7/7 frontend (PASS)
