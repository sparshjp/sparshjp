# Nexora IT ERP — Product Requirements Document

## Original Problem Statement
Build an IT Services ERP ("Nexora IT ERP") with a Kairos AI Engine (autonomous developer), then layer enterprise modules with full inter-module linking and AI-first data entry.

## Core Architecture
- **Backend**: FastAPI + Motor (async MongoDB)
- **Frontend**: React + Tailwind + Shadcn UI, dark theme
- **Auth**: No login required. Creator Mode (password-gated via login page) for Kairos AI Engine access
- **AI**: Kairos AI Engine v4 + AI-first data entry via `/api/ai/parse-entry`
- **Events**: `module_events.py` — cross-module triggers
- **Subagents**: 4 upgraded subagents (Testing v3, Designer v2, Integrator v2, Troubleshooter v2) + 33 tools

## What's Been Implemented

### Phase 1-3 — Core ERP + Kairos AI (Done)
### Phase 4 — 10 Advanced Enterprise Modules (Done)
### Phase 5 — Inter-Module Linking (Done)
### Phase 6 — AI-First Data Entry + Manual Forms (Done)
### Phase 7 — Remove Login + Creator Mode (Done)
### Phase 8 — Company Data Linking + Free LLM Providers (Done)

### Phase 9 — Kairos Subagent Upgrade to E1 Parity (Done — April 9, 2026)
- **Testing Agent v3**: Playwright browser automation, API test runner, batch test suites with JSON reports
- **Design Agent v2**: Full UI/UX design system generation, anti-AI-slop philosophy, dark theme mastery, JSX skeletons
- **Integration Playbook Expert v2**: 12 verified playbooks (Stripe, Groq, Cerebras, HuggingFace, Razorpay, Twilio, SendGrid, Redis, S3, Firebase, Elasticsearch, OpenAI)
- **Troubleshoot Agent v2**: Structured 10-step RCA (Gather → Isolate → Root Cause → Fix & Verify)
- **3 new direct tools**: run_test, run_test_suite, get_playbook (no LLM needed)
- Total tools: 33

## Prioritized Backlog
- P2: E-Way Bill generation
- P2: Mobile Responsiveness
- P3: Refactor routes_agents.py

## Key Files
- `/app/backend/kairos_subagents.py` — v2 subagents with Playwright, playbooks, RCA
- `/app/backend/routes_agents.py` — 33-tool Kairos Engine
- `/app/frontend/src/App.js` — Sidebar, Creator Mode dropdown
