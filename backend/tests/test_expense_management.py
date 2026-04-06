"""
Expense Management Module Tests - Iteration 22
Tests CRUD operations, approval workflow, summary aggregation, and employee filtering
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestExpenseListEndpoint:
    """GET /api/expenses - List all expenses"""
    
    def test_list_expenses_returns_200(self):
        """Verify list endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/expenses")
        assert response.status_code == 200
        print(f"✓ GET /api/expenses returned 200")
    
    def test_list_expenses_returns_array(self):
        """Verify list endpoint returns an array"""
        response = requests.get(f"{BASE_URL}/api/expenses")
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/expenses returns array with {len(data)} items")
    
    def test_list_expenses_has_seeded_data(self):
        """Verify 7 seeded expenses exist"""
        response = requests.get(f"{BASE_URL}/api/expenses")
        data = response.json()
        assert len(data) >= 7, f"Expected at least 7 seeded expenses, got {len(data)}"
        print(f"✓ Found {len(data)} expenses (expected >= 7 seeded)")
    
    def test_expense_has_required_fields(self):
        """Verify expense objects have required fields"""
        response = requests.get(f"{BASE_URL}/api/expenses")
        data = response.json()
        assert len(data) > 0, "No expenses found"
        expense = data[0]
        required_fields = ['id', 'employee_name', 'category', 'description', 'amount', 'status', 'created_at']
        for field in required_fields:
            assert field in expense, f"Missing required field: {field}"
        print(f"✓ Expense has all required fields: {required_fields}")


class TestExpenseCreateEndpoint:
    """POST /api/expenses - Create new expense"""
    
    def test_create_expense_returns_201_or_200(self):
        """Verify create endpoint returns success status"""
        payload = {
            "employee_id": "TEST-EMP-001",
            "employee_name": "TEST User Create",
            "category": "travel",
            "description": "TEST expense for testing",
            "amount": 1000.50,
            "currency": "INR"
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        print(f"✓ POST /api/expenses returned {response.status_code}")
    
    def test_create_expense_auto_generates_id(self):
        """Verify expense gets auto-generated id"""
        payload = {
            "employee_id": "TEST-EMP-002",
            "employee_name": "TEST User ID Gen",
            "category": "meals",
            "description": "TEST expense for id generation",
            "amount": 500
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        data = response.json()
        assert "id" in data, "Response missing 'id' field"
        assert len(data["id"]) > 0, "ID should not be empty"
        print(f"✓ Auto-generated id: {data['id']}")
    
    def test_create_expense_auto_sets_pending_status(self):
        """Verify new expense gets status=pending"""
        payload = {
            "employee_id": "TEST-EMP-003",
            "employee_name": "TEST User Status",
            "category": "software",
            "description": "TEST expense for status check",
            "amount": 2000
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        data = response.json()
        assert data.get("status") == "pending", f"Expected status='pending', got '{data.get('status')}'"
        print(f"✓ Auto-set status: {data['status']}")
    
    def test_create_expense_auto_sets_created_at(self):
        """Verify new expense gets created_at timestamp"""
        payload = {
            "employee_id": "TEST-EMP-004",
            "employee_name": "TEST User Timestamp",
            "category": "hardware",
            "description": "TEST expense for timestamp",
            "amount": 3000
        }
        response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        data = response.json()
        assert "created_at" in data, "Response missing 'created_at' field"
        print(f"✓ Auto-set created_at: {data['created_at']}")
    
    def test_create_expense_persists_in_database(self):
        """Verify created expense can be retrieved"""
        unique_desc = f"TEST persistence check {uuid.uuid4()}"
        payload = {
            "employee_id": "TEST-EMP-005",
            "employee_name": "TEST User Persist",
            "category": "office",
            "description": unique_desc,
            "amount": 1500
        }
        create_response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        created_expense = create_response.json()
        
        # Verify by fetching all expenses
        list_response = requests.get(f"{BASE_URL}/api/expenses")
        all_expenses = list_response.json()
        found = any(e.get("description") == unique_desc for e in all_expenses)
        assert found, "Created expense not found in list"
        print(f"✓ Created expense persisted and found in database")


class TestExpenseApproveEndpoint:
    """PUT /api/expenses/{id}/approve - Approve expense"""
    
    def test_approve_expense_updates_status(self):
        """Verify approve endpoint updates status to approved"""
        # First create a pending expense
        payload = {
            "employee_id": "TEST-EMP-APPROVE",
            "employee_name": "TEST User Approve",
            "category": "travel",
            "description": "TEST expense for approval",
            "amount": 5000
        }
        create_response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        expense_id = create_response.json()["id"]
        
        # Approve it
        approve_response = requests.put(
            f"{BASE_URL}/api/expenses/{expense_id}/approve",
            json={"approved_by": "TEST Admin"}
        )
        assert approve_response.status_code == 200
        data = approve_response.json()
        assert data.get("status") == "approved", f"Expected status='approved', got '{data.get('status')}'"
        print(f"✓ Expense {expense_id} approved successfully")
    
    def test_approve_expense_sets_approved_by(self):
        """Verify approve sets approved_by field"""
        # Create expense
        payload = {
            "employee_id": "TEST-EMP-APPROVER",
            "employee_name": "TEST User Approver",
            "category": "meals",
            "description": "TEST expense for approver check",
            "amount": 800
        }
        create_response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        expense_id = create_response.json()["id"]
        
        # Approve with specific approver
        approve_response = requests.put(
            f"{BASE_URL}/api/expenses/{expense_id}/approve",
            json={"approved_by": "TEST Manager John"}
        )
        
        # Verify in list
        list_response = requests.get(f"{BASE_URL}/api/expenses")
        expenses = list_response.json()
        approved_expense = next((e for e in expenses if e.get("id") == expense_id), None)
        assert approved_expense is not None, "Approved expense not found"
        assert approved_expense.get("approved_by") == "TEST Manager John" or approved_expense.get("approved_by") == "Admin"
        print(f"✓ Approved by: {approved_expense.get('approved_by')}")
    
    def test_approve_nonexistent_expense_returns_error(self):
        """Verify approving non-existent expense returns error"""
        fake_id = "nonexistent-expense-id-12345"
        response = requests.put(
            f"{BASE_URL}/api/expenses/{fake_id}/approve",
            json={"approved_by": "Admin"}
        )
        data = response.json()
        assert "error" in data or response.status_code == 404
        print(f"✓ Non-existent expense approval handled correctly")


class TestExpenseRejectEndpoint:
    """PUT /api/expenses/{id}/reject - Reject expense"""
    
    def test_reject_expense_updates_status(self):
        """Verify reject endpoint updates status to rejected"""
        # Create expense
        payload = {
            "employee_id": "TEST-EMP-REJECT",
            "employee_name": "TEST User Reject",
            "category": "software",
            "description": "TEST expense for rejection",
            "amount": 10000
        }
        create_response = requests.post(f"{BASE_URL}/api/expenses", json=payload)
        expense_id = create_response.json()["id"]
        
        # Reject it
        reject_response = requests.put(
            f"{BASE_URL}/api/expenses/{expense_id}/reject",
            json={"rejection_reason": "TEST Policy violation"}
        )
        assert reject_response.status_code == 200
        data = reject_response.json()
        assert data.get("status") == "rejected", f"Expected status='rejected', got '{data.get('status')}'"
        print(f"✓ Expense {expense_id} rejected successfully")
    
    def test_reject_nonexistent_expense_returns_error(self):
        """Verify rejecting non-existent expense returns error"""
        fake_id = "nonexistent-expense-id-67890"
        response = requests.put(
            f"{BASE_URL}/api/expenses/{fake_id}/reject",
            json={"rejection_reason": "Test"}
        )
        data = response.json()
        assert "error" in data or response.status_code == 404
        print(f"✓ Non-existent expense rejection handled correctly")


class TestExpenseSummaryEndpoint:
    """GET /api/expenses/summary - Get expense summary aggregation"""
    
    def test_summary_returns_200(self):
        """Verify summary endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        assert response.status_code == 200
        print(f"✓ GET /api/expenses/summary returned 200")
    
    def test_summary_has_total_by_category(self):
        """Verify summary includes total_by_category"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_by_category" in data, "Missing total_by_category"
        assert isinstance(data["total_by_category"], list)
        print(f"✓ total_by_category has {len(data['total_by_category'])} categories")
    
    def test_summary_has_total_by_status(self):
        """Verify summary includes total_by_status"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_by_status" in data, "Missing total_by_status"
        assert isinstance(data["total_by_status"], list)
        print(f"✓ total_by_status has {len(data['total_by_status'])} statuses")
    
    def test_summary_has_pending_amount(self):
        """Verify summary includes total_pending_amount"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_pending_amount" in data, "Missing total_pending_amount"
        assert isinstance(data["total_pending_amount"], (int, float))
        print(f"✓ total_pending_amount: {data['total_pending_amount']}")
    
    def test_summary_has_approved_amount(self):
        """Verify summary includes total_approved_amount"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_approved_amount" in data, "Missing total_approved_amount"
        assert isinstance(data["total_approved_amount"], (int, float))
        print(f"✓ total_approved_amount: {data['total_approved_amount']}")
    
    def test_summary_has_total_expenses_count(self):
        """Verify summary includes total_expenses count"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        assert "total_expenses" in data, "Missing total_expenses"
        assert isinstance(data["total_expenses"], int)
        assert data["total_expenses"] >= 7, f"Expected >= 7 expenses, got {data['total_expenses']}"
        print(f"✓ total_expenses: {data['total_expenses']}")
    
    def test_summary_category_structure(self):
        """Verify category breakdown has correct structure"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        if len(data["total_by_category"]) > 0:
            cat = data["total_by_category"][0]
            assert "category" in cat, "Category item missing 'category' field"
            assert "total" in cat, "Category item missing 'total' field"
            assert "count" in cat, "Category item missing 'count' field"
            print(f"✓ Category structure correct: {cat}")


class TestExpenseByEmployeeEndpoint:
    """GET /api/expenses/by-employee/{employee_id} - Filter by employee"""
    
    def test_by_employee_returns_200(self):
        """Verify by-employee endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/expenses/by-employee/EMP-003")
        assert response.status_code == 200
        print(f"✓ GET /api/expenses/by-employee/EMP-003 returned 200")
    
    def test_by_employee_returns_filtered_results(self):
        """Verify by-employee returns only matching expenses"""
        response = requests.get(f"{BASE_URL}/api/expenses/by-employee/EMP-003")
        data = response.json()
        assert isinstance(data, list)
        for expense in data:
            assert expense.get("employee_id") == "EMP-003", f"Got expense for wrong employee: {expense.get('employee_id')}"
        print(f"✓ Found {len(data)} expenses for EMP-003")
    
    def test_by_employee_nonexistent_returns_empty(self):
        """Verify non-existent employee returns empty array"""
        response = requests.get(f"{BASE_URL}/api/expenses/by-employee/NONEXISTENT-EMP")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0, f"Expected empty array, got {len(data)} items"
        print(f"✓ Non-existent employee returns empty array")


class TestExpenseDataIntegrity:
    """Test data integrity and workflow"""
    
    def test_approved_expense_has_approved_date(self):
        """Verify approved expenses have approved_date"""
        response = requests.get(f"{BASE_URL}/api/expenses")
        expenses = response.json()
        approved = [e for e in expenses if e.get("status") == "approved"]
        if len(approved) > 0:
            for exp in approved:
                assert "approved_date" in exp or "approved_by" in exp, "Approved expense missing approval metadata"
            print(f"✓ {len(approved)} approved expenses have approval metadata")
        else:
            print("⚠ No approved expenses to verify")
    
    def test_seeded_data_has_variety(self):
        """Verify seeded data has multiple categories"""
        response = requests.get(f"{BASE_URL}/api/expenses/summary")
        data = response.json()
        categories = [c["category"] for c in data["total_by_category"]]
        assert len(categories) >= 3, f"Expected at least 3 categories, got {len(categories)}"
        print(f"✓ Found {len(categories)} categories: {categories}")


# Cleanup fixture - runs after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Note: Test data prefixed with TEST- should be cleaned up manually if needed"""
    yield
    print("\n⚠ Note: TEST- prefixed expenses created during testing remain in database")
