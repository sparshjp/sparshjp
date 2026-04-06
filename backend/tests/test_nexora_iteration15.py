"""
Iteration 15 Tests: Nexora Digital Solutions Data Pivot
Tests for: Projects, Timesheets, Revenue Recognition, Transaction Explorer, Company Settings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestCompanySettings:
    """Company settings should show Nexora Digital Solutions"""
    
    def test_company_settings_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/company/settings")
        assert response.status_code == 200
    
    def test_company_is_nexora(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/company/settings")
        data = response.json()
        assert "Nexora" in data.get("legal_name", ""), "Company should be Nexora Digital Solutions"
        assert data.get("gstin") == "24AABCN4567P1Z8", "GSTIN should be Gujarat-based"
        assert data.get("state") == "Gujarat"


class TestProjectsAPI:
    """Project Management API tests"""
    
    def test_list_projects_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
    
    def test_projects_count_is_8(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects")
        data = response.json()
        assert len(data) == 8, f"Expected 8 projects, got {len(data)}"
    
    def test_projects_have_required_fields(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects")
        data = response.json()
        for proj in data:
            assert "id" in proj
            assert "name" in proj
            assert "client" in proj
            assert "type" in proj
            assert "pm" in proj
    
    def test_health_dashboard_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects/health/dashboard")
        assert response.status_code == 200
    
    def test_health_dashboard_count_is_7(self, api_client):
        """Health dashboard excludes PRJ-INT (internal)"""
        response = api_client.get(f"{BASE_URL}/api/projects/health/dashboard")
        data = response.json()
        assert len(data) == 7, f"Expected 7 projects in health dashboard, got {len(data)}"
    
    def test_health_dashboard_has_health_status(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects/health/dashboard")
        data = response.json()
        for proj in data:
            assert "health" in proj
            assert proj["health"] in ["GREEN", "YELLOW", "RED", "CLOSED"]
    
    def test_health_dashboard_has_billable_hours(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects/health/dashboard")
        data = response.json()
        for proj in data:
            assert "billable_hours" in proj
            assert isinstance(proj["billable_hours"], (int, float))
    
    def test_project_detail_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects/PRJ-001")
        assert response.status_code == 200
    
    def test_project_timesheets_endpoint(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/projects/PRJ-001/timesheets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTimesheetsAPI:
    """Timesheet API tests"""
    
    def test_list_timesheets_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets")
        assert response.status_code == 200
    
    def test_timesheets_count_is_27(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets")
        data = response.json()
        assert len(data) == 27, f"Expected 27 timesheets, got {len(data)}"
    
    def test_timesheets_have_required_fields(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets")
        data = response.json()
        for ts in data[:5]:  # Check first 5
            assert "employee_id" in ts
            assert "employee_name" in ts
            assert "week" in ts
            assert "entries" in ts
            assert "total_hours" in ts
            assert "status" in ts
    
    def test_utilization_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets/utilization")
        assert response.status_code == 200
    
    def test_utilization_has_15_employees(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets/utilization")
        data = response.json()
        assert "employees" in data
        assert len(data["employees"]) == 15, f"Expected 15 billable employees, got {len(data['employees'])}"
    
    def test_utilization_summary(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets/utilization")
        data = response.json()
        summary = data.get("summary", {})
        assert summary.get("total_billable") == 908, f"Expected 908 billable hours, got {summary.get('total_billable')}"
        assert summary.get("headcount") == 15
        assert summary.get("avg_utilization") == 85.3
    
    def test_consolidation_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets/consolidation")
        assert response.status_code == 200
    
    def test_consolidation_has_project_hours(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/timesheets/consolidation")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        for item in data[:3]:
            assert "project_id" in item
            assert "billable_hours" in item
            assert "total_hours" in item


class TestRevenueAPI:
    """Revenue Recognition API tests"""
    
    def test_schedule_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/schedule")
        assert response.status_code == 200
    
    def test_schedule_has_7_entries(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/schedule")
        data = response.json()
        assert "schedule" in data
        assert len(data["schedule"]) == 7, f"Expected 7 revenue schedule entries, got {len(data['schedule'])}"
    
    def test_schedule_summary(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/schedule")
        data = response.json()
        summary = data.get("summary", {})
        # Total revenue ~221L = 22,100,000
        assert summary.get("total_revenue_march", 0) > 20000000, "Total revenue should be > 200L"
        assert summary.get("total_contract_assets", 0) > 1000000, "Contract assets should be > 10L"
    
    def test_ind_as_115_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/ind-as-115")
        assert response.status_code == 200
    
    def test_ind_as_115_disclosure_structure(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/ind-as-115")
        data = response.json()
        assert "disaggregation" in data
        assert "contract_balances" in data
        assert "remaining_performance_obligations" in data
        assert "significant_judgments" in data
    
    def test_ind_as_115_disaggregation(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/ind-as-115")
        data = response.json()
        disagg = data.get("disaggregation", {})
        assert "by_type" in disagg
        assert "by_geography" in disagg
        # Export should be significant
        geo = disagg.get("by_geography", {})
        assert geo.get("export_pct", 0) > 50, "Export should be > 50% of revenue"
    
    def test_ind_as_115_rpo(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/ind-as-115")
        data = response.json()
        # RPO ~85L = 8,500,000
        assert data.get("total_rpo", 0) > 8000000, "Total RPO should be > 80L"
    
    def test_revenue_transactions_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/transactions")
        assert response.status_code == 200


class TestTransactionExplorerAPI:
    """Transaction Explorer API tests"""
    
    def test_all_transactions_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/all-transactions")
        assert response.status_code == 200
    
    def test_all_transactions_count_is_140(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/all-transactions")
        data = response.json()
        assert data.get("total") == 140, f"Expected 140 transactions, got {data.get('total')}"
    
    def test_module_counts(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/all-transactions")
        data = response.json()
        counts = data.get("module_counts", {})
        # Expected: CRM 15, PRJ 15, TS 24, BUY 16, SEL 15, HR 20, ACC 25, RPT 10
        assert counts.get("CRM") == 15
        assert counts.get("Projects") == 15
        assert counts.get("Timesheets") == 24
        assert counts.get("Buying") == 16
        assert counts.get("Selling") == 15
        assert counts.get("HR") == 20
        assert counts.get("Accounting") == 25
        assert counts.get("Reports") == 10
    
    def test_transactions_have_required_fields(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/all-transactions")
        data = response.json()
        for txn in data["transactions"][:5]:
            assert "id" in txn
            assert "date" in txn
            assert "module" in txn
            assert "type" in txn
            assert "prompt" in txn
            assert "accounting" in txn
            assert "integrity" in txn
    
    def test_filter_by_module(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/all-transactions?module=CRM")
        assert response.status_code == 200
        data = response.json()
        for txn in data["transactions"]:
            assert txn["module"] == "CRM"
    
    def test_filter_by_priority(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/revenue/all-transactions?priority=Critical")
        assert response.status_code == 200
        data = response.json()
        for txn in data["transactions"]:
            assert txn["priority"] == "Critical"


class TestEntitiesAPI:
    """Vendors and Customers API tests"""
    
    def test_vendors_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        assert response.status_code == 200
    
    def test_vendors_count_is_10(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        data = response.json()
        assert len(data) == 10, f"Expected 10 vendors, got {len(data)}"
    
    def test_customers_returns_200(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/entities?entity_type=customer")
        assert response.status_code == 200
    
    def test_customers_count_is_7(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/entities?entity_type=customer")
        data = response.json()
        assert len(data) == 7, f"Expected 7 customers, got {len(data)}"


class TestOldDataCleared:
    """Verify old PolyMerx data is cleared"""
    
    def test_items_collection_empty(self, api_client):
        """Items collection should have no items (old chemical items removed)"""
        response = api_client.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0, f"Items collection should be empty, got {len(data)} items"
    
    def test_no_polymerx_in_company_name(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/company/settings")
        data = response.json()
        assert "PolyMerx" not in data.get("legal_name", ""), "Company should not be PolyMerx"
        assert "PolyMerx" not in data.get("short_name", ""), "Company should not be PolyMerx"
