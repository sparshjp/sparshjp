"""
AI Agents Module Tests - Iteration 16
Tests for Business Agent, Coding Agent, and Testing Agent APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAgentSessions:
    """Tests for agent session management APIs"""
    
    def test_list_sessions_returns_200(self):
        """GET /api/agents/sessions should return 200"""
        response = requests.get(f"{BASE_URL}/api/agents/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ List sessions: {len(data)} sessions found")
    
    def test_create_session_returns_200(self):
        """POST /api/agents/sessions should create a new session"""
        response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "business", "title": "TEST_Session"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["agent_type"] == "business"
        assert data["title"] == "TEST_Session"
        assert "created_at" in data
        assert "messages" in data
        print(f"✅ Created session: {data['id']}")
        return data["id"]
    
    def test_get_session_by_id(self):
        """GET /api/agents/sessions/{id} should return session details"""
        # First create a session
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "testing", "title": "TEST_GetSession"}
        )
        session_id = create_response.json()["id"]
        
        # Then get it
        response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["agent_type"] == "testing"
        print(f"✅ Get session by ID: {session_id}")
    
    def test_delete_session(self):
        """DELETE /api/agents/sessions/{id} should delete session"""
        # First create a session
        create_response = requests.post(
            f"{BASE_URL}/api/agents/sessions",
            json={"agent_type": "coding", "title": "TEST_DeleteSession"}
        )
        session_id = create_response.json()["id"]
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert get_response.status_code == 404
        print(f"✅ Deleted session: {session_id}")


class TestTestingAgentQueries:
    """Tests for Testing Agent database query APIs"""
    
    def test_full_health_check(self):
        """POST /api/agents/testing/query with full_health_check"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "full_health_check"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "full_health_check"
        results = data["results"]
        
        # Verify expected fields
        assert "tb_balanced" in results
        assert "tb_total" in results
        assert "vendors" in results
        assert "customers" in results
        assert "projects" in results
        assert "employees" in results
        assert "timesheets" in results
        assert "transactions" in results
        
        # Verify TB is balanced
        assert results["tb_balanced"] == True
        print(f"✅ Full health check: TB balanced={results['tb_balanced']}, vendors={results['vendors']}, customers={results['customers']}")
    
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
        assert results["balanced"] == True
        assert results["total_debit"] == results["total_credit"]
        print(f"✅ TB Balance: Dr={results['total_debit']}, Cr={results['total_credit']}, balanced={results['balanced']}")
    
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
        assert "issues" in results
        print(f"✅ Project health: {results['projects']} projects, {len(results['issues'])} issues")
    
    def test_timesheet_integrity_query(self):
        """POST /api/agents/testing/query with timesheet_integrity"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "timesheet_integrity"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "timesheets" in results
        assert "issues" in results
        print(f"✅ Timesheet integrity: {results['timesheets']} timesheets, {len(results['issues'])} issues")
    
    def test_revenue_schedule_query(self):
        """POST /api/agents/testing/query with revenue_schedule"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "revenue_schedule"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "entries" in results
        assert "total_revenue_march" in results
        assert "contract_assets" in results
        assert "contract_liabilities" in results
        print(f"✅ Revenue schedule: {results['entries']} entries, total_rev={results['total_revenue_march']}")
    
    def test_transaction_coverage_query(self):
        """POST /api/agents/testing/query with transaction_coverage"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "transaction_coverage"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "total" in results
        assert "by_module" in results
        assert results["total"] == 140
        print(f"✅ Transaction coverage: {results['total']} transactions, modules={list(results['by_module'].keys())}")
    
    def test_gst_compliance_query(self):
        """POST /api/agents/testing/query with gst_compliance"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "gst_compliance"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "company_gstin" in results
        assert "gstin_format_valid" in results
        print(f"✅ GST compliance: GSTIN={results['company_gstin']}, valid={results['gstin_format_valid']}")
    
    def test_collection_stats_query(self):
        """POST /api/agents/testing/query with collection_stats"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "collection_stats"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "collections" in results
        assert "total_collections" in results
        print(f"✅ Collection stats: {results['total_collections']} collections")
    
    def test_invalid_query_type(self):
        """POST /api/agents/testing/query with invalid query_type"""
        response = requests.post(
            f"{BASE_URL}/api/agents/testing/query",
            json={"query_type": "invalid_query"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        assert "error" in results
        assert "available" in results
        print(f"✅ Invalid query returns available options: {results['available']}")


class TestCodingAgentFileAPIs:
    """Tests for Coding Agent file access APIs"""
    
    def test_list_backend_files(self):
        """GET /api/agents/coding/files?directory=/app/backend"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/app/backend")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check file structure
        first_file = data[0]
        assert "path" in first_file
        assert "relative" in first_file
        assert "size" in first_file
        assert "ext" in first_file
        
        # Verify Python files are included
        py_files = [f for f in data if f["ext"] == ".py"]
        assert len(py_files) > 0
        print(f"✅ Backend files: {len(data)} files, {len(py_files)} Python files")
    
    def test_list_frontend_files(self):
        """GET /api/agents/coding/files?directory=/app/frontend/src"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/app/frontend/src")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify JS/JSX files are included
        js_files = [f for f in data if f["ext"] in [".js", ".jsx"]]
        assert len(js_files) > 0
        print(f"✅ Frontend files: {len(data)} files, {len(js_files)} JS/JSX files")
    
    def test_read_server_file(self):
        """POST /api/agents/coding/read-file with server.py"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/server.py"}
        )
        assert response.status_code == 200
        data = response.json()
        
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
        
        assert "content" in data
        assert "BUSINESS_AGENT_PROMPT" in data["content"]
        assert "CODING_AGENT_PROMPT" in data["content"]
        assert "TESTING_AGENT_PROMPT" in data["content"]
        print(f"✅ Read routes_agents.py: {data['size']} chars, contains all agent prompts")
    
    def test_blocked_env_file(self):
        """POST /api/agents/coding/read-file should block .env files"""
        response = requests.post(
            f"{BASE_URL}/api/agents/coding/read-file",
            json={"path": "/app/backend/.env"}
        )
        assert response.status_code == 403
        print("✅ .env file access correctly blocked")
    
    def test_blocked_directory(self):
        """GET /api/agents/coding/files should block unauthorized directories"""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files?directory=/etc")
        assert response.status_code == 403
        print("✅ Unauthorized directory access correctly blocked")


class TestAgentChat:
    """Tests for agent chat API (uses Claude API - longer timeout)"""
    
    def test_business_agent_chat(self):
        """POST /api/agents/chat with business agent"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={
                "agent_type": "business",
                "message": "What is the GST rate for IT services in India?",
                "session_id": ""
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "agent_type" in data
        assert data["agent_type"] == "business"
        assert len(data["response"]) > 0
        # Business agent should mention GST rate
        assert "18" in data["response"] or "GST" in data["response"]
        print(f"✅ Business agent chat: response length={len(data['response'])}")
    
    def test_testing_agent_chat_with_db_context(self):
        """POST /api/agents/chat with testing agent - should include DB query results"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={
                "agent_type": "testing",
                "message": "Run a quick health check on the database",
                "session_id": ""
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert data["agent_type"] == "testing"
        # Testing agent should include test results
        assert "PASS" in data["response"] or "balanced" in data["response"].lower() or "✅" in data["response"]
        print(f"✅ Testing agent chat with DB context: response length={len(data['response'])}")
    
    def test_chat_missing_message(self):
        """POST /api/agents/chat without message should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"agent_type": "business", "message": ""}
        )
        assert response.status_code == 400
        print("✅ Empty message correctly returns 400")
    
    def test_chat_invalid_agent_type(self):
        """POST /api/agents/chat with invalid agent_type should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/agents/chat",
            json={"agent_type": "invalid", "message": "Hello"}
        )
        assert response.status_code == 400
        print("✅ Invalid agent type correctly returns 400")


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
