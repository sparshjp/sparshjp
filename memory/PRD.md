# Kairos Advisory - AI-Native ERP (India Localization)
## Product Requirements Document

### Original Problem Statement
Build an AI-Native ERP called "Kairos Advisory" with India localization, operating on a "Zero-Touch" UI with NLP-driven data entry. Must follow Ind AS / Indian GAAP, Schedule III Companies Act 2013 compliant Financial Statements.

### Company
PolyMerx Specialty Chemicals Pvt. Ltd.

### Tech Stack
- Frontend: React, Tailwind CSS, Shadcn UI
- Backend: FastAPI, Motor (async MongoDB), reportlab, openpyxl
- AI: Claude Sonnet 4.5 (text parsing), Gemini 3 Vision (OCR) via Emergent LLM Key
- Theme: Navy (#0D1B2A) / Teal (#00C9A7)

### Architecture
Modular monolith with strict Linked Document Flow:
- Purchase: PO → GRN → Purchase Invoice → Vendor Payment
- Selling: SO → Delivery Note → Sales Invoice → Customer Receipt
- Manufacturing: Work Order (consume RM → WIP → FG) with auto-JEs

### Core Differentiator: AI-First Entry
The primary data entry mechanism is natural language. User types a prompt → AI parses intent + extracts structured data → Smart popup shows pre-filled form → User confirms → Entry created.

**Backend**: `/api/ai/parse-prompt` endpoint sends prompt to Claude with full master data context (vendors, customers, items, ledgers, pending POs/SOs) for accurate entity matching.

**Supported intents**: purchase_order, sales_order, work_order, journal_entry, goods_receipt, delivery_note, crm_lead

### Modules Implemented
1. **Dashboard** - Module stats overview (CRM, Selling, Buying, Stock, HR)
2. **Chart of Accounts** - 77 ledgers, category-based classification
3. **Buying (Purchase-to-Pay)** - PO→GRN→Invoice→Payment linked flow
4. **Selling (Order-to-Cash)** - SO→DN→Invoice→Receipt linked flow
5. **Financial Statements** - Schedule III BS, P&L, TB with dynamic classification
6. **Manufacturing** - Work Orders with BOM, auto-accounting (RM→WIP→FG)
7. **CRM** - Leads, Customers, Lead qualification & conversion
8. **HR & Payroll** - Employees, attendance, leave, salary processing
9. **GST & TDS** - Statutory compliance modules
10. **Journal Entries** - Manual and auto-generated
11. **AI Entry Module** - NLP prompt → smart popup → create entry
12. **Master Data** - Entities, items, cost centers
13. **Reports** - Trial Balance, Balance Sheet, P&L exports (PDF/Excel)
14. **CSV Import** - Smart validation with CoA cross-checking
15. **GSTIN/PAN Validation** - Format checking, state code mapping

### Data Seeded (PolyMerx 200 Transactions)
- 77 CoA accounts, 7 cost centers, 12 vendors, 10 customers, 18 items
- 9 employees, 7 CRM leads
- 12 POs (10 seeded + 2 AI-created), 10 GRNs, 6 purchase invoices
- 8 SOs, 8 delivery notes, 8 sales invoices, 8 customer receipts
- 8 work orders (7 completed + 1 in-progress)
- 49+ journal entries (auto-generated)
- TB Balanced

### Upcoming Tasks (P1)
- Conversational Reporting ("Show me top 5 vendors by purchase value")
- AP/AR Aging Report (0-30, 30-60, 60-90, 90+ days)
- Inventory landed cost calculation
- Fixed asset auto-depreciation

### Backlog (P2)
- Bank reconciliation / statement matching
- General Ledger drill-down
- Mobile responsiveness polish
- Multi-company support
- Subcontracting module

### Key API Endpoints
- `/api/ai/parse-prompt` - AI prompt parsing (POST)
- `/api/coa` - Chart of Accounts
- `/api/purchase/*` - Purchase module
- `/api/selling/*` - Selling module
- `/api/financial-statements/*` - BS, P&L, TB
- `/api/manufacturing/*` - Work Orders
- `/api/crm/*` - Leads, Customers
- `/api/hr/*` - Employees, Payroll
- `/api/reports/*` - Various reports
