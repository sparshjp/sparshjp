# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine that acts as an autonomous developer.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB), anthropic SDK, openai SDK
- AI: 7 LLM Providers — Claude Direct, GPT-4o Direct, Claude (Emergent), Gemini 3 Flash, GPT-5 (Emergent), Groq Llama 3.3, OpenRouter
- DB: MongoDB

## Kairos AI Engine v4 — Full Access (Updated 2026-04-07)
### 30 Tools (full parity with E1):
**File I/O**: read_file, create_file, write_file, patch_file, insert_lines, delete_lines, delete_file, move_file
**Search**: grep_search, list_files
**Bash**: run_command (full access, 120s timeout)
**DB**: run_query (full CRUD), get_schema
**Infra**: restart_service, install_package, check_logs, run_tests
**Verification**: verify_deployment, test_api
**Research**: web_search, crawl_url, take_screenshot
**Config**: manage_env
**Code Quality**: lint_code
**Git**: git_info
**Compound**: scaffold_module, create_page
**Subagents**: call_subagent (tester, designer, integrator, troubleshooter)
**Batch**: batch_operations (parallel multi-file ops, max 20)
**Image**: generate_image (GPT Image 1)

### LLM Providers (Priority Order — Direct keys first):
1. Claude Direct (User's Anthropic key) — Zero Emergent credits
2. GPT-4o Direct (User's OpenAI key) — Zero Emergent credits
3. Claude Sonnet 4.5 (Emergent Key) — Primary Emergent
4. Gemini 3 Flash (Emergent Key) — Fast fallback
5. GPT-5 (Emergent Key) — Strong code gen
6. Groq / Llama 3.3 (User Groq Key) — Fast inference
7. OpenRouter Auto (User OpenRouter Key) — Last resort

### System Prompt: E1-Level Reasoning
- **Reasoning Methodology**: Decompose → Risk assess → Plan tool calls → Execute → Verify → Self-heal
- **Debugging Discipline**: Reproduce first → Trace chain → Fix root cause → Verify → Regression check
- **Token Efficiency**: Minimal args, patch_file over write_file, compound tools, compressed results (8KB cap), context window 10 messages

### API Key Management (NEW 2026-04-07)
- **GET /api/agents/api-keys** — Check which direct keys are configured (masked)
- **POST /api/agents/api-keys** — Save/remove API key for any provider
- Keys persisted to backend/.env, loaded on startup
- UI panel in AI Engine page with Save/Remove for all 4 providers

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management, Timesheets, Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer, Unified AI Engine v4
### Finance: Expense Management, Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback, Announcements

## Bug Fixes (2026-04-07)
- Fixed backend STOPPED causing "body stream already read" errors across all ERP modules
- Fixed double `/api` prefix bug in 18+ frontend files
- Added resilient `r.ok` checks to all fetch-based pages
- Fixed FinancialStatements.js using process.env directly instead of API constant

## Backlog
### P1: Client Portal, Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
### P3: Refactor routes_agents.py (>2100 lines, extract tools into tools.py)
