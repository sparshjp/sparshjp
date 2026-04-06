"""
Unified AI Engine Tests - Iteration 17
Tests for Kairos AI Engine: unified orchestrator combining BA + DEV + QA brains
Endpoints: sessions, chat, coding/files, coding/read-file, testing/query
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSessionManagement:
    """Tests for session CRUD operations"""
    
    def test_list_sessions_returns_200(self):
        """GET /api/agents/sessions should return 200 with list"""
        response = requests.get(f"{BASE_URL}/api/agents/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ List sessions: {len(data)} sessions found")
    
    def test_create_session_auto_mode(self):
        """POST /api/agents/sessions with auto mode"""
        response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "TEST_Auto_Session"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["agent_type"] == "auto"
        assert data["title"] == "TEST_Auto_Session"
        assert "created_at" in data
        assert "updated_at" in data
        assert "messages" in data
        assert isinstance(data["messages"], list)
        print(f"✅ Created auto session: {data['id']}")
        return data["id"]
    
    def test_create_session_ba_mode(self):
        """POST /api/agents/sessions with ba (business) mode"""
        response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "ba", "title": "TEST_BA_Session"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "ba"
        print(f"✅ Created BA session: {data['id']}")
    
    def test_create_session_dev_mode(self):
        """POST /api/agents/sessions with dev (coding) mode"""
        response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "dev", "title": "TEST_Dev_Session"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "dev"
        print(f"✅ Created Dev session: {data['id']}")
    
    def test_create_session_qa_mode(self):
        """POST /api/agents/sessions with qa (testing) mode"""
        response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "qa", "title": "TEST_QA_Session"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "qa"
        print(f"✅ Created QA session: {data['id']}")
    
    def test_get_session_by_id(self):
        """GET /api/agents/sessions/{id} should return session details"""
        # Create session first
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "TEST_GetById"}
        )
        session_id = create_response.json()["id"]
        
        # Get by ID
        response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["title"] == "TEST_GetById"
        print(f"✅ Get session by ID: {session_id}")
    
    def test_get_nonexistent_session_returns_404(self):
        """GET /api/agents/sessions/{id} with invalid ID returns 404"""
        response = requests.get(f"{BASE_URL}/api/agents/sessions/nonexistent-id-12345")
        assert response.status_code == 404
        print("✅ Nonexistent session returns 404")
    
    def test_delete_session(self):
        """DELETE /api/agents/sessions/{id} should delete session"""
        # Create session
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "TEST_ToDelete"}
        )
        session_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "deleted"
        
        # Verify deleted
        get_response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert get_response.status_code == 404
        print(f"✅ Deleted session: {session_id}")


class TestTestingQueries:
    """Tests for POST /api/agents/testing/query endpoint"""
    
    def test_full_health_check(self):
        """POST /api/agents/testing/query with full_health_check"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "full_health_check"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["query_type"] == "full_health_check"
        results = data["results"]
        
        # Verify expected fields
        assert "tb_balanced" in results
        assert "tb_total" in results
        assert "accounts" in results
        assert "vendors" in results
        assert "customers" in results
        assert "projects" in results
        assert "employees" in results
        assert "timesheets" in results
        assert "transactions" in results
        
        # Verify TB is balanced
        assert results["tb_balanced"] == True
        print(f"✅ Full health check: TB balanced={results['tb_balanced']}, total={results['tb_total']}")
    
    def test_tb_balance_query(self):
        """POST /api/agents/testing/query with tb_balance"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "tb_balance"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "total_debit" in results
        assert "total_credit" in results
        assert "balanced" in results
        assert "accounts" in results
        assert results["balanced"] == True
        assert results["total_debit"] == results["total_credit"]
        print(f"✅ TB Balance: Dr={results['total_debit']}, Cr={results['total_credit']}")
    
    def test_collection_stats_query(self):
        """POST /api/agents/testing/query with collection_stats"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "collection_stats"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Should have collection counts
        assert isinstance(results, dict)
        assert len(results) > 0
        # Verify some expected collections
        assert "chart_of_accounts" in results or "employees" in results
        print(f"✅ Collection stats: {len(results)} collections")
    
    def test_entity_validation_query(self):
        """POST /api/agents/testing/query with entity_validation"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "entity_validation"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "vendors" in results
        assert "customers" in results
        assert results["vendors"] == 10
        assert results["customers"] == 7
        print(f"✅ Entity validation: vendors={results['vendors']}, customers={results['customers']}")
    
    def test_project_health_query(self):
        """POST /api/agents/testing/query with project_health"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "project_health"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "projects" in results
        print(f"✅ Project health: {results['projects']} projects")
    
    def test_invalid_query_type(self):
        """POST /api/agents/testing/query with invalid query_type"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "invalid_query_xyz"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        # Should return error with unknown query message
        assert "error" in results
        print(f"✅ Invalid query returns error: {results['error']}")


class TestCodingFileAPIs:
    """Tests for coding agent file access APIs"""
    
    def test_list_backend_files(self):
        """GET /api/agents/coding/files?directory=/app/backend"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/app/backend")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "files" in data
        assert "count" in data
        assert len(data["files"]) > 0
        
        # Check file structure
        first_file = data["files"][0]
        assert "path" in first_file
        assert "relative" in first_file
        assert "size" in first_file
        
        # Verify Python files are included
        py_files = [f for f in data["files"] if f["path"].endswith(".py")]
        assert len(py_files) > 0
        print(f"✅ Backend files: {data['count']} files, {len(py_files)} Python files")
    
    def test_list_frontend_files(self):
        """GET /api/agents/coding/files?directory=/app/frontend/src"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/app/frontend/src")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert len(data["files"]) > 0
        
        # Verify JS/JSX files are included
        js_files = [f for f in data["files"] if f["path"].endswith((".js", ".jsx"))]
        assert len(js_files) > 0
        print(f"✅ Frontend files: {data['count']} files, {len(js_files)} JS/JSX files")
    
    def test_read_server_file(self):
        """POST /api/agents/coding/read-file with server.py"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/server.py"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "path" in data
        assert "content" in data
        assert "size" in data
        assert data["path"] == "/app/backend/server.py"
        assert len(data["content"]) > 0
        assert "FastAPI" in data["content"]
        print(f"✅ Read server.py: {data['size']} chars")
    
    def test_read_routes_agents_file(self):
        """POST /api/agents/coding/read-file with routes_agents.py"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/routes_agents.py"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "content" in data
        # Verify unified engine prompt is present
        assert "ENGINE_SYSTEM_PROMPT" in data["content"] or "Kairos AI Engine" in data["content"]
        print(f"✅ Read routes_agents.py: {data['size']} chars")
    
    def test_blocked_env_file(self):
        """POST /api/agents/coding/read-file should block .env files"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/.env"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "denied" in data["error"].lower() or "blocked" in data["error"].lower()
        print("✅ .env file access correctly blocked")
    
    def test_blocked_unauthorized_directory(self):
        """GET /api/agents/coding/files should block unauthorized directories"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/etc")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "denied" in data["error"].lower()
        print("✅ Unauthorized directory access correctly blocked")
    
    def test_read_nonexistent_file(self):
        """POST /api/agents/coding/read-file with nonexistent file"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/nonexistent_file_xyz.py"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "not found" in data["error"].lower()
        print("✅ Nonexistent file returns error")


class TestChatEndpoint:
    """Tests for POST /api/agents/chat endpoint (uses Claude API - longer timeout)"""
    
    def test_chat_auto_mode_with_session(self):
        """POST /api/agents/chat with auto mode and session"""
        # Create session first
        session_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "auto", "title": "TEST_Chat_Auto"}
        )
        session_id = session_response.json()["id"]
        
        # Send chat message
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={
                "agent_type": "auto",
                "message": "Run a quick health check on the database",
                "session_id": session_id,
                "context": ""
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "agent_type" in data
        assert "session_id" in data
        assert "timestamp" in data
        assert "tool_calls_executed" in data
        assert "files_modified" in data
        assert "questions" in data
        assert "tool_results" in data
        
        assert data["agent_type"] == "auto"
        assert data["session_id"] == session_id
        assert len(data["response"]) > 0
        print(f"✅ Chat auto mode: response length={len(data['response'])}, tool_calls={data['tool_calls_executed']}")
    
    def test_chat_ba_mode(self):
        """POST /api/agents/chat with ba (business) mode"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={
                "agent_type": "ba",
                "message": "What is the GST rate for IT services in India?",
                "session_id": "",
                "context": ""
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert data["agent_type"] == "ba"
        assert len(data["response"]) > 0
        # BA mode should mention GST
        assert "18" in data["response"] or "GST" in data["response"]
        print(f"✅ Chat BA mode: response length={len(data['response'])}")
    
    def test_chat_qa_mode(self):
        """POST /api/agents/chat with qa (testing) mode"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={
                "agent_type": "qa",
                "message": "Check if the trial balance is balanced",
                "session_id": "",
                "context": ""
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert data["agent_type"] == "qa"
        assert len(data["response"]) > 0
        print(f"✅ Chat QA mode: response length={len(data['response'])}")
    
    def test_chat_missing_message_returns_400(self):
        """POST /api/agents/chat without message should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"agent_type": "auto", "message": "", "session_id": ""}
        )
        assert response.status_code == 400
        print("✅ Empty message correctly returns 400")
    
    def test_chat_with_file_context(self):
        """POST /api/agents/chat with file context attached"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={
                "agent_type": "dev",
                "message": "What does this file do?",
                "session_id": "",
                "context": "File: /app/backend/server.py\n```\nfrom fastapi import FastAPI\napp = FastAPI()\n```"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert data["agent_type"] == "dev"
        assert len(data["response"]) > 0
        print(f"✅ Chat with file context: response length={len(data['response'])}")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_sessions():
    """Cleanup TEST_ prefixed sessions after all tests"""
    yield
    # Cleanup
    sessions_response = requests.get(f"{BASE_URL}/api/agents/sessions")
    if sessions_response.status_code == 200:
        sessions = sessions_response.json()
        for session in sessions:
            if session.get("title", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/agents/sessions/{session['id']}")
        print("✅ Cleaned up test sessions")
