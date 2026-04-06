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
2. **Selling** - CRM, Sales (Quotation > SO > Delivery > Invoice)
3. **Buying** - Purchase (MR > RFQ > PO > Receipt > Invoice), P2P Legacy
4. **Stock** - Inventory, Quality
5. **HR** - HR & Payroll, Projects
6. **Accounting** - Journal Entries (manual/correction/audit)
7. **Reports & Settings** - Reports, Admin Data Tables, Settings (CoA, Cost Centers, Master Data, CSV Import)

## What's Implemented

### Completed (Apr 6, 2026)
- [x] Base ERP UI with Shadcn/Tailwind, Kairos branding
- [x] Sidebar navigation with all module sections
- [x] Modular backend: routes_crm.py, routes_sales.py, routes_stock.py, routes_hr.py
- [x] Chart of Accounts CRUD + CSV upload
- [x] Cost Centers CRUD
- [x] Vendor/Client Master with GSTIN lookup (mocked)
- [x] CSV Import with validation (Zoho-standard headers)
- [x] Document upload with OCR extraction (Gemini 3 Flash vision)
- [x] NLP Transaction prompt (Claude Sonnet 4.5) - creates draft transactions with journal entries
- [x] Transaction posting to ledger with CoA balance updates
- [x] Financial reports: Balance Sheet, P&L, Trial Balance
- [x] PDF export (Balance Sheet), Excel export (Trial Balance)
- [x] Universal AI Assistant modal (routes to appropriate module)
- [x] AI Orchestrator with module-specific handlers (CRM, Sales, Purchase, Stock, HR, Projects, Quality, Accounting)
- [x] **Journal Entry module** - Manual entries, corrections, audit adjustments with debit/credit balancing
- [x] **Admin Data Tables** - View all DB collections with search, pagination, CSV export
- [x] Conversational reporting via AI

### AI Integration Status
- Claude Sonnet 4.5: LIVE via Emergent LLM Key (text generation, NLP parsing)
- Gemini 3 Flash: LIVE via Emergent LLM Key (OCR/vision for invoice extraction)
- GSTIN/PAN lookup: MOCKED (returns mock data)

## Prioritized Backlog

### P0 (Next)
- OCR end-to-end testing with real invoice images
- GSTIN/PAN lookup - integrate with real government API or third-party service

### P1
- CSV/Excel Import Template validation against Chart of Accounts
- Downloadable artifacts (PDF/Excel) for P&L, GSTR-1, Fixed Asset Register

### P2
- Inventory landed cost calculation
- Fixed asset automatic depreciation
- Bank statement matching for Bank Reconciliation
- Mobile responsiveness polish

## Architecture
```
/app/backend/
  server.py          - Main FastAPI app with all core routes
  ai_orchestrator.py - AI module routing (Claude Sonnet 4.5)
  routes_crm.py      - CRM module routes
  routes_sales.py    - Sales module routes
  routes_stock.py    - Stock module routes
  routes_hr.py       - HR module routes
  models.py          - Pydantic models

/app/frontend/src/
  App.js             - Routes, sidebar, layout
  components/
    UniversalAI.js   - AI assistant floating button + modal
  pages/
    Dashboard, CRM, Sales, Purchase, Stock, HR, Projects, Quality
    PurchaseToPay, Reports, ChartOfAccounts, CostCenters, MasterData, CSVImport
    JournalEntry, AdminDataTables
```

## Key API Endpoints
- `POST /api/transactions/prompt` - NLP to structured journal entries
- `POST /api/ai/universal-prompt` - Universal AI assistant
- `POST /api/journal-entries/manual` - Create manual journal entry
- `GET /api/journal-entries/manual` - List journal entries
- `POST /api/journal-entries/manual/{id}/post` - Post entry to ledger
- `GET /api/admin/tables` - List all DB collections
- `GET /api/admin/tables/{name}` - Get table data with pagination/search
- `GET /api/admin/tables/{name}/export` - CSV export
- `GET /api/reports/balance-sheet`, `/profit-loss`, `/trial-balance`
- `POST /api/documents/upload` - OCR document processing
