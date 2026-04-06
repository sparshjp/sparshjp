# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) called "Kairos AI ERP", operating heavily on a "Zero-Touch" UI where data entry is performed via Natural Language Processing (NLP).

## Core Modules
- Purchase-to-Pay, Order-to-Cash, Inventory & Fixed Assets, Payroll & TDS, Banking, Conversational Reporting
- Follow Ind AS / Indian GAAP, Schedule III Companies Act 2013 compliant Financial Statements
- Auto-accounting: Sales and Purchase modules auto-generate journal entries and post to ledgers
- Strict Linked Document Flow: PO -> GRN -> Invoice -> Payment
- Master Data lookup (GSTIN/PAN automation) and Smart CSV validation
- AI-First Data Entry: Natural language prompts → smart verification popups

## Architecture
- Frontend: React, Tailwind CSS, Shadcn UI, Recharts
- Backend: FastAPI, Motor (PyMongo)
- AI: Claude Sonnet 4.5 via Emergent LLM Key
- DB: MongoDB

## What's Been Implemented

### Completed Features
1. **AI-First Data Entry** (AISmartEntry.js) - Unified NLP prompt bar replacing all forms across Buying, Selling, Manufacturing, Journals ✅
2. **Master Data Lock** - POs/SOs reject free-text entities; must match existing vendors/customers/items ✅
3. **Schedule III Financial Statements** - Dynamic CoA-based Trial Balance, Balance Sheet, P&L (perfectly balanced) ✅
4. **200 PolyMerx Test Transactions** - Seeded and balanced via seed_polymerx.py ✅
5. **Company Setup Module** - Core identification, contact, financial, statutory, document settings ✅
6. **Reporting AI** - Conversational data querying with charts & tables (Claude-powered) ✅
7. **Kairos Branding** - Custom SVG KairosIcon (K mark), "Kairos AI ERP" throughout ✅
8. **Audit Trail (Companies Act 2013)** - Append-only, tamper-proof, field-level change tracking ✅ (Apr 2026)
   - Compliant with Rule 3(1), Companies (Accounts) Rules, 2014
   - Logs CREATE/UPDATE/DELETE/SUBMIT/CANCEL/POST actions
   - Before/after field-level diff for UPDATE events
   - Full document snapshots for CREATE events
   - CSV export for auditor handoff
   - Filterable by date, doc type, action, search
   - Integrated into: Purchase, Selling, Manufacturing, Journal Entries, CoA, Entities, Company Settings

### Key Collections
- `audit_trail`: Immutable append-only audit log (no edit/delete)
- `company_settings`, `chart_of_accounts`, `journal_entries`, `manual_journal_entries`
- `purchase_orders`, `selling_sales_orders`, `items`, `vendors`, `customers`
- `purchase_invoices`, `selling_invoices`, `work_orders`

### Key API Endpoints
- `/api/audit-trail` (GET) - List with filters, pagination
- `/api/audit-trail/stats` (GET) - Summary counts
- `/api/audit-trail/document-types` (GET) - Distinct types for dropdowns
- `/api/audit-trail/export` (GET) - CSV download
- `/api/company/settings` (GET/PUT)
- `/api/company/reporting-ai` (POST)
- `/api/ai/parse-prompt` (POST)

## Backlog

### P0 (High Priority)
- GST Module enhancements (GSTR-1 B2C/HSN, GSTR-3B detail, GSTR-2B ITC matching) — User requested

### P1
- Wire Company Setup to downstream docs (Financial Statement headers, Invoice PDFs)
- AP/AR Aging Report (0-30, 30-60, 60-90, 90+ day buckets)
- Verify Company Logo Upload end-to-end

### P2
- Inventory landed cost calculation
- Fixed asset automatic depreciation logic
- Bank reconciliation / statement matching
- E-Invoice / E-Way Bill format generation
- Mobile responsiveness polish
