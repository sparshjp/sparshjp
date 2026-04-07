"""
Iteration 37: Manual Entry Form Testing
Tests the __manual__ fast-path for POST /api/ai/parse-entry endpoint
Verifies schema returns 'fields' sub-property for array_of_objects types
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestManualEntryFastPath:
    """Test POST /api/ai/parse-entry with prompt='__manual__' for all modules"""
    
    def test_manual_entry_project_returns_schema_with_fields(self):
        """Project module: milestones should have fields sub-property"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "project",
            "prompt": "__manual__"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "schema" in data, "Response should contain 'schema'"
        assert "parsed" in data, "Response should contain 'parsed' (defaults)"
        assert "missing_fields" in data, "Response should contain 'missing_fields'"
        
        # Verify milestones has fields sub-property
        schema = data["schema"]
        assert "milestones" in schema, "Schema should have 'milestones' field"
        assert schema["milestones"]["type"] == "array_of_objects", "milestones should be array_of_objects"
        assert "fields" in schema["milestones"], "milestones should have 'fields' sub-property"
        
        # Verify fields structure
        milestone_fields = schema["milestones"]["fields"]
        assert "name" in milestone_fields, "milestones.fields should have 'name'"
        assert "value" in milestone_fields, "milestones.fields should have 'value'"
        assert "date" in milestone_fields, "milestones.fields should have 'date'"
        print(f"✓ Project milestones fields: {milestone_fields}")
    
    def test_manual_entry_timesheet_returns_schema_with_fields(self):
        """Timesheet module: entries should have fields sub-property"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "timesheet",
            "prompt": "__manual__"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        schema = data["schema"]
        
        # Verify entries has fields sub-property
        assert "entries" in schema, "Schema should have 'entries' field"
        assert schema["entries"]["type"] == "array_of_objects", "entries should be array_of_objects"
        assert "fields" in schema["entries"], "entries should have 'fields' sub-property"
        
        # Verify fields structure
        entries_fields = schema["entries"]["fields"]
        assert "project_id" in entries_fields, "entries.fields should have 'project_id'"
        assert "hours" in entries_fields, "entries.fields should have 'hours'"
        assert "billable" in entries_fields, "entries.fields should have 'billable'"
        print(f"✓ Timesheet entries fields: {entries_fields}")
    
    def test_manual_entry_contract_returns_schema_with_fields(self):
        """Contract module: milestones should have fields sub-property"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "contract",
            "prompt": "__manual__"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        schema = data["schema"]
        
        # Verify milestones has fields sub-property
        assert "milestones" in schema, "Schema should have 'milestones' field"
        assert schema["milestones"]["type"] == "array_of_objects", "milestones should be array_of_objects"
        assert "fields" in schema["milestones"], "milestones should have 'fields' sub-property"
        
        # Verify fields structure
        milestone_fields = schema["milestones"]["fields"]
        assert "name" in milestone_fields, "milestones.fields should have 'name'"
        assert "amount" in milestone_fields, "milestones.fields should have 'amount'"
        assert "due_date" in milestone_fields, "milestones.fields should have 'due_date'"
        print(f"✓ Contract milestones fields: {milestone_fields}")
    
    def test_manual_entry_approval_workflow_returns_schema_with_fields(self):
        """Approval workflow module: steps should have fields sub-property"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "approval_workflow",
            "prompt": "__manual__"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        schema = data["schema"]
        
        # Verify steps has fields sub-property
        assert "steps" in schema, "Schema should have 'steps' field"
        assert schema["steps"]["type"] == "array_of_objects", "steps should be array_of_objects"
        assert "fields" in schema["steps"], "steps should have 'fields' sub-property"
        
        steps_fields = schema["steps"]["fields"]
        assert "role" in steps_fields, "steps.fields should have 'role'"
        assert "label" in steps_fields, "steps.fields should have 'label'"
        print(f"✓ Approval workflow steps fields: {steps_fields}")
    
    def test_manual_entry_budget_returns_schema_with_fields(self):
        """Budget module: line_items should have fields sub-property"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "budget",
            "prompt": "__manual__"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        schema = data["schema"]
        
        # Verify line_items has fields sub-property
        assert "line_items" in schema, "Schema should have 'line_items' field"
        assert schema["line_items"]["type"] == "array_of_objects", "line_items should be array_of_objects"
        assert "fields" in schema["line_items"], "line_items should have 'fields' sub-property"
        
        line_items_fields = schema["line_items"]["fields"]
        assert "category" in line_items_fields, "line_items.fields should have 'category'"
        assert "amount" in line_items_fields, "line_items.fields should have 'amount'"
        print(f"✓ Budget line_items fields: {line_items_fields}")


class TestManualEntryDefaults:
    """Test that __manual__ returns proper defaults for all modules"""
    
    @pytest.mark.parametrize("module", [
        "project", "timesheet", "contract", "approval_workflow", 
        "approval_request", "budget", "resource_allocation", 
        "forex_transaction", "portal_client"
    ])
    def test_manual_entry_returns_defaults_and_missing_fields(self, module):
        """All 9 modules should return defaults and missing_fields"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": module,
            "prompt": "__manual__"
        })
        assert response.status_code == 200, f"Module {module}: Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify structure
        assert "parsed" in data, f"Module {module}: should have 'parsed'"
        assert "schema" in data, f"Module {module}: should have 'schema'"
        assert "missing_fields" in data, f"Module {module}: should have 'missing_fields'"
        assert data["module"] == module, f"Module {module}: should return correct module name"
        
        # Verify defaults are set
        parsed = data["parsed"]
        assert isinstance(parsed, dict), f"Module {module}: parsed should be a dict"
        
        # Verify missing_fields contains required fields
        missing = data["missing_fields"]
        assert isinstance(missing, list), f"Module {module}: missing_fields should be a list"
        
        print(f"✓ Module {module}: {len(parsed)} defaults, {len(missing)} required fields")


class TestManualEntrySchemaStructure:
    """Test schema structure for proper form rendering"""
    
    def test_project_schema_has_all_field_types(self):
        """Project schema should have string, number, enum, array, array_of_objects types"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "project",
            "prompt": "__manual__"
        })
        data = response.json()
        schema = data["schema"]
        
        # Check field types
        assert schema["name"]["type"] == "string", "name should be string"
        assert schema["value_inr"]["type"] == "number", "value_inr should be number"
        assert schema["type"]["type"] == "enum", "type should be enum"
        assert "options" in schema["type"], "enum should have options"
        assert schema["team_names"]["type"] == "array", "team_names should be array"
        assert schema["milestones"]["type"] == "array_of_objects", "milestones should be array_of_objects"
        
        # Check required flags
        assert schema["name"]["required"] == True, "name should be required"
        assert schema["client"]["required"] == True, "client should be required"
        
        print("✓ Project schema has all expected field types")
    
    def test_timesheet_schema_has_date_and_boolean_types(self):
        """Timesheet schema should have date and boolean types"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "timesheet",
            "prompt": "__manual__"
        })
        data = response.json()
        schema = data["schema"]
        
        # Check date type
        assert schema["week_start"]["type"] == "date", "week_start should be date"
        assert schema["week_end"]["type"] == "date", "week_end should be date"
        
        # Check entries has boolean in fields
        entries_fields = schema["entries"]["fields"]
        assert entries_fields["billable"] == "boolean", "entries.billable should be boolean"
        
        print("✓ Timesheet schema has date and boolean types")
    
    def test_contract_schema_has_boolean_type(self):
        """Contract schema should have boolean type for auto_renew"""
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "contract",
            "prompt": "__manual__"
        })
        data = response.json()
        schema = data["schema"]
        
        assert schema["auto_renew"]["type"] == "boolean", "auto_renew should be boolean"
        assert schema["auto_renew"]["default"] == False, "auto_renew default should be False"
        
        print("✓ Contract schema has boolean type")


class TestManualEntryNoLLMCall:
    """Verify __manual__ fast-path doesn't call LLM (should be instant)"""
    
    def test_manual_entry_is_fast(self):
        """__manual__ should respond quickly (no LLM call)"""
        import time
        
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/ai/parse-entry", json={
            "module": "project",
            "prompt": "__manual__"
        })
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"__manual__ took {elapsed:.2f}s - should be instant (no LLM)"
        print(f"✓ __manual__ responded in {elapsed:.3f}s (fast-path working)")
