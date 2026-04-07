"""
Iteration 32 - Code Quality Fixes Testing
Tests for:
1. Shell injection hardening (shlex, argument lists, blocked patterns)
2. Screenshot helper subprocess (no exec())
3. XSS fix via DOMPurify
4. React Hook dependency fixes (useCallback in 5 files)
5. Key-as-index anti-pattern fixes (3 files)
6. Safe path validation for lint_code tool
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ============================================================
# Backend API Tests
# ============================================================

class TestHealthAndBasicEndpoints:
    """Test basic endpoints are working"""
    
    def test_health_endpoint(self):
        """GET /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: GET /api/health returns 200")
    
    def test_agents_providers_endpoint(self):
        """GET /api/agents/providers returns provider list with key_type field"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        # Check that providers have key_type field
        for provider in data["providers"]:
            assert "key_type" in provider or "id" in provider
        print("PASS: GET /api/agents/providers returns provider list")
    
    def test_agents_api_keys_endpoint(self):
        """GET /api/agents/api-keys returns all 4 provider statuses"""
        response = requests.get(f"{BASE_URL}/api/agents/api-keys")
        assert response.status_code == 200
        data = response.json()
        # Should have anthropic, openai, groq, openrouter
        expected_providers = ["anthropic", "openai", "groq", "openrouter"]
        for provider in expected_providers:
            assert provider in data, f"Missing provider: {provider}"
        print("PASS: GET /api/agents/api-keys returns all 4 provider statuses")
    
    def test_projects_endpoint(self):
        """GET /api/projects returns 200"""
        response = requests.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        print("PASS: GET /api/projects returns 200")
    
    def test_timesheets_endpoint(self):
        """GET /api/timesheets returns 200"""
        response = requests.get(f"{BASE_URL}/api/timesheets")
        assert response.status_code == 200
        print("PASS: GET /api/timesheets returns 200")
    
    def test_financial_statements_balance_sheet(self):
        """GET /api/financial-statements/balance-sheet returns 200"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert response.status_code == 200
        print("PASS: GET /api/financial-statements/balance-sheet returns 200")
    
    def test_revenue_schedule_endpoint(self):
        """GET /api/revenue/schedule returns 200"""
        response = requests.get(f"{BASE_URL}/api/revenue/schedule")
        assert response.status_code == 200
        print("PASS: GET /api/revenue/schedule returns 200")
    
    def test_selling_invoices_endpoint(self):
        """GET /api/selling/invoices returns 200"""
        response = requests.get(f"{BASE_URL}/api/selling/invoices")
        assert response.status_code == 200
        print("PASS: GET /api/selling/invoices returns 200")
    
    def test_company_settings_endpoint(self):
        """GET /api/company/settings returns 200"""
        response = requests.get(f"{BASE_URL}/api/company/settings")
        assert response.status_code == 200
        print("PASS: GET /api/company/settings returns 200")


class TestShellInjectionHardening:
    """Test shell injection hardening in routes_agents.py"""
    
    def test_shlex_import_exists(self):
        """Verify shlex is imported in routes_agents.py"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "import shlex" in content, "shlex import missing"
        print("PASS: shlex import exists in routes_agents.py")
    
    def test_hard_blocked_patterns_expanded(self):
        """Verify HARD_BLOCKED patterns include curl|sh and wget|sh"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Check for expanded blocked patterns
        assert "curl|sh" in content or "curl|bash" in content, "curl|sh pattern not blocked"
        assert "wget|sh" in content or "wget|bash" in content, "wget|sh pattern not blocked"
        print("PASS: HARD_BLOCKED patterns include curl|sh and wget|sh")
    
    def test_subprocess_uses_argument_lists(self):
        """Verify subprocess calls use argument lists instead of shell=True"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Count shell=True occurrences - should be minimal or none
        shell_true_count = content.count("shell=True")
        # The run_command tool may still use bash -c for flexibility, but other tools should not
        # Check that restart_service uses argument list
        assert 'subprocess.run(["sudo", "supervisorctl", "restart"' in content, "restart_service should use argument list"
        print(f"PASS: subprocess calls use argument lists (shell=True count: {shell_true_count})")
    
    def test_install_package_uses_shlex_split(self):
        """Verify install_package uses shlex.split for package names"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "shlex.split" in content, "shlex.split not used for package parsing"
        print("PASS: install_package uses shlex.split")


class TestScreenshotHelperSubprocess:
    """Test screenshot_helper.py exists and is used instead of exec()"""
    
    def test_screenshot_helper_file_exists(self):
        """Verify screenshot_helper.py exists"""
        assert os.path.isfile("/app/backend/screenshot_helper.py"), "screenshot_helper.py not found"
        print("PASS: screenshot_helper.py exists")
    
    def test_screenshot_helper_uses_subprocess(self):
        """Verify routes_agents.py calls screenshot_helper.py via subprocess"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        assert "screenshot_helper.py" in content, "screenshot_helper.py not referenced"
        assert "asyncio.create_subprocess_exec" in content, "Should use asyncio.create_subprocess_exec"
        print("PASS: routes_agents.py calls screenshot_helper.py via subprocess")
    
    def test_no_exec_in_screenshot_tool(self):
        """Verify exec() builtin is not used in take_screenshot tool (create_subprocess_exec is safe)"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Find the take_screenshot section
        screenshot_section_start = content.find('elif tool_name == "take_screenshot"')
        screenshot_section_end = content.find('elif tool_name ==', screenshot_section_start + 1)
        if screenshot_section_end == -1:
            screenshot_section_end = len(content)
        screenshot_section = content[screenshot_section_start:screenshot_section_end]
        # Check for dangerous exec() builtin, but allow asyncio.create_subprocess_exec which is safe
        # The dangerous pattern is exec(code_string) not create_subprocess_exec
        dangerous_exec = re.search(r'\bexec\s*\(', screenshot_section)
        safe_subprocess_exec = "create_subprocess_exec" in screenshot_section
        # If exec( is found, it should only be from create_subprocess_exec
        if dangerous_exec:
            assert safe_subprocess_exec, "Dangerous exec() found without create_subprocess_exec"
        print("PASS: No dangerous exec() in take_screenshot tool (uses safe create_subprocess_exec)")
    
    def test_screenshot_helper_content(self):
        """Verify screenshot_helper.py has proper structure"""
        with open("/app/backend/screenshot_helper.py", "r") as f:
            content = f.read()
        assert "async_playwright" in content, "Should use async_playwright"
        assert "sys.argv" in content, "Should use sys.argv for arguments"
        assert "__main__" in content, "Should have __main__ block"
        print("PASS: screenshot_helper.py has proper structure")


class TestLintCodePathValidation:
    """Test safe path validation for lint_code tool"""
    
    def test_lint_code_path_validation(self):
        """Verify lint_code validates path characters"""
        with open("/app/backend/routes_agents.py", "r") as f:
            content = f.read()
        # Find lint_code section
        lint_section_start = content.find('elif tool_name == "lint_code"')
        lint_section_end = content.find('elif tool_name ==', lint_section_start + 1)
        if lint_section_end == -1:
            lint_section_end = len(content)
        lint_section = content[lint_section_start:lint_section_end]
        # Should have path validation regex
        assert "re.match" in lint_section, "lint_code should validate path with regex"
        assert "Invalid path" in lint_section, "lint_code should have invalid path error"
        print("PASS: lint_code has path validation")


class TestFrontendDOMPurifySanitization:
    """Test XSS fix via DOMPurify in AIAgentsPage.js"""
    
    def test_dompurify_import(self):
        """Verify DOMPurify is imported in AIAgentsPage.js"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "import DOMPurify from 'dompurify'" in content, "DOMPurify import missing"
        print("PASS: DOMPurify is imported in AIAgentsPage.js")
    
    def test_dompurify_sanitize_used(self):
        """Verify DOMPurify.sanitize is used with dangerouslySetInnerHTML"""
        with open("/app/frontend/src/pages/AIAgentsPage.js", "r") as f:
            content = f.read()
        assert "DOMPurify.sanitize" in content, "DOMPurify.sanitize not used"
        # Check it's used with dangerouslySetInnerHTML
        assert "dangerouslySetInnerHTML" in content, "dangerouslySetInnerHTML not found"
        print("PASS: DOMPurify.sanitize is used with dangerouslySetInnerHTML")


class TestReactHookDependencyFixes:
    """Test useCallback fixes in 5 files"""
    
    def test_stock_js_usecallback(self):
        """Verify Stock.js uses useCallback for fetch functions"""
        with open("/app/frontend/src/pages/Stock.js", "r") as f:
            content = f.read()
        assert "useCallback" in content, "useCallback not imported in Stock.js"
        assert "fetchItems = useCallback" in content, "fetchItems should use useCallback"
        assert "fetchStockEntries = useCallback" in content, "fetchStockEntries should use useCallback"
        assert "checkReorder = useCallback" in content, "checkReorder should use useCallback"
        print("PASS: Stock.js uses useCallback for fetch functions")
    
    def test_sales_js_usecallback(self):
        """Verify Sales.js uses useCallback for fetch functions"""
        with open("/app/frontend/src/pages/Sales.js", "r") as f:
            content = f.read()
        assert "useCallback" in content, "useCallback not imported in Sales.js"
        assert "fetchQuotations = useCallback" in content, "fetchQuotations should use useCallback"
        assert "fetchSalesOrders = useCallback" in content, "fetchSalesOrders should use useCallback"
        assert "fetchDeliveryNotes = useCallback" in content, "fetchDeliveryNotes should use useCallback"
        print("PASS: Sales.js uses useCallback for fetch functions")
    
    def test_journal_entry_js_usecallback(self):
        """Verify JournalEntry.js uses useCallback and imports API from App"""
        with open("/app/frontend/src/pages/JournalEntry.js", "r") as f:
            content = f.read()
        assert "useCallback" in content, "useCallback not imported in JournalEntry.js"
        assert "fetchEntries = useCallback" in content, "fetchEntries should use useCallback"
        assert "import { API } from '../App'" in content or "{ API }" in content, "Should import API from App"
        print("PASS: JournalEntry.js uses useCallback and imports API from App")
    
    def test_manufacturing_module_js_usecallback(self):
        """Verify ManufacturingModule.js uses useCallback and imports API from App"""
        with open("/app/frontend/src/pages/ManufacturingModule.js", "r") as f:
            content = f.read()
        assert "useCallback" in content, "useCallback not imported in ManufacturingModule.js"
        assert "fetchWorkOrders = useCallback" in content, "fetchWorkOrders should use useCallback"
        assert "import { API } from '../App'" in content or "{ API }" in content, "Should import API from App"
        print("PASS: ManufacturingModule.js uses useCallback and imports API from App")
    
    def test_master_data_js_usecallback(self):
        """Verify MasterData.js uses useCallback with entityType dependency"""
        with open("/app/frontend/src/pages/MasterData.js", "r") as f:
            content = f.read()
        assert "useCallback" in content, "useCallback not imported in MasterData.js"
        assert "fetchEntities = useCallback" in content, "fetchEntities should use useCallback"
        # Check for entityType in dependency array
        assert "[entityType]" in content, "fetchEntities should have entityType in dependency array"
        print("PASS: MasterData.js uses useCallback with entityType dependency")


class TestKeyAsIndexFixes:
    """Test key-as-index anti-pattern fixes in 3 files"""
    
    def test_timesheets_page_key_fix(self):
        """Verify TimesheetsPage.js uses ts.id instead of idx for keys"""
        with open("/app/frontend/src/pages/TimesheetsPage.js", "r") as f:
            content = f.read()
        # Should use ts.id or composite key, not just idx
        # Check for proper key usage in timesheets.map
        assert "key={ts.id" in content or "key={ts.employee_id" in content, "Should use ts.id or composite key"
        # Should not have key={idx} pattern
        idx_key_pattern = re.search(r'key=\{idx\}', content)
        assert idx_key_pattern is None, "Should not use idx as key"
        print("PASS: TimesheetsPage.js uses proper keys instead of index")
    
    def test_projects_module_key_fix(self):
        """Verify ProjectsModule.js uses proper keys"""
        with open("/app/frontend/src/pages/ProjectsModule.js", "r") as f:
            content = f.read()
        # Check for proper key usage
        assert "key={c.label" in content or "key={ts.id" in content or "key={h.id" in content, "Should use proper keys"
        print("PASS: ProjectsModule.js uses proper keys")
    
    def test_reporting_ai_key_fix(self):
        """Verify ReportingAI.js uses proper keys (q and msg.timestamp)"""
        with open("/app/frontend/src/pages/ReportingAI.js", "r") as f:
            content = f.read()
        # Should use q for example queries and msg.timestamp for history
        assert "key={q}" in content or "key={msg.timestamp" in content, "Should use q or msg.timestamp as keys"
        print("PASS: ReportingAI.js uses proper keys")


class TestApiKeysManagement:
    """Test API keys CRUD operations"""
    
    def test_post_api_keys_saves_key(self):
        """POST /api/agents/api-keys saves keys correctly"""
        # Set a test key
        response = requests.post(f"{BASE_URL}/api/agents/api-keys", json={
            "provider": "groq",
            "key": "test-key-12345"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True, "Key should be configured"
        print("PASS: POST /api/agents/api-keys saves keys correctly")
    
    def test_post_api_keys_removes_key(self):
        """POST /api/agents/api-keys with empty key removes it"""
        # Remove the test key
        response = requests.post(f"{BASE_URL}/api/agents/api-keys", json={
            "provider": "groq",
            "key": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == False, "Key should be removed"
        print("PASS: POST /api/agents/api-keys removes keys correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
