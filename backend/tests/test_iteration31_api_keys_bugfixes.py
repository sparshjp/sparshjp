"""
Iteration 31 Tests: Direct API Key Management + Bug Fixes
Tests for:
1. GET /api/agents/api-keys - returns status of all 4 key providers
2. POST /api/agents/api-keys - set/remove API keys
3. GET /api/agents/providers - shows direct key providers when configured
4. Bug fixes for double /api prefix in frontend pages
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestApiKeysEndpoint:
    """Tests for GET /api/agents/api-keys endpoint"""
    
    def test_get_api_keys_returns_200(self):
        """GET /api/agents/api-keys should return 200"""
        response = requests.get(f"{BASE_URL}/api/agents/api-keys")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/agents/api-keys returns 200")
    
    def test_get_api_keys_returns_all_4_providers(self):
        """GET /api/agents/api-keys should return status for anthropic, openai, groq, openrouter"""
        response = requests.get(f"{BASE_URL}/api/agents/api-keys")
        assert response.status_code == 200
        data = response.json()
        
        # Check all 4 providers are present
        assert "anthropic" in data, "Missing 'anthropic' in response"
        assert "openai" in data, "Missing 'openai' in response"
        assert "groq" in data, "Missing 'groq' in response"
        assert "openrouter" in data, "Missing 'openrouter' in response"
        print("PASS: GET /api/agents/api-keys returns all 4 providers")
    
    def test_get_api_keys_provider_structure(self):
        """Each provider should have 'configured' and 'masked' fields"""
        response = requests.get(f"{BASE_URL}/api/agents/api-keys")
        assert response.status_code == 200
        data = response.json()
        
        for provider in ["anthropic", "openai", "groq", "openrouter"]:
            assert "configured" in data[provider], f"Missing 'configured' in {provider}"
            assert "masked" in data[provider], f"Missing 'masked' in {provider}"
            assert isinstance(data[provider]["configured"], bool), f"'configured' should be bool for {provider}"
        print("PASS: Each provider has 'configured' and 'masked' fields")


class TestSetApiKeyEndpoint:
    """Tests for POST /api/agents/api-keys endpoint"""
    
    def test_set_api_key_returns_200(self):
        """POST /api/agents/api-keys with valid provider should return 200"""
        response = requests.post(
            f"{BASE_URL}/api/agents/api-keys",
            json={"provider": "anthropic", "key": "test-key-1234"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: POST /api/agents/api-keys returns 200")
    
    def test_set_api_key_returns_configured_true(self):
        """POST /api/agents/api-keys with key should return configured=true"""
        response = requests.post(
            f"{BASE_URL}/api/agents/api-keys",
            json={"provider": "anthropic", "key": "test-key-5678"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True, f"Expected configured=true, got {data}"
        assert data.get("provider") == "anthropic"
        print("PASS: POST /api/agents/api-keys returns configured=true when key is set")
    
    def test_remove_api_key_returns_configured_false(self):
        """POST /api/agents/api-keys with empty key should return configured=false"""
        response = requests.post(
            f"{BASE_URL}/api/agents/api-keys",
            json={"provider": "anthropic", "key": ""}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == False, f"Expected configured=false, got {data}"
        print("PASS: POST /api/agents/api-keys returns configured=false when key is empty")
    
    def test_set_api_key_invalid_provider_returns_400(self):
        """POST /api/agents/api-keys with invalid provider should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/agents/api-keys",
            json={"provider": "invalid_provider", "key": "test-key"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: POST /api/agents/api-keys returns 400 for invalid provider")
    
    def test_set_api_key_all_providers(self):
        """POST /api/agents/api-keys should work for all 4 providers"""
        for provider in ["anthropic", "openai", "groq", "openrouter"]:
            response = requests.post(
                f"{BASE_URL}/api/agents/api-keys",
                json={"provider": provider, "key": f"test-key-{provider}"}
            )
            assert response.status_code == 200, f"Failed for provider {provider}: {response.status_code}"
            data = response.json()
            assert data.get("provider") == provider
            assert data.get("configured") == True
        print("PASS: POST /api/agents/api-keys works for all 4 providers")
        
        # Clean up - remove test keys
        for provider in ["anthropic", "openai", "groq", "openrouter"]:
            requests.post(
                f"{BASE_URL}/api/agents/api-keys",
                json={"provider": provider, "key": ""}
            )


class TestProvidersEndpointDirectKeys:
    """Tests for GET /api/agents/providers with direct key support"""
    
    def test_get_providers_returns_200(self):
        """GET /api/agents/providers should return 200"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/agents/providers returns 200")
    
    def test_get_providers_has_direct_keys_field(self):
        """GET /api/agents/providers should include direct_keys status"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        
        assert "direct_keys" in data, "Missing 'direct_keys' in response"
        assert "anthropic" in data["direct_keys"], "Missing 'anthropic' in direct_keys"
        assert "openai" in data["direct_keys"], "Missing 'openai' in direct_keys"
        print("PASS: GET /api/agents/providers includes direct_keys status")
    
    def test_get_providers_shows_direct_provider_when_configured(self):
        """When direct key is set, provider should appear with key_type=direct"""
        # Set a test key
        requests.post(
            f"{BASE_URL}/api/agents/api-keys",
            json={"provider": "anthropic", "key": "test-direct-key-abc"}
        )
        
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        
        # Check direct_keys shows anthropic as configured
        assert data["direct_keys"]["anthropic"] == True, "direct_keys.anthropic should be True"
        
        # Check claude_direct provider is in the list
        providers = data.get("providers", [])
        direct_providers = [p for p in providers if p.get("key_type") == "direct"]
        assert len(direct_providers) > 0, "Should have at least one direct key provider"
        
        claude_direct = next((p for p in providers if p.get("name") == "claude_direct"), None)
        assert claude_direct is not None, "claude_direct provider should be in list"
        assert claude_direct.get("key_type") == "direct"
        print("PASS: GET /api/agents/providers shows direct provider when configured")
        
        # Clean up
        requests.post(
            f"{BASE_URL}/api/agents/api-keys",
            json={"provider": "anthropic", "key": ""}
        )


class TestFinancialStatementsPage:
    """Tests for Financial Statements page - bug fix for double /api prefix"""
    
    def test_financial_statements_balance_sheet_endpoint(self):
        """GET /api/financial-statements/balance-sheet should return 200"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/financial-statements/balance-sheet returns 200")
    
    def test_financial_statements_profit_loss_endpoint(self):
        """GET /api/financial-statements/profit-and-loss should return 200"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/profit-and-loss")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/financial-statements/profit-and-loss returns 200")
    
    def test_financial_statements_trial_balance_endpoint(self):
        """GET /api/financial-statements/trial-balance should return 200"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/trial-balance")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/financial-statements/trial-balance returns 200")


class TestProjectsModulePage:
    """Tests for Projects Module page - bug fix for r.ok checks"""
    
    def test_projects_endpoint(self):
        """GET /api/projects should return 200"""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/projects returns 200")
    
    def test_projects_health_dashboard_endpoint(self):
        """GET /api/projects/health/dashboard should return 200"""
        response = requests.get(f"{BASE_URL}/api/projects/health/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/projects/health/dashboard returns 200")


class TestTimesheetsPage:
    """Tests for Timesheets page - bug fix for r.ok checks"""
    
    def test_timesheets_endpoint(self):
        """GET /api/timesheets should return 200"""
        response = requests.get(f"{BASE_URL}/api/timesheets")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/timesheets returns 200")
    
    def test_timesheets_utilization_endpoint(self):
        """GET /api/timesheets/utilization should return 200"""
        response = requests.get(f"{BASE_URL}/api/timesheets/utilization")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/timesheets/utilization returns 200")
    
    def test_timesheets_consolidation_endpoint(self):
        """GET /api/timesheets/consolidation should return 200"""
        response = requests.get(f"{BASE_URL}/api/timesheets/consolidation")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/timesheets/consolidation returns 200")
    
    def test_timesheets_employees_endpoint(self):
        """GET /api/timesheets/employees should return 200"""
        response = requests.get(f"{BASE_URL}/api/timesheets/employees")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/timesheets/employees returns 200")


class TestRevenueRecognitionPage:
    """Tests for Revenue Recognition page - skipped as endpoint not in scope"""
    
    def test_revenue_recognition_page_exists(self):
        """RevenueRecognition.js page file should exist"""
        import os
        assert os.path.exists("/app/frontend/src/pages/RevenueRecognition.js"), "RevenueRecognition.js should exist"
        print("PASS: RevenueRecognition.js page file exists")


class TestAIEnginePageApiKeysUI:
    """Tests for AI Engine page API Keys button and panel"""
    
    def test_ai_agents_sessions_endpoint(self):
        """GET /api/agents/sessions should return 200"""
        response = requests.get(f"{BASE_URL}/api/agents/sessions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/agents/sessions returns 200")


class TestEngineSystemPromptUpgrade:
    """Tests for upgraded ENGINE_SYSTEM_PROMPT"""
    
    def test_system_prompt_has_reasoning_methodology(self):
        """ENGINE_SYSTEM_PROMPT should include REASONING METHODOLOGY section"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "REASONING METHODOLOGY" in content, "Missing REASONING METHODOLOGY section"
        print("PASS: ENGINE_SYSTEM_PROMPT has REASONING METHODOLOGY section")
    
    def test_system_prompt_has_debugging_discipline(self):
        """ENGINE_SYSTEM_PROMPT should include DEBUGGING DISCIPLINE section"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "DEBUGGING DISCIPLINE" in content, "Missing DEBUGGING DISCIPLINE section"
        print("PASS: ENGINE_SYSTEM_PROMPT has DEBUGGING DISCIPLINE section")
    
    def test_system_prompt_has_token_efficiency(self):
        """ENGINE_SYSTEM_PROMPT should include TOKEN EFFICIENCY section"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "TOKEN EFFICIENCY" in content, "Missing TOKEN EFFICIENCY section"
        print("PASS: ENGINE_SYSTEM_PROMPT has TOKEN EFFICIENCY section")


class TestDirectApiCallFunctions:
    """Tests for _call_claude_direct and _call_gpt_direct functions"""
    
    def test_call_claude_direct_function_exists(self):
        """_call_claude_direct function should exist in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "async def _call_claude_direct" in content, "Missing _call_claude_direct function"
        print("PASS: _call_claude_direct function exists")
    
    def test_call_gpt_direct_function_exists(self):
        """_call_gpt_direct function should exist in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "async def _call_gpt_direct" in content, "Missing _call_gpt_direct function"
        print("PASS: _call_gpt_direct function exists")
    
    def test_call_llm_includes_direct_providers_in_order(self):
        """call_llm should include claude_direct and gpt_direct in provider order"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "claude_direct" in content, "Missing claude_direct in call_llm"
        assert "gpt_direct" in content, "Missing gpt_direct in call_llm"
        print("PASS: call_llm includes direct providers in order")


class TestFrontendApiKeysUI:
    """Tests for frontend API Keys UI components"""
    
    def test_frontend_has_api_keys_button(self):
        """AIAgentsPage.js should have API Keys button"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert 'data-testid="api-keys-btn"' in content, "Missing API Keys button"
        print("PASS: Frontend has API Keys button")
    
    def test_frontend_has_api_keys_panel(self):
        """AIAgentsPage.js should have API Keys panel"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert 'data-testid="api-keys-panel"' in content, "Missing API Keys panel"
        print("PASS: Frontend has API Keys panel")
    
    def test_frontend_has_save_api_key_function(self):
        """AIAgentsPage.js should have saveApiKey function"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "saveApiKey" in content, "Missing saveApiKey function"
        print("PASS: Frontend has saveApiKey function")
    
    def test_frontend_has_remove_api_key_function(self):
        """AIAgentsPage.js should have removeApiKey function"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "removeApiKey" in content, "Missing removeApiKey function"
        print("PASS: Frontend has removeApiKey function")
    
    def test_frontend_has_key_icon_import(self):
        """AIAgentsPage.js should import Key icon"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "Key" in content, "Missing Key icon import"
        print("PASS: Frontend has Key icon import")


class TestFrontendBugFixes:
    """Tests for frontend bug fixes - double /api prefix"""
    
    def test_financial_statements_uses_correct_api_url(self):
        """FinancialStatements.js should use API without double /api prefix"""
        with open("/app/frontend/src/pages/FinancialStatements.js", "r") as f:
            content = f.read()
        # Should use ${API}/financial-statements not ${API}/api/financial-statements
        assert "/api/financial-statements" not in content or "REACT_APP_BACKEND_URL" in content, \
            "FinancialStatements.js may have double /api prefix"
        # Check it uses the correct pattern
        assert "${API}/financial-statements" in content, "Should use ${API}/financial-statements pattern"
        print("PASS: FinancialStatements.js uses correct API URL pattern")
    
    def test_projects_module_has_ok_checks(self):
        """ProjectsModule.js should have r.ok checks for fetch responses"""
        with open("/app/frontend/src/pages/ProjectsModule.js", "r") as f:
            content = f.read()
        assert "r.ok" in content, "ProjectsModule.js should have r.ok checks"
        print("PASS: ProjectsModule.js has r.ok checks")
    
    def test_timesheets_page_has_ok_checks(self):
        """TimesheetsPage.js should have r.ok checks for fetch responses"""
        with open("/app/frontend/src/pages/TimesheetsPage.js", "r") as f:
            content = f.read()
        assert "r.ok" in content, "TimesheetsPage.js should have r.ok checks"
        print("PASS: TimesheetsPage.js has r.ok checks")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
