# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules with full inter-module linking and AI-first data entry.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Tailwind + Shadcn UI, dark theme
- **Auth**: No login required. Creator Mode (password-gated) for Kairos AI Engine access
- **AI**: Kairos AI Engine v4 + AI-first data entry via `/api/ai/parse-entry`
- **Events**: `module_events.py` — cross-module triggers

## What's Been Implemented

### Phase 1-3 — Core ERP + Kairos AI + Auth (Done)
22 core modules, Kairos AI Engine, JWT RBAC

### Phase 4 — 10 Advanced Enterprise Modules (Done)
Approvals, Budgets, Contracts, Resources, Forex, Billing, Documents, Notifications, Compliance, Client Portal

### Phase 5 — Inter-Module Linking (Done)
Contract→Project, Milestone→Billing+Forex+Notification, Timesheet→Billing, Approval→Notification, Resource→Project, Document→Compliance

### Phase 6 — AI-First Data Entry (Done)
Backend `/api/ai/parse-entry` + `AiEntryModal` component across 9 modules. Manual Entry form with dynamic field rendering.

### Phase 7 — Remove Login + Creator Mode (Done — April 8, 2026)
1. **Removed login page** — ERP loads directly to Dashboard, all modules accessible
2. **Creator Mode** — Password-gated button at bottom of sidebar
3. **Kairos AI Engine** — Only visible/accessible after entering Creator Mode password
4. **Password validation** — Uses existing `/api/auth/login` endpoint with `kairoserp` credentials
5. **Persistence** — Creator token stored in localStorage, auto-validates on reload

## Prioritized Backlog
- P2: E-Way Bill generation
- P2: Mobile Responsiveness
- P3: Refactor routes_agents.py

## Key Files
- `/app/frontend/src/App.js` — Sidebar with Creator Mode, no login gate
- `/app/frontend/src/contexts/AuthContext.js` — Default user, creatorMode state
- `/app/backend/routes_ai_entry.py` — AI parse endpoint with 9 module schemas
- `/app/frontend/src/components/AiEntryModal.js` — Reusable AI entry modal
- `/app/backend/module_events.py` — Cross-module event triggers

## Test Reports
- Iteration 34: 10 Enterprise modules (42/42 PASS)
- Iteration 35: Inter-module linking + CRUD (17/17 PASS)
- Iteration 36: AI-first entry (30/30 PASS)
- Iteration 37: Manual Entry form (18/18 PASS)
- Iteration 38: Login removal + Creator Mode (12/12 PASS)
