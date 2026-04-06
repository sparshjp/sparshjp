# Kairos Accounting - Product Requirements Document

## Product Overview
AI-Native ERP (India Localization) called "Kairos Accounting", operating on a "Zero-Touch" UI where data entry is via Natural Language Processing (NLP). Follows Ind AS / Indian GAAP, default April 1 - March 31 fiscal cycle.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Lucide React icons
- **Backend**: FastAPI, Motor (async MongoDB driver)
- **Database**: MongoDB
- **AI**: Claude Sonnet 4.5 (text/NLP), Gemini 3 Flash (OCR/vision) via Emergent LLM Key

## Core Modules
1. **Dashboard** - Overview metrics
2. **Selling** - CRM, Sales Module (Quotation > SO > Delivery Note > Sales Invoice > Customer Payment) with **auto journal entry generation**
3. **Buying** - Purchase Module (PO > GRN > Purchase Invoice > Vendor Payment) with **auto journal entry generation**
4. **Stock** - Inventory, Quality
5. **HR** - HR & Payroll, Projects
6. **Accounting** - Journal Entries (manual/correction/audit), **Financial Statements (Schedule III Companies Act 2013)**
7. **Reports & Admin** - Reports, Admin Data Tables, Settings (CoA, Cost Centers, Master Data, CSV Import)

## What's Implemented

### Completed (Apr 6, 2026)
- [x] Base ERP UI with Shadcn/Tailwind, Kairos branding
- [x] Sidebar navigation with all module sections
- [x] Modular backend: routes_crm, routes_sales, routes_stock, routes_hr, routes_purchase, routes_selling, routes_financial_statements
- [x] Chart of Accounts CRUD + CSV upload
- [x] Cost Centers CRUD
- [x] Vendor/Client Master with GSTIN lookup (mocked)
- [x] CSV Import with validation
- [x] Document upload with OCR extraction (Gemini 3 Flash vision)
- [x] NLP Transaction prompt (Claude Sonnet 4.5)
- [x] Transaction posting to ledger with CoA balance updates
- [x] Journal Entry module - Manual entries, corrections, audit adjustments
- [x] Admin Data Tables - View all DB collections with search, pagination, CSV export
- [x] Universal AI Assistant modal
- [x] AI Orchestrator with module-specific handlers

### NEW - Comprehensive Sales & Purchase with Auto-Accounting
- [x] **Selling Module**: Quotation > Sales Order > Delivery Note > Sales Invoice > Customer Payment
  - Sales Invoice auto-creates: DR Accounts Receivable, CR Sales Revenue, CR GST Output, DR COGS, CR FG Inventory
  - Customer Payment auto-creates: DR Bank, CR Accounts Receivable (or Advance from Customer)
- [x] **Buying Module**: Purchase Order > GRN > Purchase Invoice > Vendor Payment
  - GRN auto-creates: DR Raw Material Inventory, DR GST Input, CR Accounts Payable + updates stock levels
  - Purchase Invoice auto-creates: DR Expense/Inventory, DR GST Input, CR Accounts Payable
  - Vendor Payment auto-creates: DR Accounts Payable, CR Bank

### NEW - Schedule III Financial Statements (Companies Act 2013)
- [x] **Balance Sheet** - Division I format with Equity & Liabilities / Assets hierarchy, Note references
- [x] **Statement of Profit & Loss** - Line items I through XVI per Schedule III
- [x] **Trial Balance** - Debit/Credit with balance check
- [x] Expandable detail rows (click to see Inventory breakdown, Expense breakdown, etc.)

### AI Integration Status
- Claude Sonnet 4.5: LIVE via Emergent LLM Key
- Gemini 3 Flash: LIVE via Emergent LLM Key
- GSTIN/PAN lookup: MOCKED

### Deep Test Results - NanoChip Industries
- 48 transactions processed across all modules
- Trial Balance: IN BALANCE
- All auto-accounting JE verified
- Testing agent: 100% pass rate (27/27 backend + all frontend)

## Prioritized Backlog

### P0 (Next)
- GSTIN/PAN lookup with real API
- Built-in test runner UI (user requested)

### P1
- Negative stock enforcement (block overselling)
- Credit limit enforcement on Sales Orders
- CSV/Excel Import Template validation against Chart of Accounts
- PDF/Excel downloads for all financial statements

### P2
- Inventory landed cost calculation
- Fixed asset automatic depreciation
- Bank statement matching for Bank Reconciliation
- Manufacturing Work Order lifecycle module
- Mobile responsiveness polish

## Architecture
```
/app/backend/
  server.py                    - Main FastAPI app with core routes
  ai_orchestrator.py           - AI module routing (Claude Sonnet 4.5)
  routes_crm.py                - CRM module routes
  routes_sales.py              - Sales module routes (legacy)
  routes_selling.py            - NEW: Selling with auto-accounting
  routes_purchase.py           - NEW: Buying with auto-accounting
  routes_stock.py              - Stock module routes
  routes_hr.py                 - HR module routes
  routes_financial_statements.py - NEW: Schedule III reports

/app/frontend/src/
  App.js                       - Routes, sidebar, layout
  pages/
    FinancialStatements.js     - NEW: Schedule III BS, P&L, TB
    SellingModule.js            - NEW: Sales Order > DN > Invoice > Payment
    BuyingModule.js             - NEW: PO > GRN > Invoice > Payment
    JournalEntry.js, AdminDataTables.js
    Dashboard, CRM, Stock, HR, etc.
```

## Key API Endpoints
### Selling (auto-accounting)
- `POST /api/selling/sales-orders` - Create SO
- `POST /api/selling/delivery-notes` - Create DN (updates stock)
- `POST /api/selling/invoices` - Create SI (auto: Revenue + COGS + GST JE)
- `POST /api/selling/payments` - Customer receipt (auto: Bank + AR JE)

### Buying (auto-accounting)
- `POST /api/purchase/orders` - Create PO
- `POST /api/purchase/grn` - Goods Receipt (auto: Inventory + GST + AP JE, stock update)
- `POST /api/purchase/invoices` - Purchase Invoice (auto: Expense + GST + AP JE)
- `POST /api/purchase/payments` - Vendor payment (auto: AP + Bank JE)

### Financial Statements
- `GET /api/financial-statements/balance-sheet` - Schedule III BS
- `GET /api/financial-statements/profit-and-loss` - Schedule III P&L
- `GET /api/financial-statements/trial-balance` - TB with balance check
