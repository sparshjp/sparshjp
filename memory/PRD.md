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

## Core Modules
1. **Dashboard** - Overview metrics
2. **Selling** - CRM, Sales Module (SO > DN > Invoice > Payment) with auto-accounting
3. **Buying** - Purchase Module (PO > GRN > Invoice > Payment) with auto-accounting
4. **Stock & Manufacturing** - Inventory, Quality, Work Orders (BOM, lifecycle, FG receipt)
5. **HR** - Employees, Attendance, Leave, Payroll
6. **Accounting** - Journal Entries, Financial Statements (Schedule III), GST & TDS
7. **Reports & Admin** - Data Tables, Settings (CoA, Cost Centers, Master Data, CSV Import)

## What's Implemented

### Completed (Apr 6, 2026)
- [x] Full Kairos Advisory brand: Navy/Teal theme across ALL pages (Settings, Reports, etc.)
- [x] Selling Module: Quotation > SO > DN > Sales Invoice > Customer Payment (auto JE)
- [x] Buying Module: PO > GRN > Purchase Invoice > Vendor Payment (auto JE)
- [x] **Manufacturing Module**: Work Orders with BOM, lifecycle (Draft > In Progress > Completed), auto-accounting (material issue, FG receipt, scrap/loss)
- [x] **Schedule III Financial Statements**: Balance Sheet + P&L + Trial Balance with Excel export
- [x] **GST & TDS Statutory Reports**: GSTR-1, GSTR-3B, TDS Return with CSV/JSON export
- [x] **GSTIN/PAN Intelligence**: Format validation, PAN extraction from GSTIN, state code mapping, entity type detection
- [x] **Enhanced CSV Import Validation**: Header validation, CoA cross-check, journal balance check, numeric/date validation, entity lookup
- [x] **Smart AI Prompt Forms**: Module-specific compulsory fields
- [x] **Negative Stock Enforcement**: Warning when delivery exceeds available stock
- [x] **Credit Limit Checks**: Warning when SO exceeds customer credit limit
- [x] Journal Entry module (manual entries, corrections, audit)
- [x] Admin Data Tables (view all DB collections)
- [x] CRM (Leads, Opportunities, Customers)
- [x] Chart of Accounts, Cost Centers, Master Data, CSV Import
- [x] Claude Sonnet 4.5 NLP integration (LIVE)
- [x] Gemini 3 Flash OCR integration (LIVE)
- [x] Deep tested with 48 NanoChip Industries transactions

### Auto-Accounting Flows
- Sales Invoice -> DR AR, CR Revenue, CR GST Output, DR COGS, CR FG Inventory
- Customer Payment -> DR Bank, CR AR (or Advance)
- GRN -> DR RM Inventory, DR GST Input, CR AP + stock update
- Purchase Invoice -> DR Expense/Inventory, DR GST Input, CR AP
- Vendor Payment -> DR AP, CR Bank
- Work Order Start -> DR WIP, CR Raw Material (material issue)
- Work Order Complete -> DR Finished Goods, CR WIP (FG receipt); DR Scrap/Loss, CR WIP (scrap)

### Testing Status
- Deep test: 48 transactions, TB balanced at ₹15M+
- Iteration 4: 100% pass (23/23 backend + all frontend)
- Iteration 5: 100% pass (Manufacturing + Excel exports, 14/14 backend + all frontend)
- Iteration 6: 100% pass (GSTIN/PAN + CSV validation, 22/22 backend + all frontend)

## Architecture
```
/app/backend/
  server.py, ai_orchestrator.py
  routes_crm.py, routes_sales.py, routes_selling.py
  routes_purchase.py, routes_stock.py, routes_hr.py
  routes_financial_statements.py, routes_statutory.py
  routes_manufacturing.py (NEW - Work Orders with auto-accounting)

/app/frontend/src/
  App.js, index.css (Kairos Advisory brand)
  components/UniversalAI.js (Smart forms)
  pages/
    ManufacturingModule.js (NEW - WO lifecycle UI)
    FinancialStatements.js (Excel download buttons)
    SellingModule.js, BuyingModule.js, GSTModule.js
    JournalEntry.js, AdminDataTables.js
    Dashboard, CRM, Stock, HR, etc.
```

## Remaining Backlog

### P2
- Bank reconciliation statement matching
- Fixed asset register with auto depreciation
- Inventory landed cost calculation
- Mobile responsiveness polish

### P3
- Built-in test runner UI
- Real GSTIN government API integration (paid service)
