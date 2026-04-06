# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) called "Kairos AI ERP", operating heavily on a "Zero-Touch" UI. Pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB)
- AI: Claude Sonnet 4.5 (Emergent) + Groq (Llama 3.3 70B) + OpenRouter
- DB: MongoDB

## Modules Implemented

### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll

### Delivery: Project Management (8 projects), Timesheets (27 entries), Revenue Recognition (Ind AS 115)

### Intelligence
- **Transaction Explorer** — 140 transactions, 8 module filters
- **Unified AI Engine v3** — Parallel execution, compound tools, auto-restart, 18 tools, ~95% of E1

### Expense Management (Completed 2026-05-02)
- **Backend**: 6 endpoints (list, create, approve, reject, summary, by-employee)
- **Frontend**: Summary cards, category breakdown, expense table with status badges, create form, approve/reject workflow, status/category filters
- **Scaffolded by Kairos AI v3** compound tool, polished by E1
- **Tested**: 26/26 backend, all frontend — 100% pass

### Other Modules
- Leave Management (scaffolded by Kairos), Employee Analytics, Bank Reconciliation
- Accounting & Compliance: Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS

## Benchmark Results
- v2: 67/80 (84% of E1) | Avg 10.8s
- v3: ~76/80 (95% of E1) | Avg 4.3s | 2.5x faster

## Backlog
### P1: Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
### P3: Kairos web search tool, screenshot capability
