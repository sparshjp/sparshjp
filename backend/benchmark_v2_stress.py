#!/usr/bin/env python3
"""Kairos v2 vs E1 Benchmark — Comprehensive Stress Test
Runs identical tasks through Kairos AI Engine and records results."""

import requests
import time
import json
import sys

API = "https://prompt-to-post-4.preview.emergentagent.com/api"
RESULTS = []
TIMEOUT_PER_TASK = 90  # seconds

def create_session(title):
    r = requests.post(f"{API}/agents/sessions", json={"agent_type": "auto", "title": title})
    return r.json()["id"]

def run_kairos_task(message, mode="auto", session_id=None):
    """Send a task to Kairos and poll until complete. Returns full result dict."""
    if not session_id:
        session_id = create_session(message[:50])
    
    r = requests.post(f"{API}/agents/chat", json={
        "agent_type": mode,
        "message": message,
        "session_id": session_id,
    })
    task_id = r.json().get("task_id", "")
    if not task_id:
        return {"error": "No task_id returned", "time": 0}
    
    start = time.time()
    while time.time() - start < TIMEOUT_PER_TASK:
        time.sleep(2)
        poll = requests.get(f"{API}/agents/tasks/{task_id}")
        if poll.status_code == 404:
            return {"error": "Task disappeared", "time": time.time() - start}
        data = poll.json()
        if data.get("status") in ["complete", "error"]:
            elapsed = time.time() - start
            return {
                "status": data["status"],
                "response": data.get("response", "")[:2000],
                "iterations": data.get("iterations", 0),
                "tool_calls_executed": data.get("tool_calls_executed", 0),
                "files_modified": data.get("files_modified", []),
                "steps": data.get("steps", []),
                "provider": data.get("provider", ""),
                "time": round(elapsed, 1),
            }
    return {"error": "Timeout", "time": TIMEOUT_PER_TASK}


def benchmark(test_id, category, task, mode="auto"):
    """Run a single benchmark task."""
    print(f"\n{'='*60}")
    print(f"TEST {test_id}: {category}")
    print(f"Task: {task[:100]}...")
    print(f"{'='*60}")
    
    result = run_kairos_task(task, mode)
    
    status = result.get("status", result.get("error", "unknown"))
    iters = result.get("iterations", 0)
    tools = result.get("tool_calls_executed", 0)
    prov = result.get("provider", "N/A")
    elapsed = result.get("time", 0)
    resp_len = len(result.get("response", ""))
    files_mod = result.get("files_modified", [])
    steps = result.get("steps", [])
    
    print(f"  Status: {status} | Provider: {prov}")
    print(f"  Time: {elapsed}s | Iterations: {iters} | Tools: {tools}")
    print(f"  Response length: {resp_len} chars | Files modified: {len(files_mod)}")
    if steps:
        for s in steps:
            print(f"    Step {s.get('step',0)}: {s.get('type','')} — tools: {s.get('tools_used',[])} ")
    
    record = {
        "test_id": test_id,
        "category": category,
        "task": task[:200],
        "mode": mode,
        "kairos_status": status,
        "kairos_provider": prov,
        "kairos_time_sec": elapsed,
        "kairos_iterations": iters,
        "kairos_tools_used": tools,
        "kairos_files_modified": len(files_mod),
        "kairos_response_length": resp_len,
        "kairos_steps": len(steps),
        "kairos_response_preview": result.get("response", "")[:500],
    }
    RESULTS.append(record)
    return result

# ═══════════════════════════════════════════════════════════
# BENCHMARK SUITE
# ═══════════════════════════════════════════════════════════

print("\n" + "█"*60)
print("  KAIROS AI ENGINE v2 — STRESS TEST BENCHMARK")
print("  Testing agentic loop, tools, multi-step execution")
print("█"*60)

# ── TEST 1: INSTANT KNOWLEDGE (no tools needed) ──
benchmark("T1", "Knowledge Retrieval",
    "What is Nexora's GSTIN, total TB balance, and how many employees are billable vs non-billable? Answer precisely with numbers.")

# ── TEST 2: DATABASE QUERY ──
benchmark("T2", "Database Query",
    "Run a full health check on the database and tell me the exact counts for projects, employees, timesheets, vendors, and customers.",
    mode="qa")

# ── TEST 3: CODE READING ──
benchmark("T3", "Code Reading",
    "Read the first 30 lines of /app/backend/routes_projects.py and tell me what endpoints are defined in that file. List them all.",
    mode="dev")

# ── TEST 4: CODE SEARCH (grep) ──
benchmark("T4", "Code Search",
    "Search across all backend files for any function that calculates 'utilization' or 'billable'. Show me where these calculations happen.",
    mode="dev")

# ── TEST 5: MULTI-STEP INVESTIGATION ──
benchmark("T5", "Multi-Step Investigation",
    "I need a full audit: (1) Check the database health, (2) Read routes_revenue.py to understand the revenue recognition endpoints, (3) Test GET /api/revenue/schedule to verify it works. Give me a complete report.",
    mode="auto")

# ── TEST 6: SCHEMA ANALYSIS ──
benchmark("T6", "Schema Analysis",
    "Get the MongoDB schema for 'projects' and 'timesheets' collections and tell me how they relate to each other. What fields link them?",
    mode="dev")

# ── TEST 7: CODE GENERATION (create a new endpoint) ──
benchmark("T7", "Code Generation",
    "Create a new file /app/backend/routes_employee_analytics.py with a FastAPI router that has these endpoints: GET /employee-analytics/utilization-summary (returns each employee's name, total hours, billable hours, utilization percentage from timesheets collection), GET /employee-analytics/top-performers (returns top 5 by utilization). Use the standard pattern: router = APIRouter, set_db function, exclude _id from MongoDB.",
    mode="dev")

# ── TEST 8: BUG DETECTION ──
benchmark("T8", "Bug Detection",
    "Read /app/backend/routes_bank_recon.py and check if there are any potential bugs related to: (1) MongoDB _id serialization issues, (2) Missing error handling, (3) Edge cases in the auto-match algorithm. Report any issues found.",
    mode="dev")

# ── TEST 9: BUSINESS ANALYSIS ──
benchmark("T9", "Business Analysis",
    "Analyze Nexora's project portfolio: Which projects have the highest revenue risk under Ind AS 115? Consider contract type, completion percentage, and contract asset/liability balances. Give specific recommendations.",
    mode="ba")

# ── TEST 10: SELF-VALIDATION (code + test cycle) ──
benchmark("T10", "Self-Validation Cycle",
    "Check if the file /app/backend/routes_employee_analytics.py was created in the previous task. If it exists, read it and test the endpoints GET /api/employee-analytics/utilization-summary and GET /api/employee-analytics/top-performers. If the endpoints fail, diagnose why (check logs, check if the route is registered in server.py). Report your findings.",
    mode="auto")

# ═══════════════════════════════════════════════════════════
# WRITE RESULTS
# ═══════════════════════════════════════════════════════════

output = {
    "benchmark_name": "Kairos AI Engine v2 Stress Test",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    "total_tests": len(RESULTS),
    "results": RESULTS,
    "summary": {
        "completed": sum(1 for r in RESULTS if r["kairos_status"] == "complete"),
        "errored": sum(1 for r in RESULTS if r["kairos_status"] != "complete"),
        "avg_time_sec": round(sum(r["kairos_time_sec"] for r in RESULTS) / max(len(RESULTS), 1), 1),
        "total_tools_used": sum(r["kairos_tools_used"] for r in RESULTS),
        "total_iterations": sum(r["kairos_iterations"] for r in RESULTS),
        "multi_step_tasks": sum(1 for r in RESULTS if r["kairos_iterations"] > 1),
        "files_created": sum(r["kairos_files_modified"] for r in RESULTS),
    }
}

with open("/app/backend/benchmark_v2_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n\n" + "█"*60)
print("  BENCHMARK COMPLETE")
print("█"*60)
print(f"  Tests run: {output['summary']['completed']}/{output['total_tests']}")
print(f"  Avg time: {output['summary']['avg_time_sec']}s")
print(f"  Total tools used: {output['summary']['total_tools_used']}")
print(f"  Total iterations: {output['summary']['total_iterations']}")
print(f"  Multi-step tasks: {output['summary']['multi_step_tasks']}/{output['total_tests']}")
print(f"  Files created/modified: {output['summary']['files_created']}")
print(f"\nResults saved to: /app/backend/benchmark_v2_results.json")
