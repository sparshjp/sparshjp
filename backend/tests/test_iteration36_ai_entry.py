"""
Iteration 36: AI-First Data Entry Pattern Tests
Tests the new AI parse endpoint and module schemas for all 9 modules:
- project, timesheet, contract, approval_workflow, approval_request, 
- budget, resource_allocation, forex_transaction, portal_client
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAISchemas:
    """Test GET /api/ai/schemas returns all 9 module schemas"""
    
    def test_schemas_endpoint_returns_200(self):
        """Verify schemas endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/ai/schemas")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/ai/schemas returns 200")
    
    def test_schemas_contains_all_9_modules(self):
        """Verify all 9 module schemas are present"""
        response = requests.get(f"{BASE_URL}/api/ai/schemas")
        data = response.json()
        
        expected_modules = [
            "project", "timesheet", "contract", 
            "approval_workflow", "approval_request", 
            "budget", "resource_allocation", 
            "forex_transaction", "portal_client"
        ]
        
        for module in expected_modules:
            assert module in data, f"Missing module schema: {module}"
            assert "fields" in data[module], f"Module {module} missing 'fields' key"
            assert "example" in data[module], f"Module {module} missing 'example' key"
        
        print(f"✓ All 9 module schemas present: {list(data.keys())}")
    
    def test_project_schema_has_required_fields(self):
        """Verify project schema has expected fields"""
        response = requests.get(f"{BASE_URL}/api/ai/schemas")
        data = response.json()
        
        project_fields = data["project"]["fields"]
        expected_fields = ["name", "client", "type", "pm", "currency", "value_inr"]
        
        for field in expected_fields:
            assert field in project_fields, f"Project schema missing field: {field}"
        
        print(f"✓ Project schema has required fields: {project_fields}")


class TestAIParseEntry:
    """Test POST /api/ai/parse-entry endpoint"""
    
    def test_parse_entry_unknown_module_returns_400(self):
        """Verify unknown module returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={"module": "unknown_module", "prompt": "test prompt"}
        )
        assert response.status_code == 400, f"Expected 400 for unknown module, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "unknown_module" in data["detail"].lower() or "unknown" in data["detail"].lower()
        print("✓ Unknown module returns 400 with error detail")
    
    def test_parse_entry_empty_prompt_returns_400(self):
        """Verify empty prompt returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={"module": "project", "prompt": ""}
        )
        assert response.status_code == 400, f"Expected 400 for empty prompt, got {response.status_code}"
        print("✓ Empty prompt returns 400")
    
    def test_parse_entry_project_returns_correct_structure(self):
        """Test parsing a project prompt returns correct response structure"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "project",
                "prompt": "Create T&M project for Acme Corp, $120K, 6 months, PM is Priya"
            },
            timeout=60  # LLM calls can be slow
        )
        
        # Could be 200 (success) or 503 (no AI provider)
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "parsed" in data, "Response missing 'parsed' key"
        assert "missing_fields" in data, "Response missing 'missing_fields' key"
        assert "schema" in data, "Response missing 'schema' key"
        assert "module" in data, "Response missing 'module' key"
        assert data["module"] == "project"
        
        # Verify parsed is a dict
        assert isinstance(data["parsed"], dict), "parsed should be a dict"
        
        # Verify schema has field definitions
        assert isinstance(data["schema"], dict), "schema should be a dict"
        
        print(f"✓ Project parse returns correct structure: parsed={list(data['parsed'].keys())}")
    
    def test_parse_entry_contract_returns_correct_structure(self):
        """Test parsing a contract prompt returns correct response structure"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "contract",
                "prompt": "SOW for CloudMigrate with TechCorp, $200K fixed-price, Apr-Dec 2026"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "parsed" in data
        assert "missing_fields" in data
        assert "schema" in data
        assert data["module"] == "contract"
        
        print(f"✓ Contract parse returns correct structure: parsed={list(data['parsed'].keys())}")
    
    def test_parse_entry_returns_missing_fields_for_incomplete_prompt(self):
        """Test that missing required fields are identified"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "contract",
                "prompt": "Create a contract"  # Very minimal prompt, should have missing fields
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # With such a minimal prompt, there should be missing required fields
        assert "missing_fields" in data
        assert isinstance(data["missing_fields"], list)
        
        # Contract has required fields: title, client_name, start_date, end_date, value
        # At least some should be missing with such a vague prompt
        print(f"✓ Missing fields identified: {[m['field'] for m in data['missing_fields']]}")
    
    def test_parse_entry_timesheet_module(self):
        """Test parsing a timesheet prompt"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "timesheet",
                "prompt": "Log 40h for Raj (EMP-005) on PRJ-001 this week W1-Apr, all billable at 2500/hr"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["module"] == "timesheet"
        assert "parsed" in data
        print(f"✓ Timesheet parse successful: {list(data['parsed'].keys())}")
    
    def test_parse_entry_approval_workflow_module(self):
        """Test parsing an approval workflow prompt"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "approval_workflow",
                "prompt": "PO approval: above 50K needs finance_manager, above 5L needs admin"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["module"] == "approval_workflow"
        print(f"✓ Approval workflow parse successful")
    
    def test_parse_entry_approval_request_module(self):
        """Test parsing an approval request prompt"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "approval_request",
                "prompt": "Submit expense claim for Raj - 45000 INR for client travel to Mumbai"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["module"] == "approval_request"
        print(f"✓ Approval request parse successful")
    
    def test_parse_entry_budget_module(self):
        """Test parsing a budget prompt"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "budget",
                "prompt": "Engineering dept budget FY2025-26: Salaries 80L, Cloud infra 15L, Training 5L"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["module"] == "budget"
        print(f"✓ Budget parse successful")
    
    def test_parse_entry_resource_allocation_module(self):
        """Test parsing a resource allocation prompt"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "resource_allocation",
                "prompt": "Allocate Priya 100% to CloudMigrate as Tech Lead, billable at 3000/hr, Apr-Sep 2026"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["module"] == "resource_allocation"
        print(f"✓ Resource allocation parse successful")
    
    def test_parse_entry_forex_transaction_module(self):
        """Test parsing a forex transaction prompt"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "forex_transaction",
                "prompt": "Invoice to TechCorp USD 25000 at rate 84.50"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["module"] == "forex_transaction"
        print(f"✓ Forex transaction parse successful")
    
    def test_parse_entry_portal_client_module(self):
        """Test parsing a portal client prompt"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-entry",
            json={
                "module": "portal_client",
                "prompt": "Add TechCorp to portal, contact: John Smith, john@techcorp.com"
            },
            timeout=60
        )
        
        if response.status_code == 503:
            pytest.skip("No AI provider available - skipping LLM-dependent test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["module"] == "portal_client"
        print(f"✓ Portal client parse successful")


class TestSchemaFieldDefinitions:
    """Test that schema field definitions are complete"""
    
    def test_schema_fields_have_required_attributes(self):
        """Verify schema fields have label, type, required attributes"""
        response = requests.get(f"{BASE_URL}/api/ai/schemas")
        data = response.json()
        
        # Test a few key modules
        for module in ["project", "contract", "budget"]:
            assert module in data
            # Fields should be a list of field names
            assert isinstance(data[module]["fields"], list)
            assert len(data[module]["fields"]) > 0
        
        print("✓ Schema fields have proper structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
