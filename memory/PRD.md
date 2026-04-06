# Kairos Advisory - Product Requirements Document

## Product Overview
AI-Native ERP (India Localization) called "Kairos Advisory", operating on a "Zero-Touch" UI where data entry is via NLP. Follows Ind AS / Indian GAAP, April 1 - March 31 fiscal cycle. Schedule III Companies Act 2013 compliant financial statements.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Lucide React, Outfit + JetBrains Mono fonts
- **Backend**: FastAPI, Motor (async MongoDB driver)
- **Database**: MongoDB
- **AI**: Claude Sonnet 4.5 (NLP), Gemini 3 Flash (OCR) via Emergent LLM Key
- **Brand**: Navy #0D1B2A, Teal #00C9A7, Off-white #F4F3EF

## Core Modules
1. **Dashboard** - Overview metrics
2. **Selling** - CRM, Sales Module (SO > DN > Invoice > Payment) with auto-accounting
3. **Buying** - Purchase Module (PO > GRN > Invoice > Payment) with auto-accounting
4. **Stock** - Inventory, Quality
5. **HR** - Employees, Attendance, Leave, Payroll
6. **Accounting** - Journal Entries, Financial Statements (Schedule III), GST & TDS
7. **Reports & Admin** - Data Tables, Settings (CoA, Cost Centers, Master Data, CSV Import)

## What's Implemented

### Completed (Apr 6, 2026)
- [x] Full Kairos Advisory brand: Navy/Teal theme, Outfit font, logo
- [x] Selling Module: Quotation > SO > DN > Sales Invoice > Customer Payment (auto JE)
- [x] Buying Module: PO > GRN > Purchase Invoice > Vendor Payment (auto JE)
- [x] **Schedule III Financial Statements**: Balance Sheet + P&L + Trial Balance
- [x] **GST & TDS Statutory Reports**: GSTR-1, GSTR-3B, TDS Return with CSV/JSON export
- [x] **Smart AI Prompt Forms**: Module-specific compulsory fields (Customer/Vendor name, GSTIN, Item, Qty, Rate)
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
- Sales Invoice → DR AR, CR Revenue, CR GST Output, DR COGS, CR FG Inventory
- Customer Payment → DR Bank, CR AR (or Advance from Customer)
- GRN → DR RM Inventory, DR GST Input, CR AP + stock level update
- Purchase Invoice → DR Expense/Inventory, DR GST Input, CR AP
- Vendor Payment → DR AP, CR Bank

### Testing Status
- Deep test: 48 transactions, TB balanced at ₹15M+
- Iteration 4: 100% pass (23/23 backend + all frontend)
- GST verified: GSTR-1 (5 invoices), GSTR-3B (Net payable ₹1.91L), TDS Return

## Architecture
```
/app/backend/
  server.py, ai_orchestrator.py
  routes_crm.py, routes_sales.py, routes_selling.py
  routes_purchase.py, routes_stock.py, routes_hr.py
  routes_financial_statements.py, routes_statutory.py

/app/frontend/src/
  App.js, index.css (Kairos Advisory brand)
  components/UniversalAI.js (Smart forms)
  pages/
    FinancialStatements.js, GSTModule.js
    SellingModule.js, BuyingModule.js
    JournalEntry.js, AdminDataTables.js
    Dashboard, CRM, Stock, HR, etc.
```

## Remaining Backlog

### P1
- PDF/Excel download for Balance Sheet, P&L, Trial Balance
- Manufacturing Work Order lifecycle (Open > Material Issue > Close > FG Receipt)
- GSTIN/PAN real API lookup

### P2
- Bank reconciliation statement matching
- Fixed asset register with auto depreciation
- Inventory landed cost calculation
- Mobile responsiveness polish
- Built-in test runner UI
