# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules with full inter-module linking and AI-first data entry.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Tailwind + Shadcn UI, dark theme
- **Auth**: JWT RBAC (10 roles)
- **AI**: Kairos AI Engine v4 + AI-first data entry via `/api/ai/parse-entry`
- **Events**: `module_events.py` — cross-module triggers

## What's Been Implemented

### Phase 1-3 — Core ERP + Kairos AI + Auth (Done)
22 core modules, Kairos AI Engine, JWT RBAC

### Phase 4 — 10 Advanced Enterprise Modules (Done)
Approvals, Budgets, Contracts, Resources, Forex, Billing, Documents, Notifications, Compliance, Client Portal

### Phase 5 — Inter-Module Linking (Done)
Contract->Project, Milestone->Billing+Forex+Notification, Timesheet->Billing, Approval->Notification, Resource->Project, Document->Compliance

### Phase 6 — AI-First Data Entry (Done — April 7, 2026)
1. **Backend**: `/api/ai/parse-entry` endpoint — takes natural language + module name -> returns structured JSON with missing fields
2. **Frontend**: `AiEntryModal` reusable component — 2-step flow (prompt -> confirm)
3. **Applied to 9 modules**: project, timesheet, contract, approval_workflow, approval_request, budget, resource_allocation, forex_transaction, portal_client
4. **LLM fallback chain**: User Anthropic key -> User OpenAI key -> Emergent Gemini -> Emergent GPT-4o-mini
5. **Manual Entry fallback**: Standard form with dynamic field rendering (text, number, date, enum/select, boolean, array, array_of_objects) — no JSON editor

### Phase 6b — Manual Entry Form Fix (Done — April 7, 2026)
- Fixed backend schema response to include `fields` sub-property for `array_of_objects` types
- Frontend `AiEntryModal` renders proper form inputs for all field types when Manual Entry is selected
- Tested across Projects and Timesheets modules (Iteration 37: 18/18 backend, all frontend PASS)

## Prioritized Backlog
- P2: E-Way Bill generation
- P2: Mobile Responsiveness
- P3: Refactor routes_agents.py

## Key Files
- `/app/backend/routes_ai_entry.py` — AI parse endpoint with 9 module schemas
- `/app/frontend/src/components/AiEntryModal.js` — Reusable AI entry modal
- `/app/backend/module_events.py` — Cross-module event triggers

## Test Reports
- Iteration 34: 10 Enterprise modules (42/42 PASS)
- Iteration 35: Inter-module linking + CRUD (17/17 PASS)
- Iteration 36: AI-first entry — 16/16 backend, 14/14 frontend (PASS)
- Iteration 37: Manual Entry form — 18/18 backend, all frontend (PASS)
