# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine that acts as an autonomous developer.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
- Backend: FastAPI, Motor (async MongoDB)
- AI: 5 LLM Providers via Emergent Universal Key + Groq/OpenRouter API keys
- DB: MongoDB

## Kairos AI Engine v3.3 — 5-Provider Multi-Model (Updated 2026-04-06)
### LLM Providers (Priority Order):
1. **Claude Sonnet 4.5** (Emergent Key) — Primary, most capable for code generation
2. **Gemini 3 Flash** (Emergent Key) — Fast, falls back to next on complex prompts
3. **GPT-5** (Emergent Key) — Strong code generation, verified working
4. **Groq / Llama 3.3** (Groq API Key) — Fast inference, rate-limited on free tier
5. **OpenRouter Auto** (OpenRouter Key) — Last resort fallback

### Capabilities:
- **21 Tools + 2 Compound**: read_file, create_file, patch_file, insert_lines, delete_lines, write_file, get_schema, run_query, restart_service, test_api, check_logs, install_package, run_tests, grep_search, list_files, run_command, verify_deployment, web_search, take_screenshot + scaffold_module, create_page
- **Smart Provider Routing**: Auto-skips rate-limited providers, user-selectable via dropdown
- **Web Search**: DuckDuckGo via `ddgs` library
- **Screenshots**: Headless Chromium via Playwright
- **Live Thought Process**: Streams LLM reasoning to frontend in real-time
- **Deployment Verification**: Backend health, API endpoints, frontend routes, file existence
- **Auto-Polish/Fix/Restart**: AST-based code fixes, startup error diagnosis

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management, Timesheets, Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer, Unified AI Engine v3.3
### Finance: Expense Management, Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback

## Recent Changes (2026-04-06)
- Added Gemini 3 Flash (gemini-3-flash-preview) via Emergent Universal Key
- Added GPT-5 (gpt-5) via Emergent Universal Key
- Added provider selector dropdown in UI with all 5 providers + Auto
- Provider badges show correct model names and colors on responses
- Smart fallback: Gemini gracefully falls back when None returned for complex prompts

## Backlog
### P1: Client Portal, Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
