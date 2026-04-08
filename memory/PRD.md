# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules with full inter-module linking and AI-first data entry.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Tailwind + Shadcn UI, dark theme
- **Auth**: No login required. Creator Mode (password-gated via login page) for Kairos AI Engine access
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
- Removed login page — ERP loads directly to Dashboard
- Creator Mode via top-right dropdown → full-page login → Kairos Engine access

### Phase 8 — Company Data Linking + UI Fixes (Done — April 9, 2026)
- Financial Statements dynamically pull company name from company_settings DB
- Hidden "Made with Emergent" badge. Seeded ABC Ltd company defaults.

### Phase 9 — Free LLM Provider Integration (Done — April 9, 2026)
- **Added 3 free-tier providers**: Groq (Llama 3.3 70B), Cerebras (Llama 3.3 70B), HuggingFace (Qwen 2.5 Coder 32B)
- Smart routing: Free providers prioritized first → user's own paid keys → Emergent credits as fallback
- Provider selector updated with 7 options (3 free + 4 paid)
- API Keys panel shows FREE badges, signup URLs, and priority explanation
- All providers with failure tracking and automatic fallback

## LLM Provider Priority (call_llm)
1. **FREE**: Groq → Cerebras → HuggingFace (if keys configured)
2. **Direct Keys**: Anthropic Claude → OpenAI GPT-4o → OpenRouter (if keys configured)
3. **Emergent Credits**: Claude → Gemini → GPT-5 (fallback)

## Prioritized Backlog
- P2: E-Way Bill generation
- P2: Mobile Responsiveness
- P3: Refactor routes_agents.py

## Key Files
- `/app/backend/routes_agents.py` — Kairos AI Engine + 6-provider LLM routing + API key management
- `/app/frontend/src/pages/AIAgentsPage.js` — Kairos UI + provider selector + API keys panel
- `/app/frontend/src/App.js` — Sidebar, Creator Mode dropdown
- `/app/frontend/src/contexts/AuthContext.js` — Default user, creatorMode state

## Test Reports
- Iteration 34-36: Enterprise modules + AI-first entry (PASS)
- Iteration 37: Manual Entry form (18/18 PASS)
- Iteration 38: Login removal + Creator Mode (12/12 PASS)
