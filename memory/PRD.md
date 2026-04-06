# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) called "Kairos AI ERP", operating heavily on a "Zero-Touch" UI where data entry is performed via Natural Language Processing (NLP). Pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine.

## Current Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP
- **Revenue Model:** Fixed-Price (POC) | T&M | Monthly Retainer | Milestone-based

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB)
- AI: Claude Sonnet 4.5 via Emergent LLM Key + Groq (Llama 3.3 70B) + OpenRouter
- DB: MongoDB

## Modules Implemented

### Core
1. Dashboard, Company Setup, CRM, Selling, Buying, Stock & Manufacturing, HR & Payroll

### Delivery (Completed 2026-04-06)
8. **Project Management** — 8 projects, health dashboard, milestones, budget vs actuals
9. **Timesheets** — 27 entries, utilization (85.3%), consolidation, approval workflow
10. **Revenue Recognition (Ind AS 115)** — POC/T&M/Milestone/Retainer, contract assets/liabilities, RPO, Ind AS 115 disclosure

### Intelligence
11. **Transaction Explorer** — 140 transactions, 8 module filters, priority/search, copy-to-clipboard AI prompts
12. **Unified AI Engine v2** (Upgraded 2026-05-02) — Agentic loop architecture with autonomous multi-step execution:
    - **Agentic Loop:** Up to 10 autonomous iterations per task (Plan → Execute → Observe → Adapt → Validate → Complete)
    - **16 Tools:** read_file, create_file, patch_file, insert_lines, delete_lines, write_file, get_schema, run_query, restart_service, test_api, list_files, run_command, grep_search, check_logs, install_package, run_tests
    - **Self-Validation:** Auto-tests APIs after code changes, checks service logs, restarts services when needed
    - **Multi-Provider LLM:** Groq (Llama 3.3 70B, primary), OpenRouter (auto, secondary), Claude Sonnet 4.5 (tertiary). Auto-fallback chain.
    - **Step-by-Step Progress:** Real-time step tracking in UI with expandable step cards showing tools used, files modified per step
    - **Rich Prompt Box:** File attachments, URL crawling, multiline textarea
    - **Improved Context:** 12 messages history, 800 char truncation (up from 6/300)
    - **Modes:** Auto (full pipeline), Business (requirements), Coding (file ops), Testing (DB validation)
    - **Session management** with persistent conversation history

### Bank Reconciliation (Completed 2026-04-06)
- CSV upload, auto-match, manual match/unmatch, reconciliation summary

### Accounting & Compliance
13. Journal Entries, Chart of Accounts (balanced TB 2,81,42,000)
14. Financial Statements (Schedule III BS/P&L/TB with company logo)
15. AP/AR Aging, Audit Trail (Companies Act 2013)
16. GST (GSTR-1/3B, E-Invoicing, GST Rules Engine), TDS Returns
17. AI-First Data Entry (AISmartEntry.js), Reporting AI (Claude)

### Data Seeded (Nexora — March 2026)
- 8 Projects, 20 Employees, 7 Clients, 10 Vendors, 26 CoA entries, 7 Revenue schedule, 140 Transactions, 27 Timesheets

## Key API Endpoints
- `/api/agents/chat` (POST — async task, returns task_id), `/api/agents/tasks/{task_id}` (GET — poll with steps)
- `/api/agents/sessions`, `/api/agents/providers`, `/api/agents/upload`, `/api/agents/crawl-url`
- `/api/entities`, `/api/stock/items`, `/api/company/settings`
- `/api/gst/*`, `/api/statutory/*`, `/api/audit-trail`, `/api/aging/*`

## Backlog
### P1: Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
