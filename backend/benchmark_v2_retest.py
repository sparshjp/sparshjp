#!/usr/bin/env python3
"""Kairos v2 Retest — Focus on previously weak tests (T6, T7, T8)."""
import requests, time, json

API = "https://prompt-to-post-4.preview.emergentagent.com/api"

def run_kairos(msg, mode="auto"):
    sid = requests.post(f"{API}/agents/sessions", json={"agent_type": mode, "title": msg[:40]}).json()["id"]
    tid = requests.post(f"{API}/agents/chat", json={"agent_type": mode, "message": msg, "session_id": sid}).json().get("task_id", "")
    if not tid: return {"error": "no task_id"}
    start = time.time()
    for _ in range(30):
        time.sleep(3)
        r = requests.get(f"{API}/agents/tasks/{tid}")
        if r.status_code == 404: return {"error": "consumed"}
        d = r.json()
        if d.get("status") in ["complete", "error"]:
            return {
                "status": d["status"], "time": round(time.time()-start, 1),
                "iterations": d.get("iterations", 0), "tools": d.get("tool_calls_executed", 0),
                "files_modified": d.get("files_modified", []), "steps": d.get("steps", []),
                "response": d.get("response", "")[:1000], "provider": d.get("provider", ""),
            }
    return {"error": "timeout"}

# T6 Retest: Schema analysis — should use get_schema tool now
print("\n=== T6 RETEST: Schema Analysis ===")
r6 = run_kairos("Use the get_schema tool on 'projects' and 'timesheets' collections, then explain how they relate to each other.", "dev")
print(f"  Status: {r6.get('status')} | Time: {r6.get('time')}s | Iters: {r6.get('iterations')} | Tools: {r6.get('tools')}")
for s in r6.get('steps', []):
    print(f"    Step {s.get('step')}: {s.get('type')} — tools: {s.get('tools_used', [])}")
print(f"  Response (first 300): {r6.get('response','')[:300]}")

# T7 Retest: Code generation with tool execution
print("\n=== T7 RETEST: Code Generation ===")
r7 = run_kairos("Check if /app/backend/routes_employee_analytics.py exists. If yes, read it. If no, create it with a FastAPI router with endpoints: GET /employee-analytics/utilization-summary and GET /employee-analytics/top-performers. After creating or reading, verify by testing GET /api/employee-analytics/utilization-summary.", "dev")
print(f"  Status: {r7.get('status')} | Time: {r7.get('time')}s | Iters: {r7.get('iterations')} | Tools: {r7.get('tools')}")
for s in r7.get('steps', []):
    print(f"    Step {s.get('step')}: {s.get('type')} — tools: {s.get('tools_used', [])} files: {s.get('files_modified', [])}")
print(f"  Response (first 300): {r7.get('response','')[:300]}")

# T8 Retest: Bug detection with read_file
print("\n=== T8 RETEST: Bug Detection ===")
r8 = run_kairos("Read /app/backend/routes_bank_recon.py (lines 1-100 then 100-200) and analyze it for: (1) potential MongoDB _id serialization issues, (2) missing error handling, (3) edge cases in the auto-match algorithm.", "dev")
print(f"  Status: {r8.get('status')} | Time: {r8.get('time')}s | Iters: {r8.get('iterations')} | Tools: {r8.get('tools')}")
for s in r8.get('steps', []):
    print(f"    Step {s.get('step')}: {s.get('type')} — tools: {s.get('tools_used', [])}")
print(f"  Response (first 500): {r8.get('response','')[:500]}")

results = {"T6": r6, "T7": r7, "T8": r8}
with open("/app/backend/benchmark_v2_retest.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("\n=== RETEST COMPLETE ===")
