# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine that acts as an autonomous developer.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React, DOMPurify
- Backend: FastAPI, Motor (async MongoDB), anthropic SDK, openai SDK, shlex (security)
- AI: 7 LLM Providers — Claude Direct, GPT-4o Direct, Claude (Emergent), Gemini 3 Flash, GPT-5 (Emergent), Groq Llama 3.3, OpenRouter
- DB: MongoDB

## Kairos AI Engine v4 — 30 Tools
### LLM Providers (Direct keys first, zero Emergent credits when configured):
1. Claude Direct (User Anthropic key) | 2. GPT-4o Direct (User OpenAI key)
3. Claude Sonnet 4.5 (Emergent) | 4. Gemini 3 Flash (Emergent) | 5. GPT-5 (Emergent)
6. Groq Llama 3.3 (User key) | 7. OpenRouter (User key)

### System Prompt: E1-Level Reasoning
- Reasoning Methodology: Decompose → Risk assess → Plan → Execute → Verify → Self-heal
- Debugging Discipline: Reproduce → Trace → Root cause → Verify → Regression check
- Token Efficiency: 8KB result cap, 10-msg context window, compressed prompt

## Code Quality Fixes Applied (2026-04-07)
### Security (Critical)
- **Shell Injection**: All `shell=True` removed; subprocess uses argument lists; `shlex.quote()` imported; HARD_BLOCKED expanded to include `curl|sh`, `wget|sh`, `curl|bash`, `wget|bash`
- **Code Injection**: Replaced `exec()` screenshot with safe `screenshot_helper.py` subprocess called via `asyncio.create_subprocess_exec` with argument passing
- **XSS**: Added DOMPurify sanitization to `dangerouslySetInnerHTML` in AIAgentsPage.js
- **Path Validation**: Added regex validation for `lint_code` tool path parameter

### React Hook Dependencies (5 files)
- Stock.js: useCallback for fetchItems, fetchStockEntries, checkReorder
- Sales.js: useCallback for fetchQuotations, fetchSalesOrders, fetchDeliveryNotes
- JournalEntry.js: useCallback for fetchEntries + fixed API import
- ManufacturingModule.js: useCallback for fetchWorkOrders + fixed API import
- MasterData.js: useCallback for fetchEntities with entityType dependency

### Key-as-Index Anti-pattern (3 files)
- TimesheetsPage.js: ts.id instead of idx
- ProjectsModule.js: c.label, ts.id instead of i
- ReportingAI.js: q and msg.timestamp instead of i

### execute_tool Refactoring (P3 - In Progress)
- Security hardening applied to all 30 tool handlers
- Tool registry pattern designed but not yet extracted (function works, code is functional)

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management, Timesheets, Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer, Unified AI Engine v4
### Finance: Expense Management, Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback, Announcements

## Backlog
### P1: Client Portal, Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
### P3: Extract tool handlers from execute_tool() into kairos_tools.py (refactoring)
### P3: Split large React components (AIAgentsPage 820→multiple, BuyingModule 304, SellingModule 306)
