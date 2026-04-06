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

### Core Differentiator: AI-First Entry (Zero-Touch UI)
ALL data entry across the entire ERP is AI-first. No dropdown forms anywhere.
- **Global prompt bar** (bottom center, all pages) — for any entry type
- **Module-level prompt bars** (inline in Buying, Selling, Manufacturing, JournalEntry)
- **Smart popup** with pre-filled fields from AI parsing + strict master data dropdowns
- **Backend enforces** master data validation (vendor/customer/item must exist in master)
- **Shared component**: `AISmartEntry.js` (SmartFormPopup, ModuleAIPrompt, StrictDropdown)

**Supported intents**: purchase_order, sales_order, work_order, journal_entry, goods_receipt, delivery_note, crm_lead

### Master Data Enforcement
- PO/SO can ONLY use vendors/customers/items from master data
- StrictDropdown component prevents free-text entry
- Backend validates existence before creation (returns 400 if not in master)
- CRM leads are exempt (not converted yet, no statutory info needed)

### Modules Implemented
1. **Dashboard** - Module stats (CRM, Selling, Buying, Stock, HR)
2. **Chart of Accounts** - 77 ledgers, category-based classification
3. **Buying (Purchase-to-Pay)** - AI-first PO creation + linked flow
4. **Selling (Order-to-Cash)** - AI-first SO creation + linked flow
5. **Financial Statements** - Schedule III BS, P&L, TB (dynamic classification)
6. **Manufacturing** - AI-first WO creation + BOM + auto-accounting
7. **Journal Entries** - AI-first JE creation
8. **CRM** - Leads, Customers
9. **HR & Payroll** - Employees, attendance, leave, salary processing
10. **GST & TDS** - Statutory compliance modules
11. **Master Data** - Entities, items, cost centers
12. **Reports** - TB, BS, P&L exports (PDF/Excel)
13. **CSV Import** - Smart validation with CoA cross-checking
14. **GSTIN/PAN Validation** - Format checking, state code mapping

### Upcoming Tasks (P1)
- Conversational Reporting (P0 priority: "Show me top 5 vendors by purchase value")
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
- `/api/purchase/*` - Purchase module (with master data validation)
- `/api/selling/*` - Selling module (with master data validation)
- `/api/financial-statements/*` - BS, P&L, TB
- `/api/manufacturing/*` - Work Orders
- `/api/crm/*` - Leads, Customers
- `/api/hr/*` - Employees, Payroll

### Key Frontend Components
- `AISmartEntry.js` - SmartFormPopup, ModuleAIPrompt, StrictDropdown (shared)
- `UniversalAI.js` - Global prompt bar (imports SmartFormPopup from AISmartEntry)
