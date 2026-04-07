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

## Kairos AI Engine v4 — Full Access (Updated 2026-04-06)
### 27 Tools + 2 Compound (parity with E1):
**File I/O**: read_file, create_file, write_file, patch_file, insert_lines, delete_lines, delete_file, move_file
**Search**: grep_search, list_files
**Bash**: run_command (full access, 120s timeout — rm, mv, cp, sudo, apt, yarn all allowed)
**DB**: run_query (full CRUD: find, count, insert_one, insert_many, update_one, update_many, delete_one, delete_many, aggregate, distinct, drop), get_schema
**Infra**: restart_service (backend + frontend), install_package (pip + yarn), check_logs, run_tests
**Verification**: verify_deployment, test_api
**Research**: web_search, crawl_url, take_screenshot
**Config**: manage_env (read/set/delete .env vars with protected keys)
**Code Quality**: lint_code (ruff for Python, eslint for JS)
**Git**: git_info (log, status, diff)
**Compound**: scaffold_module, create_page

### LLM Providers (Priority Order):
1. Claude Sonnet 4.5 (Emergent Key) — Primary
2. Gemini 3 Flash (Emergent Key) — Fast, graceful fallback
3. GPT-5 (Emergent Key) — Strong code generation
4. Groq / Llama 3.3 (Groq API Key) — Fast inference
5. OpenRouter Auto (OpenRouter Key) — Last resort

### Autonomous Execution:
- Executes immediately without asking "proceed" — mandated by system prompt
- Auto-continue logic when LLM outputs plan without tool calls
- Task state persisted to MongoDB for restart resilience
- Smart provider routing with failure tracking

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management, Timesheets, Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer, Unified AI Engine v4
### Finance: Expense Management, Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback, Announcements

## Backlog
### P1: Client Portal, Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
