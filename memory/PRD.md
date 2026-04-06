# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) called "Kairos AI ERP", operating heavily on a "Zero-Touch" UI where data entry is performed via Natural Language Processing (NLP).

## Core Modules
- Purchase-to-Pay, Order-to-Cash, Inventory & Fixed Assets, Payroll & TDS, Banking, Conversational Reporting
- Follow Ind AS / Indian GAAP, Schedule III Companies Act 2013 compliant Financial Statements
- Auto-accounting: Sales and Purchase modules auto-generate journal entries and post to ledgers
- Strict Linked Document Flow: PO -> GRN -> Invoice -> Payment
- Master Data lookup (GSTIN/PAN automation) and Smart CSV validation
- AI-First Data Entry: Natural language prompts -> smart verification popups

## Architecture
- Frontend: React, Tailwind CSS, Shadcn UI, Recharts
- Backend: FastAPI, Motor (PyMongo)
- AI: Claude Sonnet 4.5 via Emergent LLM Key
- DB: MongoDB

## What's Been Implemented

### Completed Features
1. **AI-First Data Entry** (AISmartEntry.js) - Unified NLP prompt bar replacing all forms
2. **Master Data Lock** - POs/SOs reject free-text entities; must match master data
3. **Schedule III Financial Statements** - Dynamic CoA-based TB, BS, P&L (balanced)
4. **200 PolyMerx Test Transactions** - Seeded and balanced
5. **Company Setup Module** - Core ID, contact, financial, statutory, document settings
6. **Reporting AI** - Conversational data querying with charts & tables (Claude)
7. **Kairos Branding** - Custom KairosIcon SVG, "Kairos AI ERP" throughout
8. **Audit Trail (Companies Act 2013)** - Append-only, tamper-proof, field-level change tracking
9. **GST Rules Engine** - All 36 states/UTs, CGST+SGST/IGST/UTGST auto-determination
10. **AI HSN/SAC Suggest** - Claude-powered item classification with HSN chapter + rate
11. **GSTR-1 (Outward Supplies)** - B2B, B2C Large, B2C Small, HSN Summary, Doc Summary with state-aware IGST/CGST+SGST split, CSV export
12. **GSTR-3B (Monthly Summary)** - Sections 3.1 (outward), 3.2 (inter-state), 4 (ITC), 6.1 (payment with cash payable), JSON export
13. **E-Invoicing** - IRN generation for B2B invoices, NIC-format JSON (v1.1), copy-to-clipboard
14. **TDS Returns** - Form 26Q, deductee list, CSV export
15. **Separate GST & TDS sidebar sections** - Clean navigation
16. **Master Data Pages** - Separate Vendors, Customers, Items pages with full CRUD forms, GSTIN validation, GST state extraction, AI HSN suggest (Completed 2026-04-06)
17. **AP/AR Aging Report** - 0-30, 30-60, 60-90, 90+ day buckets with vendor/customer drill-down, expandable invoice details (Completed 2026-04-06)
18. **Company Logo/Name Wiring** - Company logo and name dynamically render on Dashboard, Financial Statements (BS, P&L, TB headers) (Completed 2026-04-06)
19. **Legacy Cleanup** - Removed old MasterData.js from Settings, cleaned up App.js routes and imports (Completed 2026-04-06)

### Key Collections
- `audit_trail`, `company_settings`, `chart_of_accounts`
- `items` (with hsn_sac, gst_rate), `entities` (with gst_state_code, state)
- `purchase_orders`, `selling_sales_orders` (with tax_breakdown, supply_type)
- `purchase_invoices`, `selling_invoices`, `work_orders`

### Key API Endpoints
- `/api/gst/states`, `/api/gst/compute-tax`, `/api/gst/compute-line-items`, `/api/gst/suggest-hsn`, `/api/gst/validate-hsn`, `/api/gst/rate-slabs`
- `/api/statutory/gstr1`, `/api/statutory/gstr3b`, `/api/statutory/e-invoices`, `/api/statutory/e-invoice/{num}/json`, `/api/statutory/tds-return`
- `/api/audit-trail`, `/api/audit-trail/stats`, `/api/audit-trail/export`
- `/api/entities`, `/api/stock/items`
- `/api/aging/payables`, `/api/aging/receivables`
- `/api/company/settings`, `/api/company/settings/logo`

## Backlog

### P1
- Inventory landed cost calculation
- Fixed asset automatic depreciation logic

### P2
- Bank reconciliation / statement matching
- E-Way Bill data for goods movement
- Mobile responsiveness polish
