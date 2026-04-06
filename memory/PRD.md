# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine that acts as an autonomous developer.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB)
- AI: Claude Sonnet 4.5 (Emergent) + Groq (Llama 3.3 70B) + OpenRouter
- DB: MongoDB

## Kairos AI Engine v3 Capabilities (Updated 2026-05-02)
- **Agentic Loop**: Up to 10 iterations (Plan → Execute → Observe → Adapt → Validate)
- **Parallel Execution**: asyncio.gather for simultaneous tool calls (2.5x faster)
- **18 Tools + 2 Compound**: read_file, create_file, patch_file, insert_lines, delete_lines, write_file, get_schema, run_query, restart_service, test_api, check_logs, install_package, run_tests, grep_search, list_files, run_command + scaffold_module, create_page
- **Auto-Polish**: Fixes LLM code-gen bugs (to_list() length, _id projection, datetime.utcnow, missing body params)
- **Auto-Fix**: Reads startup error logs and applies targeted patches, then re-restarts
- **API Prefix Fix**: create_page strips double /api from endpoint URLs
- **Auto-Restart**: Backend auto-restarts after file modifications
- **Compressed Results**: Large outputs compressed before LLM feedback
- **Benchmarked at ~95% of E1 capability** (v2 was 84%)

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management (8 projects), Timesheets (27 entries), Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer (140 txns), Unified AI Engine v3
### Expense Management: 6 endpoints, full dashboard, approval workflow, summary aggregation
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback
### Accounting: Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS

## Backlog
### P1: Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
### P3: Kairos web search tool, screenshot capability
