# Kairos AI Engine — Knowledge Repository
# ═══════════════════════════════════════════════════════════
# This file is the canonical reference for the Kairos engine.
# Read this with `read_file` at startup or when debugging.
# Last updated: 2026-04-09
# ═══════════════════════════════════════════════════════════

## 1. ARCHITECTURE OVERVIEW

Kairos is an autonomous AI Engine embedded inside the Nexora IT ERP.
It can read, write, and modify the ERP codebase, run database queries,
execute shell commands, and orchestrate subagents.

Stack: FastAPI backend + React frontend + MongoDB (Motor async driver).
Kairos is INDEPENDENT of ERP modules — it loads first and survives ERP failures.

### Key Principle: Kairos → ERP (one-way dependency)
Kairos CAN modify/query ERP collections and files.
ERP CANNOT affect Kairos availability — they're isolated at startup.

## 2. FILE MAP

### Kairos Core (DO NOT break these)
```
/app/backend/routes_agents.py     — Kairos routes, LLM client, agentic loop
/app/backend/kairos_tools.py      — 33 tool handlers + TOOL_REGISTRY dispatcher
/app/backend/kairos_subagents.py  — 4 subagents (testing, integrator, troubleshooter, designer)
/app/backend/prompt_compressor.py — Smart compression for free LLM tiers
/app/backend/kairos_knowledge.md  — THIS FILE (self-reference)
```

### ERP Modules (safe to modify — failures won't crash Kairos)
```
/app/backend/server.py              — FastAPI app + route registration
/app/backend/routes_projects.py     — IT project management
/app/backend/routes_timesheets.py   — Employee timesheets
/app/backend/routes_revenue.py      — Revenue recognition (Ind AS 115)
/app/backend/routes_crm.py          — CRM / Leads / Opportunities
/app/backend/routes_hr.py           — HR master + employee records
/app/backend/routes_purchase.py     — Purchase orders + GRN
/app/backend/routes_selling.py      — Sales orders + delivery notes
/app/backend/routes_stock.py        — Inventory / BOM / Work Orders
/app/backend/routes_manufacturing.py— Manufacturing module
/app/backend/routes_billing.py      — Billing & invoicing
/app/backend/routes_contracts.py    — Contract management
/app/backend/routes_budgets.py      — Budget tracking
/app/backend/routes_approvals.py    — Approval workflows
/app/backend/routes_resources.py    — Resource allocation
/app/backend/routes_forex.py        — Multi-currency / forex
/app/backend/routes_compliance.py   — Regulatory compliance
/app/backend/routes_portal.py       — Client portal
/app/backend/routes_notifications.py— Notifications engine
/app/backend/routes_documents.py    — Document management
/app/backend/routes_financial_statements.py — Balance sheet, P&L, TB
/app/backend/routes_statutory.py    — Statutory returns (GST, TDS)
/app/backend/routes_gst.py          — GST rules engine
/app/backend/routes_bank_recon.py   — Bank reconciliation
/app/backend/routes_expense_management.py — Expense claims
/app/backend/routes_leave_management.py   — Leave management
/app/backend/routes_chart_of_accounts.py  — CoA CRUD
/app/backend/routes_vendors.py      — Vendor master
/app/backend/routes_customers.py    — Customer master
/app/backend/routes_ai_entry.py     — AI-first data entry endpoint
/app/backend/module_events.py       — Cross-module event triggers
/app/backend/audit_trail.py         — Audit logging utility
/app/backend/ai_orchestrator.py     — AI orchestrator for ERP prompts
/app/backend/gst_rules.py           — GST tax rules engine
```

### Frontend
```
/app/frontend/src/App.js                   — Main app + routing + sidebar
/app/frontend/src/pages/AIAgentsPage.js     — Kairos UI + API Keys
/app/frontend/src/components/AiEntryModal.js— AI-first data entry modal
/app/frontend/src/contexts/AuthContext.js   — Auth context (login removed)
```

## 3. TOOL REGISTRY

All 33 tools live in `/app/backend/kairos_tools.py`.
Dispatched via TOOL_REGISTRY dict in `execute_tool()`.

### File I/O
- read_file(path, start_line?, end_line?)
- create_file(path, content) — fails if file exists
- write_file(path, content) — overwrites, but refuses files >50 lines (use patch_file)
- patch_file(path, old_str, new_str) — search & replace
- insert_lines(path, after_line, content)
- delete_lines(path, start_line, end_line)
- delete_file(path)
- move_file(source, destination)

### Compound Tools
- scaffold_module(module_name, prefix, endpoints, imports?)
  → Creates route file + registers in server.py + restarts + auto-polish + verifies
- create_page(page_name, route_path, title?, api_endpoints?, icon?, nav_section?)
  → Creates React page + registers route in App.js + adds sidebar nav

### Database
- run_query(query_type, collection?, query?, projection?, limit?, document?, update?, pipeline?)
  query_types: find, count, insert, insert_many, update, update_one, update_many,
               delete, delete_one, delete_many, aggregate, distinct, drop, full_health_check
- get_schema(collection) → returns field types + count + sample keys

### Infrastructure
- restart_service(service: backend|frontend)
- test_api(method, url, body?) → call internal API
- check_logs(service, lines?) → tail supervisor logs
- install_package(package, manager: pip|yarn)
- run_tests(test_path?) → pytest runner

### Search
- grep_search(pattern, directory?, file_ext?)
- list_files(directory?) → list source files
- run_command(command, timeout?) → execute bash

### Verification
- verify_deployment(checks[]) → backend_health, api, frontend_route, file_exists

### Research
- web_search(query, max_results?) → DuckDuckGo
- take_screenshot(url, full_page?, wait_ms?)
- crawl_url(url) → fetch and extract text

### Config
- manage_env(action: read|set|delete, file: backend|frontend, key?, value?)
- lint_code(path, fix?)
- git_info(action: log|status|diff, file?)

### Subagents
- call_subagent(agent_type, task, context?, run_tests?)
  agent_types: tester, integrator, troubleshooter, designer
- run_test(type: curl|playwright, command|script, name?)
- run_test_suite(tests[])
- get_playbook(service) → verified integration playbooks

### Batch & Media
- batch_operations(operations[]) → parallel file ops
- generate_image(prompt, size?)

## 4. TOOL DEPENDENCY INJECTION

kairos_tools.py uses module-level config injected at startup:
```python
# In routes_agents.py set_config():
configure_tools(database, is_safe_path, _audit_file_write)
```
This gives tools access to: _db, _is_safe_path, _audit_file_write.

## 5. PROMPT COMPRESSION

File: `/app/backend/prompt_compressor.py`

### Pipeline (5 stages)
1. Protected Content Extraction — saves TOOL_CALL format + all 33 tool names + code patterns
2. Section Priority Ranking — identity > tools > modules > rules > examples
3. Redundancy Elimination — deduplicate near-identical lines
4. Markdown/Syntax Stripping — remove headers, fences, decorations
5. Abbreviation Engine — abbreviate common patterns + prune examples

### Tier Limits
- groq: 3500 chars
- cerebras: 6000 chars
- huggingface: 6000 chars
- default: 8000 chars

### Cache
Compressed prompts cached by hash. Call `clear_cache()` to invalidate.
Stats: `GET /api/agents/compression-stats`

## 6. LLM PROVIDER PRIORITY

1. FREE (compressed prompt): Groq → Cerebras → HuggingFace
2. Direct API Keys (full prompt): Anthropic → OpenAI → OpenRouter
3. Emergent Credits (full prompt): Claude → Gemini → GPT-5

Provider config stored in `api_keys` MongoDB collection.
Keys also read from backend .env on startup.

## 7. DATABASE COLLECTIONS (Key ones for Kairos)

### ERP Collections
- chart_of_accounts: {id, ledger_name, category, opening_balance, current_balance}
- entities: {id, entity_type, name, gstin, pan, state, state_code}
- projects: {id, project_id, name, client, type, value_usd, status, milestones[]}
- timesheets: {id, employee_id, project_id, entries[], total_hours, status}
- employees: {id, employee_id, name, department, designation, salary}
- erp_transactions: {id, module, posting_date, journal_entries[], status}
- billing_invoices: {invoice_id, amount, status, billing_type}
- company_settings: {legal_name, gstin, state, address, ...}

### Kairos Collections
- api_keys: {provider, key, masked, created_at}
- kairos_sessions: {session_id, title, messages[], created_at}
- audit_trail: {id, action, module, record_id, changes[], timestamp, user}

## 8. COMMON PATTERNS

### Creating a New Backend Module
Use `scaffold_module` tool — it handles everything:
```
scaffold_module({
  module_name: "e_way_bill",
  prefix: "/e-way-bills",
  endpoints: [
    {method: "GET", path: "", name: "list_bills", body: "..."},
    {method: "POST", path: "", name: "create_bill", body: "..."},
  ]
})
```
This auto-creates the route file, registers it in server.py, restarts backend,
auto-polishes the code (fixes to_list(), _id exclusion, etc.), and verifies startup.

### Creating a New Frontend Page
Use `create_page` tool:
```
create_page({
  page_name: "EWayBillPage",
  route_path: "/e-way-bills",
  title: "E-Way Bills",
  api_endpoints: ["/e-way-bills"],
  nav_section: "Compliance"
})
```

### MongoDB Best Practices
- ALWAYS exclude _id: db.collection.find({}, {"_id": 0})
- After insert_one(doc): doc.pop("_id", None) before returning
- Use datetime.now(timezone.utc) not datetime.utcnow()
- Use uuid.uuid4() for IDs, not ObjectId
- to_list() needs a length arg: .to_list(500)

### Backend Route Pattern
Every module follows:
```python
router = APIRouter(prefix="/module-name", tags=["Module Name"])
db = None
def set_db(database):
    global db
    db = database
```

### Error Recovery Sequence
1. check_logs(service="backend") — read last 50 lines
2. grep_search the error message across codebase
3. read_file the broken file
4. patch_file to fix
5. restart_service if needed
6. verify_deployment to confirm

## 9. DEBUGGING RECIPES

### Backend won't start
```
check_logs → look for ImportError/SyntaxError
→ read_file the offending file → patch_file to fix
→ restart_service("backend") → verify_deployment
```

### Frontend blank page
```
check_logs(service="frontend") → look for compile errors
→ Usually: missing import, undefined component, JSX syntax error
→ read_file → patch_file → frontend hot-reloads automatically
```

### MongoDB _id serialization error
```
grep_search("_id") in the file → ensure projection excludes _id
→ patch_file to add {"_id": 0} to find() calls
```

### Tool not found error
```
Check TOOL_REGISTRY in kairos_tools.py
→ Ensure tool is registered in the dict at bottom of file
→ Ensure function signature matches: async def tool_xxx(args)
```

## 10. SECURITY BOUNDARIES

### is_safe_path blocks:
- /etc, /root, /proc, /sys, /dev, /boot, /var (except /var/log/supervisor)
- .git directories, .env files (read-only via manage_env tool)
- node_modules, __pycache__, .pyc files
- /app/.emergent

### Protected .env keys (cannot be modified):
MONGO_URL, DB_NAME, REACT_APP_BACKEND_URL

### Creator Mode
Password: ¢re@tor@AIengine
Accessed via top-right dropdown → "Switch to Creator"
Required to access the Kairos AI Engine UI on the frontend.

## 11. SUBAGENTS

### Tester (agent_type: "tester")
Generates and runs test suites. Returns pass/fail with details.

### Integrator (agent_type: "integrator")  
Provides integration playbooks for 3rd-party services.

### Troubleshooter (agent_type: "troubleshooter")
10-step systematic debugging. Read-only diagnosis.

### Designer (agent_type: "designer")
UI/UX design guidelines and component blueprints.

## 12. SELF-REPAIR CHECKLIST

If Kairos tools stop working:
1. Is kairos_tools.py importable? `python -c "import kairos_tools"`
2. Is configure() called? Check set_config() in routes_agents.py
3. Is TOOL_REGISTRY populated? Check bottom of kairos_tools.py
4. Are dependencies injected? _db, _is_safe_path, _audit_file_write must not be None

If compression breaks:
1. Run benchmark: `pytest backend/tests/compression_benchmark.py -v`
2. Check _PROTECTED_SNIPPET in prompt_compressor.py
3. Verify TIER_LIMITS haven't changed
4. clear_cache() and retry

If ERP modules crash but Kairos is fine:
1. check_logs("backend") to find which module failed
2. The failing module is isolated — other modules still work
3. Fix the broken module file, restart backend
4. Kairos continues operating throughout

## 13. ADDING NEW TOOLS TO KAIROS

1. Add async handler in kairos_tools.py:
   ```python
   async def tool_new_thing(args):
       param = args.get("param", "")
       # ... implementation ...
       return {"status": "ok", "result": ...}
   ```

2. Register in TOOL_REGISTRY dict (bottom of kairos_tools.py):
   ```python
   "new_thing": tool_new_thing,
   ```

3. Add tool definition in ENGINE_SYSTEM_PROMPT (routes_agents.py):
   ```
   - new_thing(param): Description of what it does
   ```

4. Update this knowledge file!

5. Run benchmark to verify compression still works with the longer prompt.
