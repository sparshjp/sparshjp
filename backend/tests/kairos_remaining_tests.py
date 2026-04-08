"""Kairos AI Engine — Remaining Tests (4-6)"""
import requests, time, json, sys

API = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/api"
login = requests.post(f"{API}/auth/login", json={"email": "kairoserp", "password": "¢re@tor@AIengine"})
TOKEN = login.json().get("token", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def run_kairos(message, timeout=90):
    resp = requests.post(f"{API}/agents/chat", json={
        "agent_type": "auto", "message": message, "session_id": f"test-{int(time.time())}",
        "preferred_provider": "auto"
    }, headers=HEADERS)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    task_id = resp.json().get("task_id")
    start = time.time()
    while time.time() - start < timeout:
        poll = requests.get(f"{API}/agents/tasks/{task_id}", headers=HEADERS)
        if poll.status_code != 200:
            time.sleep(3)
            continue
        data = poll.json()
        if data["status"] in ["complete", "error"]:
            return data
        time.sleep(2)
    return {"error": "Timeout"}

tests = [
    ("Code Writing", "Create a file /app/backend/tests/test_health.py with content: import pytest\\ndef test_health():\\n    assert 1+1 == 2"),
    ("Multi-Step Reasoning", "Check the backend logs using check_logs tool, then read /app/backend/server.py lines 1-5 and tell me the web framework."),
    ("Schema Understanding", "Use the get_schema tool for the 'billing_invoices' collection and describe 3 fields."),
]

for i, (cat, prompt) in enumerate(tests, 4):
    print(f"\nTEST {i}: {cat}")
    start = time.time()
    result = run_kairos(prompt)
    elapsed = time.time() - start
    steps = result.get("steps", [])
    provider = result.get("provider", "?")
    response = result.get("response", result.get("error", ""))[:300]
    print(f"  Provider: {provider} | Steps: {len(steps)} | Time: {elapsed:.1f}s")
    print(f"  Response: {response[:250]}")
    tool_names = [s.get("tool","") for s in steps if s.get("tool")]
    print(f"  Tools used: {tool_names}")
    time.sleep(2)  # breathing room between tests
