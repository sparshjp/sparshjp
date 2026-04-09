"""Kairos AI Engine — Tool Handlers.

Extracted from routes_agents.py for maintainability.
Each tool is a standalone async function registered in TOOL_REGISTRY.
Dependencies (db, path safety, audit) injected via configure().
"""
import os
import re
import glob
import json
import uuid
import shlex
import logging
import asyncio
import subprocess
from datetime import datetime, timezone

import httpx
from kairos_subagents import (
    call_subagent,
    generate_image as gen_image,
    run_test_suite,
    run_playwright_test,
    run_api_test,
    VERIFIED_PLAYBOOKS,
)

# ═══════════════════════════════════════
# MODULE-LEVEL CONFIGURATION
# ═══════════════════════════════════════

_db = None
_is_safe_path = None
_audit_file_write = None


def configure(database, safe_path_fn, audit_fn):
    """Inject shared dependencies from routes_agents."""
    global _db, _is_safe_path, _audit_file_write
    _db = database
    _is_safe_path = safe_path_fn
    _audit_file_write = audit_fn


# ═══════════════════════════════════════
# FILE I/O TOOLS
# ═══════════════════════════════════════

async def tool_read_file(args):
    path = args.get("path", "")
    start_line = args.get("start_line", 1)
    end_line = args.get("end_line")
    if not _is_safe_path(path):
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


async def tool_create_file(args):
    path = args.get("path", "")
    content = args.get("content", "")
    if not _is_safe_path(path):
        return {"status": "error", "error": "Access denied — blocked path"}
    if os.path.isfile(path):
        return {"status": "error", "error": f"File already exists: {path}. Use patch_file."}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    await _audit_file_write(path, content, "CREATE")
    return {"status": "ok", "path": path, "size": len(content)}


async def tool_write_file(args):
    path = args.get("path", "")
    content = args.get("content", "")
    if not _is_safe_path(path):
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


async def tool_patch_file(args):
    path = args.get("path", "")
    old_str = args.get("old_str", "")
    new_str = args.get("new_str", "")
    if not _is_safe_path(path):
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


async def tool_insert_lines(args):
    path = args.get("path", "")
    after_line = args.get("after_line", 0)
    content = args.get("content", "")
    if not _is_safe_path(path):
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


async def tool_delete_lines(args):
    path = args.get("path", "")
    start_line = args.get("start_line", 1)
    end_line = args.get("end_line", 1)
    if not _is_safe_path(path):
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


async def tool_delete_file(args):
    path = args.get("path", "")
    if not _is_safe_path(path):
        return {"status": "error", "error": "Access denied — blocked path"}
    if not os.path.isfile(path):
        return {"status": "error", "error": f"File not found: {path}"}
    size = os.path.getsize(path)
    os.remove(path)
    await _audit_file_write(path, f"DELETED ({size} bytes)", "DELETE_FILE")
    return {"status": "ok", "path": path, "deleted": True, "size_was": size}


async def tool_move_file(args):
    import shutil
    source = args.get("source", "")
    destination = args.get("destination", "")
    if not _is_safe_path(source) or not _is_safe_path(destination):
        return {"status": "error", "error": "Access denied — blocked path"}
    if not os.path.isfile(source):
        return {"status": "error", "error": f"Source not found: {source}"}
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.move(source, destination)
    await _audit_file_write(destination, f"MOVED from {source}", "MOVE_FILE")
    return {"status": "ok", "source": source, "destination": destination}


# ═══════════════════════════════════════
# DATABASE TOOLS
# ═══════════════════════════════════════

async def _run_test_query(query_type):
    if query_type == "tb_balance":
        coa = await _db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        dr = sum(max(0, e["opening_balance"]) for e in coa)
        cr = sum(max(0, -e["opening_balance"]) for e in coa)
        return {"total_debit": dr, "total_credit": cr, "balanced": dr == cr, "accounts": len(coa)}
    elif query_type == "entity_validation":
        v = await _db.entities.find({"entity_type": "vendor"}, {"_id": 0}).to_list(100)
        c = await _db.entities.find({"entity_type": "customer"}, {"_id": 0}).to_list(100)
        return {"vendors": len(v), "customers": len(c), "vendor_missing_gstin": [x["name"] for x in v if not x.get("gstin")]}
    elif query_type == "project_health":
        p = await _db.projects.find({"id": {"$ne": "PRJ-INT"}}, {"_id": 0}).to_list(20)
        return {"projects": len(p)}
    elif query_type == "collection_stats":
        cols = await _db.list_collection_names()
        stats = {}
        for col in sorted(cols):
            stats[col] = await _db[col].count_documents({})
        return stats
    elif query_type == "full_health_check":
        coa = await _db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
        dr = sum(max(0, e["opening_balance"]) for e in coa)
        cr = sum(max(0, -e["opening_balance"]) for e in coa)
        return {
            "tb_balanced": dr == cr, "tb_total": dr, "accounts": len(coa),
            "vendors": await _db.entities.count_documents({"entity_type": "vendor"}),
            "customers": await _db.entities.count_documents({"entity_type": "customer"}),
            "projects": await _db.projects.count_documents({}),
            "employees": await _db.employees.count_documents({}),
            "timesheets": await _db.timesheets.count_documents({}),
            "transactions": await _db.erp_transactions.count_documents({}),
        }
    else:
        return {"error": f"Unknown query: {query_type}"}


async def tool_run_query(args):
    query_type = args.get("query_type", args.get("operation", "full_health_check"))
    collection_name = args.get("collection", "")

    if query_type == "full_health_check":
        result = await _run_test_query("full_health_check")
        return {"status": "ok", "query_type": "full_health_check", "results": result}

    if not collection_name:
        return {"status": "error", "error": "collection name required"}

    coll = _db[collection_name]
    query = args.get("query", {})
    try:
        if query_type in ["find", "read"]:
            projection = args.get("projection", {"_id": 0})
            if "_id" not in projection:
                projection["_id"] = 0
            limit = min(args.get("limit", 20), 100)
            docs = await coll.find(query, projection).limit(limit).to_list(limit)
            return {"status": "ok", "collection": collection_name, "count": len(docs), "documents": docs}

        elif query_type == "count":
            count = await coll.count_documents(query)
            return {"status": "ok", "collection": collection_name, "count": count}

        elif query_type in ["insert", "insert_one"]:
            doc = args.get("document", args.get("doc", {}))
            if not doc:
                return {"status": "error", "error": "document required for insert"}
            await coll.insert_one(doc)
            doc.pop("_id", None)
            return {"status": "ok", "collection": collection_name, "inserted": doc}

        elif query_type in ["insert_many"]:
            docs = args.get("documents", [])
            if not docs:
                return {"status": "error", "error": "documents array required"}
            await coll.insert_many(docs)
            for d in docs:
                d.pop("_id", None)
            return {"status": "ok", "collection": collection_name, "inserted_count": len(docs)}

        elif query_type in ["update", "update_many"]:
            update = args.get("update", {})
            if not update:
                return {"status": "error", "error": "update object required"}
            result = await coll.update_many(query, update)
            return {"status": "ok", "collection": collection_name, "matched": result.matched_count, "modified": result.modified_count}

        elif query_type in ["update_one"]:
            update = args.get("update", {})
            result = await coll.update_one(query, update)
            return {"status": "ok", "collection": collection_name, "matched": result.matched_count, "modified": result.modified_count}

        elif query_type in ["delete", "delete_many"]:
            result = await coll.delete_many(query)
            return {"status": "ok", "collection": collection_name, "deleted": result.deleted_count}

        elif query_type in ["delete_one"]:
            result = await coll.delete_one(query)
            return {"status": "ok", "collection": collection_name, "deleted": result.deleted_count}

        elif query_type == "aggregate":
            pipeline = args.get("pipeline", [])
            if not pipeline:
                return {"status": "error", "error": "pipeline array required"}
            docs = await coll.aggregate(pipeline).to_list(100)
            for d in docs:
                d.pop("_id", None)
            return {"status": "ok", "collection": collection_name, "results": docs, "count": len(docs)}

        elif query_type == "distinct":
            field = args.get("field", "")
            if not field:
                return {"status": "error", "error": "field required for distinct"}
            values = await coll.distinct(field, query)
            return {"status": "ok", "collection": collection_name, "field": field, "values": values, "count": len(values)}

        elif query_type == "drop":
            await coll.drop()
            return {"status": "ok", "collection": collection_name, "dropped": True}

        else:
            return {"status": "error", "error": f"Unknown query_type: {query_type}. Use: find, count, insert, insert_many, update, update_one, update_many, delete, delete_one, delete_many, aggregate, distinct, drop"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def tool_get_schema(args):
    collection = args.get("collection", "")
    if not collection:
        return {"status": "error", "error": "collection name required"}
    try:
        sample = await _db[collection].find_one({}, {"_id": 0})
        if not sample:
            return {"status": "ok", "collection": collection, "fields": [], "note": "Collection empty"}
        fields = {k: type(v).__name__ for k, v in sample.items()}
        count = await _db[collection].count_documents({})
        return {"status": "ok", "collection": collection, "count": count, "fields": fields, "sample_keys": list(sample.keys())}
    except Exception as ex:
        return {"status": "error", "error": str(ex)}


# ═══════════════════════════════════════
# INFRASTRUCTURE TOOLS
# ═══════════════════════════════════════

async def tool_restart_service(args):
    service = args.get("service", "backend")
    if service not in ["backend", "frontend"]:
        return {"status": "error", "error": "Can only restart 'backend' or 'frontend'"}
    proc = subprocess.run(["sudo", "supervisorctl", "restart", service], capture_output=True, text=True, timeout=15)
    wait_time = 4 if service == "backend" else 8
    await asyncio.sleep(wait_time)
    return {"status": "ok", "service": service, "output": proc.stdout.strip()}


async def tool_test_api(args):
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


async def tool_check_logs(args):
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
        proc = subprocess.run(["tail", "-n", str(min(lines, 200)), log_path], capture_output=True, text=True, timeout=5)
        return {"status": "ok", "service": service, "lines": proc.stdout[-8000:] if proc.stdout else "(empty)"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def tool_install_package(args):
    package = args.get("package", "")
    manager = args.get("manager", "pip")
    if not package or not re.match(r'^[a-zA-Z0-9\-_.=<>!@\[\],\s]+$', package):
        return {"status": "error", "error": "Invalid package name"}
    try:
        pkg_list = shlex.split(package)
        if manager == "pip":
            proc = subprocess.run(["pip", "install"] + pkg_list, capture_output=True, text=True, timeout=60, cwd="/app/backend")
            if proc.returncode == 0:
                subprocess.run(["sh", "-c", "pip freeze > /app/backend/requirements.txt"], timeout=10)
            return {"status": "ok" if proc.returncode == 0 else "error", "package": package, "output": proc.stdout[-2000:]}
        elif manager == "yarn":
            proc = subprocess.run(["yarn", "add"] + pkg_list, capture_output=True, text=True, timeout=90, cwd="/app/frontend")
            return {"status": "ok" if proc.returncode == 0 else "error", "package": package, "output": proc.stdout[-2000:]}
        else:
            return {"status": "error", "error": f"Unknown manager: {manager}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Installation timed out"}


async def tool_run_tests(args):
    test_path = args.get("test_path", "/app/backend/tests/")
    if not re.match(r'^[a-zA-Z0-9/_.\-]+$', test_path):
        return {"status": "error", "error": "Invalid test path"}
    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", test_path, "-v", "--tb=short", "--no-header", "-q"],
            capture_output=True, text=True, timeout=60, cwd="/app")
        output = proc.stdout[-5000:]
        if proc.stderr:
            output += proc.stderr[-1000:]
        return {"status": "ok", "output": output, "exit_code": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Tests timed out"}


# ═══════════════════════════════════════
# SEARCH & COMMAND TOOLS
# ═══════════════════════════════════════

async def tool_grep_search(args):
    pattern = args.get("pattern", "")
    directory = args.get("directory", "/app/backend")
    file_ext = args.get("file_ext", "")
    if not pattern:
        return {"status": "error", "error": "pattern is required"}
    if not _is_safe_path(directory):
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


async def tool_list_files(args):
    directory = args.get("directory", "/app/backend")
    if not _is_safe_path(directory):
        return {"status": "error", "error": "Access denied"}
    files = []
    for f in sorted(glob.glob(f"{directory}/**", recursive=True)):
        if os.path.isfile(f) and _is_safe_path(f):
            ext = os.path.splitext(f)[1]
            if ext in [".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".md"]:
                files.append({"path": f, "relative": f.replace("/app/", ""), "size": os.path.getsize(f)})
    return {"status": "ok", "files": files[:100], "count": len(files)}


async def tool_run_command(args):
    cmd = args.get("command", "")
    timeout_secs = min(args.get("timeout", 60), 120)
    HARD_BLOCKED = ["rm -rf /", "mkfs", ":(){", "dd if=", "curl|sh", "wget|sh", "curl|bash", "wget|bash"]
    for bc in HARD_BLOCKED:
        if bc in cmd:
            return {"status": "error", "error": f"Command blocked for safety: contains '{bc}'"}
    try:
        proc = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout_secs, cwd="/app",
            env={**os.environ, "PATH": os.environ.get("PATH", "/usr/bin:/bin")})
        output = proc.stdout[:8000]
        if proc.stderr:
            output += f"\n[STDERR]: {proc.stderr[:2000]}"
        return {"status": "ok", "command": cmd, "output": output, "exit_code": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": f"Command timed out ({timeout_secs}s)"}


# ═══════════════════════════════════════
# VERIFICATION TOOLS
# ═══════════════════════════════════════

async def tool_verify_deployment(args):
    checks = args.get("checks", [])
    if not checks:
        checks = [{"type": "backend_health"}]
    results = []
    for check in checks[:8]:
        check_type = check.get("type", "api")
        if check_type == "backend_health":
            try:
                log_proc = subprocess.run(["tail", "-n", "10", "/var/log/supervisor/backend.err.log"], capture_output=True, text=True, timeout=5)
                startup_ok = "Application startup complete" in (log_proc.stdout or "")
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get("http://localhost:8001/api/health")
                    health_ok = resp.status_code == 200
                results.append({"check": "backend_health", "startup_ok": startup_ok, "health_endpoint": health_ok, "status": "pass" if (startup_ok and health_ok) else "fail"})
            except Exception as e:
                results.append({"check": "backend_health", "status": "fail", "error": str(e)})
        elif check_type == "api":
            url_path = check.get("url", "")
            method = check.get("method", "GET").upper()
            expected_status = check.get("expected_status", 200)
            try:
                base_url = "http://localhost:8001"
                full_url = f"{base_url}{url_path}"
                async with httpx.AsyncClient(timeout=10) as client:
                    if method == "GET":
                        resp = await client.get(full_url)
                    elif method == "POST":
                        resp = await client.post(full_url, json=check.get("body", {}))
                    else:
                        resp = await client.request(method, full_url)
                passed = resp.status_code == expected_status
                body_preview = resp.text[:500]
                try:
                    body_preview = resp.json()
                    if isinstance(body_preview, list):
                        body_preview = {"count": len(body_preview), "sample": body_preview[:2]}
                except Exception:
                    pass
                results.append({"check": "api", "url": url_path, "method": method, "http_status": resp.status_code, "expected": expected_status, "status": "pass" if passed else "fail", "response_preview": body_preview})
            except Exception as e:
                results.append({"check": "api", "url": url_path, "status": "fail", "error": str(e)})
        elif check_type == "frontend_route":
            route = check.get("route", "")
            try:
                with open("/app/frontend/src/App.js", "r") as f:
                    app_content = f.read()
                route_exists = f'path="{route}"' in app_content
                results.append({"check": "frontend_route", "route": route, "registered": route_exists, "status": "pass" if route_exists else "fail"})
            except Exception as e:
                results.append({"check": "frontend_route", "route": route, "status": "fail", "error": str(e)})
        elif check_type == "file_exists":
            path = check.get("path", "")
            exists = os.path.isfile(path)
            size = os.path.getsize(path) if exists else 0
            results.append({"check": "file_exists", "path": path, "exists": exists, "size": size, "status": "pass" if exists else "fail"})
    all_passed = all(r.get("status") == "pass" for r in results)
    return {"status": "ok", "all_passed": all_passed, "checks": results, "summary": f"{sum(1 for r in results if r['status']=='pass')}/{len(results)} checks passed"}


# ═══════════════════════════════════════
# RESEARCH TOOLS
# ═══════════════════════════════════════

async def tool_web_search(args):
    query = args.get("query", "")
    max_results = min(args.get("max_results", 5), 10)
    if not query:
        return {"status": "error", "error": "query is required"}
    try:
        from ddgs import DDGS
        raw_results = list(DDGS().text(query, max_results=max_results))
        results = []
        for r in raw_results:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")[:400],
            })
        return {"status": "ok", "query": query, "results": results, "count": len(results)}
    except Exception as e:
        return {"status": "error", "error": f"Web search failed: {str(e)}"}


async def tool_take_screenshot(args):
    url = args.get("url", "")
    full_page = args.get("full_page", False)
    wait_ms = min(args.get("wait_ms", 2000), 10000)
    if not url:
        return {"status": "error", "error": "url is required"}
    if url.startswith("/"):
        url = f"http://localhost:3000{url}"
    elif not url.startswith("http"):
        url = f"http://localhost:3000/{url}"
    screenshot_id = str(uuid.uuid4())[:8]
    screenshot_path = f"/app/backend/uploads/screenshot_{screenshot_id}.png"
    try:
        proc = await asyncio.create_subprocess_exec(
            "python3", "/app/backend/screenshot_helper.py",
            url, screenshot_path, str(full_page), str(wait_ms),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=20)
        if proc.returncode != 0:
            err = stderr.decode()[-500:] if stderr else "Unknown error"
            return {"status": "error", "error": f"Screenshot failed: {err}"}
        file_size = os.path.getsize(screenshot_path) if os.path.isfile(screenshot_path) else 0
        return {
            "status": "ok",
            "path": screenshot_path,
            "url_captured": url,
            "file_size_kb": round(file_size / 1024, 1),
            "full_page": full_page,
            "note": "Screenshot saved. Use read_file or serve from /uploads/ to view.",
        }
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return {"status": "error", "error": "Screenshot timed out (20s limit). Try a simpler URL or increase wait_ms."}
    except Exception as e:
        return {"status": "error", "error": f"Screenshot error: {str(e)}"}


async def tool_crawl_url(args):
    url = args.get("url", "")
    if not url or not url.startswith("http"):
        return {"status": "error", "error": "Valid HTTP URL required"}
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 Kairos Engine"})
        text = resp.text
        clean = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<[^>]+>', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return {"status": "ok", "url": url, "http_status": resp.status_code, "content": clean[:8000], "full_length": len(clean)}
    except Exception as e:
        return {"status": "error", "error": f"Crawl failed: {str(e)}"}


# ═══════════════════════════════════════
# CONFIG & QUALITY TOOLS
# ═══════════════════════════════════════

async def tool_manage_env(args):
    action = args.get("action", "read")
    env_file = args.get("file", "backend")
    env_path = "/app/backend/.env" if env_file == "backend" else "/app/frontend/.env"

    if action == "read":
        if not os.path.isfile(env_path):
            return {"status": "error", "error": f".env not found: {env_path}"}
        with open(env_path, "r") as f:
            lines = f.readlines()
        vars_list = []
        for line in lines:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key = line.split("=", 1)[0]
                val = line.split("=", 1)[1]
                masked = val[:4] + "..." + val[-4:] if len(val) > 12 else val
                vars_list.append({"key": key, "value_preview": masked, "length": len(val)})
        return {"status": "ok", "file": env_path, "variables": vars_list}

    elif action == "set":
        key = args.get("key", "")
        value = args.get("value", "")
        if not key or not re.match(r'^[A-Z_][A-Z0-9_]*$', key):
            return {"status": "error", "error": "Invalid env key. Must be UPPER_SNAKE_CASE."}
        PROTECTED = {"MONGO_URL", "DB_NAME", "REACT_APP_BACKEND_URL"}
        if key in PROTECTED:
            return {"status": "error", "error": f"Cannot modify protected key: {key}"}
        lines = []
        if os.path.isfile(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break
        if not found:
            lines.append(f"{key}={value}\n")
        with open(env_path, "w") as f:
            f.writelines(lines)
        return {"status": "ok", "file": env_path, "key": key, "action": "updated" if found else "added"}

    elif action == "delete":
        key = args.get("key", "")
        PROTECTED = {"MONGO_URL", "DB_NAME", "REACT_APP_BACKEND_URL", "EMERGENT_LLM_KEY"}
        if key in PROTECTED:
            return {"status": "error", "error": f"Cannot delete protected key: {key}"}
        if os.path.isfile(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
            new_lines = [line for line in lines if not line.strip().startswith(f"{key}=")]
            with open(env_path, "w") as f:
                f.writelines(new_lines)
        return {"status": "ok", "file": env_path, "key": key, "action": "deleted"}
    else:
        return {"status": "error", "error": f"Unknown action: {action}. Use read, set, or delete."}


async def tool_lint_code(args):
    path = args.get("path", "")
    fix = args.get("fix", False)
    if not path:
        return {"status": "error", "error": "path is required"}
    if not re.match(r'^[a-zA-Z0-9/_.\-]+$', path):
        return {"status": "error", "error": "Invalid path characters"}
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".py" or (os.path.isdir(path) and not path.endswith("src")):
            cmd = ["ruff", "check", path]
            if fix:
                cmd.append("--fix")
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd="/app")
            issues = proc.stdout.strip() if proc.stdout.strip() else "No issues found"
            return {"status": "ok", "linter": "ruff", "path": path, "output": issues[:3000], "exit_code": proc.returncode}
        elif ext in [".js", ".jsx", ".ts", ".tsx"] or path.endswith("src"):
            cmd = ["npx", "eslint", path]
            if fix:
                cmd.append("--fix")
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd="/app/frontend")
            issues = proc.stdout.strip() if proc.stdout.strip() else "No issues found"
            return {"status": "ok", "linter": "eslint", "path": path, "output": issues[:3000], "exit_code": proc.returncode}
        else:
            return {"status": "error", "error": f"No linter for extension: {ext}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Linting timed out"}


# ═══════════════════════════════════════
# GIT TOOLS
# ═══════════════════════════════════════

async def tool_git_info(args):
    action = args.get("action", "log")
    try:
        if action == "log":
            proc = subprocess.run(["git", "log", "--oneline", "-20"], capture_output=True, text=True, timeout=10, cwd="/app")
        elif action == "status":
            proc = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=10, cwd="/app")
        elif action == "diff":
            file_path = args.get("file", "")
            git_cmd = ["git", "diff", "HEAD"]
            if file_path:
                git_cmd.extend(["--", file_path])
            else:
                git_cmd.append("--stat")
            proc = subprocess.run(git_cmd, capture_output=True, text=True, timeout=10, cwd="/app")
        else:
            return {"status": "error", "error": f"Unknown git action: {action}"}
        return {"status": "ok", "action": action, "output": proc.stdout[:5000]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ═══════════════════════════════════════
# SUBAGENT & TESTING TOOLS
# ═══════════════════════════════════════

async def tool_call_subagent(args):
    agent_type = args.get("agent_type", "")
    task = args.get("task", "")
    context = args.get("context", "")
    run_tests = args.get("run_tests", False)
    if not agent_type or not task:
        return {"status": "error", "error": "agent_type and task are required"}
    return await call_subagent(agent_type, task, context, run_tests=run_tests)


async def tool_run_test(args):
    test_type = args.get("type", "curl")
    command = args.get("command", "")
    script = args.get("script", "")
    name = args.get("name", "test")
    if test_type == "playwright":
        return await run_playwright_test(script or command, name)
    else:
        return await run_api_test(command, name)


async def tool_run_test_suite_handler(args):
    tests = args.get("tests", [])
    if not tests:
        return {"status": "error", "error": "tests array required. Each: {id, name, type: curl|playwright, command|script}"}
    return await run_test_suite(tests)


async def tool_get_playbook(args):
    service = args.get("service", "").lower()
    if service in VERIFIED_PLAYBOOKS:
        return {"status": "ok", "verified": True, "playbook": VERIFIED_PLAYBOOKS[service]}
    available = list(VERIFIED_PLAYBOOKS.keys())
    return {"status": "not_found", "message": f"No verified playbook for '{service}'. Available: {available}. Use call_subagent(agent_type='integrator') for unverified."}


async def tool_generate_image(args):
    prompt = args.get("prompt", "")
    size = args.get("size", "1024x1024")
    if not prompt:
        return {"status": "error", "error": "prompt is required"}
    return await gen_image(prompt, size)


# ═══════════════════════════════════════
# BATCH OPERATIONS
# ═══════════════════════════════════════

async def tool_batch_operations(args):
    operations = args.get("operations", [])
    if not operations:
        return {"status": "error", "error": "operations array required"}

    async def _do_op(op):
        action = op.get("action", "")
        path = op.get("path", "")
        try:
            action_map = {
                "create": ("create_file", {"path": path, "content": op.get("content", "")}),
                "write": ("write_file", {"path": path, "content": op.get("content", "")}),
                "delete": ("delete_file", {"path": path}),
                "move": ("move_file", {"source": path, "destination": op.get("destination", "")}),
                "patch": ("patch_file", {"path": path, "old_str": op.get("search", ""), "new_str": op.get("replace", "")}),
                "read": ("read_file", {"path": path}),
            }
            if action not in action_map:
                return {"status": "error", "error": f"Unknown action: {action}"}
            tool_name, tool_args = action_map[action]
            handler = TOOL_REGISTRY.get(tool_name)
            if handler:
                return await handler(tool_args)
            return {"status": "error", "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"status": "error", "path": path, "error": str(e)}

    results = await asyncio.gather(*[_do_op(op) for op in operations[:20]])
    succeeded = sum(1 for r in results if r.get("status") == "ok")
    return {
        "status": "ok",
        "total": len(operations),
        "succeeded": succeeded,
        "failed": len(operations) - succeeded,
        "results": [{"action": op.get("action"), "path": op.get("path"), "status": r.get("status"), "error": r.get("error")} for op, r in zip(operations, results)],
    }


# ═══════════════════════════════════════
# COMPOUND TOOLS
# ═══════════════════════════════════════

def _polish_generated_python(code: str) -> str:
    """Fix common LLM code-generation bugs in Python code targeting Motor/MongoDB."""
    original = code
    code = re.sub(r'\.to_list\(\s*\)', '.to_list(500)', code)
    code = re.sub(
        r'\.find\(\{([^}]*)\}\)\s*\.to_list',
        lambda m: f'.find({{{m.group(1)}}}, {{"_id": 0}}).to_list' if '"_id"' not in m.group(0) else m.group(0),
        code
    )
    code = re.sub(
        r'\.find_one\(\{([^}]*)\}\)\s*$',
        lambda m: f'.find_one({{{m.group(1)}}}, {{"_id": 0}})' if '"_id"' not in m.group(0) else m.group(0),
        code,
        flags=re.MULTILINE,
    )
    code = re.sub(
        r'await db\.\w+\.insert_one\((\w+)\)\s*\n(\s*)return \1\s*$',
        lambda m: f'await db.{m.group(0).split("db.")[1].split(".insert")[0]}.insert_one({m.group(1)})\n{m.group(2)}return {{k: v for k, v in {m.group(1)}.items() if k != "_id"}}',
        code,
        flags=re.MULTILINE,
    )
    for match in re.finditer(r'async def (\w+)\(\):\n((?:    .*\n)*)', code):
        fn_name, fn_body = match.group(1), match.group(2)
        if 'body' in fn_body and 'body' not in match.group(0).split('(')[1]:
            code = code.replace(f'async def {fn_name}():', f'async def {fn_name}(body: dict):', 1)
    code = re.sub(
        r'\{k:\s*v\s+for\s+k,\s*v\s+in\s+item\.items\(\)\s+if\s+k\s*!=\s*"_id"\}',
        '{**{("name" if k == "_id" else k): v for k, v in item.items()}}',
        code,
    )
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

    if "to_list() missing 1 required positional argument" in log_output:
        code = re.sub(r'\.to_list\(\s*\)', '.to_list(500)', code)
        fixed = True
    if "name 'body' is not defined" in log_output:
        code = re.sub(r'(async def \w+)\(\)(:.*\n(?:    .*body.*\n))', r'\1(body: dict)\2', code)
        fixed = True
    if "IndentationError" in log_output:
        lines = code.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() and line[0] not in (' ', '\t', '#', '@', 'd', 'f', 'i', 'r', 'a', '"', "'"):
                new_lines.append('    ' + line)
            else:
                new_lines.append(line)
        code = '\n'.join(new_lines)
        fixed = True
    if "SyntaxError" in log_output:
        match = re.search(r'line (\d+)', log_output)
        if match:
            line_num = int(match.group(1))
            lines = code.split('\n')
            if 0 < line_num <= len(lines):
                problem_line = lines[line_num - 1]
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


async def tool_scaffold_module(args):
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
        path_params = re.findall(r'\{(\w+)\}', path)

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

    marker = 'logging.info(f"ERP modules: {len(_erp_modules_loaded)} loaded'
    if marker not in server_content:
        marker = 'logging.info("ERP modules integrated (including 10 advanced modules)")'
    if marker not in server_content:
        marker = 'logging.info("ERP modules will be integrated")'
    if marker in server_content:
        server_content = server_content.replace(marker, f"{registration_code}\n    {marker}")
        with open(server_path, "w") as f:
            f.write(server_content)
    else:
        return {"status": "partial", "path": file_path, "warning": "Could not find server.py marker. Register manually."}

    proc = subprocess.run(["sudo", "supervisorctl", "restart", "backend"], capture_output=True, text=True, timeout=15)
    await asyncio.sleep(3)

    log_proc = subprocess.run(["tail", "-n", "15", "/var/log/supervisor/backend.err.log"], capture_output=True, text=True, timeout=5)
    startup_ok = "Application startup complete" in (log_proc.stdout or "")

    auto_fix_applied = False
    if not startup_ok:
        fix_result = _auto_fix_startup_error(file_path, log_proc.stdout or "")
        if fix_result:
            auto_fix_applied = True
            subprocess.run(["sudo", "supervisorctl", "restart", "backend"], capture_output=True, text=True, timeout=15)
            await asyncio.sleep(3)
            log_proc = subprocess.run(["tail", "-n", "15", "/var/log/supervisor/backend.err.log"], capture_output=True, text=True, timeout=5)
            startup_ok = "Application startup complete" in (log_proc.stdout or "")

    test_result = None
    first_get = next((ep for ep in endpoints if ep.get("method", "GET").upper() == "GET"), None)
    if first_get and startup_ok:
        test_url = f"http://localhost:8001/api{prefix}{first_get.get('path', '')}"
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


async def tool_create_page(args):
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
            ep = api_endpoints[0]
            if ep.startswith("/api/"):
                ep = ep[4:]
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
      {'{loading ? <p className="text-[#4A5B6E]">Loading...</p> : <pre className="text-xs text-[#c8d4e0] bg-[#0D1B2A] p-4 rounded-lg border border-[#1B2D42] overflow-auto">{JSON.stringify(data, null, 2)}</pre>}' if api_endpoints else '<p className="text-[#4A5B6E]">Content goes here</p>'}
    </div>
  );
}}
"""

    with open(file_path, "w") as f:
        f.write(page_code)

    app_path = "/app/frontend/src/App.js"
    with open(app_path, "r") as f:
        app_content = f.read()

    import_line = f"import {page_name} from './pages/{page_name}';"
    if import_line not in app_content:
        import_match = list(re.finditer(r'^import .+ from .+;$', app_content, re.MULTILINE))
        if import_match:
            last_import_end = import_match[-1].end()
            app_content = app_content[:last_import_end] + f"\n{import_line}" + app_content[last_import_end:]

    route_line = f'<Route path="{route_path}" element={{<{page_name} />}} />'
    if route_line not in app_content:
        routes_end = app_content.find("</Routes>")
        if routes_end != -1:
            indent = "              "
            app_content = app_content[:routes_end] + f"{indent}{route_line}\n{indent}" + app_content[routes_end:]

    sidebar_added = False
    if nav_section:
        nav_marker = f"label: '{nav_section}'"
        if nav_marker not in app_content:
            nav_entry = f"        {{ path: '{route_path}', label: '{title}', icon: {icon} }},"
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


# ═══════════════════════════════════════
# KNOWLEDGE BASE
# ═══════════════════════════════════════

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "kairos_knowledge.md")


async def tool_read_knowledge(args):
    """Read the Kairos knowledge repository for architecture info, debugging recipes, and tool docs."""
    section = args.get("section", "")
    if not os.path.isfile(KNOWLEDGE_PATH):
        return {"status": "error", "error": "Knowledge file not found at kairos_knowledge.md"}
    with open(KNOWLEDGE_PATH, "r") as f:
        content = f.read()
    if section:
        # Extract specific section by heading
        import re as _re
        pattern = _re.compile(rf'^##\s+\d+\.\s+{_re.escape(section)}.*?(?=^##\s+\d+\.|\Z)', _re.MULTILINE | _re.DOTALL | _re.IGNORECASE)
        match = pattern.search(content)
        if match:
            return {"status": "ok", "section": section, "content": match.group(0).strip()}
        return {"status": "ok", "section": section, "content": f"Section '{section}' not found. Available sections in knowledge base.", "full_length": len(content)}
    return {"status": "ok", "content": content[:15000], "full_length": len(content)}


async def tool_update_knowledge(args):
    """Append new knowledge to the Kairos knowledge repository."""
    entry = args.get("entry", "")
    if not entry:
        return {"status": "error", "error": "entry text is required"}
    with open(KNOWLEDGE_PATH, "a") as f:
        f.write(f"\n\n## LEARNED — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\n{entry}\n")
    await _audit_file_write(KNOWLEDGE_PATH, f"Knowledge updated: {entry[:100]}", "UPDATE")
    return {"status": "ok", "appended_chars": len(entry)}


# ═══════════════════════════════════════
# TOOL REGISTRY — name → handler mapping
# ═══════════════════════════════════════

TOOL_REGISTRY = {
    # File I/O
    "read_file": tool_read_file,
    "create_file": tool_create_file,
    "write_file": tool_write_file,
    "patch_file": tool_patch_file,
    "insert_lines": tool_insert_lines,
    "delete_lines": tool_delete_lines,
    "delete_file": tool_delete_file,
    "move_file": tool_move_file,
    # Compound
    "scaffold_module": tool_scaffold_module,
    "create_page": tool_create_page,
    # Database
    "run_query": tool_run_query,
    "get_schema": tool_get_schema,
    # Infrastructure
    "restart_service": tool_restart_service,
    "test_api": tool_test_api,
    "check_logs": tool_check_logs,
    "install_package": tool_install_package,
    "run_tests": tool_run_tests,
    # Search & Commands
    "grep_search": tool_grep_search,
    "list_files": tool_list_files,
    "run_command": tool_run_command,
    # Verification
    "verify_deployment": tool_verify_deployment,
    # Research
    "web_search": tool_web_search,
    "take_screenshot": tool_take_screenshot,
    "crawl_url": tool_crawl_url,
    # Config & Quality
    "manage_env": tool_manage_env,
    "lint_code": tool_lint_code,
    # Git
    "git_info": tool_git_info,
    # Subagents & Testing
    "call_subagent": tool_call_subagent,
    "run_test": tool_run_test,
    "run_test_suite": tool_run_test_suite_handler,
    "get_playbook": tool_get_playbook,
    # Batch & Image
    "batch_operations": tool_batch_operations,
    "generate_image": tool_generate_image,
    # Knowledge Base
    "read_knowledge": tool_read_knowledge,
    "update_knowledge": tool_update_knowledge,
}
