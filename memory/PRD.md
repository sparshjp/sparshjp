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
8. **Audit Trail (Companies Act 2013)** - Append-only, tamper-proof, field-level change tracking (Apr 2026)
9. **GST Rules Engine (India Localization)** - Full state-wise tax logic (Apr 2026)
   - All 36 Indian states/UTs with GST state codes
   - CGST+SGST for intra-state supply
   - IGST for inter-state supply
   - CGST+UTGST for UTs without legislature (Chandigarh, Ladakh, Lakshadweep, A&N Islands, DNH&DD)
   - HSN/SAC code validation (goods vs services)
   - Standard GST rate slabs (0, 0.25, 3, 5, 12, 18, 28%)
   - Auto state extraction from GSTIN
   - Items enriched with hsn_sac and gst_rate fields
   - Entities enriched with gst_state_code and state from GSTIN
   - PO and SO creation auto-computes correct tax_breakdown based on supplier/recipient states

### Key Collections
- `audit_trail`: Immutable append-only audit log
- `company_settings`: {state, gst_state_code, ...}
- `items`: {item_code, item_name, hsn_sac, gst_rate, ...}
- `entities`: {name, entity_type, gstin, gst_state_code, state, ...}
- `purchase_orders`, `selling_sales_orders` (now include tax_breakdown, supply_type, vendor/customer_state)

### Key API Endpoints
- `/api/gst/states` (GET) - All states/UTs
- `/api/gst/state/{input}` (GET) - Resolve state
- `/api/gst/compute-tax` (POST) - Single transaction GST
- `/api/gst/compute-line-items` (POST) - Multi-item GST
- `/api/gst/validate-hsn` (POST) - HSN/SAC validation
- `/api/gst/rate-slabs` (GET) - Standard rate slabs
- `/api/audit-trail` (GET) - Audit log with filters
- `/api/audit-trail/export` (GET) - CSV export

## Backlog

### P0
- GST Module UI enhancements (user to specify scope)
- GSTR-1/3B returns with state-aware tax breakdowns

### P1
- Wire Company Setup to downstream docs (FS headers, Invoice PDFs)
- AP/AR Aging Report (0-30, 30-60, 60-90, 90+ days)
- Verify Company Logo Upload end-to-end

### P2
- Inventory landed cost calculation
- Fixed asset automatic depreciation logic
- Bank reconciliation / statement matching
- E-Invoice / E-Way Bill format generation
