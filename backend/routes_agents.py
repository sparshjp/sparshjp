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

ENGINE_SYSTEM_PROMPT = """You are the Kairos AI Engine — the unified intelligence for Kairos AI ERP (Nexora Digital Solutions Pvt. Ltd). You analyze requirements, write code, run DB queries, test APIs, and deploy changes.

COMPANY: Nexora Digital Solutions | GSTIN: 24AABCN4567P1Z8 | Gujarat | IT Services
Revenue: INR/USD(84.50)/GBP(106.80) | 8 Projects, 20 Employees, 7 Clients, 10 Vendors
Bank Accounts: HDFC Bank Current (6840000), Axis Bank Current (2250000), EEFC USD (3042000)
TB Balance: 28142000 (balanced) | 26 CoA ledgers

PROJECTS: PRJ-001 FinTrack(Axis Sec,FP 45L,88%), PRJ-002 CloudMigration(Mahindra,T&M USD95/hr), PRJ-003 Analytics(HDFC AMC,Milestone 28L,50%), PRJ-004 ManagedSvcs(Havells,Retainer 4.5L/mo), PRJ-005 PayEdge(TechFin USA,FP USD120K,CLOSED), PRJ-006 DevOps(RetailCo UK,T&M GBP140/hr), PRJ-007 DataWarehouse(AsianPaints,Milestone 18L,33%)

TECH: FastAPI+Motor(MongoDB) backend:8001 | React+Tailwind+Shadcn frontend:3000
Design: Dark theme #0D1B2A bg, #152236 cards, #1B2D42 borders, #E8EDF2 text, #00d4aa accent

FILES: /app/backend/server.py(main), routes_*.py(purchase,selling,crm,hr,stock,manufacturing,projects,timesheets,revenue,agents,financial_statements,statutory,gst,company,audit,aging,sales), seed_nexora.py
/app/frontend/src/App.js, pages/*.js, components/ui/*.jsx

PATTERNS: APIRouter(prefix="/module"), IDs: str(uuid.uuid4()), Timestamps: datetime.now(timezone.utc).isoformat(), exclude _id from MongoDB, API prefix /api, frontend uses process.env.REACT_APP_BACKEND_URL+'/api'

DB COLLECTIONS: chart_of_accounts, entities, employees, projects, timesheets, erp_transactions, revenue_schedule, company_settings, agent_sessions, purchase_orders, goods_receipt_notes, purchase_invoices, vendor_payments, selling_sales_orders, selling_delivery_notes, selling_invoices, customer_payments, journal_entries, manual_journal_entries, leads, audit_trail, items, work_orders, monthly_hours

BUSINESS RULES: GST intra-state=CGST+SGST, inter-state=IGST. Export=zero-rated LUT. TDS: 194J(10%), 194C(2%), 194I(10%). Revenue Ind AS 115: FP=POC, T&M=right to invoice, Milestone=acceptance, Retainer=straight-line.

TOOLS (use via ```TOOL_CALL blocks):
1. read_file(path) — read project file
2. write_file(path, content) — create/modify file (COMPLETE content, no placeholders)
3. run_query(query_type) — full_health_check|tb_balance|entity_validation|project_health|collection_stats
4. restart_service(service) — "backend" or "frontend"
5. test_api(method, url, body) — test API endpoint
6. list_files(directory) — list files

WORKFLOW: Understand→Plan→Execute→Validate→Deploy
OUTPUT: Use ```TOOL_CALL\n{"tool":"x","args":{...}}\n``` blocks. Use ```QUESTION\ntext\n``` for clarifications.
When writing code: produce COMPLETE files, match existing patterns, include data-testid on interactive elements, register new routes in server.py."""

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
            lines = [l.strip() for l in text.splitlines() if l.strip()]
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

@router.post("/chat")
async def engine_chat(body: dict):
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    mode = body.get("agent_type", "auto")
    message = body.get("message", "")
    session_id = body.get("session_id", "")
    context = body.get("context", "")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Use a compact system prompt for faster responses; full prompt is too large for gateway timeout
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
        # Trim context to avoid bloating the request
        full_message += f"\n\n[ATTACHED CONTEXT]\n{context[:12000]}"

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"engine-{session_id or uuid.uuid4()}",
            system_message=system
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        # Inject conversation history as context in the message itself (avoids multiple LLM round-trips)
        history_context = ""
        if history:
            recent = history[-6:]
            history_lines = []
            for h in recent:
                role = "User" if h["role"] == "user" else "Assistant"
                content = h["content"][:300]
                history_lines.append(f"[{role}]: {content}")
            history_context = "[CONVERSATION HISTORY]\n" + "\n".join(history_lines) + "\n\n"

        # Phase 1: Get initial response from Claude (single LLM call with timeout)
        response_text = await asyncio.wait_for(
            chat.send_message(UserMessage(text=history_context + full_message)),
            timeout=50
        )

        # Phase 2: Parse and execute tool calls
        tool_calls = parse_tool_calls(response_text)
        questions = parse_questions(response_text)
        tool_results = []
        files_modified = []

        if tool_calls:
            for tc in tool_calls[:6]:
                tool_name = tc.get("tool", "")
                tool_args = tc.get("args", {})
                result = await execute_tool(tool_name, tool_args)
                tool_results.append({"tool": tool_name, "args": tool_args, "result": result})
                if tool_name == "write_file" and result.get("status") == "ok":
                    files_modified.append(result.get("path", ""))

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
    except asyncio.TimeoutError:
        return {
            "response": "The request took too long to process. Please try a shorter or more specific prompt.",
            "agent_type": mode,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_calls_executed": 0,
            "files_modified": [],
            "questions": [],
            "tool_results": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine error: {str(e)}")
