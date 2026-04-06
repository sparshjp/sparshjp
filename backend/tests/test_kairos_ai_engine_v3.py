"""
Kairos AI Engine v3 — Backend API Tests
Tests for: Parallel execution, compound tools (scaffold_module, create_page), 
compressed tool results, auto-restart, v3 branding, leave_management module
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLLMProviders:
    """Test GET /api/agents/providers returns 3 providers with correct structure"""
    
    def test_providers_returns_three_providers(self):
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) == 3
        print("PASS: GET /api/agents/providers returns 3 providers")
    
    def test_providers_have_correct_structure(self):
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        for provider in data["providers"]:
            assert "name" in provider
            assert "model" in provider
            assert "status" in provider
            assert "priority" in provider
        print("PASS: All providers have correct structure (name, model, status, priority)")
    
    def test_groq_is_primary_provider(self):
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        groq = next((p for p in data["providers"] if p["name"] == "groq"), None)
        assert groq is not None
        assert groq["priority"] == 1
        print("PASS: Groq is primary provider with priority 1")
    
    def test_fallback_order_is_correct(self):
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        assert "fallback_order" in data
        assert data["fallback_order"] == ["groq", "openrouter", "claude"]
        print("PASS: Fallback order is groq -> openrouter -> claude")


class TestAsyncChatArchitecture:
    """Test POST /api/agents/chat returns {task_id, status:'queued'}"""
    
    def test_chat_returns_task_id_instantly(self):
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 2+2?", "agent_type": "auto"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "queued"
        print(f"PASS: POST /api/agents/chat returns task_id={data['task_id']}, status=queued")
    
    def test_task_polling_returns_status(self):
        # Start a task
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 2+2?", "agent_type": "auto"}
        )
        task_id = response.json()["task_id"]
        
        # Poll for status
        poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
        assert poll_response.status_code == 200
        data = poll_response.json()
        assert "status" in data
        assert data["status"] in ["queued", "thinking", "executing", "iterating", "complete", "error"]
        print(f"PASS: GET /api/agents/tasks/{task_id} returns status={data['status']}")
    
    def test_task_returns_steps_array(self):
        # Start a task
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "What is 2+2?", "agent_type": "auto"}
        )
        task_id = response.json()["task_id"]
        
        # Wait for completion
        for _ in range(30):
            poll_response = requests.get(f"{BASE_URL}/api/agents/tasks/{task_id}")
            data = poll_response.json()
            if data["status"] in ["complete", "error"]:
                break
            time.sleep(1)
        
        assert "steps" in data or data["status"] == "error"
        print(f"PASS: Task returns steps array (status={data['status']})")
    
    def test_invalid_task_id_returns_404(self):
        response = requests.get(f"{BASE_URL}/api/agents/tasks/invalid-task-id-12345")
        assert response.status_code == 404
        print("PASS: Invalid task_id returns 404")
    
    def test_empty_message_returns_400(self):
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "", "agent_type": "auto"}
        )
        assert response.status_code == 400
        print("PASS: Empty message returns 400")


class TestSessionManagement:
    """Test session CRUD operations"""
    
    def test_create_session(self):
        response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "Test Session v3"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Session v3"
        print(f"PASS: Create session returns id={data['id']}")
        return data["id"]
    
    def test_list_sessions(self):
        response = requests.get(f"{BASE_URL}/api/agents/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: List sessions returns {len(data)} sessions")
    
    def test_get_session_by_id(self):
        # Create a session first
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "Get Test Session"}
        )
        session_id = create_response.json()["id"]
        
        # Get the session
        response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        print(f"PASS: Get session by id returns correct session")
    
    def test_delete_session(self):
        # Create a session first
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "Delete Test Session"}
        )
        session_id = create_response.json()["id"]
        
        # Delete the session
        response = requests.delete(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert get_response.status_code == 404
        print("PASS: Delete session works correctly")
    
    def test_session_not_found_returns_404(self):
        response = requests.get(f"{BASE_URL}/api/agents/sessions/nonexistent-session-id")
        assert response.status_code == 404
        print("PASS: Non-existent session returns 404")


class TestLeaveManagementModule:
    """Test the scaffold_module compound tool output - leave_management module"""
    
    def test_leave_management_list_endpoint(self):
        """GET /api/leave-mgmt returns a list"""
        response = requests.get(f"{BASE_URL}/api/leave-mgmt")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/leave-mgmt returns list with {len(data)} items")
    
    def test_leave_management_create_endpoint(self):
        """POST /api/leave-mgmt creates a new leave request with auto-generated fields"""
        leave_request = {
            "employee_id": "EMP-001",
            "employee_name": "Test Employee",
            "leave_type": "Annual",
            "start_date": "2026-02-01",
            "end_date": "2026-02-05",
            "reason": "Vacation"
        }
        response = requests.post(
            f"{BASE_URL}/api/leave-mgmt",
            json=leave_request
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify auto-generated fields
        assert "id" in data, "Missing auto-generated id"
        assert "status" in data, "Missing auto-generated status"
        assert data["status"] == "pending", f"Expected status 'pending', got '{data['status']}'"
        assert "created_at" in data, "Missing auto-generated created_at"
        assert "_id" not in data, "MongoDB _id should be excluded"
        
        print(f"PASS: POST /api/leave-mgmt creates leave request with id={data['id']}, status={data['status']}")
        return data["id"]
    
    def test_leave_management_persistence(self):
        """Verify created leave request persists in database"""
        # Create a leave request
        leave_request = {
            "employee_id": "EMP-002",
            "employee_name": "Persistence Test",
            "leave_type": "Sick",
            "start_date": "2026-03-01",
            "end_date": "2026-03-02",
            "reason": "Medical appointment"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/leave-mgmt",
            json=leave_request
        )
        created_id = create_response.json()["id"]
        
        # Fetch all and verify it exists
        list_response = requests.get(f"{BASE_URL}/api/leave-mgmt")
        data = list_response.json()
        
        found = any(item.get("id") == created_id for item in data)
        assert found, f"Created leave request {created_id} not found in list"
        print(f"PASS: Leave request {created_id} persists in database")


class TestEmployeeAnalyticsModule:
    """Test employee analytics endpoints created during v2 benchmark"""
    
    def test_utilization_summary_endpoint(self):
        """GET /api/employee-analytics/utilization-summary returns employee utilization data"""
        response = requests.get(f"{BASE_URL}/api/employee-analytics/utilization-summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/employee-analytics/utilization-summary returns {len(data)} employees")
    
    def test_top_performers_endpoint(self):
        """GET /api/employee-analytics/top-performers returns top 5 employees"""
        response = requests.get(f"{BASE_URL}/api/employee-analytics/top-performers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5, f"Expected max 5 top performers, got {len(data)}"
        print(f"PASS: GET /api/employee-analytics/top-performers returns {len(data)} employees")


class TestFileUploadEndpoint:
    """Test file upload endpoint"""
    
    def test_upload_endpoint_exists(self):
        """POST /api/agents/upload accepts files"""
        # Create a simple test file
        files = {'file': ('test.txt', b'Hello World', 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "filename" in data
        assert "type" in data
        print(f"PASS: POST /api/agents/upload works, returned id={data['id']}")


class TestURLCrawlEndpoint:
    """Test URL crawl endpoint"""
    
    def test_crawl_url_missing_url_returns_400(self):
        """POST /api/agents/crawl-url without URL returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={}
        )
        assert response.status_code == 400
        print("PASS: POST /api/agents/crawl-url without URL returns 400")
    
    def test_crawl_url_adds_https_prefix(self):
        """POST /api/agents/crawl-url adds https:// prefix"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "google.com"}
        )
        # May fail due to SSL but should not return 400
        assert response.status_code == 200
        data = response.json()
        # URL should have https:// prefix
        assert data.get("url", "").startswith("https://") or data.get("status") == "error"
        print("PASS: POST /api/agents/crawl-url adds https:// prefix")


class TestCodingEndpoints:
    """Test coding/file access endpoints"""
    
    def test_list_backend_files(self):
        """GET /api/agents/coding/files lists backend files"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/app/backend")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data or "status" in data
        print(f"PASS: GET /api/agents/coding/files returns file list")
    
    def test_read_file(self):
        """POST /api/agents/coding/read-file reads a file"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/server.py"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data or "status" in data
        print("PASS: POST /api/agents/coding/read-file works")
    
    def test_read_file_blocked_path(self):
        """POST /api/agents/coding/read-file blocks .env files"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/.env"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "error"
        assert "blocked" in data.get("error", "").lower() or "denied" in data.get("error", "").lower()
        print("PASS: POST /api/agents/coding/read-file blocks .env files")


class TestTestingEndpoints:
    """Test database query endpoints"""
    
    def test_run_full_health_check(self):
        """POST /api/agents/testing/query with full_health_check"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "full_health_check"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print(f"PASS: full_health_check query works")
    
    def test_run_tb_balance(self):
        """POST /api/agents/testing/query with tb_balance"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "tb_balance"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print("PASS: tb_balance query works")
    
    def test_run_collection_stats(self):
        """POST /api/agents/testing/query with collection_stats"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "collection_stats"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print("PASS: collection_stats query works")


class TestChatModes:
    """Test all 4 chat modes work"""
    
    def test_auto_mode(self):
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Hello", "agent_type": "auto"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
        print("PASS: auto mode works")
    
    def test_ba_mode(self):
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Hello", "agent_type": "ba"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
        print("PASS: ba (Business) mode works")
    
    def test_dev_mode(self):
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Hello", "agent_type": "dev"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
        print("PASS: dev (Coding) mode works")
    
    def test_qa_mode(self):
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"message": "Hello", "agent_type": "qa"}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()
        print("PASS: qa (Testing) mode works")


class TestScaffoldModuleVerification:
    """Verify scaffold_module compound tool created routes_leave_management.py correctly"""
    
    def test_leave_management_file_exists(self):
        """Verify /app/backend/routes_leave_management.py exists via read-file endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/routes_leave_management.py"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok", f"File read failed: {data.get('error')}"
        assert "content" in data
        assert "router = APIRouter" in data["content"]
        print("PASS: routes_leave_management.py exists and has router definition")
    
    def test_leave_management_registered_in_server(self):
        """Verify leave_management is registered by checking the endpoint works"""
        # The fact that GET /api/leave-mgmt works proves it's registered
        response = requests.get(f"{BASE_URL}/api/leave-mgmt")
        assert response.status_code == 200
        # Also verify POST works
        response = requests.post(
            f"{BASE_URL}/api/leave-mgmt",
            json={"employee_id": "TEST-REG", "leave_type": "Test"}
        )
        assert response.status_code == 200
        print("PASS: leave_management is registered in server.py (verified via working endpoints)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
