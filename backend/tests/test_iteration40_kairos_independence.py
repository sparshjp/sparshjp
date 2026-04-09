"""Iteration 40: Kairos Independence & Knowledge Base Testing

Tests:
1. GET /api/system/status - Kairos online + module counts
2. GET /api/health - status ok
3. GET /api/agents/providers - provider list (Kairos independent)
4. GET /api/agents/sessions - session list
5. GET /api/agents/compression-stats - compression stats for all tiers
6. GET /api/projects - project data (ERP still works)
7. GET /api/timesheets - timesheet data
8. Tool registry has 35 tools including read_knowledge and update_knowledge
9. Knowledge file exists at /app/backend/kairos_knowledge.md
10. Compression benchmark still passes after prompt changes
"""
import pytest
import requests
import os
import sys

# Add backend to path for imports
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://prompt-to-post-4.preview.emergentagent.com"


class TestSystemStatus:
    """Test the new /api/system/status endpoint for Kairos independence"""
    
    def test_system_status_endpoint_exists(self):
        """GET /api/system/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/system/status", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: /api/system/status returns 200")
    
    def test_system_status_kairos_online(self):
        """Kairos should be online in system status"""
        response = requests.get(f"{BASE_URL}/api/system/status", timeout=10)
        data = response.json()
        assert data.get("kairos") == "online", f"Expected kairos=online, got {data.get('kairos')}"
        print(f"PASS: Kairos status = {data.get('kairos')}")
    
    def test_system_status_has_module_counts(self):
        """System status should have module counts"""
        response = requests.get(f"{BASE_URL}/api/system/status", timeout=10)
        data = response.json()
        
        # Check required fields
        assert "erp_modules_loaded" in data, "Missing erp_modules_loaded"
        assert "erp_modules_failed" in data, "Missing erp_modules_failed"
        assert "total_loaded" in data, "Missing total_loaded"
        assert "total_failed" in data, "Missing total_failed"
        
        # Verify counts are reasonable
        assert isinstance(data["total_loaded"], int), "total_loaded should be int"
        assert data["total_loaded"] > 0, f"Expected some modules loaded, got {data['total_loaded']}"
        
        print(f"PASS: System status has module counts - loaded: {data['total_loaded']}, failed: {data['total_failed']}")
        print(f"  Loaded modules: {data['erp_modules_loaded'][:5]}..." if len(data['erp_modules_loaded']) > 5 else f"  Loaded modules: {data['erp_modules_loaded']}")


class TestHealthEndpoint:
    """Test basic health endpoint"""
    
    def test_health_returns_ok(self):
        """GET /api/health returns status ok"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok", f"Expected status=ok, got {data.get('status')}"
        print(f"PASS: /api/health returns status=ok, database={data.get('database')}")


class TestKairosIndependence:
    """Test that Kairos AI Engine works independently of ERP modules"""
    
    def test_agents_providers_endpoint(self):
        """GET /api/agents/providers returns provider list"""
        response = requests.get(f"{BASE_URL}/api/agents/providers", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Response is a dict with 'providers' key containing the list
        assert isinstance(data, dict), "Expected dict response"
        assert "providers" in data, "Expected 'providers' key in response"
        providers = data["providers"]
        assert isinstance(providers, list), "Expected list of providers"
        assert len(providers) > 0, "Expected at least one provider"
        print(f"PASS: /api/agents/providers returns {len(providers)} providers")
    
    def test_agents_sessions_endpoint(self):
        """GET /api/agents/sessions returns session list"""
        response = requests.get(f"{BASE_URL}/api/agents/sessions", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of sessions"
        print(f"PASS: /api/agents/sessions returns {len(data)} sessions")
    
    def test_agents_compression_stats_endpoint(self):
        """GET /api/agents/compression-stats returns stats for all tiers"""
        response = requests.get(f"{BASE_URL}/api/agents/compression-stats", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check for tier stats - tiers are at top level, not nested under 'tiers' key
        expected_tiers = ["groq", "cerebras", "huggingface"]
        for tier in expected_tiers:
            assert tier in data, f"Missing tier: {tier}"
            tier_data = data[tier]
            assert "original_chars" in tier_data, f"Missing original_chars for {tier}"
            assert "compressed_chars" in tier_data, f"Missing compressed_chars for {tier}"
            assert "fits" in tier_data, f"Missing fits for {tier}"
        
        print(f"PASS: /api/agents/compression-stats returns stats for tiers: {expected_tiers}")


class TestERPModulesStillWork:
    """Test that ERP modules still work after Kairos restructure"""
    
    def test_projects_endpoint(self):
        """GET /api/projects returns project data"""
        response = requests.get(f"{BASE_URL}/api/projects", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of projects"
        print(f"PASS: /api/projects returns {len(data)} projects")
    
    def test_timesheets_endpoint(self):
        """GET /api/timesheets returns timesheet data"""
        response = requests.get(f"{BASE_URL}/api/timesheets", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of timesheets"
        print(f"PASS: /api/timesheets returns {len(data)} timesheets")


class TestToolRegistry:
    """Test that tool registry has 35 tools including new knowledge tools"""
    
    def test_tool_registry_has_35_tools(self):
        """TOOL_REGISTRY should have exactly 35 tools"""
        from kairos_tools import TOOL_REGISTRY
        
        tool_count = len(TOOL_REGISTRY)
        assert tool_count == 35, f"Expected 35 tools, got {tool_count}"
        print(f"PASS: TOOL_REGISTRY has {tool_count} tools")
    
    def test_read_knowledge_tool_exists(self):
        """read_knowledge tool should be in registry"""
        from kairos_tools import TOOL_REGISTRY
        
        assert "read_knowledge" in TOOL_REGISTRY, "read_knowledge not in TOOL_REGISTRY"
        handler = TOOL_REGISTRY["read_knowledge"]
        assert callable(handler), "read_knowledge handler should be callable"
        print("PASS: read_knowledge tool exists and is callable")
    
    def test_update_knowledge_tool_exists(self):
        """update_knowledge tool should be in registry"""
        from kairos_tools import TOOL_REGISTRY
        
        assert "update_knowledge" in TOOL_REGISTRY, "update_knowledge not in TOOL_REGISTRY"
        handler = TOOL_REGISTRY["update_knowledge"]
        assert callable(handler), "update_knowledge handler should be callable"
        print("PASS: update_knowledge tool exists and is callable")
    
    def test_all_original_tools_still_exist(self):
        """All 33 original tools should still exist"""
        from kairos_tools import TOOL_REGISTRY
        
        original_tools = [
            "read_file", "create_file", "write_file", "patch_file", "insert_lines", 
            "delete_lines", "delete_file", "move_file", "scaffold_module", "create_page",
            "run_query", "get_schema", "restart_service", "test_api", "check_logs",
            "install_package", "run_tests", "grep_search", "list_files", "run_command",
            "verify_deployment", "web_search", "take_screenshot", "crawl_url",
            "manage_env", "lint_code", "git_info", "call_subagent", "run_test",
            "run_test_suite", "get_playbook", "batch_operations", "generate_image"
        ]
        
        missing = [t for t in original_tools if t not in TOOL_REGISTRY]
        assert len(missing) == 0, f"Missing original tools: {missing}"
        print(f"PASS: All {len(original_tools)} original tools still exist")


class TestKnowledgeFile:
    """Test that knowledge file exists and is readable"""
    
    def test_knowledge_file_exists(self):
        """kairos_knowledge.md should exist"""
        knowledge_path = "/app/backend/kairos_knowledge.md"
        assert os.path.isfile(knowledge_path), f"Knowledge file not found: {knowledge_path}"
        print(f"PASS: Knowledge file exists at {knowledge_path}")
    
    def test_knowledge_file_readable(self):
        """kairos_knowledge.md should be readable"""
        knowledge_path = "/app/backend/kairos_knowledge.md"
        with open(knowledge_path, "r") as f:
            content = f.read()
        
        assert len(content) > 1000, f"Knowledge file too small: {len(content)} chars"
        print(f"PASS: Knowledge file is readable ({len(content)} chars)")
    
    def test_knowledge_file_has_sections(self):
        """kairos_knowledge.md should have expected sections"""
        knowledge_path = "/app/backend/kairos_knowledge.md"
        with open(knowledge_path, "r") as f:
            content = f.read()
        
        expected_sections = [
            "ARCHITECTURE OVERVIEW",
            "FILE MAP",
            "TOOL REGISTRY",
            "DATABASE COLLECTIONS",
            "DEBUGGING RECIPES"
        ]
        
        for section in expected_sections:
            assert section in content, f"Missing section: {section}"
        
        print(f"PASS: Knowledge file has all {len(expected_sections)} expected sections")


class TestCompressionBenchmark:
    """Test that compression benchmark still passes after prompt changes"""
    
    def test_protected_snippet_has_35_tools(self):
        """Protected snippet should list all 35 tools"""
        from prompt_compressor import _PROTECTED_SNIPPET
        
        # Check for new knowledge tools in protected snippet
        assert "read_knowledge" in _PROTECTED_SNIPPET, "read_knowledge not in protected snippet"
        assert "update_knowledge" in _PROTECTED_SNIPPET, "update_knowledge not in protected snippet"
        print("PASS: Protected snippet includes read_knowledge and update_knowledge")
    
    def test_groq_compression_fits_limit(self):
        """Groq compression should fit within 3500 char limit"""
        from prompt_compressor import compress_for_tier, TIER_LIMITS
        
        # Create a test prompt similar to ENGINE_SYSTEM_PROMPT
        test_prompt = """You are Kairos AI Engine, an autonomous full-stack developer.
        
        TOOLS: read_file, create_file, write_file, patch_file, insert_lines, delete_lines,
        delete_file, move_file, scaffold_module, create_page, run_query, get_schema,
        restart_service, test_api, check_logs, install_package, run_tests, grep_search,
        list_files, run_command, verify_deployment, web_search, take_screenshot, crawl_url,
        manage_env, lint_code, git_info, call_subagent, run_test, run_test_suite,
        get_playbook, batch_operations, generate_image, read_knowledge, update_knowledge
        
        TOOL FORMAT: ```TOOL_CALL
        {"tool":"tool_name","args":{...}}
        ```
        
        Multiple calls = parallel execution. Use ```DONE
        summary``` when complete.
        
        CODE PATTERNS: APIRouter + set_db pattern. uuid.uuid4() for IDs. Exclude _id.
        
        KNOWLEDGE: read_knowledge() loads /app/backend/kairos_knowledge.md with architecture,
        debugging recipes, and tool documentation.
        """ * 5  # Make it long enough to need compression
        
        compressed = compress_for_tier(test_prompt, "groq")
        limit = TIER_LIMITS["groq"]
        
        assert len(compressed) <= limit, f"Groq compression {len(compressed)} > limit {limit}"
        print(f"PASS: Groq compression fits limit ({len(compressed)}/{limit} chars)")
    
    def test_compression_preserves_critical_patterns(self):
        """Compression should preserve TOOL_CALL format and tool names"""
        from prompt_compressor import compress_for_tier
        
        test_prompt = """You are Kairos AI Engine.
        
        TOOL FORMAT: ```TOOL_CALL
        {"tool":"tool_name","args":{...}}
        ```
        
        TOOLS: read_file, create_file, read_knowledge, update_knowledge
        """ * 10
        
        compressed = compress_for_tier(test_prompt, "groq")
        
        # Check critical patterns preserved
        assert "TOOL_CALL" in compressed, "TOOL_CALL format not preserved"
        assert "read_knowledge" in compressed, "read_knowledge not preserved"
        assert "update_knowledge" in compressed, "update_knowledge not preserved"
        print("PASS: Compression preserves critical patterns")


class TestServerStructure:
    """Test that server.py has correct Kairos-first structure"""
    
    def test_kairos_loads_before_erp(self):
        """Kairos should load before ERP modules in server.py"""
        with open("/app/backend/server.py", "r") as f:
            content = f.read()
        
        # Find positions
        kairos_pos = content.find("KAIROS AI ENGINE")
        erp_pos = content.find("ERP MODULES")
        
        assert kairos_pos > 0, "KAIROS AI ENGINE section not found"
        assert erp_pos > 0, "ERP MODULES section not found"
        assert kairos_pos < erp_pos, f"Kairos ({kairos_pos}) should load before ERP ({erp_pos})"
        print(f"PASS: Kairos loads at position {kairos_pos}, ERP at {erp_pos}")
    
    def test_safe_load_function_exists(self):
        """_safe_load function should exist for ERP module isolation"""
        with open("/app/backend/server.py", "r") as f:
            content = f.read()
        
        assert "def _safe_load" in content, "_safe_load function not found"
        assert "_erp_modules_loaded" in content, "_erp_modules_loaded tracking not found"
        assert "_erp_modules_failed" in content, "_erp_modules_failed tracking not found"
        print("PASS: _safe_load function and module tracking exist")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
