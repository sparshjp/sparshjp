"""Iteration 39: Tool Registry Refactor Testing

Tests that the execute_tool function refactoring from routes_agents.py to kairos_tools.py
works correctly. Validates:
1. All 33 tools are registered in TOOL_REGISTRY
2. API endpoints still work after refactor
3. Compression stats endpoint works
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasicEndpoints:
    """Test basic API health and connectivity."""
    
    def test_health_endpoint(self):
        """Backend health endpoint returns status ok."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        print(f"Health check passed: {data}")
    
    def test_providers_endpoint(self):
        """GET /api/agents/providers returns provider list."""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)
        assert len(data["providers"]) > 0
        print(f"Providers: {[p['name'] for p in data['providers']]}")
    
    def test_api_keys_endpoint(self):
        """GET /api/agents/api-keys returns API key status."""
        response = requests.get(f"{BASE_URL}/api/agents/api-keys")
        assert response.status_code == 200
        data = response.json()
        # Should have keys for groq, cerebras, huggingface, etc.
        assert "groq" in data
        assert "cerebras" in data
        assert "huggingface" in data
        print(f"API keys configured: groq={data['groq']['configured']}, cerebras={data['cerebras']['configured']}, huggingface={data['huggingface']['configured']}")


class TestCompressionStats:
    """Test compression stats endpoint."""
    
    def test_compression_stats_endpoint(self):
        """GET /api/agents/compression-stats returns compression stats for all tiers."""
        response = requests.get(f"{BASE_URL}/api/agents/compression-stats")
        assert response.status_code == 200
        data = response.json()
        
        # Should have stats for groq, cerebras, huggingface
        assert "groq" in data
        assert "cerebras" in data
        assert "huggingface" in data
        
        # Each tier should have compression stats
        for tier in ["groq", "cerebras", "huggingface"]:
            tier_data = data[tier]
            assert "original_chars" in tier_data
            assert "compressed_chars" in tier_data
            assert "ratio" in tier_data
            assert "fits" in tier_data
            assert tier_data["fits"] == True, f"{tier} compression doesn't fit limit"
            print(f"{tier}: {tier_data['compressed_chars']}/{tier_data['target_limit']} chars ({tier_data['ratio']}%)")


class TestSessionManagement:
    """Test session CRUD operations."""
    
    def test_sessions_list(self):
        """GET /api/agents/sessions returns session list."""
        response = requests.get(f"{BASE_URL}/api/agents/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Sessions count: {len(data)}")
    
    def test_create_session(self):
        """POST /api/agents/sessions creates a new session."""
        payload = {
            "agent_type": "auto",
            "title": "TEST_Iteration39_Session"
        }
        response = requests.post(f"{BASE_URL}/api/agents/sessions", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "TEST_Iteration39_Session"
        assert data["agent_type"] == "auto"
        print(f"Created session: {data['id']}")
        
        # Cleanup - delete the test session
        session_id = data["id"]
        delete_response = requests.delete(f"{BASE_URL}/api/agents/sessions/{session_id}")
        assert delete_response.status_code == 200


class TestProjectsAndTimesheets:
    """Test core ERP endpoints."""
    
    def test_projects_endpoint(self):
        """GET /api/projects returns project data."""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Projects count: {len(data)}")
    
    def test_timesheets_endpoint(self):
        """GET /api/timesheets returns timesheet data."""
        response = requests.get(f"{BASE_URL}/api/timesheets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Timesheets count: {len(data)}")


class TestToolRegistry:
    """Test that all 33 tools are registered in kairos_tools.py."""
    
    def test_tool_registry_count(self):
        """Tool registry has all 33 tools registered."""
        import sys
        sys.path.insert(0, '/app/backend')
        from kairos_tools import TOOL_REGISTRY
        
        expected_tools = [
            # File I/O (8)
            "read_file", "create_file", "write_file", "patch_file",
            "insert_lines", "delete_lines", "delete_file", "move_file",
            # Compound (2)
            "scaffold_module", "create_page",
            # Database (2)
            "run_query", "get_schema",
            # Infrastructure (5)
            "restart_service", "test_api", "check_logs", "install_package", "run_tests",
            # Search & Commands (3)
            "grep_search", "list_files", "run_command",
            # Verification (1)
            "verify_deployment",
            # Research (3)
            "web_search", "take_screenshot", "crawl_url",
            # Config & Quality (2)
            "manage_env", "lint_code",
            # Git (1)
            "git_info",
            # Subagents & Testing (4)
            "call_subagent", "run_test", "run_test_suite", "get_playbook",
            # Batch & Image (2)
            "batch_operations", "generate_image",
        ]
        
        # Check all expected tools are registered
        missing_tools = []
        for tool in expected_tools:
            if tool not in TOOL_REGISTRY:
                missing_tools.append(tool)
        
        assert len(missing_tools) == 0, f"Missing tools: {missing_tools}"
        
        # Verify count
        actual_count = len(TOOL_REGISTRY)
        assert actual_count == 33, f"Expected 33 tools, got {actual_count}"
        
        print(f"All {actual_count} tools registered: {list(TOOL_REGISTRY.keys())}")
    
    def test_tool_handlers_are_callable(self):
        """All tool handlers are async callable functions."""
        import sys
        sys.path.insert(0, '/app/backend')
        from kairos_tools import TOOL_REGISTRY
        import asyncio
        
        for tool_name, handler in TOOL_REGISTRY.items():
            assert callable(handler), f"Tool {tool_name} handler is not callable"
            assert asyncio.iscoroutinefunction(handler), f"Tool {tool_name} handler is not async"
        
        print("All tool handlers are async callable")


class TestExecuteToolDispatcher:
    """Test that execute_tool dispatcher works correctly."""
    
    def test_execute_tool_imports_from_kairos_tools(self):
        """routes_agents.py imports TOOL_REGISTRY from kairos_tools."""
        import sys
        sys.path.insert(0, '/app/backend')
        
        # Read routes_agents.py and verify import
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        
        assert 'from kairos_tools import TOOL_REGISTRY' in content, "TOOL_REGISTRY not imported from kairos_tools"
        assert 'configure as configure_tools' in content, "configure function not imported"
        print("routes_agents.py correctly imports from kairos_tools")
    
    def test_execute_tool_uses_registry(self):
        """execute_tool function uses TOOL_REGISTRY for dispatch."""
        with open('/app/backend/routes_agents.py', 'r') as f:
            content = f.read()
        
        # Find execute_tool function
        assert 'async def execute_tool(tool_name, args):' in content
        assert 'TOOL_REGISTRY.get(tool_name)' in content
        print("execute_tool correctly uses TOOL_REGISTRY dispatcher")


class TestDirectAccessEndpoints:
    """Test direct access coding endpoints."""
    
    def test_coding_files_endpoint(self):
        """GET /api/agents/coding/files returns file list."""
        response = requests.get(f"{BASE_URL}/api/agents/coding/files")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "files" in data
        print(f"Files in /app/backend: {len(data['files'])}")
    
    def test_coding_read_file_endpoint(self):
        """POST /api/agents/coding/read-file reads a file."""
        payload = {"path": "/app/backend/server.py", "start_line": 1, "end_line": 10}
        response = requests.post(f"{BASE_URL}/api/agents/coding/read-file", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "content" in data
        print(f"Read server.py: {data['total_lines']} total lines")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
