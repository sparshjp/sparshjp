"""Kairos AI Engine — Unified orchestrator combining BA + DEV + QA brains.
Understands requirements, plans, writes code, validates, and deploys."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime, timezone
import uuid
import os
import json
import glob
import subprocess
import asyncio
import httpx
import tempfile
import logging

router = APIRouter(prefix="/agents", tags=["AI Engine"])

EMERGENT_KEY = None
GROQ_KEY = ""
OPENROUTER_KEY = ""
db = None

def set_config(key, database):
    global EMERGENT_KEY, db, GROQ_KEY, OPENROUTER_KEY
    EMERGENT_KEY = key
    db = database
    # Read keys here (after dotenv has loaded in server.py)
    GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
    OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ══════════════════════════════════════════════════════════
# MULTI-PROVIDER LLM CLIENT (Claude → Groq → OpenRouter fallback)
# ══════════════════════════════════════════════════════════

PROVIDERS = [
    {"name": "groq", "model": "llama-3.3-70b-versatile"},
    {"name": "openrouter", "model": "openrouter/auto"},
    {"name": "claude", "model": "claude-sonnet-4-5-20250929"},
]


def _call_groq_sync(system: str, messages: list) -> str:
    """Call Groq API with Llama 3.3 70B (sync for executor)."""
    from groq import Groq
    client = Groq(api_key=GROQ_KEY)
    msgs = [{"role": "system", "content": system}]
    msgs.extend(messages)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=msgs,
        max_tokens=8000,
        temperature=0.3,
    )
    return response.choices[0].message.content


def _call_openrouter_sync(system: str, messages: list) -> str:
    """Call OpenRouter API with free model auto-selection (sync for executor)."""
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY,
        default_headers={"HTTP-Referer": "https://kairos-erp.app", "X-Title": "Kairos AI Engine"},
    )
    msgs = [{"role": "system", "content": system}]
    msgs.extend(messages)
    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=msgs,
        max_tokens=8000,
        temperature=0.3,
    )
    return response.choices[0].message.content


async def _call_claude(system: str, messages: list) -> str:
    """Call Claude via Emergent LLM Key."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=f"engine-{uuid.uuid4()}",
        system_message=system,
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")
    # Combine all messages into a single prompt
    combined = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in messages])
    return await chat.send_message(UserMessage(text=combined))


async def call_llm(system: str, messages: list, preferred: str = "auto") -> tuple:
    """
    Call LLM with automatic fallback: Groq → OpenRouter → Claude.
    Returns (response_text, provider_used).
    """
    if preferred == "claude":
        order = ["claude", "groq", "openrouter"]
    elif preferred == "groq":
        order = ["groq", "openrouter", "claude"]
    elif preferred == "openrouter":
        order = ["openrouter", "groq", "claude"]
    else:
        order = ["groq", "openrouter", "claude"]

    errors = []
    loop = asyncio.get_event_loop()

    for provider in order:
        try:
            if provider == "groq" and GROQ_KEY:
                logging.info("AI Engine: trying Groq (llama-3.3-70b)")
                text = await loop.run_in_executor(None, _call_groq_sync, system, messages)
                return text, "groq"
            elif provider == "openrouter" and OPENROUTER_KEY:
                logging.info("AI Engine: trying OpenRouter (auto)")
                text = await loop.run_in_executor(None, _call_openrouter_sync, system, messages)
                return text, "openrouter"
            elif provider == "claude" and EMERGENT_KEY:
                logging.info("AI Engine: trying Claude Sonnet 4.5")
                text = await _call_claude(system, messages)
                return text, "claude"
        except Exception as e:
            err_msg = str(e)[:200]
            logging.warning(f"AI Engine: {provider} failed: {err_msg}")
            errors.append(f"{provider}: {err_msg}")
            continue

    raise Exception(f"All LLM providers failed: {'; '.join(errors)}")

# ══════════════════════════════════════════════════════════
# PATH SAFETY
# ══════════════════════════════════════════════════════════
ALLOWED_DIRS = ["/app/backend", "/app/frontend/src"]
BLOCKED_PATTERNS = [".env", "node_modules", "__pycache__", ".git", ".emergent"]

def is_safe_path(path):
    for blocked in BLOCKED_PATTERNS:
        if blocked in path:
            return False
    for allowed in ALLOWED_DIRS:
        if path.startswith(allowed):
            return True
    return False

# ══════════════════════════════════════════════════════════
# UNIFIED SYSTEM PROMPT
# ══════════════════════════════════════════════════════════

ENGINE_SYSTEM_PROMPT = """You are the Kairos AI Engine — the unified intelligence for Kairos AI ERP (Nexora Digital Solutions Pvt. Ltd). You analyze requirements, write code, run DB queries, test APIs, and deploy changes.

COMPANY: Nexora Digital Solutions | GSTIN: 24AABCN4567P1Z8 | Gujarat | IT Services
Revenue: INR/USD(84.50)/GBP(106.80) | 8 Projects, 20 Employees, 7 Clients, 10 Vendors
Bank Accounts: HDFC Bank - Current (6840000), Axis Bank - Current (2250000), EEFC USD (3042000)
TB Balance: 28142000 (balanced) | 26 CoA ledgers
Billable employees: 16 (E002-E016) | Non-billable: 4 (E001 CEO, E017 Finance, E018 HR, E019 Sales, E020 Inside Sales) = TOTAL 20

PROJECTS: PRJ-001 FinTrack(FP 45L,88%,asset=1.6L), PRJ-002 CloudMigration(T&M USD95/hr), PRJ-003 Analytics(Milestone 28L,50%,asset=7L), PRJ-004 ManagedSvcs(Retainer 4.5L/mo,liability=4.5L), PRJ-005 PayEdge(FP USD120K,CLOSED), PRJ-006 DevOps(T&M GBP140/hr), PRJ-007 DataWarehouse(Milestone 18L,33%,asset=7.08L)
Total Contract Asset: Rs.15.68L | Total Contract Liability: Rs.4.50L

TECH: FastAPI+Motor(MongoDB) backend:8001 | React+Tailwind+Shadcn frontend:3000
Design: Dark theme #0D1B2A bg, #152236 cards, #1B2D42 borders, #E8EDF2 text, #00d4aa accent

FILES: /app/backend/server.py(main hub), routes_*.py(purchase,selling,crm,hr,stock,manufacturing,projects,timesheets,revenue,agents,financial_statements,statutory,gst,company,audit,aging,sales,bank_recon), seed_nexora.py
/app/frontend/src/App.js, pages/*.js, components/ui/*.jsx

CRITICAL CODE PATTERNS (you MUST follow these):
- Each route file uses: `router = APIRouter(prefix="/module")` and `set_db(database)` function — NEVER create your own motor client
- IDs: `str(uuid.uuid4())` | Timestamps: `datetime.now(timezone.utc).isoformat()`
- ALWAYS exclude `_id` from MongoDB: `{"_id": 0}` in projection
- Frontend API: `import { API } from '../App'` then `fetch(\`\${API}/endpoint\`)`
- Lucide React for icons, Shadcn/UI from ../components/ui/, data-testid on all elements

BUSINESS RULES: GST intra-state=CGST+SGST, inter-state=IGST. Export=zero-rated LUT. TDS: 194J(10%), 194C(2%), 194I(10%). Revenue Ind AS 115: FP=POC, T&M=right to invoice, Milestone=acceptance, Retainer=straight-line.

## YOUR TOOLS
1. **read_file(path, start_line?, end_line?)** — Read file with line numbers. Use start_line/end_line for large files.
2. **create_file(path, content)** — Create NEW files only. Fails if file exists.
3. **patch_file(path, old_str, new_str)** — Safe search-and-replace in existing files. old_str must match exactly.
4. **insert_lines(path, after_line, content)** — Insert text after a specific line number.
5. **delete_lines(path, start_line, end_line)** — Delete a range of lines.
6. **write_file(path, content)** — Full overwrite (ONLY for files <50 lines or new files). Blocked for large files.
7. **get_schema(collection)** — Get actual field names and types from a MongoDB collection.
8. **run_query(query_type)** — full_health_check|tb_balance|entity_validation|project_health|collection_stats
9. **restart_service(service)** — "backend" or "frontend"
10. **test_api(method, url, body)** — Test any /api/* endpoint
11. **list_files(directory)** — List project files
12. **run_command(command)** — Run read-only bash commands (grep, wc, find, cat). No rm/mv/sudo.

## WORKFLOW
When modifying existing code: ALWAYS read_file first → then use patch_file or insert_lines. NEVER use write_file on existing large files.
When creating new code: Use get_schema first to learn actual field names → then create_file.
When adding to existing route files: read_file → insert_lines to add new endpoints at the end.

## OUTPUT FORMAT
```TOOL_CALL
{"tool": "read_file", "args": {"path": "/app/backend/routes_projects.py", "start_line": 1, "end_line": 50}}
```
```TOOL_CALL
{"tool": "get_schema", "args": {"collection": "projects"}}
```
```TOOL_CALL
{"tool": "patch_file", "args": {"path": "/app/backend/routes_projects.py", "old_str": "return projects", "new_str": "return projects\\n\\n@router.get(\\"/profitability\\")..."}}
```
```TOOL_CALL
{"tool": "create_file", "args": {"path": "/app/backend/routes_new.py", "content": "full content"}}
```
```TOOL_CALL
{"tool": "insert_lines", "args": {"path": "/app/backend/routes_projects.py", "after_line": 113, "content": "@router.get(\\"/profitability\\")..."}}
```
```TOOL_CALL
{"tool": "run_command", "args": {"command": "grep -n 'def ' backend/routes_projects.py"}}
```
```QUESTION
Your clarifying question here
```

IMPORTANT RULES:
- When you know the answer from the system prompt, ANSWER DIRECTLY. Don't say "I would need to query" when you have the data.
- ALWAYS read existing files before modifying them. NEVER guess file contents.
- ALWAYS use get_schema before writing DB queries to learn actual field names.
- NEVER overwrite large files. Use patch_file or insert_lines.
- Register new route files in server.py using insert_lines."""

# Individual mode prompts (for when user forces a specific brain)
BA_ONLY_SUFFIX = "\n\nMODE: Business Analysis Only. Focus on requirements, compliance, accounting implications. Do NOT generate code or tool calls for file writing."
DEV_ONLY_SUFFIX = "\n\nMODE: Coding Only. Focus on reading files, generating code, and deploying. Skip business analysis."
QA_ONLY_SUFFIX = "\n\nMODE: Testing/Validation Only. Focus on running queries, testing APIs, and checking data integrity."

# ══════════════════════════════════════════════════════════
# TOOL EXECUTION ENGINE
# ══════════════════════════════════════════════════════════

async def execute_tool(tool_name, args):
    """Execute a tool call and return the result"""
    try:
        if tool_name == "read_file":
            path = args.get("path", "")
            start_line = args.get("start_line", 1)
            end_line = args.get("end_line")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if not os.path.isfile(path):
                return {"status": "error", "error": f"File not found: {path}"}
            with open(path, "r") as f:
                lines = f.readlines()
            total = len(lines)
            s = max(1, start_line) - 1
            e = min(end_line or total, total)
            numbered = [f"{i+s+1}| {line}" for i, line in enumerate(lines[s:e])]
            content = "".join(numbered)
            if len(content) > 30000:
                content = content[:30000] + "\n... [TRUNCATED] ..."
            return {"status": "ok", "path": path, "total_lines": total, "showing": f"{s+1}-{e}", "content": content}

        elif tool_name == "create_file":
            # Only for NEW files — refuses if file already exists
            path = args.get("path", "")
            content = args.get("content", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if os.path.isfile(path):
                return {"status": "error", "error": f"File already exists: {path}. Use patch_file to modify existing files, or delete_lines + insert_lines."}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            await _audit_file_write(path, content, "CREATE")
            return {"status": "ok", "path": path, "size": len(content), "message": f"New file created: {path}"}

        elif tool_name == "patch_file":
            # Safe search-and-replace in existing files
            path = args.get("path", "")
            old_str = args.get("old_str", "")
            new_str = args.get("new_str", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if not os.path.isfile(path):
                return {"status": "error", "error": f"File not found: {path}"}
            with open(path, "r") as f:
                content = f.read()
            if old_str not in content:
                # Try fuzzy match — strip whitespace differences
                stripped_old = old_str.strip()
                found = False
                for line in content.split("\n"):
                    if stripped_old in line.strip():
                        found = True
                        break
                if not found:
                    return {"status": "error", "error": "old_str not found in file. Read the file first to get the exact text to replace.", "hint": "Use read_file to see the current content, then copy the exact string to replace."}
            new_content = content.replace(old_str, new_str, 1)
            with open(path, "w") as f:
                f.write(new_content)
            await _audit_file_write(path, f"PATCH: replaced {len(old_str)} chars with {len(new_str)} chars", "PATCH")
            return {"status": "ok", "path": path, "chars_removed": len(old_str), "chars_added": len(new_str)}

        elif tool_name == "insert_lines":
            # Insert text after a specific line number
            path = args.get("path", "")
            after_line = args.get("after_line", 0)
            content = args.get("content", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if not os.path.isfile(path):
                return {"status": "error", "error": f"File not found: {path}"}
            with open(path, "r") as f:
                lines = f.readlines()
            insert_pos = min(max(0, after_line), len(lines))
            new_lines = content.split("\n")
            for i, nl in enumerate(new_lines):
                lines.insert(insert_pos + i, nl + "\n")
            with open(path, "w") as f:
                f.writelines(lines)
            await _audit_file_write(path, f"INSERT: {len(new_lines)} lines after line {after_line}", "INSERT")
            return {"status": "ok", "path": path, "lines_inserted": len(new_lines), "at_line": after_line + 1, "new_total": len(lines)}

        elif tool_name == "delete_lines":
            # Delete a range of lines from a file
            path = args.get("path", "")
            start_line = args.get("start_line", 1)
            end_line = args.get("end_line", 1)
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if not os.path.isfile(path):
                return {"status": "error", "error": f"File not found: {path}"}
            with open(path, "r") as f:
                lines = f.readlines()
            s = max(1, start_line) - 1
            e = min(end_line, len(lines))
            deleted = lines[s:e]
            new_lines = lines[:s] + lines[e:]
            with open(path, "w") as f:
                f.writelines(new_lines)
            await _audit_file_write(path, f"DELETE: lines {start_line}-{end_line} ({len(deleted)} lines)", "DELETE")
            return {"status": "ok", "path": path, "lines_deleted": len(deleted), "new_total": len(new_lines)}

        elif tool_name == "write_file":
            # Legacy — only for NEW files or explicit full rewrites
            path = args.get("path", "")
            content = args.get("content", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            # GUARDRAIL: If file exists and is large, warn
            if os.path.isfile(path):
                with open(path, "r") as f:
                    existing = f.readlines()
                if len(existing) > 50:
                    return {"status": "error", "error": f"File has {len(existing)} lines. Use patch_file, insert_lines, or delete_lines instead. Full overwrite blocked for files >50 lines. Read the file first, then make targeted changes."}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            await _audit_file_write(path, content, "WRITE")
            return {"status": "ok", "path": path, "size": len(content), "message": f"File written: {path}"}

        elif tool_name == "run_query":
            query_type = args.get("query_type", "full_health_check")
            result = await _run_test_query(query_type)
            return {"status": "ok", "query_type": query_type, "results": result}

        elif tool_name == "restart_service":
            service = args.get("service", "backend")
            if service not in ["backend", "frontend"]:
                return {"status": "error", "error": "Can only restart 'backend' or 'frontend'"}
            proc = subprocess.run(
                ["sudo", "supervisorctl", "restart", service],
                capture_output=True, text=True, timeout=15
            )
            await asyncio.sleep(3)
            return {"status": "ok", "service": service, "output": proc.stdout.strip(), "stderr": proc.stderr.strip() if proc.returncode != 0 else ""}

        elif tool_name == "test_api":
            method = args.get("method", "GET").upper()
            url_path = args.get("url", "")
            body = args.get("body")
            base_url = "http://localhost:8001"
            full_url = f"{base_url}{url_path}"
            async with httpx.AsyncClient(timeout=15) as client:
                if method == "GET":
                    resp = await client.get(full_url)
                elif method == "POST":
                    resp = await client.post(full_url, json=body)
                elif method == "PUT":
                    resp = await client.put(full_url, json=body)
                elif method == "DELETE":
                    resp = await client.delete(full_url)
                else:
                    return {"status": "error", "error": f"Unsupported method: {method}"}
            resp_body = resp.text[:3000]
            try:
                resp_body = resp.json()
                if isinstance(resp_body, list) and len(resp_body) > 5:
                    resp_body = {"count": len(resp_body), "sample": resp_body[:3], "note": f"...{len(resp_body)} total items"}
            except Exception:
                pass
            return {"status": "ok", "http_status": resp.status_code, "url": url_path, "response": resp_body}

        elif tool_name == "list_files":
            directory = args.get("directory", "/app/backend")
            if not is_safe_path(directory):
                return {"status": "error", "error": "Access denied"}
            files = []
            for f in sorted(glob.glob(f"{directory}/**", recursive=True)):
                if os.path.isfile(f) and is_safe_path(f):
                    ext = os.path.splitext(f)[1]
                    if ext in [".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".md"]:
                        files.append({"path": f, "relative": f.replace("/app/", ""), "size": os.path.getsize(f)})
            return {"status": "ok", "files": files[:100], "count": len(files)}

        elif tool_name == "get_schema":
            # Get actual field names from a MongoDB collection by sampling
            collection = args.get("collection", "")
            if not collection:
                return {"status": "error", "error": "collection name required"}
            try:
                sample = await db[collection].find_one({}, {"_id": 0})
                if not sample:
                    return {"status": "ok", "collection": collection, "fields": [], "note": "Collection empty"}
                fields = {}
                for k, v in sample.items():
                    fields[k] = type(v).__name__
                count = await db[collection].count_documents({})
                return {"status": "ok", "collection": collection, "count": count, "fields": fields, "sample_keys": list(sample.keys())}
            except Exception as ex:
                return {"status": "error", "error": str(ex)}

        elif tool_name == "run_command":
            # Run a safe read-only bash command (grep, wc, find, head, etc.)
            cmd = args.get("command", "")
            BLOCKED_CMDS = ["rm ", "mv ", "cp ", "chmod", "chown", "kill", "sudo", "apt", "pip ", "npm ", "yarn", "> ", ">>"]
            for bc in BLOCKED_CMDS:
                if bc in cmd:
                    return {"status": "error", "error": f"Command blocked for safety: contains '{bc.strip()}'"}
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, cwd="/app")
                output = proc.stdout[:5000]
                if proc.stderr:
                    output += f"\n[STDERR]: {proc.stderr[:1000]}"
                return {"status": "ok", "command": cmd, "output": output, "exit_code": proc.returncode}
            except subprocess.TimeoutExpired:
                return {"status": "error", "error": "Command timed out (10s limit)"}

        else:
            return {"status": "error", "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def _audit_file_write(path, detail, action_type):
    """Log file modifications to audit trail."""
    await db.audit_trail.insert_one({
        "id": str(uuid.uuid4()),
        "action": f"FILE_{action_type}",
        "module": "AI_ENGINE",
        "record_id": path,
        "record_name": os.path.basename(path),
        "changes": [{"field": "content", "new_value": str(detail)[:500]}],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": "kairos-engine",
    })


async def _run_test_query(query_type):
    """Run a predefined test query"""
    if query_type == "tb_balance":
        coa = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        dr = sum(max(0, e["opening_balance"]) for e in coa)
        cr = sum(max(0, -e["opening_balance"]) for e in coa)
        return {"total_debit": dr, "total_credit": cr, "balanced": dr == cr, "accounts": len(coa)}
    elif query_type == "entity_validation":
        v = await db.entities.find({"entity_type": "vendor"}, {"_id": 0}).to_list(100)
        c = await db.entities.find({"entity_type": "customer"}, {"_id": 0}).to_list(100)
        return {"vendors": len(v), "customers": len(c), "vendor_missing_gstin": [x["name"] for x in v if not x.get("gstin")]}
    elif query_type == "project_health":
        p = await db.projects.find({"id": {"$ne": "PRJ-INT"}}, {"_id": 0}).to_list(20)
        return {"projects": len(p), "by_health": {}}
    elif query_type == "collection_stats":
        cols = await db.list_collection_names()
        stats = {}
        for col in sorted(cols):
            stats[col] = await db[col].count_documents({})
        return stats
    elif query_type == "full_health_check":
        coa = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        dr = sum(max(0, e["opening_balance"]) for e in coa)
        cr = sum(max(0, -e["opening_balance"]) for e in coa)
        return {
            "tb_balanced": dr == cr, "tb_total": dr,
            "accounts": len(coa),
            "vendors": await db.entities.count_documents({"entity_type": "vendor"}),
            "customers": await db.entities.count_documents({"entity_type": "customer"}),
            "projects": await db.projects.count_documents({}),
            "employees": await db.employees.count_documents({}),
            "timesheets": await db.timesheets.count_documents({}),
            "transactions": await db.erp_transactions.count_documents({}),
        }
    else:
        return {"error": f"Unknown query: {query_type}"}


def parse_tool_calls(text):
    """Extract TOOL_CALL blocks from LLM response"""
    calls = []
    parts = text.split("```TOOL_CALL")
    for part in parts[1:]:
        end = part.find("```")
        if end != -1:
            raw = part[:end].strip()
            try:
                call = json.loads(raw)
                calls.append(call)
            except json.JSONDecodeError:
                pass
    return calls


def parse_questions(text):
    """Extract QUESTION blocks from LLM response"""
    questions = []
    parts = text.split("```QUESTION")
    for part in parts[1:]:
        end = part.find("```")
        if end != -1:
            questions.append(part[:end].strip())
    return questions

# ══════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════
# FILE UPLOAD & URL CRAWLING
# ══════════════════════════════════════════════════════════

UPLOAD_DIR = "/app/backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _extract_pdf(path):
    import pdfplumber
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages[:50]):
            t = page.extract_text()
            if t:
                text_parts.append(f"--- Page {i+1} ---\n{t}")
            tables = page.extract_tables()
            for ti, table in enumerate(tables):
                text_parts.append(f"[Table {ti+1}]\n" + "\n".join([" | ".join(str(c or "") for c in row) for row in table]))
    return "\n\n".join(text_parts)

def _extract_docx(path):
    from docx import Document
    doc = Document(path)
    parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    for table in doc.tables:
        rows = []
        for row in table.rows:
            rows.append(" | ".join(cell.text for cell in row.cells))
        parts.append("[Table]\n" + "\n".join(rows))
    return "\n".join(parts)

def _extract_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    parts = []
    for sheet_name in wb.sheetnames[:10]:
        ws = wb[sheet_name]
        rows = []
        for row in ws.iter_rows(max_row=200, values_only=True):
            rows.append(" | ".join(str(c or "") for c in row))
        parts.append(f"--- Sheet: {sheet_name} ---\n" + "\n".join(rows))
    return "\n\n".join(parts)

def _extract_pptx(path):
    from pptx import Presentation
    prs = Presentation(path)
    parts = []
    for i, slide in enumerate(prs.slides[:50]):
        slide_text = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        slide_text.append(para.text)
            if shape.has_table:
                for row in shape.table.rows:
                    slide_text.append(" | ".join(cell.text for cell in row.cells))
        if slide_text:
            parts.append(f"--- Slide {i+1} ---\n" + "\n".join(slide_text))
    return "\n\n".join(parts)

def _extract_csv(path):
    import csv
    rows = []
    with open(path, "r", errors="replace") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 500:
                rows.append("... [TRUNCATED at 500 rows]")
                break
            rows.append(" | ".join(row))
    return "\n".join(rows)

EXTRACTORS = {
    ".pdf": _extract_pdf,
    ".docx": _extract_docx,
    ".doc": _extract_docx,
    ".xlsx": _extract_xlsx,
    ".xls": _extract_xlsx,
    ".pptx": _extract_pptx,
    ".ppt": _extract_pptx,
    ".csv": _extract_csv,
}

TEXT_EXTS = {".txt", ".md", ".json", ".xml", ".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".yaml", ".yml", ".ini", ".cfg", ".log", ".sql"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".heic", ".heif"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and extract text from a file. Returns extracted content."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    file_id = str(uuid.uuid4())[:8]
    safe_name = f"{file_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    content_bytes = await file.read()
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    size_kb = len(content_bytes) / 1024
    result = {
        "id": file_id,
        "filename": file.filename,
        "ext": ext,
        "size_kb": round(size_kb, 1),
        "type": "unknown",
        "content": "",
    }

    try:
        if ext in EXTRACTORS:
            result["content"] = EXTRACTORS[ext](save_path)
            result["type"] = "document"
        elif ext in TEXT_EXTS:
            with open(save_path, "r", errors="replace") as f:
                result["content"] = f.read()[:50000]
            result["type"] = "text"
        elif ext in IMAGE_EXTS:
            result["type"] = "image"
            result["content"] = f"[Image: {file.filename} ({size_kb:.0f}KB). Describe what you need analyzed from this image.]"
            result["image_path"] = save_path
        else:
            result["type"] = "binary"
            result["content"] = f"[Unsupported file type: {ext}. File saved as {safe_name}]"
    except Exception as e:
        result["content"] = f"[Extraction error: {str(e)}]"
        result["type"] = "error"

    # Truncate to avoid overloading the LLM
    if len(result["content"]) > 40000:
        result["content"] = result["content"][:40000] + "\n... [TRUNCATED — content exceeds 40KB]"

    return result


@router.post("/crawl-url")
async def crawl_url(body: dict):
    """Crawl a URL and extract its text content."""
    url = body.get("url", "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; KairosBot/1.0)"
            })
            resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        raw = resp.text

        # If it's HTML, extract text
        if "html" in content_type:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw, "html.parser")
            # Remove scripts, styles, nav
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()
            title = soup.title.string if soup.title else url
            text = soup.get_text(separator="\n", strip=True)
            # Clean up excessive whitespace
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            text = "\n".join(lines)
            if len(text) > 30000:
                text = text[:30000] + "\n... [TRUNCATED]"
            return {
                "status": "ok",
                "url": url,
                "title": title,
                "type": "html",
                "content": text,
                "size_kb": round(len(text) / 1024, 1),
            }
        # If it's JSON
        elif "json" in content_type:
            return {
                "status": "ok",
                "url": url,
                "title": url,
                "type": "json",
                "content": raw[:30000],
                "size_kb": round(len(raw) / 1024, 1),
            }
        # Plain text / XML
        else:
            return {
                "status": "ok",
                "url": url,
                "title": url,
                "type": "text",
                "content": raw[:30000],
                "size_kb": round(len(raw) / 1024, 1),
            }
    except httpx.HTTPStatusError as e:
        return {"status": "error", "url": url, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"status": "error", "url": url, "error": str(e)}


# ══════════════════════════════════════════════════════════
# SESSION MANAGEMENT (kept from previous)
# ══════════════════════════════════════════════════════════

@router.get("/sessions")
async def list_sessions():
    sessions = await db.agent_sessions.find({}, {"_id": 0}).sort("updated_at", -1).to_list(50)
    return sessions

@router.post("/sessions")
async def create_session(body: dict):
    session = {
        "id": str(uuid.uuid4()),
        "agent_type": body.get("agent_type", "auto"),
        "title": body.get("title", "New Session"),
        "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_sessions.insert_one(session)
    return {k: v for k, v in session.items() if k != "_id"}

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    await db.agent_sessions.delete_one({"id": session_id})
    return {"status": "deleted"}

# ══════════════════════════════════════════════════════════
# FILE + QUERY ENDPOINTS (kept for direct access)
# ══════════════════════════════════════════════════════════

@router.get("/coding/files")
async def api_list_files(directory: str = "/app/backend"):
    return await execute_tool("list_files", {"directory": directory})

@router.post("/coding/read-file")
async def api_read_file(body: dict):
    return await execute_tool("read_file", body)

@router.post("/coding/write-file")
async def api_write_file(body: dict):
    return await execute_tool("write_file", body)

@router.post("/testing/query")
async def api_run_test_query(body: dict):
    return await execute_tool("run_query", body)

# ══════════════════════════════════════════════════════════
# UNIFIED CHAT — THE ORCHESTRATOR
# ══════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════
# BACKGROUND TASK ENGINE (bypasses gateway timeout)
# ══════════════════════════════════════════════════════════

# In-memory task store (tasks are ephemeral — results move to MongoDB sessions)
_tasks = {}  # task_id -> {status, progress, result, ...}


async def _run_engine_task(task_id, mode, message, session_id, context):
    """Background coroutine that runs the full LLM + tool pipeline with multi-provider fallback."""
    try:
        _tasks[task_id]["status"] = "thinking"
        _tasks[task_id]["progress"] = "Analyzing your request..."

        system = ENGINE_SYSTEM_PROMPT
        if mode == "ba":
            system += BA_ONLY_SUFFIX
        elif mode == "dev":
            system += DEV_ONLY_SUFFIX
            # Inject live DB schemas for dev mode so Kairos uses real field names
            try:
                _tasks[task_id]["progress"] = "Loading DB schemas..."
                schema_info = []
                key_collections = ["projects", "timesheets", "employees", "entities", "chart_of_accounts", "erp_transactions", "revenue_schedule"]
                for coll in key_collections:
                    sample = await db[coll].find_one({}, {"_id": 0})
                    if sample:
                        schema_info.append(f"{coll}: {list(sample.keys())}")
                if schema_info:
                    system += "\n\n[LIVE DB SCHEMAS]\n" + "\n".join(schema_info)
            except Exception:
                pass
        elif mode == "qa":
            system += QA_ONLY_SUFFIX

        # Get conversation history
        history = []
        if session_id:
            session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
            if session:
                history = session.get("messages", [])

        full_message = message
        if context:
            full_message += f"\n\n[ATTACHED CONTEXT]\n{context[:12000]}"

        # Inject history as inline context
        history_context = ""
        if history:
            recent = history[-6:]
            hlines = [f"[{'User' if h['role']=='user' else 'Assistant'}]: {h['content'][:300]}" for h in recent]
            history_context = "[CONVERSATION HISTORY]\n" + "\n".join(hlines) + "\n\n"

        # Phase 1: LLM call with multi-provider fallback
        _tasks[task_id]["progress"] = "Generating response..."
        llm_messages = [{"role": "user", "content": history_context + full_message}]
        response_text, provider = await call_llm(system, llm_messages)
        _tasks[task_id]["progress"] = f"Response from {provider}. Processing..."

        # Phase 2: Parse and execute tool calls
        tool_calls = parse_tool_calls(response_text)
        questions = parse_questions(response_text)
        tool_results = []
        files_modified = []

        if tool_calls:
            _tasks[task_id]["status"] = "executing"
            for i, tc in enumerate(tool_calls[:8]):
                tool_name = tc.get("tool", "")
                tool_args = tc.get("args", {})
                _tasks[task_id]["progress"] = f"Executing tool {i+1}/{len(tool_calls[:8])}: {tool_name}..."
                result = await execute_tool(tool_name, tool_args)
                tool_results.append({"tool": tool_name, "args": tool_args, "result": result})
                if tool_name in ("write_file", "create_file", "patch_file", "insert_lines", "delete_lines") and result.get("status") == "ok":
                    files_modified.append(result.get("path", tool_args.get("path", "")))

            # Phase 3: Follow-up LLM call with tool results
            _tasks[task_id]["progress"] = f"Analyzing results via {provider}..."
            tool_summary = json.dumps(tool_results, indent=2, default=str)
            if len(tool_summary) > 12000:
                tool_summary = tool_summary[:12000] + "\n... [TRUNCATED]"
            followup_msgs = [{"role": "user", "content": f"[TOOL EXECUTION RESULTS]\n{tool_summary}\n\nBriefly confirm what was done and suggest next steps."}]
            followup, _ = await call_llm(system, followup_msgs, preferred=provider)
            response_text += f"\n\n---\n\n{followup}"

        # Save to session
        timestamp = datetime.now(timezone.utc).isoformat()
        if session_id:
            new_messages = [
                {"role": "user", "content": message, "timestamp": timestamp},
                {"role": "assistant", "content": response_text, "agent_type": mode, "timestamp": timestamp,
                 "tool_calls": len(tool_calls), "files_modified": files_modified, "questions": questions,
                 "provider": provider},
            ]
            update = {
                "$push": {"messages": {"$each": new_messages}},
                "$set": {"updated_at": timestamp}
            }
            sess = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
            if sess and len(sess.get("messages", [])) == 0:
                update["$set"]["title"] = message[:80]
            await db.agent_sessions.update_one({"id": session_id}, update)

        _tasks[task_id] = {
            "status": "complete",
            "progress": "Done",
            "result": {
                "response": response_text,
                "agent_type": mode,
                "session_id": session_id,
                "timestamp": timestamp,
                "tool_calls_executed": len(tool_calls),
                "files_modified": files_modified,
                "questions": questions,
                "tool_results": tool_results[:10],
                "provider": provider,
            }
        }
    except Exception as e:
        _tasks[task_id] = {
            "status": "error",
            "progress": str(e),
            "result": {
                "response": f"Engine error: {str(e)}",
                "agent_type": mode,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool_calls_executed": 0,
                "files_modified": [],
                "questions": [],
                "tool_results": [],
            }
        }


@router.post("/chat")
async def engine_chat(body: dict):
    """Start an AI Engine task. Returns task_id for polling."""
    mode = body.get("agent_type", "auto")
    message = body.get("message", "")
    session_id = body.get("session_id", "")
    context = body.get("context", "")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    task_id = str(uuid.uuid4())[:12]
    _tasks[task_id] = {"status": "queued", "progress": "Starting...", "result": None}

    # Fire-and-forget background task
    asyncio.create_task(_run_engine_task(task_id, mode, message, session_id, context))

    return {"task_id": task_id, "status": "queued"}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Poll for task completion. Returns status + result when done."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] in ["complete", "error"]:
        result = task.get("result", {})
        # Clean up after delivery
        _tasks.pop(task_id, None)
        return {"status": task["status"], "progress": task["progress"], **result}

    return {"status": task["status"], "progress": task["progress"]}


@router.get("/providers")
async def get_providers():
    """List available LLM providers and their status."""
    return {
        "providers": [
            {"name": "groq", "model": "llama-3.3-70b-versatile", "status": "active" if GROQ_KEY else "no_key", "priority": 1},
            {"name": "openrouter", "model": "auto (free models)", "status": "active" if OPENROUTER_KEY else "no_key", "priority": 2},
            {"name": "claude", "model": "claude-sonnet-4-5", "status": "active" if EMERGENT_KEY else "no_key", "priority": 3},
        ],
        "fallback_order": ["groq", "openrouter", "claude"],
    }
