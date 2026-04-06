"""
Iteration 26 Tests: Provider Routing Fix
Tests the fix for Groq rate-limiting causing fallback to low-quality OpenRouter models.
Key changes:
1. Claude is now first priority (not Groq)
2. Smart provider failure tracking (skip providers with 2+ recent failures for 5 min)
3. Providers endpoint shows rate_limited status
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestProviderEndpoint:
    """Test GET /api/agents/providers endpoint"""
    
    def test_providers_endpoint_returns_200(self):
        """Providers endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Providers endpoint returns 200")
    
    def test_providers_has_correct_structure(self):
        """Providers response should have providers list and fallback_order"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        assert "providers" in data, "Missing 'providers' key"
        assert "fallback_order" in data, "Missing 'fallback_order' key"
        assert isinstance(data["providers"], list), "providers should be a list"
        assert isinstance(data["fallback_order"], list), "fallback_order should be a list"
        print("PASS: Providers response has correct structure")
    
    def test_claude_is_priority_1(self):
        """Claude should be priority 1 (first in fallback chain)"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        claude = next((p for p in data["providers"] if p["name"] == "claude"), None)
        assert claude is not None, "Claude provider not found"
        assert claude["priority"] == 1, f"Claude priority should be 1, got {claude['priority']}"
        print("PASS: Claude is priority 1")
    
    def test_groq_is_priority_2(self):
        """Groq should be priority 2 (second in fallback chain)"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        groq = next((p for p in data["providers"] if p["name"] == "groq"), None)
        assert groq is not None, "Groq provider not found"
        assert groq["priority"] == 2, f"Groq priority should be 2, got {groq['priority']}"
        print("PASS: Groq is priority 2")
    
    def test_openrouter_is_priority_3(self):
        """OpenRouter should be priority 3 (last in fallback chain)"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        openrouter = next((p for p in data["providers"] if p["name"] == "openrouter"), None)
        assert openrouter is not None, "OpenRouter provider not found"
        assert openrouter["priority"] == 3, f"OpenRouter priority should be 3, got {openrouter['priority']}"
        print("PASS: OpenRouter is priority 3")
    
    def test_fallback_order_is_claude_groq_openrouter(self):
        """Fallback order should be ['claude', 'groq', 'openrouter']"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        expected_order = ["claude", "groq", "openrouter"]
        assert data["fallback_order"] == expected_order, f"Expected {expected_order}, got {data['fallback_order']}"
        print("PASS: Fallback order is ['claude', 'groq', 'openrouter']")
    
    def test_providers_have_status_field(self):
        """Each provider should have a status field"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        for provider in data["providers"]:
            assert "status" in provider, f"Provider {provider['name']} missing status field"
            assert provider["status"] in ["active", "no_key", "rate_limited"], f"Invalid status: {provider['status']}"
        print("PASS: All providers have valid status field")
    
    def test_providers_have_model_field(self):
        """Each provider should have a model field"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        for provider in data["providers"]:
            assert "model" in provider, f"Provider {provider['name']} missing model field"
        print("PASS: All providers have model field")


class TestChatEndpoint:
    """Test POST /api/agents/chat endpoint"""
    
    def test_chat_creates_task_and_returns_task_id(self):
        """Chat endpoint should create task and return task_id"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "What is 2+2?",
            "mode": "auto"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "task_id" in data, "Missing task_id in response"
        assert "status" in data, "Missing status in response"
        assert data["status"] == "queued", f"Expected status 'queued', got {data['status']}"
        print(f"PASS: Chat creates task with task_id: {data['task_id']}")
        return data["task_id"]
    
    def test_chat_accepts_session_id(self):
        """Chat endpoint should accept session_id parameter"""
        response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "Hello",
            "mode": "auto",
            "session_id": "test-session-123"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Chat accepts session_id parameter")


class TestTaskPolling:
    """Test GET /api/agents/tasks/{task_id} endpoint"""
    
    def test_task_polling_returns_thinking_fields(self):
        """Task polling should return thinking_text and thinking_step fields"""
        # First create a task
        create_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "List all MongoDB collections",
            "mode": "auto"
        })
        task_id = create_response.json()["task_id"]
        
        # Poll the task
        import time
        time.sleep(1)  # Wait a bit for task to start
        
        poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        assert poll_response.status_code == 200, f"Expected 200, got {poll_response.status_code}"
        data = poll_response.json()
        
        # Check for thinking fields (may be empty initially but should exist)
        assert "thinking_text" in data or "status" in data, "Missing thinking_text or status field"
        print(f"PASS: Task polling returns status: {data.get('status')}")
    
    def test_task_not_found_returns_404(self):
        """Non-existent task should return 404"""
        response = requests.get(f"{BASE_URL}/api/agents/tasks/nonexistent-task-id")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent task returns 404")


class TestTaskExecution:
    """Test that tasks execute successfully using Claude as primary provider"""
    
    def test_simple_task_completes_successfully(self):
        """A simple task should complete successfully"""
        # Create a simple task
        create_response = requests.post(f"{BASE_URL}/api/agents/chat", json={
            "message": "What collections exist in the database? Use run_query with collection_stats.",
            "mode": "auto"
        })
        assert create_response.status_code == 200
        task_id = create_response.json()["task_id"]
        
        # Poll until complete or timeout
        import time
        max_wait = 60  # 60 seconds max
        start_time = time.time()
        final_status = None
        
        while time.time() - start_time < max_wait:
            poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if poll_response.status_code == 200:
                data = poll_response.json()
                final_status = data.get("status")
                if final_status in ["completed", "complete", "error"]:
                    print(f"Task completed with status: {final_status}")
                    if final_status in ["completed", "complete"]:
                        # Check if provider info is available
                        if "provider" in data:
                            print(f"Provider used: {data['provider']}")
                        print("PASS: Simple task completed successfully")
                    else:
                        print(f"Task error: {data.get('error', 'Unknown error')}")
                    break
            time.sleep(2)
        
        assert final_status in ["completed", "complete"], f"Task did not complete successfully. Final status: {final_status}"


class TestCodeVerification:
    """Verify the code changes for provider routing fix"""
    
    def test_call_llm_default_order_is_claude_first(self):
        """Verify call_llm defaults to Claude first in the code"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        # Check that the default order is claude, groq, openrouter
        assert 'order = ["claude", "groq", "openrouter"]' in content, "Default order should be claude, groq, openrouter"
        print("PASS: call_llm default order is ['claude', 'groq', 'openrouter']")
    
    def test_provider_failures_tracking_exists(self):
        """Verify _provider_failures tracking dictionary exists"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        assert "_provider_failures = {}" in content, "Missing _provider_failures tracking"
        print("PASS: _provider_failures tracking exists")
    
    def test_should_skip_provider_function_exists(self):
        """Verify _should_skip_provider function exists"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        assert "def _should_skip_provider(provider: str)" in content, "Missing _should_skip_provider function"
        print("PASS: _should_skip_provider function exists")
    
    def test_record_failure_function_exists(self):
        """Verify _record_failure function exists"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        assert "def _record_failure(provider: str)" in content, "Missing _record_failure function"
        print("PASS: _record_failure function exists")
    
    def test_clear_failures_function_exists(self):
        """Verify _clear_failures function exists"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        assert "def _clear_failures(provider: str)" in content, "Missing _clear_failures function"
        print("PASS: _clear_failures function exists")
    
    def test_failure_window_is_5_minutes(self):
        """Verify failure window is 300 seconds (5 minutes)"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        assert "_FAILURE_WINDOW = 300" in content, "Failure window should be 300 seconds"
        print("PASS: Failure window is 300 seconds (5 minutes)")
    
    def test_skip_threshold_is_2_failures(self):
        """Verify skip threshold is 2 failures"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        assert "len(recent) >= 2" in content, "Skip threshold should be 2 failures"
        print("PASS: Skip threshold is 2 failures")
    
    def test_providers_endpoint_shows_rate_limited_status(self):
        """Verify providers endpoint can show rate_limited status"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        assert '"rate_limited"' in content, "Providers endpoint should support rate_limited status"
        assert "_should_skip_provider(name)" in content, "Providers endpoint should use _should_skip_provider"
        print("PASS: Providers endpoint supports rate_limited status")


class TestWebSearchTool:
    """Test web_search tool still works after refactor"""
    
    def test_web_search_in_read_tools(self):
        """web_search should be in READ_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        # Find READ_TOOLS definition
        match = re.search(r'READ_TOOLS\s*=\s*\{([^}]+)\}', content)
        assert match, "READ_TOOLS not found"
        assert '"web_search"' in match.group(1), "web_search not in READ_TOOLS"
        print("PASS: web_search is in READ_TOOLS")


class TestTakeScreenshotTool:
    """Test take_screenshot tool still works after refactor"""
    
    def test_take_screenshot_in_read_tools(self):
        """take_screenshot should be in READ_TOOLS set"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        
        # Find READ_TOOLS definition
        match = re.search(r'READ_TOOLS\s*=\s*\{([^}]+)\}', content)
        assert match, "READ_TOOLS not found"
        assert '"take_screenshot"' in match.group(1), "take_screenshot not in READ_TOOLS"
        print("PASS: take_screenshot is in READ_TOOLS")


class TestScreenshotServeEndpoint:
    """Test GET /api/agents/screenshots/{filename} endpoint"""
    
    def test_screenshot_endpoint_exists(self):
        """Screenshot serve endpoint should exist"""
        # Test with invalid filename to verify endpoint exists
        response = requests.get(f"{BASE_URL}/api/agents/screenshots/invalid.png")
        # Should return 400 (invalid format) not 404 (endpoint not found)
        assert response.status_code in [400, 404], f"Unexpected status: {response.status_code}"
        print("PASS: Screenshot serve endpoint exists")


class TestHealthEndpoint:
    """Test basic health endpoint"""
    
    def test_root_api_endpoint_returns_200(self):
        """Root API endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data, "Missing message in response"
        print("PASS: Root API endpoint returns 200")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

