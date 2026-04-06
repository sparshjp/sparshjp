"""
Iteration 23 Backend Tests - Kairos AI Engine v3 Features
Tests: Expenses, Feedback, Leave Management, Employee Analytics, Agents Providers
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestExpenseEndpoints:
    """Expense Management CRUD + approval workflow tests"""
    
    def test_list_expenses_returns_200(self):
        """GET /api/expenses returns 200"""
        response = requests.get(f"{BASE_URL}/api/expenses")
        assert response.status_code == 200
        print(f"PASS: GET /api/expenses returned {response.status_code}")
    
    def test_list_expenses_returns_array(self):
        """GET /api/expenses returns array"""
        response = requests.get(f"{BASE_URL}/api/expenses")
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/expenses returned array with {len(data)} items")
    
    def test_create_expense_auto_generates_id(self):
        """POST /api/expenses auto-generates id"""
        payload = {
            "employee_id": f"TEST-{uuid.uuid4().hex[:6]}",
            "employee_name": "Test Create ID",
            "category": "travel",
            "description": "Test auto id generation",
            "amount": 100
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert len(data["id"]) > 0
        print(f"PASS: POST /api/expenses auto-generated id: {data['id'][:8]}...")
    
    def test_create_expense_auto_sets_status_pending(self):
        """POST /api/expenses auto-sets status to pending"""
        payload = {
            "employee_id": f"TEST-{uuid.uuid4().hex[:6]}",
            "employee_name": "Test Status Pending",
            "category": "meals",
            "description": "Test auto status",
            "amount": 50
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        data = response.json()
        assert data.get("status") == "pending"
        print(f"PASS: POST /api/expenses auto-set status to 'pending'")
    
    def test_create_expense_auto_sets_created_at(self):
        """POST /api/expenses auto-sets created_at"""
        payload = {
            "employee_id": f"TEST-{uuid.uuid4().hex[:6]}",
            "employee_name": "Test Created At",
            "category": "software",
            "description": "Test auto created_at",
            "amount": 200
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        data = response.json()
        assert "created_at" in data
        assert len(data["created_at"]) > 0
        print(f"PASS: POST /api/expenses auto-set created_at: {data['created_at'][:19]}")
    
    def test_approve_expense_updates_status(self):
        """PUT /api/expenses/{id}/approve updates status to approved"""
        # Create expense first
        payload = {
            "employee_id": f"TEST-{uuid.uuid4().hex[:6]}",
            "employee_name": "Test Approve",
            "category": "travel",
            "description": "Test approval",
            "amount": 300
        }
        create_resp = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        expense_id = create_resp.json()["id"]
        
        # Approve it
        approve_resp = requests.put(
            f"{BASE_URL}/api/expenses/{expense_id}/approve",
            json={"approved_by": "Test Admin"}
        )
        assert approve_resp.status_code == 200
        data = approve_resp.json()
        assert data.get("status") == "approved"
        print(f"PASS: PUT /api/expenses/{expense_id[:8]}.../approve returned status=approved")
    
    def test_reject_expense_updates_status(self):
        """PUT /api/expenses/{id}/reject updates status to rejected"""
        # Create expense first
        payload = {
            "employee_id": f"TEST-{uuid.uuid4().hex[:6]}",
            "employee_name": "Test Reject",
            "category": "meals",
            "description": "Test rejection",
            "amount": 150
        }
        create_resp = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        expense_id = create_resp.json()["id"]
        
        # Reject it
        reject_resp = requests.put(
            f"{BASE_URL}/api/expenses/{expense_id}/reject",
            json={"rejection_reason": "Policy violation"}
        )
        assert reject_resp.status_code == 200
        data = reject_resp.json()
        assert data.get("status") == "rejected"
        print(f"PASS: PUT /api/expenses/{expense_id[:8]}.../reject returned status=rejected")


class TestExpenseSummaryEndpoint:
    """GET /api/expenses/summary tests - verifies proper field names (category, status, not _id)"""
    
    def test_summary_returns_200(self):
        """GET /api/expenses/summary returns 200"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        assert response.status_code == 200
        print(f"PASS: GET /api/expenses/summary returned {response.status_code}")
    
    def test_summary_has_total_by_category(self):
        """Summary has total_by_category array"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_by_category" in data
        assert isinstance(data["total_by_category"], list)
        print(f"PASS: Summary has total_by_category with {len(data['total_by_category'])} categories")
    
    def test_summary_category_uses_category_field_not_id(self):
        """Summary total_by_category uses 'category' field, not '_id'"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        if data["total_by_category"]:
            first_cat = data["total_by_category"][0]
            assert "category" in first_cat, "Expected 'category' field, not '_id'"
            assert "_id" not in first_cat, "Should not have '_id' field"
            print(f"PASS: total_by_category uses 'category' field: {first_cat.get('category')}")
        else:
            pytest.skip("No categories in summary")
    
    def test_summary_has_total_by_status(self):
        """Summary has total_by_status array"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_by_status" in data
        assert isinstance(data["total_by_status"], list)
        print(f"PASS: Summary has total_by_status with {len(data['total_by_status'])} statuses")
    
    def test_summary_status_uses_status_field_not_id(self):
        """Summary total_by_status uses 'status' field, not '_id'"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        if data["total_by_status"]:
            first_status = data["total_by_status"][0]
            assert "status" in first_status, "Expected 'status' field, not '_id'"
            assert "_id" not in first_status, "Should not have '_id' field"
            print(f"PASS: total_by_status uses 'status' field: {first_status.get('status')}")
        else:
            pytest.skip("No statuses in summary")
    
    def test_summary_has_pending_amount(self):
        """Summary has total_pending_amount"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_pending_amount" in data
        print(f"PASS: Summary has total_pending_amount: {data['total_pending_amount']}")
    
    def test_summary_has_approved_amount(self):
        """Summary has total_approved_amount"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_approved_amount" in data
        print(f"PASS: Summary has total_approved_amount: {data['total_approved_amount']}")
    
    def test_summary_has_total_expenses_count(self):
        """Summary has total_expenses count"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_expenses" in data
        assert isinstance(data["total_expenses"], int)
        print(f"PASS: Summary has total_expenses: {data['total_expenses']}")


class TestExpenseByEmployeeEndpoint:
    """GET /api/expenses/by-employee/{employee_id} tests"""
    
    def test_by_employee_returns_200(self):
        """GET /api/expenses/by-employee/{id} returns 200"""
        response = requests.get(f"{BASE_URL}/api/expenses/by-employee/EMP-003")
        assert response.status_code == 200
        print(f"PASS: GET /api/expenses/by-employee/EMP-003 returned {response.status_code}")
    
    def test_by_employee_returns_filtered_results(self):
        """GET /api/expenses/by-employee/{id} returns only that employee's expenses"""
        response = requests.get(f"{BASE_URL}/api/expenses/by-employee/EMP-003")
        data = response.json()
        assert isinstance(data, list)
        for exp in data:
            assert exp.get("employee_id") == "EMP-003"
        print(f"PASS: by-employee returned {len(data)} expenses for EMP-003")
    
    def test_by_employee_nonexistent_returns_empty(self):
        """GET /api/expenses/by-employee/{nonexistent} returns empty array"""
        response = requests.get(f"{BASE_URL}/api/expenses/by-employee/NONEXISTENT-999")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
        print(f"PASS: by-employee for nonexistent ID returned empty array")


class TestFeedbackEndpoints:
    """Feedback module tests - auto-scaffolded by Kairos with auto-polish"""
    
    def test_list_feedback_returns_200(self):
        """GET /api/feedback returns 200"""
        response = requests.get(f"{BASE_URL}/api/feedback")
        assert response.status_code == 200
        print(f"PASS: GET /api/feedback returned {response.status_code}")
    
    def test_list_feedback_returns_array(self):
        """GET /api/feedback returns array"""
        response = requests.get(f"{BASE_URL}/api/feedback")
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/feedback returned array with {len(data)} items")
    
    def test_create_feedback_auto_generates_id(self):
        """POST /api/feedback auto-generates id"""
        payload = {
            "user_name": f"Test User {uuid.uuid4().hex[:6]}",
            "rating": 5,
            "comment": "Test feedback creation"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert len(data["id"]) > 0
        print(f"PASS: POST /api/feedback auto-generated id: {data['id'][:8]}...")
    
    def test_create_feedback_auto_sets_created_at(self):
        """POST /api/feedback auto-sets created_at"""
        payload = {
            "user_name": f"Test User {uuid.uuid4().hex[:6]}",
            "rating": 4,
            "comment": "Test created_at"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        data = response.json()
        assert "created_at" in data
        assert len(data["created_at"]) > 0
        print(f"PASS: POST /api/feedback auto-set created_at: {data['created_at'][:19]}")
    
    def test_create_feedback_validates_rating(self):
        """POST /api/feedback validates rating 1-5"""
        payload = {
            "user_name": "Test Invalid Rating",
            "rating": 10,  # Invalid
            "comment": "Should fail"
        }
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        data = response.json()
        # Should return error for invalid rating
        assert "error" in data or response.status_code >= 400
        print(f"PASS: POST /api/feedback rejected invalid rating (10)")


class TestLeaveMgmtEndpoints:
    """Leave Management module tests"""
    
    def test_list_leave_requests_returns_200(self):
        """GET /api/leave-mgmt returns 200"""
        response = requests.get(f"{BASE_URL}/api/leave-mgmt")
        assert response.status_code == 200
        print(f"PASS: GET /api/leave-mgmt returned {response.status_code}")
    
    def test_list_leave_requests_returns_array(self):
        """GET /api/leave-mgmt returns array"""
        response = requests.get(f"{BASE_URL}/api/leave-mgmt")
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/leave-mgmt returned array with {len(data)} items")
    
    def test_leave_requests_have_required_fields(self):
        """Leave requests have required fields"""
        response = requests.get(f"{BASE_URL}/api/leave-mgmt")
        data = response.json()
        if data:
            first = data[0]
            assert "id" in first
            assert "employee_id" in first
            assert "leave_type" in first
            assert "status" in first
            print(f"PASS: Leave requests have required fields (id, employee_id, leave_type, status)")
        else:
            pytest.skip("No leave requests in database")


class TestEmployeeAnalyticsEndpoints:
    """Employee Analytics module tests"""
    
    def test_utilization_summary_returns_200(self):
        """GET /api/employee-analytics/utilization-summary returns 200"""
        response = requests.get(f"{BASE_URL}/api/employee-analytics/utilization-summary")
        assert response.status_code == 200
        print(f"PASS: GET /api/employee-analytics/utilization-summary returned {response.status_code}")
    
    def test_utilization_summary_returns_array(self):
        """GET /api/employee-analytics/utilization-summary returns array"""
        response = requests.get(f"{BASE_URL}/api/employee-analytics/utilization-summary")
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: utilization-summary returned array with {len(data)} employees")
    
    def test_utilization_summary_has_required_fields(self):
        """Utilization summary has required fields"""
        response = requests.get(f"{BASE_URL}/api/employee-analytics/utilization-summary")
        data = response.json()
        if data:
            first = data[0]
            assert "employee_id" in first
            assert "name" in first
            assert "utilization_pct" in first
            print(f"PASS: Utilization summary has required fields (employee_id, name, utilization_pct)")
        else:
            pytest.skip("No utilization data")


class TestAgentsProvidersEndpoint:
    """GET /api/agents/providers tests - v3 multi-provider support"""
    
    def test_providers_returns_200(self):
        """GET /api/agents/providers returns 200"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        assert response.status_code == 200
        print(f"PASS: GET /api/agents/providers returned {response.status_code}")
    
    def test_providers_returns_3_providers(self):
        """GET /api/agents/providers returns 3 providers"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) == 3
        print(f"PASS: /api/agents/providers returned 3 providers")
    
    def test_providers_include_groq_openrouter_claude(self):
        """Providers include groq, openrouter, claude"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        provider_names = [p["name"] for p in data["providers"]]
        assert "groq" in provider_names
        assert "openrouter" in provider_names
        assert "claude" in provider_names
        print(f"PASS: Providers include groq, openrouter, claude")
    
    def test_providers_have_fallback_order(self):
        """Providers response has fallback_order"""
        response = requests.get(f"{BASE_URL}/api/agents/providers")
        data = response.json()
        assert "fallback_order" in data
        assert isinstance(data["fallback_order"], list)
        assert len(data["fallback_order"]) == 3
        print(f"PASS: Providers has fallback_order: {data['fallback_order']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
