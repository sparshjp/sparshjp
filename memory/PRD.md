# Kairos Advisory - Product Requirements Document

## Product Overview
AI-Native ERP (India Localization) called "Kairos Advisory", operating on a "Zero-Touch" UI where data entry is via NLP. Follows Ind AS / Indian GAAP, April 1 - March 31 fiscal cycle. Schedule III Companies Act 2013 compliant financial statements.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Lucide React, Outfit + JetBrains Mono fonts
- **Backend**: FastAPI, Motor (async MongoDB driver)
- **Database**: MongoDB
- **AI**: Claude Sonnet 4.5 (NLP), Gemini 3 Flash (OCR) via Emergent LLM Key
- **Exports**: reportlab (PDF), openpyxl (Excel)
- **Brand**: Navy #0D1B2A, Teal #00C9A7, Off-white #F4F3EF

## Core Modules (ERPNext-inspired)

### 1. Accounting
- Flexible Chart of Accounts (tree categories)
- General Ledger (auto-posted from all modules)
- Journal Entry module (manual + corrections)
- Financial Statements: Balance Sheet, P&L, Trial Balance (Schedule III compliant, Excel export)
- GST & TDS statutory reports (GSTR-1, GSTR-3B, TDS Return)
- Cost Centers & Dimensions

### 2. Procurement (Linked Document Flow)
**PO → Goods Receipt (from PO) → Purchase Invoice (from GRN) → Vendor Payment (from Invoice)**
- Purchase Order with GST, items, payment terms
- GRN: "Pending Deliveries" shows POs not yet received → "Confirm Receipt" creates GRN + auto JE (DR RM Inventory, DR GST Input, CR AP) + stock update
- Purchase Invoice: "Pending Invoices" shows GRNs not yet invoiced → "Create Invoice" attaches vendor invoice
- Vendor Payment: Outstanding invoices sorted by days outstanding with full document trail (PO#, GRN#, Invoice#) → "Pay" posts JE (DR AP, CR Bank)

### 3. Sales (Linked Document Flow)
**SO → Delivery Note (from SO) → Sales Invoice (from DN) → Customer Payment (from Invoice)**
- Sales Order with credit limit check, GST
- Delivery Note: "Pending Dispatch" shows SOs not yet delivered → "Confirm Delivery" creates DN + stock reduction + negative stock warning
- Sales Invoice: "Pending Invoices" from DNs → "Create Invoice" posts JE (DR AR, CR Revenue, CR GST Output, DR COGS, CR FG Inventory)
- Customer Payment: Outstanding AR sorted by days → "Receive" posts JE (DR Bank, CR AR)

### 4. Stock & Manufacturing
- Inventory with stock levels, auto re-order
- Work Orders with BOM, lifecycle (Draft → In Progress → Completed), auto-accounting
- Quality inspection

### 5. CRM
- Leads, Opportunities, Customers

### 6. HR & Payroll
- Employees, Attendance, Leave, Payroll

### 7. Settings
- Chart of Accounts, Cost Centers, Master Data (GSTIN/PAN validation), CSV Import

## What's Implemented

### Completed (Apr 6, 2026)
- [x] Full Navy/Teal theme across ALL pages
- [x] **Linked Purchase Flow**: PO → GRN (from-po) → Invoice (from-grn) → Payment (for-invoice) with auto JE
- [x] **Linked Selling Flow**: SO → DN (from-so) → Invoice (from-dn) → Payment (for-invoice) with auto JE
- [x] Pending sections with badge counts and action buttons (ERPNext-style)
- [x] Outstanding invoices sorted by days outstanding with aging colors
- [x] Manufacturing Module with BOM, WO lifecycle, auto-accounting
- [x] Schedule III Financial Statements with Excel export
- [x] GST & TDS Statutory Reports with CSV/JSON export
- [x] GSTIN/PAN Intelligence (format validation, PAN extraction, state mapping)
- [x] Enhanced CSV Import Validation (CoA cross-check, journal balance, numeric/date)
- [x] Smart AI Prompt Forms, Negative Stock Enforcement, Credit Limit Checks
- [x] Claude Sonnet 4.5 NLP + Gemini 3 Flash OCR (LIVE)

### Auto-Accounting Flows
- GRN: DR Raw Material Inventory, DR GST Input, CR Accounts Payable
- Vendor Payment: DR Accounts Payable, CR Bank
- Sales Invoice: DR AR, CR Revenue, CR GST Output, DR COGS, CR FG Inventory
- Customer Payment: DR Bank, CR AR
- Work Order Start: DR WIP, CR Raw Material
- Work Order Complete: DR Finished Goods, CR WIP; DR Scrap/Loss, CR WIP

### Testing Status
- Iteration 5: 100% (Manufacturing + Excel exports)
- Iteration 6: 100% (GSTIN/PAN + CSV validation)
- Iteration 7: 100% (Linked Purchase + Selling flow, 21 backend + all frontend)

## Architecture
```
/app/backend/
  server.py, ai_orchestrator.py
  routes_purchase.py (Linked: PO→GRN→Invoice→Payment)
  routes_selling.py (Linked: SO→DN→Invoice→Payment)
  routes_manufacturing.py (WO with auto-accounting)
  routes_financial_statements.py (Schedule III + Excel)
  routes_statutory.py (GST + TDS)
  routes_crm.py, routes_sales.py, routes_stock.py, routes_hr.py

/app/frontend/src/
  App.js (Sidebar + Routes)
  pages/
    BuyingModule.js (Linked flow tabs with pending sections)
    SellingModule.js (Linked flow tabs with pending sections)
    ManufacturingModule.js, FinancialStatements.js, GSTModule.js
    JournalEntry.js, Dashboard.js, etc.
```

## Remaining Backlog

### P2
- Bank reconciliation / statement matching
- Fixed asset register with auto depreciation (WDV/SLM/DDB)
- Inventory landed cost calculation
- General Ledger drill-down report
- Accounts Receivable / Payable aging reports (standalone)

### P3
- Mobile responsiveness polish
- Multi-company support
- Stock reservation for specific orders
- Subcontracting module
