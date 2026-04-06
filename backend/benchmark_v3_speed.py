#!/usr/bin/env python3
"""Kairos v3 Speed Benchmark — Comparing v2 vs v3 improvements."""
import requests, time, json

API = "https://prompt-to-post-4.preview.emergentagent.com/api"

def run_task(msg, mode="auto"):
    sid = requests.post(f"{API}/agents/sessions", json={"agent_type": mode, "title": msg[:40]}).json()["id"]
    tid = requests.post(f"{API}/agents/chat", json={"agent_type": mode, "message": msg, "session_id": sid}).json().get("task_id", "")
    if not tid: return {"error": "no task_id", "time": 0}
    start = time.time()
    for _ in range(30):
        time.sleep(2)
        r = requests.get(f"{API}/agents/tasks/{tid}")
        if r.status_code == 404: return {"error": "consumed", "time": time.time() - start}
        d = r.json()
        if d.get("status") in ["complete", "error"]:
            return {
                "status": d["status"], "time": round(time.time() - start, 1),
                "iterations": d.get("iterations", 0), "tools": d.get("tool_calls_executed", 0),
                "files_modified": d.get("files_modified", []),
                "steps": d.get("steps", []), "provider": d.get("provider", ""),
                "response": d.get("response", "")[:500],
            }
    return {"error": "timeout", "time": 90}

results = {}

# TEST A: Simple question (fast-path test)
print("TEST A: Simple Question")
r = run_task("What is Nexora's GSTIN?")
print(f"  Time: {r.get('time')}s | Iters: {r.get('iterations')} | Tools: {r.get('tools')} | Provider: {r.get('provider')}")
results["simple_question"] = r

# TEST B: Multi-tool parallel test (search + schema + query in one step)
print("\nTEST B: Multi-tool parallel")
r = run_task("I need three things at once: (1) search all backend files for 'utilization', (2) get the schema for 'projects' collection, (3) run a full health check. Do all 3 in ONE step.", "dev")
print(f"  Time: {r.get('time')}s | Iters: {r.get('iterations')} | Tools: {r.get('tools')}")
for s in r.get('steps', []):
    print(f"    Step {s.get('step')}: {s.get('type')} — {len(s.get('tools_used',[]))} tools: {s.get('tools_used', [])}")
results["parallel_tools"] = r

# TEST C: Scaffold module (compound tool test) — create a new module
print("\nTEST C: Scaffold Module (compound tool)")
r = run_task("Create a new module called 'expense_tracker' at prefix '/expenses' with two endpoints: GET '' that returns all expenses from the expenses collection, and POST '' that creates a new expense with id, description, amount, category, and created_at fields. Use scaffold_module.", "dev")
print(f"  Time: {r.get('time')}s | Iters: {r.get('iterations')} | Tools: {r.get('tools')}")
print(f"  Files modified: {r.get('files_modified', [])}")
for s in r.get('steps', []):
    print(f"    Step {s.get('step')}: {s.get('type')} — tools: {s.get('tools_used', [])}")
    for tr in s.get('tool_results', []):
        if tr.get('tool') == 'scaffold_module':
            sr = tr.get('result', {})
            print(f"      scaffold result: status={sr.get('status')}, startup_ok={sr.get('startup_ok')}, test={sr.get('test_result')}")
results["scaffold"] = r

# TEST D: Code search + read (parallel batch)
print("\nTEST D: Search + Read parallel batch")
r = run_task("Search backend files for 'revenue' AND read the first 20 lines of routes_revenue.py AND get the schema for revenue_schedule — do ALL 3 simultaneously.", "dev")
print(f"  Time: {r.get('time')}s | Iters: {r.get('iterations')} | Tools: {r.get('tools')}")
for s in r.get('steps', []):
    print(f"    Step {s.get('step')}: {s.get('type')} — tools: {s.get('tools_used', [])}")
results["batch_read"] = r

# TEST E: End-to-end code gen + validation
print("\nTEST E: Full code gen + validation cycle")
r = run_task("Check if /app/backend/routes_expense_tracker.py exists and test the GET /api/expenses endpoint. Report whether the module is working.", "auto")
print(f"  Time: {r.get('time')}s | Iters: {r.get('iterations')} | Tools: {r.get('tools')}")
for s in r.get('steps', []):
    print(f"    Step {s.get('step')}: {s.get('type')} — tools: {s.get('tools_used', [])}")
results["validation"] = r

# Summary
print("\n" + "="*60)
print("V3 SPEED BENCHMARK SUMMARY")
print("="*60)
times = [r.get("time", 0) for r in results.values() if r.get("status") == "complete"]
total_tools = sum(r.get("tools", 0) for r in results.values())
avg = round(sum(times) / len(times), 1) if times else 0
print(f"  Tests completed: {len(times)}/5")
print(f"  Average time: {avg}s")
print(f"  Total tools executed: {total_tools}")
print(f"  V2 avg was 10.8s — V3 target: <7s")

for name, r in results.items():
    print(f"  {name}: {r.get('time',0)}s, {r.get('iterations',0)} iters, {r.get('tools',0)} tools")

with open("/app/backend/benchmark_v3_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to /app/backend/benchmark_v3_results.json")
