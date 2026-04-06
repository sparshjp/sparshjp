# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine that acts as an autonomous developer.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB)
- AI: 5 LLM Providers — Claude 4.5, Gemini 3 Flash, GPT-5, Groq Llama 3.3, OpenRouter
- DB: MongoDB

## Kairos AI Engine v3.3 — Autonomous Execution (Updated 2026-04-06)
### Key Behavior Change: "Execute Immediately, Don't Plan and Wait"
- System prompt now mandates immediate tool execution — no "shall I proceed?" pauses
- Auto-continue logic: if LLM outputs a plan without tool calls, engine feeds back "Execute NOW"
- Task state persisted to MongoDB (agent_tasks collection) — survives backend hot reloads

### LLM Providers (Priority Order):
1. Claude Sonnet 4.5 (Emergent Key) — Primary
2. Gemini 3 Flash (Emergent Key) — Fast, graceful fallback
3. GPT-5 (Emergent Key) — Strong code generation
4. Groq / Llama 3.3 (Groq API Key) — Fast inference
5. OpenRouter Auto (OpenRouter Key) — Last resort

### 21 Tools + 2 Compound:
read_file, create_file, patch_file, insert_lines, delete_lines, write_file, get_schema, run_query, restart_service, test_api, check_logs, install_package, run_tests, grep_search, list_files, run_command, verify_deployment, web_search, take_screenshot + scaffold_module, create_page

### Other Capabilities:
- Smart Provider Routing with failure tracking (auto-skip rate-limited providers)
- User-selectable provider dropdown in UI
- Web Search (DuckDuckGo via ddgs)
- Screenshots (Headless Chromium via Playwright)
- Live Thought Process streaming
- Deployment Verification
- Auto-Polish, Auto-Fix, Auto-Restart

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management, Timesheets, Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer, Unified AI Engine v3.3
### Finance: Expense Management, Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback, Announcements

## Recent Changes (2026-04-06)
- CRITICAL: Implemented autonomous execution — Kairos now executes immediately without asking "proceed"
- Added auto-continue logic for plan-only responses
- Persisted task state to MongoDB for restart resilience
- Added Gemini 3 Flash and GPT-5 as LLM providers via Emergent Universal Key
- Added provider selector dropdown in UI
- Added web_search and take_screenshot tools
- Fixed provider routing: Claude first, smart failure tracking

## Backlog
### P1: Client Portal, Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
