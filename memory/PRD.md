# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) called "Kairos AI ERP", operating heavily on a "Zero-Touch" UI where data entry is performed via Natural Language Processing (NLP).

## Current Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341
- **GSTIN:** 24AABCN4567P1Z8 (Ahmedabad), 29AABCN4567P1Z1 (Bengaluru)
- **Industry:** IT Services (Custom Software Dev, IT Consulting, Managed Services, Data Analytics, Cloud & DevOps)
- **Revenue Model:** Fixed-Price (POC) | Time & Material | Monthly Retainer | Milestone-based
- **Billing Currency:** INR, USD, GBP

## Architecture
- Frontend: React, Tailwind CSS, Shadcn UI, Recharts
- Backend: FastAPI, Motor (PyMongo)
- AI: Claude Sonnet 4.5 via Emergent LLM Key
- DB: MongoDB

## Modules Implemented

### Core Modules
1. **Dashboard** — Company header with dynamic name/logo, module stat cards (CRM, Selling, Buying, Stock, HR, Projects, Timesheets)
2. **Company Setup** — Legal identity, GSTIN, CIN, logo upload, contact details
3. **CRM** — Lead management, opportunity pipeline, RFP tracking
4. **Selling Module** — Sales orders, invoices, export invoices (LUT), credit notes
5. **Buying Module** — Purchase orders, vendor invoices, GRN, payment processing
6. **Stock & Manufacturing** — Inventory, BOM, work orders, quality checks
7. **HR & Payroll** — Employees, attendance, leave, payroll processing, TDS on salary

### NEW: Delivery Modules (Completed 2026-04-06)
8. **Project Management** — 8 projects health dashboard, milestone tracking, budget vs actuals, team allocation, scope change tracking, project P&L
9. **Timesheets** — Weekly timesheet entry (27 entries), employee utilization (85.3% avg), project hours consolidation, approval workflow, OT tracking, multi-currency billing
10. **Revenue Recognition (Ind AS 115)** — POC/T&M/Milestone/Retainer methods, contract assets (unbilled AR ₹15.68L), contract liabilities (deferred revenue ₹4.50L), RPO (₹85.46L), disaggregation by type & geography, significant judgments

### NEW: Transaction Explorer (Completed 2026-04-06)
11. **Transaction Explorer** — 140 transactions across 8 modules (CRM 15, PRJ 15, TS 24, BUY 16, SEL 15, HR 20, ACC 25, RPT 10), module chips filter, priority filter, search, expandable prompts with copy-to-clipboard, accounting impact & integrity checks

### Accounting & Compliance
12. **Journal Entries** — Manual JE with CoA auto-suggest
13. **Chart of Accounts** — Full Ind AS CoA with opening TB (balanced Dr=Cr=₹2,81,42,000)
14. **Financial Statements** — Schedule III Balance Sheet + P&L + Trial Balance, company logo in headers
15. **AP/AR Aging** — 0-30/30-60/60-90/90+ buckets with drill-down
16. **Audit Trail** — Companies Act 2013 compliant, field-level diffs
17. **GST Module** — GSTR-1, GSTR-3B, E-Invoicing, GST Rules Engine (all 36 states/UTs)
18. **TDS Returns** — Form 26Q, deductee list
19. **AI-First Data Entry** — Universal NLP prompt bar (AISmartEntry.js)
20. **Reporting AI** — Claude-powered conversational queries

### Data Seeded (Nexora Digital Solutions — March 2026)
- 8 Projects (PRJ-001 to PRJ-007 + Internal)
- 20 Employees (E001-E020 + E021 new hire)
- 7 Clients (domestic + export USD/GBP)
- 10 Vendors (cloud, SaaS, sub-contractors, professional services)
- 26 Chart of Accounts entries (balanced TB)
- 7 Revenue schedule entries
- 140 ERP transactions
- 27 Timesheet entries (Weeks 1-4)

## Key API Endpoints
- `/api/projects`, `/api/projects/health/dashboard`, `/api/projects/{id}/timesheets`
- `/api/timesheets`, `/api/timesheets/utilization`, `/api/timesheets/consolidation`
- `/api/revenue/schedule`, `/api/revenue/ind-as-115`, `/api/revenue/transactions`, `/api/revenue/all-transactions`
- `/api/entities`, `/api/stock/items`, `/api/company/settings`
- `/api/gst/*`, `/api/statutory/*`, `/api/audit-trail`, `/api/aging/*`

## Backlog

### P1
- Inventory Landed Cost Calculation
- Fixed Asset Automatic Depreciation

### P2
- Bank Reconciliation / Statement Matching
- E-Way Bill Generation
- Mobile Responsiveness Polish
