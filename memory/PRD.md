# Kairos AI ERP - Product Requirements Document

## Original Problem Statement
Build an AI-Native ERP (India Localization) pivoted to IT Services context ("Nexora IT ERP") with Project Management, Timesheets, Revenue Accrual (Ind AS 115), and a Unified AI Engine that acts as an autonomous developer. Role-based access control with Creator/Admin/specialized roles.

## Company: Nexora Digital Solutions Pvt. Ltd.
- **CIN:** U72200GJ2019PTC108341 | **GSTIN:** 24AABCN4567P1Z8
- **Industry:** IT Services | **Billing:** INR, USD, GBP

## Architecture
- Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React, DOMPurify
- Backend: FastAPI, Motor (async MongoDB), bcrypt, PyJWT, anthropic SDK, openai SDK
- AI: 7 LLM Providers (Direct keys first, then Emergent, then 3rd party)
- DB: MongoDB
- Auth: JWT (24h access + 7d refresh), bcrypt password hashing, brute force protection

## RBAC System (Implemented 2026-04-07)
### Roles (9 total):
| Role | Level | Access |
|------|-------|--------|
| creator | 100 | Everything + Kairos AI Engine |
| admin | 90 | Everything except Kairos AI |
| finance_manager | 70 | Financial Statements, Journal Entries, CoA, Bank Recon, Audit Trail |
| project_manager | 70 | Projects, Timesheets, Revenue Recognition |
| hr_manager | 70 | Employees, Payroll, Leave Management |
| ap_clerk | 50 | Buying, Vendor Bills, Purchase Orders |
| ar_clerk | 50 | Selling, Invoices, Customer Receipts |
| tax_compliance | 50 | GST, TDS, E-Invoice, GSTR filings |
| viewer | 10 | Dashboard + Reports (read-only) |

### Auth Endpoints:
- POST /api/auth/login — JWT login with brute force protection
- POST /api/auth/register — Self-register (viewer default, no creator)
- GET /api/auth/me — Current user profile
- POST /api/auth/logout — Clear auth cookies
- POST /api/auth/refresh — Refresh access token
- POST /api/auth/forgot-password — Request password reset
- POST /api/auth/reset-password — Complete password reset
- GET /api/auth/roles — List all roles and section access
- GET/POST/PUT/DELETE /api/auth/users — User CRUD (admin/creator only)

## Kairos AI Engine v4 — 30 Tools (Creator-only access)
### LLM Providers: Claude Direct, GPT-4o Direct, Claude/Gemini/GPT-5 (Emergent), Groq, OpenRouter

## Modules Implemented
### Core: Dashboard, Company Setup, CRM, Selling, Buying, Stock, HR & Payroll
### Delivery: Project Management, Timesheets, Revenue Recognition (Ind AS 115)
### Intelligence: Transaction Explorer, Unified AI Engine v4
### Finance: Expense Management, Journal Entries, CoA, Financial Statements, AP/AR Aging, Audit Trail, GST, TDS
### Auth: Login, User Management, Role-Based Navigation
### Other: Leave Management, Employee Analytics, Bank Reconciliation, Client Feedback, Announcements

## Must-Have Features (Pending)
### P0 (Next priority):
1. Approval Workflows — PO/invoice/expense approvals with configurable chains
2. Budget Management — Department/project budgets, actuals vs budget, alerts
3. Multi-Currency with Forex — Auto forex gain/loss, live rate fetch
4. Contract Management — SOW/MSA tracking, auto-renewal alerts, billing triggers
5. Resource Planning — Bench management, skill matrix, staffing forecast
6. Client Portal — External client access to project status, invoices, timesheets
7. Billing Automation — Auto-generate invoices from timesheets and milestones
8. Document Management — Attach contracts, POs, receipts to transactions
9. Email Notifications — Invoice reminders, approval requests, due date alerts
10. Audit & Compliance Dashboard — SOC2/ISO readiness, data access logs

### P1: Inventory Landed Cost, Fixed Asset Depreciation
### P2: E-Way Bill, Mobile Responsiveness
### P3: Refactor routes_agents.py, Split large React components
