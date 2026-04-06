# Kairos Advisory - AI-Native ERP (India Localization)
## Product Requirements Document

### Original Problem Statement
Build an AI-Native ERP called "Kairos Advisory" with India localization, operating on a "Zero-Touch" UI with NLP-driven data entry. Must follow Ind AS / Indian GAAP, Schedule III Companies Act 2013 compliant Financial Statements.

### Company
PolyMerx Specialty Chemicals Pvt. Ltd.

### Tech Stack
- Frontend: React, Tailwind CSS, Shadcn UI
- Backend: FastAPI, Motor (async MongoDB), reportlab, openpyxl
- AI: Claude Sonnet 4.5 (text), Gemini 3 Vision (OCR) via Emergent LLM Key
- Theme: Navy (#0D1B2A) / Teal (#00C9A7)

### Architecture
Modular monolith with strict Linked Document Flow:
- Purchase: PO → GRN → Purchase Invoice → Vendor Payment
- Selling: SO → Delivery Note → Sales Invoice → Customer Receipt
- Manufacturing: Work Order (consume RM → WIP → FG) with auto-JEs

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
11. **Master Data** - Entities, items, cost centers
12. **Reports** - Trial Balance, Balance Sheet, P&L exports (PDF/Excel)
13. **CSV Import** - Smart validation with CoA cross-checking
14. **GSTIN/PAN Validation** - Format checking, state code mapping

### Data Seeded (PolyMerx 200 Transactions)
- 77 CoA accounts, 7 cost centers
- 12 vendors, 10 customers, 18 items (RM + FG)
- 9 employees, 7 CRM leads
- 10 POs, 10 GRNs, 6 purchase invoices, 5 vendor payments
- 8 SOs, 8 delivery notes, 8 sales invoices, 8 customer receipts
- 8 work orders (7 completed + 1 in-progress)
- 49+ journal entries (auto-generated)
- TB Balanced: DR = CR = 11.63 Cr

### P0 Completed
- PolyMerx 200-transaction seed script executed and validated
- Fixed opening balance gaps (Retained Earnings, FG Inventory, AR)
- Manufacturing JEs added (WO Start: DR WIP/CR RM, WO Complete: DR FG/CR WIP/CR Mfg Overhead)
- Financial statements rewritten with dynamic category-based classification
- Balance Sheet balanced at 9.67 Cr
- All 28 backend tests passed, all frontend modules functional

### Upcoming Tasks (P1)
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
- `/api/coa` - Chart of Accounts
- `/api/purchase/*` - Purchase module (orders, grn, invoices, payments)
- `/api/selling/*` - Selling module (sales-orders, delivery-notes, invoices, receipts)
- `/api/financial-statements/*` - BS, P&L, TB
- `/api/manufacturing/*` - Work Orders
- `/api/crm/*` - Leads, Customers
- `/api/hr/*` - Employees, Payroll
- `/api/reports/*` - Various reports

### Key DB Collections
- chart_of_accounts, journal_entries, manual_journal_entries
- purchase_orders, goods_receipt_notes, purchase_invoices, vendor_payments
- selling_sales_orders, selling_delivery_notes, selling_invoices, customer_payments
- items, entities (vendors/customers), employees, work_orders, leads
