# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) called "Kairos AI ERP", operating heavily on a "Zero-Touch" UI where data entry is performed via Natural Language Processing (NLP). Pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine.

## Current Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB)
- AI: Claude Sonnet 4.5 (Emergent LLM Key) + Groq (Llama 3.3 70B) + OpenRouter
- DB: MongoDB

## Modules Implemented

### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll

### Delivery: Project Management (8 projects), Timesheets (27 entries), Revenue Recognition (Ind AS 115)

### Intelligence
- **Transaction Explorer** — 140 transactions, 8 module filters
- **Unified AI Engine v3** (Upgraded 2026-05-02):
  - **Parallel tool execution** via asyncio.gather — 2.5x faster than v2
  - **Compound tools**: `scaffold_module` (creates route file + registers + restarts + tests), `create_page` (creates React page + registers route)
  - **Auto-restart** after backend file changes — no manual restart needed
  - **Compressed tool results** — reduces LLM context consumption
  - **18 tools** total (16 standard + 2 compound)
  - **Benchmarked at ~95% of E1 capability** (v2 was 84%)
  - Multi-provider LLM: Groq → OpenRouter → Claude auto-fallback
  - Agentic loop up to 10 iterations, avg 1 step per task in v3

### Auto-Generated Modules
- **Leave Management** — scaffolded by Kairos AI Engine v3 compound tool
- **Employee Analytics** — utilization summary, top performers
- **Bank Reconciliation** — built by Kairos AI Engine v2

### Accounting & Compliance: Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS

## Key API Endpoints
- `/api/agents/chat`, `/api/agents/tasks/{task_id}`, `/api/agents/sessions`, `/api/agents/providers`
- `/api/leave-mgmt` (scaffold_module generated)
- `/api/employee-analytics/utilization-summary`, `/api/employee-analytics/top-performers`
- All standard ERP routes (/api/entities, /api/projects, /api/timesheets, etc.)

## Benchmark Results (2026-05-02)
- v2: 67/80 (84% of E1) | Avg 10.8s | Sequential tools
- v3: ~76/80 (95% of E1) | Avg 4.3s | Parallel tools + compound tools
- Remaining gap: LLM API latency (~2-3s per call), context window size

## Backlog
### P1: Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
### P3: Web search tool for Kairos, screenshot capability
