"""Kairos AI Engine — Unified orchestrator combining BA + DEV + QA brains.
Understands requirements, plans, writes code, validates, and deploys."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid
import os
import json
import glob
import subprocess
import asyncio
import httpx

router = APIRouter(prefix="/agents", tags=["AI Engine"])

EMERGENT_KEY = None
db = None

def set_config(key, database):
    global EMERGENT_KEY, db
    EMERGENT_KEY = key
    db = database

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

ENGINE_SYSTEM_PROMPT = """You are the Kairos AI Engine — the unified intelligence powering Kairos AI ERP for Nexora Digital Solutions Pvt. Ltd.

You combine three specialized brains into one seamless agent:
- 📊 BUSINESS BRAIN: Indian accounting (Ind AS, GST, TDS, Schedule III), IT services (T&M, FP, Retainer, Milestone revenue), compliance (FEMA, STPI, Transfer Pricing)
- 💻 CODING BRAIN: FastAPI + React + MongoDB + Tailwind expert. Can read, write, and modify real project files.
- 🔍 TESTING BRAIN: Runs live queries against MongoDB. Validates data integrity, TB balance, GST compliance.

## COMPANY CONTEXT
Nexora Digital Solutions Pvt. Ltd. | CIN: U72200GJ2019PTC108341 | GSTIN: 24AABCN4567P1Z8
Gujarat | IT Services | 8 Projects, 21 Employees, 7 Clients, 10 Vendors
Revenue: ~₹1.06 Cr March 2026 | Export 55% (USD, GBP) | Domestic 45%

## TECH STACK
Backend: FastAPI, Motor (async MongoDB), Python 3.11
Frontend: React 18, Tailwind CSS, Shadcn/UI, Lucide React
DB: MongoDB — collections: entities, employees, projects, timesheets, erp_transactions, revenue_schedule, chart_of_accounts, purchase_orders, selling_invoices, journal_entries, audit_trail, company_settings

## FILE STRUCTURE
/app/backend/  — server.py, routes_*.py (purchase, selling, stock, company, statutory, audit, gst, aging, projects, timesheets, revenue, agents)
/app/frontend/src/ — App.js, pages/*.js, components/ui/*.jsx

## KEY PATTERNS
- Routes: APIRouter(prefix="/module"), db access via global, exclude _id from responses
- IDs: str(uuid.uuid4()), Timestamps: datetime.now(timezone.utc).isoformat()
- Frontend API: process.env.REACT_APP_BACKEND_URL + '/api'
- Styling: Dark theme (#0A1628 bg, #152236 cards, #1B2D42 borders, #E8EDF2 text, #00d4aa accent)

## YOUR TOOLS (called via function responses)
You have access to these tools through the orchestration system:
1. **read_file(path)** — Read any project file
2. **write_file(path, content)** — Create or modify any project file
3. **run_query(query_type)** — Run MongoDB validation queries
4. **restart_service(service)** — Restart backend or frontend
5. **test_api(method, url, body)** — Test an API endpoint
6. **list_files(directory)** — List files in a directory

## YOUR WORKFLOW
When a user makes a request, follow this flow:

### Phase 1: UNDERSTAND (📊 Business Brain)
- Analyze the request. What modules/collections/APIs are affected?
- If the request is ambiguous, ask clarifying questions (output them as a QUESTION block)
- Identify compliance implications (GST, TDS, Ind AS)

### Phase 2: PLAN
- Break the work into concrete steps
- List files to read, create, or modify
- Define the accounting entries if applicable
- Output as a numbered plan

### Phase 3: EXECUTE (💻 Coding Brain)
- For each step, output a TOOL_CALL block specifying which tool to use
- Generate production-ready code matching existing patterns
- Include data-testid attributes on all interactive elements

### Phase 4: VALIDATE (🔍 Testing Brain)
- Run relevant DB queries to verify changes
- Test API endpoints
- Check data integrity

### Phase 5: DEPLOY
- Restart affected services
- Verify the deployment

## OUTPUT FORMAT
Use these special blocks that the orchestrator will parse and execute:

For questions (Phase 1):
```QUESTION
Your clarifying question here
```

For tool calls (Phase 3-5):
```TOOL_CALL
{"tool": "read_file", "args": {"path": "/app/backend/server.py"}}
```

```TOOL_CALL
{"tool": "write_file", "args": {"path": "/app/backend/routes_new.py", "content": "file content here"}}
```

```TOOL_CALL
{"tool": "run_query", "args": {"query_type": "full_health_check"}}
```

```TOOL_CALL
{"tool": "restart_service", "args": {"service": "backend"}}
```

```TOOL_CALL
{"tool": "test_api", "args": {"method": "GET", "url": "/api/projects"}}
```

```TOOL_CALL
{"tool": "list_files", "args": {"directory": "/app/backend"}}
```

You can include multiple TOOL_CALL blocks in a single response. The orchestrator will execute them in sequence, collect results, and feed them back to you for the next phase.

Between tool calls, explain what you're doing and why. Be concise but clear.

For individual agent modes:
- If mode is "ba": Only do Phase 1 (business analysis, no code)
- If mode is "dev": Skip Phase 1, go straight to code
- If mode is "qa": Only do Phase 4 (testing/validation)
- If mode is "auto" (default): Full pipeline

IMPORTANT: When writing code, produce COMPLETE file contents. Don't use placeholders or "...existing code...". The write_file tool replaces the entire file."""

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
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            if not os.path.isfile(path):
                return {"status": "error", "error": f"File not found: {path}"}
            with open(path, "r") as f:
                content = f.read()
            if len(content) > 30000:
                content = content[:30000] + "\n... [TRUNCATED] ..."
            return {"status": "ok", "path": path, "content": content, "size": len(content)}

        elif tool_name == "write_file":
            path = args.get("path", "")
            content = args.get("content", "")
            if not is_safe_path(path):
                return {"status": "error", "error": "Access denied — blocked path"}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            await db.audit_trail.insert_one({
                "id": str(uuid.uuid4()),
                "action": "FILE_WRITE",
                "module": "AI_ENGINE",
                "record_id": path,
                "record_name": os.path.basename(path),
                "changes": [{"field": "content", "new_value": f"File written ({len(content)} chars)"}],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user": "kairos-engine",
            })
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

        else:
            return {"status": "error", "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


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

@router.post("/chat")
async def engine_chat(body: dict):
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    mode = body.get("agent_type", "auto")
    message = body.get("message", "")
    session_id = body.get("session_id", "")
    context = body.get("context", "")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Build system prompt based on mode
    system = ENGINE_SYSTEM_PROMPT
    if mode == "ba":
        system += BA_ONLY_SUFFIX
    elif mode == "dev":
        system += DEV_ONLY_SUFFIX
    elif mode == "qa":
        system += QA_ONLY_SUFFIX

    # Get conversation history
    history = []
    if session_id:
        session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
        if session:
            history = session.get("messages", [])

    # Build user message with optional file context
    full_message = message
    if context:
        full_message += f"\n\n[ATTACHED CONTEXT]\n{context}"

    # For auto/qa modes, inject a quick DB health snapshot
    if mode in ["auto", "qa"]:
        try:
            health = await _run_test_query("full_health_check")
            full_message += f"\n\n[CURRENT DB STATE]\n{json.dumps(health, default=str)}"
        except Exception:
            pass

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"engine-{session_id or uuid.uuid4()}",
            system_message=system
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        # Send recent history for context (last 6 turns)
        for h in history[-12:]:
            if h["role"] == "user":
                await chat.send_message(UserMessage(text=h["content"]))

        # Phase 1: Get initial response from Claude
        response_text = await chat.send_message(UserMessage(text=full_message))

        # Phase 2: Parse and execute tool calls
        tool_calls = parse_tool_calls(response_text)
        questions = parse_questions(response_text)
        tool_results = []
        files_modified = []

        if tool_calls:
            for tc in tool_calls:
                tool_name = tc.get("tool", "")
                tool_args = tc.get("args", {})
                result = await execute_tool(tool_name, tool_args)
                tool_results.append({"tool": tool_name, "args": tool_args, "result": result})
                if tool_name == "write_file" and result.get("status") == "ok":
                    files_modified.append(result.get("path", ""))

            # Phase 3: Feed tool results back to Claude for follow-up
            tool_summary = json.dumps(tool_results, indent=2, default=str)
            if len(tool_summary) > 15000:
                tool_summary = tool_summary[:15000] + "\n... [TRUNCATED]"

            followup = await chat.send_message(UserMessage(
                text=f"[TOOL EXECUTION RESULTS]\n{tool_summary}\n\nBased on these results, provide your analysis, confirm what was done, and suggest next steps. If files were modified, note which services need restart."
            ))
            response_text += f"\n\n---\n\n{followup}"

        # Save to session
        timestamp = datetime.now(timezone.utc).isoformat()
        if session_id:
            new_messages = [
                {"role": "user", "content": message, "timestamp": timestamp},
                {"role": "assistant", "content": response_text, "agent_type": mode, "timestamp": timestamp,
                 "tool_calls": len(tool_calls), "files_modified": files_modified, "questions": questions},
            ]
            update = {
                "$push": {"messages": {"$each": new_messages}},
                "$set": {"updated_at": timestamp}
            }
            session = await db.agent_sessions.find_one({"id": session_id}, {"_id": 0})
            if session and len(session.get("messages", [])) == 0:
                update["$set"]["title"] = message[:80]
            await db.agent_sessions.update_one({"id": session_id}, update)

        return {
            "response": response_text,
            "agent_type": mode,
            "session_id": session_id,
            "timestamp": timestamp,
            "tool_calls_executed": len(tool_calls),
            "files_modified": files_modified,
            "questions": questions,
            "tool_results": tool_results[:10],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine error: {str(e)}")
