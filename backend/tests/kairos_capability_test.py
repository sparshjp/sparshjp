"""Kairos AI Engine Capability Test Suite"""
import requests, time, json, sys

API = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/api"

# Login
login = requests.post(f"{API}/auth/login", json={"email": "kairoserp", "password": "¢re@tor@AIengine"})
TOKEN = login.json().get("token", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def run_kairos(message, timeout=60):
    """Send message to Kairos and poll for result."""
    resp = requests.post(f"{API}/agents/chat", json={
        "agent_type": "auto", "message": message, "session_id": f"test-{int(time.time())}",
        "preferred_provider": "auto"
    }, headers=HEADERS)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    task_id = resp.json().get("task_id")
    if not task_id:
        return {"error": "No task_id returned"}
    
    start = time.time()
    while time.time() - start < timeout:
        poll = requests.get(f"{API}/agents/tasks/{task_id}", headers=HEADERS)
        if poll.status_code != 200:
            return {"error": f"Poll failed: {poll.status_code}"}
        data = poll.json()
        if data["status"] in ["complete", "error"]:
            return data
        time.sleep(2)
    return {"error": "Timeout", "last_status": data.get("status"), "progress": data.get("progress")}

# ═══════════════════════════════════════
# TEST SUITE
# ═══════════════════════════════════════
tests = [
    {
        "category": "ERP Domain Knowledge",
        "prompt": "Explain Ind AS 115 revenue recognition for T&M IT projects in 3 sentences. Don't use any tools.",
        "evaluate": lambda r: len(r.get("response", "")) > 50 and ("revenue" in r.get("response", "").lower() or "performance" in r.get("response", "").lower()),
    },
    {
        "category": "Database Query",
        "prompt": "How many projects exist in the database? Use run_query tool to count documents in the 'projects' collection.",
        "evaluate": lambda r: any("run_query" in str(s) for s in r.get("steps", [])) or "project" in r.get("response", "").lower(),
    },
    {
        "category": "Code Reading",  
        "prompt": "Read the file /app/backend/module_events.py and tell me which cross-module triggers exist. List them briefly.",
        "evaluate": lambda r: any("read_file" in str(s) for s in r.get("steps", [])),
    },
    {
        "category": "Code Writing",
        "prompt": "Create a new file /app/backend/tests/test_health.py with a simple pytest test that checks if 1+1 equals 2. Use create_file tool.",
        "evaluate": lambda r: any("create_file" in str(s) or "write_file" in str(s) for s in r.get("steps", [])),
    },
    {
        "category": "Multi-Step Reasoning",
        "prompt": "Check the backend logs for any errors, then read server.py line 1 to 5 and tell me the framework used.",
        "evaluate": lambda r: len(r.get("steps", [])) >= 2,
    },
    {
        "category": "Schema Understanding",
        "prompt": "Use the get_schema tool to show me the schema for the 'billing_invoices' collection.",
        "evaluate": lambda r: any("get_schema" in str(s) or "schema" in str(s) for s in r.get("steps", [])) or "billing" in r.get("response", "").lower(),
    },
]

print("=" * 70)
print("KAIROS AI ENGINE — CAPABILITY TEST REPORT")
print("=" * 70)

results = []
for i, test in enumerate(tests, 1):
    print(f"\n{'─' * 50}")
    print(f"TEST {i}: {test['category']}")
    print(f"Prompt: {test['prompt'][:80]}...")
    
    start = time.time()
    result = run_kairos(test["prompt"], timeout=90)
    elapsed = time.time() - start
    
    passed = False
    provider = result.get("provider", "unknown")
    steps = result.get("steps", [])
    response = result.get("response", result.get("error", ""))[:300]
    
    if "error" not in result:
        passed = test["evaluate"](result)
    
    status = "PASS" if passed else "FAIL"
    print(f"Status: {status} | Provider: {provider} | Steps: {len(steps)} | Time: {elapsed:.1f}s")
    print(f"Response: {response[:200]}")
    
    results.append({
        "test": test["category"],
        "status": status,
        "provider": provider,
        "steps": len(steps),
        "time": round(elapsed, 1),
        "has_response": bool(result.get("response")),
    })

print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
passed_count = sum(1 for r in results if r["status"] == "PASS")
print(f"Passed: {passed_count}/{len(results)}")
for r in results:
    icon = "✓" if r["status"] == "PASS" else "✗"
    print(f"  {icon} {r['test']}: {r['status']} ({r['time']}s, {r['steps']} steps, provider={r['provider']})")

# Save results
with open("/app/test_reports/kairos_capability_test.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to /app/test_reports/kairos_capability_test.json")
