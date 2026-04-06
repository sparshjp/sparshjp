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
- AI: Claude Sonnet 4.5 via Emergent LLM Key (emergentintegrations)
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
12. **Unified AI Engine** (Completed 2026-04-06) — Single agent combining Business Analysis, Coding, and Testing brains:
    - **Modes:** Auto (full pipeline), Business (requirements & compliance), Coding (file ops & code gen), Testing (DB validation & API testing)
    - **Tools:** read_file, write_file, run_query, restart_service, test_api, list_files
    - **Workflow:** Understand → Plan → Execute → Validate → Deploy
    - **UI:** Unified chat with mode selector, file explorer, quick test queries, inline tool result cards, files modified badges
    - **Session management** with persistent conversation history

### Accounting & Compliance
13. Journal Entries, Chart of Accounts (balanced TB 2,81,42,000)
14. Financial Statements (Schedule III BS/P&L/TB with company logo)
15. AP/AR Aging, Audit Trail (Companies Act 2013)
16. GST (GSTR-1/3B, E-Invoicing, GST Rules Engine), TDS Returns
17. AI-First Data Entry (AISmartEntry.js), Reporting AI (Claude)

### Data Seeded (Nexora — March 2026)
- 8 Projects, 20 Employees, 7 Clients, 10 Vendors, 26 CoA entries, 7 Revenue schedule, 140 Transactions, 27 Timesheets

## Key API Endpoints
- `/api/agents/chat`, `/api/agents/sessions`, `/api/agents/testing/query`, `/api/agents/coding/files`, `/api/agents/coding/read-file`, `/api/agents/coding/write-file`
- `/api/projects`, `/api/timesheets`, `/api/revenue/*`
- `/api/entities`, `/api/stock/items`, `/api/company/settings`
- `/api/gst/*`, `/api/statutory/*`, `/api/audit-trail`, `/api/aging/*`

## Backlog
### P1: Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Bank Reconciliation, Mobile Responsiveness
