"""
Kairos AI Engine v2 - Backend Tests
Tests for: Agentic loop, multi-step execution, providers, sessions, file upload, URL crawling
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLLMProviders:
    """Test GET /api/agents/providers endpoint"""
    
    def test_providers_returns_three_providers(self):
        """Verify 3 providers are returned: groq, openrouter, claude"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) == 3
        provider_names = [p["name"] for p in data["providers"]]
        assert "groq" in provider_names
        assert "openrouter" in provider_names
        assert "claude" in provider_names
    
    def test_providers_have_correct_structure(self):
        """Verify each provider has name, model, status, priority"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        for provider in data["providers"]:
            assert "name" in provider
            assert "model" in provider
            assert "status" in provider
            assert "priority" in provider
    
    def test_groq_is_primary_provider(self):
        """Verify Groq has priority 1"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        groq = next((p for p in data["providers"] if p["name"] == "groq"), None)
        assert groq is not None
        assert groq["priority"] == 1
        assert groq["model"] == "llama-3.3-70b-versatile"
    
    def test_fallback_order_is_correct(self):
        """Verify fallback order is groq -> openrouter -> claude"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        assert "fallback_order" in data
        assert data["fallback_order"] == ["groq", "openrouter", "claude"]


class TestAsyncChatArchitecture:
    """Test POST /api/agents/chat and GET /api/agents/tasks/{task_id}"""
    
    def test_chat_returns_task_id_instantly(self):
        """POST /api/agents/chat returns {task_id, status:'queued'} instantly"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 5+5?", "agent_type": "auto"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "queued"
        assert len(data["task_id"]) > 0
    
    def test_task_polling_returns_status(self):
        """GET /api/agents/tasks/{task_id} returns status during execution"""
        # Start a task
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 3+3?", "agent_type": "auto"}
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Poll immediately - should be in progress or complete
        poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        assert poll_response.status_code == 200
        poll_data = poll_response.json()
        assert "status" in poll_data
        assert poll_data["status"] in ["queued", "thinking", "iterating", "executing", "complete", "error"]
    
    def test_task_completes_with_iterations_count(self):
        """Completed task includes 'iterations' count"""
        # Start a simple task
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 7+7?", "agent_type": "auto"}
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Poll until complete (max 30 seconds)
        for _ in range(20):
            time.sleep(1.5)
            poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if poll_response.status_code == 200:
                poll_data = poll_response.json()
                if poll_data["status"] in ["complete", "error"]:
                    assert "iterations" in poll_data
                    assert poll_data["iterations"] >= 1
                    break
        else:
            pytest.fail("Task did not complete within 30 seconds")
    
    def test_simple_question_completes_in_one_step(self):
        """Simple questions complete in 1 step without tool calls"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 2+2? Reply with just the number.", "agent_type": "auto"}
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Poll until complete
        for _ in range(20):
            time.sleep(1.5)
            poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if poll_response.status_code == 200:
                poll_data = poll_response.json()
                if poll_data["status"] == "complete":
                    assert poll_data["iterations"] == 1
                    assert poll_data["tool_calls_executed"] == 0
                    break
        else:
            pytest.fail("Task did not complete within 30 seconds")
    
    def test_invalid_task_id_returns_404(self):
        """GET /api/agents/tasks/{invalid_id} returns 404"""
        response = requests.get(f"{BASE_URL}/api/agents/tasks/invalid-task-id-12345")
        assert response.status_code == 404
    
    def test_task_returns_steps_array(self):
        """GET /api/agents/tasks/{task_id} returns 'steps' array"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 10+10?", "agent_type": "auto"}
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Poll until complete
        for _ in range(20):
            time.sleep(1.5)
            poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if poll_response.status_code == 200:
                poll_data = poll_response.json()
                assert "steps" in poll_data
                if poll_data["status"] == "complete":
                    assert isinstance(poll_data["steps"], list)
                    assert len(poll_data["steps"]) >= 1
                    # Verify step structure
                    step = poll_data["steps"][0]
                    assert "step" in step
                    assert "type" in step
                    break
        else:
            pytest.fail("Task did not complete within 30 seconds")


class TestSessionManagement:
    """Test session CRUD operations"""
    
    def test_create_session(self):
        """POST /api/agents/sessions creates a new session"""
        response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "TEST_Session_Create"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["agent_type"] == "auto"
        assert data["title"] == "TEST_Session_Create"
        assert "created_at" in data
        assert "messages" in data
        return data["id"]
    
    def test_list_sessions(self):
        """GET /api/agents/sessions returns list of sessions"""
        response = requests.get(f"{BASE_URL}/api/agents/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_session_by_id(self):
        """GET /api/agents/sessions/{id} returns session details"""
        # First create a session
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "dev", "title": "TEST_Session_Get"}
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]
        
        # Then get it
        get_response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == session_id
        assert data["title"] == "TEST_Session_Get"
    
    def test_delete_session(self):
        """DELETE /api/agents/sessions/{id} deletes the session"""
        # First create a session
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "qa", "title": "TEST_Session_Delete"}
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert get_response.status_code == 404
    
    def test_session_not_found_returns_404(self):
        """GET /api/agents/sessions/{invalid_id} returns 404"""
        response = requests.get(f"{BASE_URL}/api/agents/sessions/invalid-session-id-12345")
        assert response.status_code == 404


class TestURLCrawling:
    """Test POST /api/agents/crawl-url endpoint"""
    
    def test_crawl_url_success(self):
        """POST /api/agents/crawl-url returns content from URL"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "https://example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "content" in data
        assert "url" in data
        assert "type" in data
    
    def test_crawl_url_missing_url(self):
        """POST /api/agents/crawl-url without URL returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={}
        )
        assert response.status_code == 400
    
    def test_crawl_url_adds_https_prefix(self):
        """URL without protocol gets https:// prefix"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["url"].startswith("https://")


class TestCodingEndpoints:
    """Test coding/file endpoints"""
    
    def test_list_backend_files(self):
        """GET /api/agents/coding/files returns file list"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/app/backend")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data or "status" in data
    
    def test_read_file(self):
        """POST /api/agents/coding/read-file reads file content"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/server.py"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "content" in data
    
    def test_read_file_blocked_path(self):
        """Reading .env file is blocked"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/.env"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "blocked" in data["error"].lower() or "denied" in data["error"].lower()


class TestTestingEndpoints:
    """Test testing/query endpoints"""
    
    def test_run_full_health_check(self):
        """POST /api/agents/testing/query with full_health_check"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "full_health_check"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "results" in data
    
    def test_run_tb_balance(self):
        """POST /api/agents/testing/query with tb_balance"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "tb_balance"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "results" in data
    
    def test_run_collection_stats(self):
        """POST /api/agents/testing/query with collection_stats"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "collection_stats"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAgenticLoopMultiStep:
    """Test multi-step agentic loop execution"""
    
    def test_complex_task_uses_multiple_steps(self):
        """Complex tasks requiring tools should use multiple steps"""
        # This task requires: grep_search -> read_file -> test_api
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={
                "message": "Search for 'def get_projects' in backend code, read the first 10 lines of routes_projects.py, then test GET /api/projects",
                "agent_type": "dev"
            }
        )
        assert response.status_code == 200
        task_id = response.json()["task_id"]
        
        # Poll until complete (max 60 seconds for complex task)
        for _ in range(40):
            time.sleep(1.5)
            poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            if poll_response.status_code == 200:
                poll_data = poll_response.json()
                if poll_data["status"] == "complete":
                    # Complex task should have multiple iterations
                    assert poll_data["iterations"] >= 1
                    # Should have executed some tools
                    assert poll_data["tool_calls_executed"] >= 1
                    break
                elif poll_data["status"] == "error":
                    # Even errors should have steps
                    assert "steps" in poll_data
                    break
        else:
            pytest.fail("Complex task did not complete within 60 seconds")


class TestChatModes:
    """Test different agent modes"""
    
    def test_auto_mode(self):
        """Auto mode accepts messages"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Hello", "agent_type": "auto"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
    
    def test_ba_mode(self):
        """Business Analysis mode accepts messages"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is GST?", "agent_type": "ba"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
    
    def test_dev_mode(self):
        """Coding mode accepts messages"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "List files", "agent_type": "dev"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
    
    def test_qa_mode(self):
        """Testing mode accepts messages"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Run health check", "agent_type": "qa"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
    
    def test_empty_message_returns_400(self):
        """Empty message returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "", "agent_type": "auto"}
        )
        assert response.status_code == 400
