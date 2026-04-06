"""Kairos AI Engine v3 — Speed & Code Generation Upgrade.
Parallel tool execution, compound tools (scaffold_module, create_page),
auto-restart, compressed results, fast-path for simple questions."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime, timezone
import uuid
import os
import json
import glob
import subprocess
import asyncio
import httpx
import re
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
    GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
    OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ══════════════════════════════════════════════════════════
# MULTI-PROVIDER LLM CLIENT (Groq → OpenRouter → Claude)
# ══════════════════════════════════════════════════════════

def _call_groq_sync(system: str, messages: list) -> str:
    from groq import Groq
    client = Groq(api_key=GROQ_KEY)
    msgs = [{"role": "system", "content": system}]
    msgs.extend(messages)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=msgs, max_tokens=8000, temperature=0.3,
    )
    return response.choices[0].message.content

def _call_openrouter_sync(system: str, messages: list) -> str:
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY,
        default_headers={"HTTP-Referer": "https://kairos-erp.app", "X-Title": "Kairos AI Engine"},
    )
    msgs = [{"role": "system", "content": system}]
    msgs.extend(messages)
    response = client.chat.completions.create(
        model="openrouter/auto", messages=msgs, max_tokens=8000, temperature=0.3,
    )
    return response.choices[0].message.content

async def _call_claude(system: str, messages: list) -> str:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    chat = LlmChat(
        api_key=EMERGENT_KEY, session_id=f"engine-{uuid.uuid4()}", system_message=system,
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")
    combined = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in messages])
    return await chat.send_message(UserMessage(text=combined))

async def call_llm(system: str, messages: list, preferred: str = "auto") -> tuple:
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
                text = await loop.run_in_executor(None, _call_groq_sync, system, messages)
                return text, "groq"
            elif provider == "openrouter" and OPENROUTER_KEY:
                text = await loop.run_in_executor(None, _call_openrouter_sync, system, messages)
                return text, "openrouter"
            elif provider == "claude" and EMERGENT_KEY:
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
# SYSTEM PROMPT (v3 — speed optimized)
# ══════════════════════════════════════════════════════════
MAX_ITERATIONS = 10

ENGINE_SYSTEM_PROMPT = """You are the Kairos AI Engine v3 — a FAST, AUTONOMOUS developer for Nexora Digital Solutions IT ERP.
You work in an agentic loop. BE EFFICIENT: issue ALL tool calls in ONE response, prefer compound tools, minimize iterations.

COMPANY: Nexora Digital Solutions | GSTIN: 24AABCN4567P1Z8 | Gujarat | IT Services
Revenue: INR/USD(84.50)/GBP(106.80) | 8 Projects, 20 Employees, 7 Clients, 10 Vendors
Bank Accounts: HDFC Bank - Current (6840000), Axis Bank - Current (2250000), EEFC USD (3042000)
TB Balance: 28142000 (balanced) | 26 CoA ledgers

PROJECTS: PRJ-001 FinTrack(FP 45L,88%,asset=1.6L), PRJ-002 CloudMigration(T&M USD95/hr), PRJ-003 Analytics(Milestone 28L,50%,asset=7L), PRJ-004 ManagedSvcs(Retainer 4.5L/mo,liability=4.5L), PRJ-005 PayEdge(FP USD120K,CLOSED), PRJ-006 DevOps(T&M GBP140/hr), PRJ-007 DataWarehouse(Milestone 18L,33%,asset=7.08L)

TECH: FastAPI+Motor(MongoDB) backend:8001 | React+Tailwind+Shadcn frontend:3000
Design: Dark theme #0D1B2A bg, #152236 cards, #1B2D42 borders, #E8EDF2 text, #00d4aa accent

## SPEED RULES (CRITICAL)
- Issue ALL tool calls you need in a SINGLE response. Tools run in PARALLEL.
- Use `scaffold_module` for new backend modules (1 tool = creates file + registers + restarts + tests).
- Use `create_page` for new frontend pages (1 tool = creates file + registers route).
- Backend auto-restarts after file changes. Do NOT manually call restart_service.
- Answer from knowledge when possible. Only use tools when you need live data.
- Target 1-2 steps per task. Only complex work needs 3+.

## TOOLS

### File Operations
1. **read_file(path, start_line?, end_line?)** — Read file content with line numbers.
2. **create_file(path, content)** — Create NEW files only. Fails if exists.
3. **patch_file(path, old_str, new_str)** — Search-and-replace. old_str must match exactly.
4. **insert_lines(path, after_line, content)** — Insert text after a line number.
5. **delete_lines(path, start_line, end_line)** — Delete line range.
6. **write_file(path, content)** — Full overwrite (ONLY files <50 lines).

### Compound Tools (FAST — prefer these for new modules)
7. **scaffold_module(module_name, prefix, endpoints, imports?)** — Creates complete backend route file + registers in server.py + restarts backend + verifies startup. One call replaces 5+ manual steps.
   Format: endpoints is a list of {method, path, name, body}
   Body is the Python code inside the async function (indented 4 spaces, using `db` global).
   Example:
   ```TOOL_CALL
   {"tool": "scaffold_module", "args": {"module_name": "leave_management", "prefix": "/leave", "endpoints": [{"method": "GET", "path": "", "name": "list_leaves", "body": "items = await db.leaves.find({}, {\\"_id\\": 0}).to_list(500)\\n    return items"}, {"method": "POST", "path": "", "name": "create_leave", "body": "body[\\"id\\"] = str(uuid.uuid4())\\n    body[\\"created_at\\"] = datetime.now(timezone.utc).isoformat()\\n    await db.leaves.insert_one(body)\\n    return {k:v for k,v in body.items() if k != \\"_id\\"}"}]}}
   ```
8. **create_page(page_name, route_path, title, api_endpoints?, content?)** — Creates React page + registers in App.js.

### Database & Infrastructure
9. **get_schema(collection)** — Get field names/types from MongoDB collection.
10. **run_query(query_type)** — full_health_check|tb_balance|entity_validation|project_health|collection_stats
11. **restart_service(service)** — "backend" or "frontend" (auto-done by scaffold_module).
12. **test_api(method, url, body?)** — Test /api/* endpoint. Returns status + response body.
13. **check_logs(service, lines?)** — Read service logs. Default 50 lines.
14. **install_package(package, manager?)** — pip/yarn install.
15. **run_tests(test_path?)** — Run pytest.

### Search
16. **grep_search(pattern, directory?, file_ext?)** — Extended regex, case-insensitive code search.
17. **list_files(directory)** — List project files.
18. **run_command(command)** — Read-only bash (grep, wc, find, cat, head, tail).

## CODE PATTERNS
- Route file: `router = APIRouter(prefix="/x")` + `set_db(database)` — NEVER create own motor client
- IDs: `str(uuid.uuid4())` | Timestamps: `datetime.now(timezone.utc).isoformat()`
- ALWAYS exclude `_id`: `{"_id": 0}` in projection
- Frontend: `import { API } from '../App'` then `fetch(\`\${API}/endpoint\`)`
- Lucide React icons, Shadcn/UI components, data-testid on all elements

BUSINESS: GST intra=CGST+SGST, inter=IGST. Export=zero-rated LUT. TDS: 194J(10%), 194C(2%), 194I(10%). Revenue Ind AS 115: FP=POC, T&M=right-to-invoice, Milestone=acceptance, Retainer=straight-line.

## OUTPUT FORMAT
Issue MULTIPLE tool calls in one response:
```TOOL_CALL
{"tool": "tool_name", "args": {...}}
```
```TOOL_CALL
{"tool": "another_tool", "args": {...}}
```
```DONE
Summary of what was accomplished
```
```QUESTION
Clarifying question
```

RULES:
- ALL tool calls in ONE response run in PARALLEL. Be aggressive with batching.
- Prefer scaffold_module + test_api over manual create_file + insert_lines + restart_service + check_logs.
- Maximum """ + str(MAX_ITERATIONS) + """ iterations. Target 1-2 for most tasks."""

BA_ONLY_SUFFIX = "\n\nMODE: Business Analysis Only. Focus on requirements, compliance, accounting. No code generation."
DEV_ONLY_SUFFIX = "\n\nMODE: Coding Only. Read files, generate code, deploy. Skip business analysis."
QA_ONLY_SUFFIX = "\n\nMODE: Testing/Validation Only. Run queries, test APIs, check data integrity."

# ══════════════════════════════════════════════════════════
# TOOL EXECUTION ENGINE
# ══════════════════════════════════════════════════════════

WRITE_TOOLS = {"write_file", "create_file", "patch_file", "insert_lines", "delete_lines", "scaffold_module", "create_page"}
READ_TOOLS = {"read_file", "grep_search", "list_files", "run_command", "get_schema", "check_logs", "run_query"}

async def execute_tool(tool_name, args):
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
            path = args.get("path", "")
            content = args.get("content", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if os.path.isfile(path):
                return {"status": "error", "error": f"File already exists: {path}. Use patch_file."}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            await _audit_file_write(path, content, "CREATE")
            return {"status": "ok", "path": path, "size": len(content)}

        elif tool_name == "patch_file":
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
                stripped_old = old_str.strip()
                found = any(stripped_old in line.strip() for line in content.split("\n"))
                if not found:
                    return {"status": "error", "error": "old_str not found. Use read_file first.", "hint": "Read the file to get exact text."}
            new_content = content.replace(old_str, new_str, 1)
            with open(path, "w") as f:
                f.write(new_content)
            await _audit_file_write(path, f"PATCH: {len(old_str)}→{len(new_str)} chars", "PATCH")
            return {"status": "ok", "path": path, "chars_removed": len(old_str), "chars_added": len(new_str)}

        elif tool_name == "insert_lines":
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
            await _audit_file_write(path, f"INSERT: {len(new_lines)} lines after L{after_line}", "INSERT")
            return {"status": "ok", "path": path, "lines_inserted": len(new_lines), "at_line": after_line + 1}

        elif tool_name == "delete_lines":
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
            new_lines = lines[:s] + lines[e:]
            with open(path, "w") as f:
                f.writelines(new_lines)
            await _audit_file_write(path, f"DELETE: lines {start_line}-{end_line}", "DELETE")
            return {"status": "ok", "path": path, "lines_deleted": e - s}

        elif tool_name == "write_file":
            path = args.get("path", "")
            content = args.get("content", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if os.path.isfile(path):
                with open(path, "r") as f:
                    existing = f.readlines()
                if len(existing) > 50:
                    return {"status": "error", "error": f"File has {len(existing)} lines. Use patch_file."}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            await _audit_file_write(path, content, "WRITE")
            return {"status": "ok", "path": path, "size": len(content)}

        # ── COMPOUND TOOLS ──

        elif tool_name == "scaffold_module":
            return await _scaffold_module(args)

        elif tool_name == "create_page":
            return await _create_page(args)

        # ── DATABASE ──

        elif tool_name == "run_query":
            query_type = args.get("query_type", "full_health_check")
            result = await _run_test_query(query_type)
            return {"status": "ok", "query_type": query_type, "results": result}

        elif tool_name == "get_schema":
            collection = args.get("collection", "")
            if not collection:
                return {"status": "error", "error": "collection name required"}
            try:
                sample = await db[collection].find_one({}, {"_id": 0})
                if not sample:
                    return {"status": "ok", "collection": collection, "fields": [], "note": "Collection empty"}
                fields = {k: type(v).__name__ for k, v in sample.items()}
                count = await db[collection].count_documents({})
                return {"status": "ok", "collection": collection, "count": count, "fields": fields, "sample_keys": list(sample.keys())}
            except Exception as ex:
                return {"status": "error", "error": str(ex)}

        # ── INFRASTRUCTURE ──

        elif tool_name == "restart_service":
            service = args.get("service", "backend")
            if service not in ["backend", "frontend"]:
                return {"status": "error", "error": "Can only restart 'backend' or 'frontend'"}
            proc = subprocess.run(["sudo", "supervisorctl", "restart", service], capture_output=True, text=True, timeout=15)
            await asyncio.sleep(3)
            return {"status": "ok", "service": service, "output": proc.stdout.strip()}

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
                    resp_body = {"count": len(resp_body), "sample": resp_body[:3], "note": f"...{len(resp_body)} total"}
            except Exception:
                pass
            return {"status": "ok", "http_status": resp.status_code, "url": url_path, "response": resp_body}

        elif tool_name == "check_logs":
            service = args.get("service", "backend")
            lines = args.get("lines", 50)
            log_files = {
                "backend": "/var/log/supervisor/backend.err.log",
                "frontend": "/var/log/supervisor/frontend.err.log",
                "backend_out": "/var/log/supervisor/backend.out.log",
                "frontend_out": "/var/log/supervisor/frontend.out.log",
            }
            log_path = log_files.get(service, log_files["backend"])
            if not os.path.isfile(log_path):
                return {"status": "error", "error": f"Log file not found: {log_path}"}
            try:
                proc = subprocess.run(f"tail -n {min(lines, 200)} {log_path}", shell=True, capture_output=True, text=True, timeout=5)
                return {"status": "ok", "service": service, "lines": proc.stdout[-8000:] if proc.stdout else "(empty)"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        elif tool_name == "install_package":
            package = args.get("package", "")
            manager = args.get("manager", "pip")
            if not package or not re.match(r'^[a-zA-Z0-9\-_.=<>!@\[\],\s]+$', package):
                return {"status": "error", "error": "Invalid package name"}
            try:
                if manager == "pip":
                    proc = subprocess.run(f"pip install {package}", shell=True, capture_output=True, text=True, timeout=60, cwd="/app/backend")
                    if proc.returncode == 0:
                        subprocess.run("pip freeze > /app/backend/requirements.txt", shell=True, timeout=10)
                    return {"status": "ok" if proc.returncode == 0 else "error", "package": package, "output": proc.stdout[-2000:]}
                elif manager == "yarn":
                    proc = subprocess.run(f"yarn add {package}", shell=True, capture_output=True, text=True, timeout=90, cwd="/app/frontend")
                    return {"status": "ok" if proc.returncode == 0 else "error", "package": package, "output": proc.stdout[-2000:]}
                else:
                    return {"status": "error", "error": f"Unknown manager: {manager}"}
            except subprocess.TimeoutExpired:
                return {"status": "error", "error": "Installation timed out"}

        elif tool_name == "run_tests":
            test_path = args.get("test_path", "/app/backend/tests/")
            try:
                proc = subprocess.run(
                    f"cd /app && python -m pytest {test_path} -v --tb=short --no-header -q 2>&1 | tail -50",
                    shell=True, capture_output=True, text=True, timeout=60)
                return {"status": "ok", "output": proc.stdout[-5000:], "exit_code": proc.returncode}
            except subprocess.TimeoutExpired:
                return {"status": "error", "error": "Tests timed out"}

        # ── SEARCH ──

        elif tool_name == "grep_search":
            pattern = args.get("pattern", "")
            directory = args.get("directory", "/app/backend")
            file_ext = args.get("file_ext", "")
            if not pattern:
                return {"status": "error", "error": "pattern is required"}
            if not is_safe_path(directory):
                return {"status": "error", "error": "Access denied"}
            grep_args = ["grep", "-rn", "-E", "-i"]
            if file_ext:
                grep_args.extend(["--include", f"*.{file_ext}"])
            else:
                for ext in ["py", "js", "jsx", "ts", "tsx", "css", "json"]:
                    grep_args.extend(["--include", f"*.{ext}"])
            grep_args.extend([pattern, directory])
            try:
                proc = subprocess.run(grep_args, capture_output=True, text=True, timeout=10, cwd="/app")
                raw_lines = proc.stdout.strip().split("\n") if proc.stdout.strip() else []
                matches = []
                for line in raw_lines[:60]:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        matches.append({"file": parts[0], "line": parts[1], "text": parts[2].strip()[:200]})
                    else:
                        matches.append({"text": line[:200]})
                return {"status": "ok", "pattern": pattern, "matches": matches, "count": len(matches)}
            except subprocess.TimeoutExpired:
                return {"status": "error", "error": "Search timed out"}

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

        elif tool_name == "run_command":
            cmd = args.get("command", "")
            BLOCKED_CMDS = ["rm ", "mv ", "cp ", "chmod", "chown", "kill", "sudo", "apt", "> ", ">>"]
            for bc in BLOCKED_CMDS:
                if bc in cmd:
                    return {"status": "error", "error": f"Command blocked: contains '{bc.strip()}'"}
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, cwd="/app")
                output = proc.stdout[:5000]
                if proc.stderr:
                    output += f"\n[STDERR]: {proc.stderr[:1000]}"
                return {"status": "ok", "command": cmd, "output": output, "exit_code": proc.returncode}
            except subprocess.TimeoutExpired:
                return {"status": "error", "error": "Command timed out"}

        else:
            return {"status": "error", "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ══════════════════════════════════════════════════════════
# COMPOUND TOOLS
# ══════════════════════════════════════════════════════════

async def _scaffold_module(args):
    """Create a complete backend module: route file + server.py registration + restart + verify + auto-polish."""
    module_name = args.get("module_name", "")
    prefix = args.get("prefix", "")
    endpoints = args.get("endpoints", [])
    extra_imports = args.get("imports", "")

    if not module_name or not prefix or not endpoints:
        return {"status": "error", "error": "module_name, prefix, and endpoints are required"}

    safe_module = re.sub(r'[^a-z0-9_]', '_', module_name.lower())
    file_path = f"/app/backend/routes_{safe_module}.py"
    if os.path.isfile(file_path):
        return {"status": "error", "error": f"Module file already exists: {file_path}. Use patch_file to modify."}

    tag = module_name.replace("_", " ").title()
    code_lines = [
        f'"""Auto-generated module: {tag}"""',
        'from fastapi import APIRouter',
        'from datetime import datetime, timezone',
        'import uuid',
    ]
    if extra_imports:
        code_lines.append(extra_imports)
    code_lines.extend([
        '',
        f'router = APIRouter(prefix="{prefix}", tags=["{tag}"])',
        '',
        'db = None',
        '',
        'def set_db(database):',
        '    global db',
        '    db = database',
        '',
    ])
    for ep in endpoints:
        method = ep.get("method", "GET").lower()
        path = ep.get("path", "")
        name = ep.get("name", f"handler_{method}")
        body = ep.get("body", "    return {}")
        body_lines = body.split("\n")
        formatted_body = "\n".join(f"    {line}" if not line.startswith("    ") else line for line in body_lines)

        # Extract path parameters for proper function signatures
        import re as _re
        path_params = _re.findall(r'\{(\w+)\}', path)

        if method == "post":
            code_lines.append(f'@router.post("{path}")')
            params = ", ".join([f"{p}: str" for p in path_params] + ["body: dict"])
            code_lines.append(f'async def {name}({params}):')
        elif method == "put":
            code_lines.append(f'@router.put("{path}")')
            params = ", ".join([f"{p}: str" for p in path_params] + ["body: dict"])
            code_lines.append(f'async def {name}({params}):')
        elif method == "delete":
            ep_path = path if path else "/{item_id}"
            code_lines.append(f'@router.delete("{ep_path}")')
            del_params = path_params if path_params else ["item_id"]
            code_lines.append(f'async def {name}({", ".join(f"{p}: str" for p in del_params)}):')
        else:
            code_lines.append(f'@router.get("{path}")')
            if path_params:
                code_lines.append(f'async def {name}({", ".join(f"{p}: str" for p in path_params)}):')
            else:
                code_lines.append(f'async def {name}():')
        code_lines.append(formatted_body)
        code_lines.append('')

    file_content = "\n".join(code_lines)

    # ── AUTO-POLISH: fix known LLM code-gen bugs ──
    file_content = _polish_generated_python(file_content)

    with open(file_path, "w") as f:
        f.write(file_content)
    await _audit_file_write(file_path, file_content, "SCAFFOLD")

    # Register in server.py
    var_name = f"{safe_module}_router"
    set_fn = f"set_{safe_module}_db"
    registration_code = f"""
    # {tag}
    from routes_{safe_module} import router as {var_name}, set_db as {set_fn}
    {set_fn}(db)
    api_router.include_router({var_name})"""

    server_path = "/app/backend/server.py"
    with open(server_path, "r") as f:
        server_content = f.read()

    marker = 'logging.info("ERP modules will be integrated")'
    if marker in server_content:
        server_content = server_content.replace(marker, f"{registration_code}\n    {marker}")
        with open(server_path, "w") as f:
            f.write(server_content)
    else:
        return {"status": "partial", "path": file_path, "warning": "Could not find server.py marker. Register manually."}

    # Restart backend
    proc = subprocess.run(["sudo", "supervisorctl", "restart", "backend"], capture_output=True, text=True, timeout=15)
    await asyncio.sleep(3)

    # Verify startup
    log_proc = subprocess.run("tail -n 15 /var/log/supervisor/backend.err.log", shell=True, capture_output=True, text=True, timeout=5)
    startup_ok = "Application startup complete" in (log_proc.stdout or "")

    # If startup failed, try auto-fix once
    auto_fix_applied = False
    if not startup_ok:
        fix_result = _auto_fix_startup_error(file_path, log_proc.stdout or "")
        if fix_result:
            auto_fix_applied = True
            proc = subprocess.run(["sudo", "supervisorctl", "restart", "backend"], capture_output=True, text=True, timeout=15)
            await asyncio.sleep(3)
            log_proc = subprocess.run("tail -n 15 /var/log/supervisor/backend.err.log", shell=True, capture_output=True, text=True, timeout=5)
            startup_ok = "Application startup complete" in (log_proc.stdout or "")

    # Test first GET endpoint
    test_result = None
    first_get = next((ep for ep in endpoints if ep.get("method", "GET").upper() == "GET"), None)
    if first_get and startup_ok:
        test_url = f"http://localhost:8001/api{prefix}{first_get.get('path', '')}"
        # Strip path params for test URL
        test_url = re.sub(r'/\{[^}]+\}', '', test_url)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(test_url)
                test_result = {"http_status": resp.status_code, "ok": resp.status_code < 400}
        except Exception as e:
            test_result = {"http_status": 0, "ok": False, "error": str(e)}

    return {
        "status": "ok" if startup_ok else "error",
        "path": file_path,
        "module_name": safe_module,
        "prefix": prefix,
        "endpoints_created": len(endpoints),
        "registered_in_server": True,
        "backend_restarted": True,
        "startup_ok": startup_ok,
        "auto_fix_applied": auto_fix_applied,
        "auto_polish": True,
        "test_result": test_result,
        "logs": log_proc.stdout[-500:] if not startup_ok else "",
    }


async def _create_page(args):
    """Create a React page component + register route in App.js + add sidebar nav."""
    page_name = args.get("page_name", "")
    route_path = args.get("route_path", "")
    title = args.get("title", page_name)
    api_endpoints = args.get("api_endpoints", [])
    custom_content = args.get("content", "")
    icon = args.get("icon", "FileText")
    nav_section = args.get("nav_section", "")

    if not page_name or not route_path:
        return {"status": "error", "error": "page_name and route_path required"}

    file_path = f"/app/frontend/src/pages/{page_name}.js"
    if os.path.isfile(file_path):
        return {"status": "error", "error": f"Page already exists: {file_path}. Use patch_file."}

    if custom_content:
        page_code = custom_content
    else:
        fetch_code = ""
        if api_endpoints:
            # Fix: api_endpoints should NOT include /api prefix (API const already has it)
            ep = api_endpoints[0]
            if ep.startswith("/api/"):
                ep = ep[4:]  # strip /api prefix — API const already includes it
            elif not ep.startswith("/"):
                ep = "/" + ep
            fetch_code = f"""
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {{
    fetch(`${{API}}{ep}`).then(r => r.json()).then(d => {{ setData(Array.isArray(d) ? d : []); setLoading(false); }}).catch(() => setLoading(false));
  }}, []);"""

        page_code = f"""import {{ useState, useEffect }} from 'react';
import {{ API }} from '../App';

export default function {page_name}() {{
{fetch_code}
  return (
    <div className="p-6 space-y-6" data-testid="{page_name.lower()}-page">
      <h1 className="text-2xl font-bold text-[#E8EDF2]">{title}</h1>
      {f'{{loading ? <p className="text-[#4A5B6E]">Loading...</p> : <pre className="text-xs text-[#c8d4e0] bg-[#0D1B2A] p-4 rounded-lg border border-[#1B2D42] overflow-auto">{{JSON.stringify(data, null, 2)}}</pre>}}' if api_endpoints else '<p className="text-[#4A5B6E]">Content goes here</p>'}
    </div>
  );
}}
"""

    with open(file_path, "w") as f:
        f.write(page_code)

    # Register route in App.js
    app_path = "/app/frontend/src/App.js"
    with open(app_path, "r") as f:
        app_content = f.read()

    # Add import
    import_line = f"import {page_name} from './pages/{page_name}';"
    if import_line not in app_content:
        import_match = list(re.finditer(r'^import .+ from .+;$', app_content, re.MULTILINE))
        if import_match:
            last_import_end = import_match[-1].end()
            app_content = app_content[:last_import_end] + f"\n{import_line}" + app_content[last_import_end:]

    # Add route
    route_line = f'<Route path="{route_path}" element={{<{page_name} />}} />'
    if route_line not in app_content:
        routes_end = app_content.find("</Routes>")
        if routes_end != -1:
            indent = "              "
            app_content = app_content[:routes_end] + f"{indent}{route_line}\n{indent}" + app_content[routes_end:]

    # Add sidebar navigation entry
    sidebar_added = False
    if nav_section:
        # Find the nav section and add entry
        nav_marker = f"label: '{nav_section}'"
        if nav_marker not in app_content:
            # Try to add near existing nav entries
            nav_entry = f"        {{ path: '{route_path}', label: '{title}', icon: {icon} }},"
            # Find the last nav entry before a closing bracket
            last_nav = app_content.rfind("{ path: '/bank-reconciliation'")
            if last_nav == -1:
                last_nav = app_content.rfind("{ path: '/expense-management'")
            if last_nav != -1:
                line_end = app_content.find("\n", last_nav)
                if line_end != -1:
                    app_content = app_content[:line_end + 1] + nav_entry + "\n" + app_content[line_end + 1:]
                    sidebar_added = True

    with open(app_path, "w") as f:
        f.write(app_content)

    return {
        "status": "ok",
        "path": file_path,
        "page_name": page_name,
        "route_path": route_path,
        "registered_in_app_js": True,
        "sidebar_added": sidebar_added,
        "api_prefix_fixed": True,
    }


# ══════════════════════════════════════════════════════════
# AUTO-POLISH & AUTO-FIX
# ══════════════════════════════════════════════════════════

def _polish_generated_python(code: str) -> str:
    """Fix common LLM code-generation bugs in Python code targeting Motor/MongoDB."""
    original = code

    # Fix 1: .to_list() missing length argument → .to_list(500)
    code = re.sub(r'\.to_list\(\s*\)', '.to_list(500)', code)

    # Fix 2: MongoDB _id not excluded in find projections
    # Only fix if find({...}) has no projection argument
    code = re.sub(
        r'\.find\(\{([^}]*)\}\)\s*\.to_list',
        lambda m: f'.find({{{m.group(1)}}}, {{"_id": 0}}).to_list' if '"_id"' not in m.group(0) else m.group(0),
        code
    )
    # Also fix find_one without _id exclusion
    code = re.sub(
        r'\.find_one\(\{([^}]*)\}\)\s*$',
        lambda m: f'.find_one({{{m.group(1)}}}, {{"_id": 0}})' if '"_id"' not in m.group(0) else m.group(0),
        code,
        flags=re.MULTILINE,
    )

    # Fix 3: return doc that may contain _id after insert_one
    # Pattern: insert_one(var) then return var → return {k:v for k,v...}
    code = re.sub(
        r'await db\.\w+\.insert_one\((\w+)\)\s*\n(\s*)return \1\s*$',
        lambda m: f'await db.{m.group(0).split("db.")[1].split(".insert")[0]}.insert_one({m.group(1)})\n{m.group(2)}return {{k: v for k, v in {m.group(1)}.items() if k != "_id"}}',
        code,
        flags=re.MULTILINE,
    )

    # Fix 4: Missing 'body: dict' param for POST/PUT handlers
    # If function body references 'body' but signature doesn't have it
    for match in re.finditer(r'async def (\w+)\(\):\n((?:    .*\n)*)', code):
        fn_name, fn_body = match.group(1), match.group(2)
        if 'body' in fn_body and 'body' not in match.group(0).split('(')[1]:
            code = code.replace(f'async def {fn_name}():', f'async def {fn_name}(body: dict):', 1)

    # Fix 5: Aggregation _id field handling — rename _id to meaningful name
    # $group results have _id as the group key, not a MongoDB ObjectId
    code = re.sub(
        r'\{k:\s*v\s+for\s+k,\s*v\s+in\s+item\.items\(\)\s+if\s+k\s*!=\s*"_id"\}',
        '{**{("name" if k == "_id" else k): v for k, v in item.items()}}',
        code,
    )

    # Fix 6: datetime.utcnow() → datetime.now(timezone.utc)
    code = code.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')

    changes = sum(1 for a, b in zip(original.split('\n'), code.split('\n')) if a != b)
    if changes > 0:
        logging.info(f"Auto-polish: fixed {changes} lines in generated code")

    return code


def _auto_fix_startup_error(file_path: str, log_output: str) -> bool:
    """Try to auto-fix common startup errors. Returns True if a fix was applied."""
    if not os.path.isfile(file_path):
        return False

    with open(file_path, "r") as f:
        code = f.read()

    original = code
    fixed = False

    # Fix: to_list() missing positional argument 'length'
    if "to_list() missing 1 required positional argument" in log_output:
        code = re.sub(r'\.to_list\(\s*\)', '.to_list(500)', code)
        fixed = True

    # Fix: 'body' is not defined (missing function parameter)
    if "name 'body' is not defined" in log_output:
        # Find async def without body param that uses body
        code = re.sub(
            r'(async def \w+)\(\)(:.*\n(?:    .*body.*\n))',
            r'\1(body: dict)\2',
            code,
        )
        fixed = True

    # Fix: IndentationError
    if "IndentationError" in log_output:
        # Try to fix by ensuring consistent 4-space indentation
        lines = code.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() and not line[0] in (' ', '\t', '#', '@', 'd', 'f', 'i', 'r', 'a', '"', "'"):
                # Line doesn't start with expected char — might need indentation
                new_lines.append('    ' + line)
            else:
                new_lines.append(line)
        code = '\n'.join(new_lines)
        fixed = True

    # Fix: SyntaxError on specific line
    if "SyntaxError" in log_output:
        # Extract line number
        match = re.search(r'line (\d+)', log_output)
        if match:
            line_num = int(match.group(1))
            lines = code.split('\n')
            if 0 < line_num <= len(lines):
                problem_line = lines[line_num - 1]
                # Common fix: unbalanced quotes
                if problem_line.count('"') % 2 != 0:
                    lines[line_num - 1] = problem_line + '"'
                    code = '\n'.join(lines)
                    fixed = True

    if fixed and code != original:
        with open(file_path, "w") as f:
            f.write(code)
        logging.info(f"Auto-fix applied to {file_path}")
        return True

    return False


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════

async def _audit_file_write(path, detail, action_type):
    await db.audit_trail.insert_one({
        "id": str(uuid.uuid4()), "action": f"FILE_{action_type}", "module": "AI_ENGINE",
        "record_id": path, "record_name": os.path.basename(path),
        "changes": [{"field": "content", "new_value": str(detail)[:500]}],
        "timestamp": datetime.now(timezone.utc).isoformat(), "user": "kairos-engine",
    })

async def _run_test_query(query_type):
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
        return {"projects": len(p)}
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
            "tb_balanced": dr == cr, "tb_total": dr, "accounts": len(coa),
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
    calls = []
    if not text:
        return calls
    parts = text.split("```TOOL_CALL")
    for part in parts[1:]:
        end = part.find("```")
        if end != -1:
            raw = part[:end].strip()
            try:
                calls.append(json.loads(raw))
            except json.JSONDecodeError:
                pass
    return calls

def parse_questions(text):
    questions = []
    if not text:
        return questions
    parts = text.split("```QUESTION")
    for part in parts[1:]:
        end = part.find("```")
        if end != -1:
            questions.append(part[:end].strip())
    return questions

def parse_done(text):
    if not text:
        return None
    if "```DONE" in text:
        parts = text.split("```DONE")
        if len(parts) > 1:
            end = parts[1].find("```")
            if end != -1:
                return parts[1][:end].strip()
            return parts[1].strip()
    return None

def _clean_response_text(text):
    if not text:
        return ""
    cleaned = re.sub(r'```TOOL_CALL[\s\S]*?```', '', text)
    cleaned = re.sub(r'```QUESTION[\s\S]*?```', '', cleaned)
    cleaned = re.sub(r'```DONE[\s\S]*?```', '', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    return cleaned


def _compress_tool_result(tool_name, result):
    """Compress tool results to reduce LLM context consumption."""
    if result.get("status") == "error":
        return {"status": "error", "error": result.get("error", "")}

    if tool_name == "read_file":
        content = result.get("content", "")
        if len(content) > 5000:
            return {"status": "ok", "path": result.get("path"), "total_lines": result.get("total_lines"),
                    "showing": result.get("showing"), "content": content[:5000] + "\n... [COMPRESSED — showing first 5000 chars]"}
        return result

    if tool_name == "list_files":
        files = result.get("files", [])
        if len(files) > 20:
            return {"status": "ok", "count": len(files), "files": files[:20], "note": f"Showing 20/{len(files)}"}
        return result

    if tool_name == "check_logs":
        log_text = result.get("lines", "")
        if len(log_text) > 3000:
            return {"status": "ok", "service": result.get("service"), "lines": log_text[-3000:], "note": "Last 3000 chars shown"}
        return result

    if tool_name == "grep_search":
        matches = result.get("matches", [])
        if len(matches) > 20:
            return {"status": "ok", "pattern": result.get("pattern"), "count": len(matches), "matches": matches[:20], "note": f"Showing 20/{len(matches)}"}
        return result

    if tool_name in ("scaffold_module", "create_page"):
        return result  # Always return full result for compound tools

    if tool_name == "run_command":
        output = result.get("output", "")
        if len(output) > 3000:
            return {"status": "ok", "command": result.get("command"), "output": output[:3000] + "\n... [COMPRESSED]", "exit_code": result.get("exit_code")}
        return result

    return result


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
    parts = [para.text for para in doc.paragraphs if para.text.strip()]
    for table in doc.tables:
        parts.append("[Table]\n" + "\n".join(" | ".join(cell.text for cell in row.cells) for row in table.rows))
    return "\n".join(parts)

def _extract_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    parts = []
    for name in wb.sheetnames[:10]:
        ws = wb[name]
        rows = [" | ".join(str(c or "") for c in row) for row in ws.iter_rows(max_row=200, values_only=True)]
        parts.append(f"--- Sheet: {name} ---\n" + "\n".join(rows))
    return "\n\n".join(parts)

def _extract_pptx(path):
    from pptx import Presentation
    prs = Presentation(path)
    parts = []
    for i, slide in enumerate(prs.slides[:50]):
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        texts.append(para.text)
            if shape.has_table:
                for row in shape.table.rows:
                    texts.append(" | ".join(cell.text for cell in row.cells))
        if texts:
            parts.append(f"--- Slide {i+1} ---\n" + "\n".join(texts))
    return "\n\n".join(parts)

def _extract_csv(path):
    import csv
    rows = []
    with open(path, "r", errors="replace") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 500:
                rows.append("... [TRUNCATED]")
                break
            rows.append(" | ".join(row))
    return "\n".join(rows)

EXTRACTORS = {".pdf": _extract_pdf, ".docx": _extract_docx, ".doc": _extract_docx, ".xlsx": _extract_xlsx, ".xls": _extract_xlsx, ".pptx": _extract_pptx, ".ppt": _extract_pptx, ".csv": _extract_csv}
TEXT_EXTS = {".txt", ".md", ".json", ".xml", ".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".yaml", ".yml", ".ini", ".cfg", ".log", ".sql"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".heic", ".heif"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    file_id = str(uuid.uuid4())[:8]
    safe_name = f"{file_id}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    content_bytes = await file.read()
    with open(save_path, "wb") as f:
        f.write(content_bytes)
    size_kb = len(content_bytes) / 1024
    result = {"id": file_id, "filename": file.filename, "ext": ext, "size_kb": round(size_kb, 1), "type": "unknown", "content": ""}
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
            result["content"] = f"[Image: {file.filename} ({size_kb:.0f}KB)]"
        else:
            result["type"] = "binary"
            result["content"] = f"[Unsupported: {ext}]"
    except Exception as e:
        result["content"] = f"[Extraction error: {str(e)}]"
        result["type"] = "error"
    if len(result["content"]) > 40000:
        result["content"] = result["content"][:40000] + "\n... [TRUNCATED]"
    return result

@router.post("/crawl-url")
async def crawl_url(body: dict):
    url = body.get("url", "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; KairosBot/1.0)"})
            resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        raw = resp.text
        if "html" in content_type:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()
            title = soup.title.string if soup.title else url
            text = "\n".join(ln.strip() for ln in soup.get_text(separator="\n", strip=True).splitlines() if ln.strip())
            return {"status": "ok", "url": url, "title": title, "type": "html", "content": text[:30000], "size_kb": round(len(text) / 1024, 1)}
        return {"status": "ok", "url": url, "title": url, "type": "text", "content": raw[:30000], "size_kb": round(len(raw) / 1024, 1)}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "url": url, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"status": "error", "url": url, "error": str(e)}

# ══════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ══════════════════════════════════════════════════════════

@router.get("/sessions")
async def list_sessions():
    sessions = await db.agent_sessions.find({}, {"_id": 0}).sort("updated_at", -1).to_list(50)
    return sessions

@router.post("/sessions")
async def create_session(body: dict):
    session = {
        "id": str(uuid.uuid4()), "agent_type": body.get("agent_type", "auto"),
        "title": body.get("title", "New Session"), "messages": [],
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
# DIRECT ACCESS ENDPOINTS
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
# AGENTIC LOOP ENGINE (v3 — parallel tools, auto-restart, compression)
# ══════════════════════════════════════════════════════════

_tasks = {}


async def _run_engine_task(task_id, mode, message, session_id, context):
    """Background coroutine: Agentic loop with PARALLEL tool execution."""
    try:
        _tasks[task_id]["status"] = "thinking"
        _tasks[task_id]["progress"] = "Step 1: Analyzing your request..."
        _tasks[task_id]["steps"] = []

        system = ENGINE_SYSTEM_PROMPT
        if mode == "ba":
            system += BA_ONLY_SUFFIX
        elif mode == "dev":
            system += DEV_ONLY_SUFFIX
            try:
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

        history = []
        if session_id:
            session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
            if session:
                history = session.get("messages", [])

        full_message = message
        if context:
            full_message += f"\n\n[ATTACHED CONTEXT]\n{context[:15000]}"

        history_context = ""
        if history:
            recent = history[-12:]
            hlines = [f"[{'User' if h['role']=='user' else 'AI'}]: {h['content'][:800]}" for h in recent]
            history_context = "[HISTORY]\n" + "\n".join(hlines) + "\n\n"

        all_tool_results = []
        all_files_modified = []
        all_questions = []
        all_response_parts = []
        provider_used = None
        iteration = 0

        loop_messages = [{"role": "user", "content": history_context + full_message}]

        while iteration < MAX_ITERATIONS:
            iteration += 1
            step_num = iteration
            _tasks[task_id]["status"] = "thinking" if iteration == 1 else "iterating"
            _tasks[task_id]["progress"] = f"Step {step_num}: {'Analyzing request' if iteration == 1 else 'Planning next action'}..."

            response_text, provider = await call_llm(system, loop_messages, preferred=provider_used or "auto")
            provider_used = provider

            tool_calls = parse_tool_calls(response_text)
            questions = parse_questions(response_text)
            done_summary = parse_done(response_text)
            readable_text = _clean_response_text(response_text)

            step_record = {
                "step": step_num,
                "type": "thinking" if not tool_calls else "executing",
                "summary": readable_text[:300] if readable_text else "",
                "tool_count": len(tool_calls),
                "tools_used": [tc.get("tool", "") for tc in tool_calls[:10]],
                "has_questions": len(questions) > 0,
                "provider": provider,
            }

            all_questions.extend(questions)
            if readable_text:
                all_response_parts.append(readable_text)
            if done_summary:
                all_response_parts.append(done_summary)

            # No tool calls → done
            if not tool_calls:
                step_record["type"] = "complete" if done_summary else "answer"
                if done_summary:
                    step_record["summary"] = done_summary[:300]
                _tasks[task_id]["steps"].append(step_record)
                break

            # ── PARALLEL TOOL EXECUTION ──
            _tasks[task_id]["status"] = "executing"
            _tasks[task_id]["progress"] = f"Step {step_num}: Running {len(tool_calls)} tool{'s' if len(tool_calls) > 1 else ''} in parallel..."

            # Separate tools into parallel-safe and sequential groups
            # Write tools that modify the same file must be sequential; everything else parallel
            tc_list = tool_calls[:10]

            async def _exec_single(tc):
                return await execute_tool(tc.get("tool", ""), tc.get("args", {}))

            # Run ALL tools in parallel (asyncio.gather)
            results = await asyncio.gather(*[_exec_single(tc) for tc in tc_list], return_exceptions=True)

            step_tool_results = []
            step_files_modified = []
            backend_files_changed = False

            for tc, result in zip(tc_list, results):
                tool_name = tc.get("tool", "")
                if isinstance(result, Exception):
                    result = {"status": "error", "error": str(result)}
                step_tool_results.append({"tool": tool_name, "args": tc.get("args", {}), "result": result})
                if tool_name in WRITE_TOOLS and result.get("status") == "ok":
                    path = result.get("path", tc.get("args", {}).get("path", ""))
                    if path:
                        step_files_modified.append(path)
                    if path.startswith("/app/backend") and tool_name not in ("scaffold_module",):
                        backend_files_changed = True

            # AUTO-RESTART after backend file changes (scaffold_module already restarts)
            if backend_files_changed:
                _tasks[task_id]["progress"] = f"Step {step_num}: Auto-restarting backend..."
                proc = subprocess.run(["sudo", "supervisorctl", "restart", "backend"], capture_output=True, text=True, timeout=15)
                await asyncio.sleep(3)
                log_proc = subprocess.run("tail -n 5 /var/log/supervisor/backend.err.log", shell=True, capture_output=True, text=True, timeout=5)
                startup_ok = "Application startup complete" in (log_proc.stdout or "")
                step_tool_results.append({
                    "tool": "_auto_restart", "args": {},
                    "result": {"status": "ok" if startup_ok else "error", "startup_ok": startup_ok, "note": "Auto-restart after file changes"}
                })

            all_tool_results.extend(step_tool_results)
            all_files_modified.extend(step_files_modified)

            step_record["type"] = "executing"
            step_record["tool_results"] = step_tool_results
            step_record["files_modified"] = step_files_modified
            _tasks[task_id]["steps"].append(step_record)

            if done_summary:
                _tasks[task_id]["progress"] = f"Step {step_num}: Complete"
                break

            # Feed COMPRESSED results back to LLM
            compressed_results = [
                {"tool": tr["tool"], "args": {k: v for k, v in tr["args"].items() if k != "content"},
                 "result": _compress_tool_result(tr["tool"], tr["result"])}
                for tr in step_tool_results
            ]
            tool_summary = json.dumps(compressed_results, indent=1, default=str)
            if len(tool_summary) > 12000:
                tool_summary = tool_summary[:12000] + "\n... [COMPRESSED]"

            loop_messages.append({"role": "assistant", "content": response_text})
            loop_messages.append({"role": "user", "content": f"[TOOL RESULTS — Step {step_num}]\n{tool_summary}\n\nAnalyze results. Continue with tool calls if needed, or output ```DONE``` with summary."})

            _tasks[task_id]["progress"] = f"Step {step_num} complete. Analyzing..."

            if len(loop_messages) > 8:
                loop_messages = [loop_messages[0]] + loop_messages[-6:]

        # ── SAVE RESULTS ──
        final_response = "\n\n".join(all_response_parts)
        timestamp = datetime.now(timezone.utc).isoformat()

        if session_id:
            new_messages = [
                {"role": "user", "content": message, "timestamp": timestamp},
                {"role": "assistant", "content": final_response, "agent_type": mode, "timestamp": timestamp,
                 "tool_calls": len(all_tool_results), "files_modified": all_files_modified,
                 "questions": all_questions, "provider": provider_used, "iterations": iteration},
            ]
            update = {"$push": {"messages": {"$each": new_messages}}, "$set": {"updated_at": timestamp}}
            sess = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
            if sess and len(sess.get("messages", [])) == 0:
                update["$set"]["title"] = message[:80]
            await db.agent_sessions.update_one({"id": session_id}, update)

        _tasks[task_id] = {
            "status": "complete",
            "progress": f"Done ({iteration} step{'s' if iteration > 1 else ''})",
            "steps": _tasks[task_id].get("steps", []),
            "result": {
                "response": final_response, "agent_type": mode, "session_id": session_id,
                "timestamp": timestamp, "tool_calls_executed": len(all_tool_results),
                "files_modified": list(set(all_files_modified)), "questions": all_questions,
                "tool_results": all_tool_results[:20], "provider": provider_used, "iterations": iteration,
            }
        }
    except Exception as e:
        logging.error(f"Engine task error: {e}", exc_info=True)
        _tasks[task_id] = {
            "status": "error", "progress": str(e),
            "steps": _tasks.get(task_id, {}).get("steps", []),
            "result": {
                "response": f"Engine error: {str(e)}", "agent_type": mode,
                "session_id": session_id, "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool_calls_executed": 0, "files_modified": [], "questions": [],
                "tool_results": [], "iterations": 0,
            }
        }


@router.post("/chat")
async def engine_chat(body: dict):
    mode = body.get("agent_type", "auto")
    message = body.get("message", "")
    session_id = body.get("session_id", "")
    context = body.get("context", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    task_id = str(uuid.uuid4())[:12]
    _tasks[task_id] = {"status": "queued", "progress": "Starting...", "steps": [], "result": None}
    asyncio.create_task(_run_engine_task(task_id, mode, message, session_id, context))
    return {"task_id": task_id, "status": "queued"}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] in ["complete", "error"]:
        result = task.get("result", {})
        steps = task.get("steps", [])
        _tasks.pop(task_id, None)
        return {"status": task["status"], "progress": task["progress"], "steps": steps, **result}
    return {"status": task["status"], "progress": task["progress"], "steps": task.get("steps", [])}


@router.get("/providers")
async def get_providers():
    return {
        "providers": [
            {"name": "groq", "model": "llama-3.3-70b-versatile", "status": "active" if GROQ_KEY else "no_key", "priority": 1},
            {"name": "openrouter", "model": "auto (free models)", "status": "active" if OPENROUTER_KEY else "no_key", "priority": 2},
            {"name": "claude", "model": "claude-sonnet-4-5", "status": "active" if EMERGENT_KEY else "no_key", "priority": 3},
        ],
        "fallback_order": ["groq", "openrouter", "claude"],
    }
