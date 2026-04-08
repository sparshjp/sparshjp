"""Test upgraded Kairos subagents — v2 capabilities."""
import requests, time, json, sys

API = sys.argv[1]
login = requests.post(f"{API}/auth/login", json={"email": "kairoserp", "password": "¢re@tor@AIengine"})
TOKEN = login.json().get("token", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def run_kairos(message, timeout=90):
    resp = requests.post(f"{API}/agents/chat", json={
        "agent_type": "auto", "message": message, "session_id": f"test-v2-{int(time.time())}",
        "preferred_provider": "auto"
    }, headers=HEADERS)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    task_id = resp.json().get("task_id")
    start = time.time()
    while time.time() - start < timeout:
        poll = requests.get(f"{API}/agents/tasks/{task_id}", headers=HEADERS)
        if poll.status_code != 200:
            time.sleep(3); continue
        data = poll.json()
        if data["status"] in ["complete", "error"]:
            return data
        time.sleep(2)
    return {"error": "Timeout"}

print("=" * 60)
print("KAIROS v2 SUBAGENT CAPABILITY TESTS")
print("=" * 60)

# Test 1: Verified Integration Playbook
print("\n--- TEST 1: get_playbook (Stripe) ---")
r1 = run_kairos("Use get_playbook tool to get the verified integration playbook for Stripe payments.", timeout=60)
steps1 = r1.get("steps", [])
has_playbook = any("get_playbook" in str(s) for s in steps1) or "stripe" in r1.get("response", "").lower()
print(f"  Steps: {len(steps1)} | Has playbook: {has_playbook}")
print(f"  Response: {r1.get('response', r1.get('error',''))[:200]}")
time.sleep(2)

# Test 2: run_test (API test)
print("\n--- TEST 2: run_test (curl health check) ---")
r2 = run_kairos("Use run_test tool with type=curl, name='health_check', command='curl -s http://localhost:8001/api/health' to verify the backend is running.", timeout=60)
steps2 = r2.get("steps", [])
has_run_test = any("run_test" in str(s) for s in steps2)
print(f"  Steps: {len(steps2)} | Used run_test: {has_run_test}")
print(f"  Response: {r2.get('response', r2.get('error',''))[:200]}")
time.sleep(2)

# Test 3: Tester subagent with test generation
print("\n--- TEST 3: Tester subagent (generate test plan) ---")
r3 = run_kairos("Use call_subagent with agent_type='tester' and task='Generate a test plan for the /api/projects endpoint. Include 3 backend curl tests and 1 Playwright browser test.'", timeout=90)
steps3 = r3.get("steps", [])
has_subagent = any("call_subagent" in str(s) for s in steps3)
print(f"  Steps: {len(steps3)} | Used subagent: {has_subagent}")
resp3 = r3.get("response", r3.get("error", ""))
print(f"  Response length: {len(resp3)} chars")
print(f"  Preview: {resp3[:200]}")
time.sleep(2)

# Test 4: Designer subagent
print("\n--- TEST 4: Designer subagent ---")
r4 = run_kairos("Use call_subagent with agent_type='designer' and task='Design a new KPI Dashboard page showing revenue, projects, and team utilization. Provide the JSX skeleton.'", timeout=90)
steps4 = r4.get("steps", [])
has_designer = any("call_subagent" in str(s) for s in steps4)
resp4 = r4.get("response", r4.get("error", ""))
has_jsx = "className" in resp4 or "jsx" in resp4.lower() or "tailwind" in resp4.lower()
print(f"  Steps: {len(steps4)} | Used subagent: {has_designer} | Has JSX: {has_jsx}")
print(f"  Response length: {len(resp4)} chars")
time.sleep(2)

# Test 5: Troubleshooter subagent
print("\n--- TEST 5: Troubleshooter subagent (RCA) ---")
r5 = run_kairos("Use call_subagent with agent_type='troubleshooter' and task='The /api/billing endpoint returns 500 error. The error log shows: TypeError: ObjectId is not JSON serializable. Perform root cause analysis.'", timeout=90)
steps5 = r5.get("steps", [])
resp5 = r5.get("response", r5.get("error", ""))
has_rca = "root" in resp5.lower() or "fix" in resp5.lower() or "_id" in resp5
print(f"  Steps: {len(steps5)} | Has RCA: {has_rca}")
print(f"  Preview: {resp5[:200]}")

# Summary
print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
tests = [
    ("Verified Playbook (get_playbook)", has_playbook),
    ("Direct Test Runner (run_test)", has_run_test),
    ("Testing Agent v3 (tester subagent)", has_subagent and len(resp3) > 200),
    ("Design Agent (designer subagent)", has_designer and has_jsx),
    ("Troubleshoot Agent (RCA)", has_rca),
]
for name, passed in tests:
    print(f"  {'PASS' if passed else 'FAIL'} — {name}")
print(f"\nTotal: {sum(1 for _,p in tests if p)}/{len(tests)} passed")
