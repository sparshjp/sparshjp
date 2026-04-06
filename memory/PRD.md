# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine that acts as an autonomous developer.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB)
- AI: Claude Sonnet 4.5 (Emergent, Primary) + Groq (Llama 3.3 70B, Fallback) + OpenRouter (Last resort)
- DB: MongoDB

## Kairos AI Engine v3.2 Capabilities (Updated 2026-04-06)
- **Agentic Loop**: Up to 10 iterations (Plan -> Execute -> Observe -> Adapt -> Validate)
- **Parallel Execution**: asyncio.gather for simultaneous tool calls (2.5x faster)
- **21 Tools + 2 Compound**: read_file, create_file, patch_file, insert_lines, delete_lines, write_file, get_schema, run_query, restart_service, test_api, check_logs, install_package, run_tests, grep_search, list_files, run_command, verify_deployment, web_search, take_screenshot + scaffold_module, create_page
- **Smart Provider Routing**: Claude first (most capable), auto-skips rate-limited providers for 5 minutes after 2+ failures
- **Web Search**: DuckDuckGo search via `ddgs` library — finds documentation, code examples, API references
- **Screenshots**: Headless Chromium via Playwright — captures page screenshots for visual UI verification
- **Live Thought Process**: Streams LLM reasoning to frontend in real-time
- **Deployment Verification**: Checks backend health, API endpoints, frontend routes, file existence
- **Auto-Polish**: Fixes LLM code-gen bugs (to_list(), _id projection, datetime.utcnow, missing body params)
- **Auto-Fix**: Reads startup error logs and applies targeted patches
- **Auto-Restart**: Backend auto-restarts after file modifications

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management (8 projects), Timesheets (27 entries), Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer (140 txns), Unified AI Engine v3.2
### Expense Management: 6 endpoints, full dashboard, approval workflow
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback
### Accounting: Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS

## Recent Changes (2026-04-06)
- CRITICAL FIX: Changed default LLM provider from Groq to Claude (Groq was 429 rate-limited, causing fallback to low-quality OpenRouter)
- Added smart provider failure tracking: auto-skips providers with 2+ failures in 5 min window
- Added web_search tool (#20) using ddgs/DuckDuckGo
- Added take_screenshot tool (#21) using Playwright/Chromium
- Added live thought process streaming to Kairos Engine
- Added verify_deployment tool (#19)

## Backlog
### P1: Client Portal, Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
