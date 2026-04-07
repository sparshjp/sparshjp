"""
Test Suite for 10 Advanced Enterprise ERP Modules - Iteration 34
Modules: Approvals, Budgets, Contracts, Resources, Forex, Billing, Documents, Notifications, Compliance, Portal
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
CREATOR_EMAIL = "kairoserp"
CREATOR_PASSWORD = "¢re@tor@AIengine"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for creator user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": CREATOR_EMAIL,
        "password": CREATOR_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


# ==================== APPROVALS MODULE ====================
class TestApprovalsModule:
    """Tests for Approval Workflows module"""
    
    workflow_id = None
    request_id = None
    
    def test_list_workflows(self, api_client):
        """GET /api/approvals/workflows returns list"""
        response = api_client.get(f"{BASE_URL}/api/approvals/workflows")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List workflows: {len(data)} workflows found")
    
    def test_create_workflow(self, api_client):
        """POST /api/approvals/workflows creates a workflow"""
        payload = {
            "name": f"TEST_PO_Approval_{uuid.uuid4().hex[:6]}",
            "type": "purchase_order",
            "threshold_amount": 50000,
            "steps": [
                {"role": "finance_manager", "label": "Finance Review"},
                {"role": "admin", "label": "Admin Approval"}
            ]
        }
        response = api_client.post(f"{BASE_URL}/api/approvals/workflows", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data["type"] == "purchase_order"
        assert len(data["steps"]) == 2
        TestApprovalsModule.workflow_id = data["id"]
        print(f"✓ Created workflow: {data['id']}")
    
    def test_list_requests(self, api_client):
        """GET /api/approvals/requests returns list"""
        response = api_client.get(f"{BASE_URL}/api/approvals/requests")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List requests: {len(data)} requests found")
    
    def test_create_request(self, api_client):
        """POST /api/approvals/requests creates an approval request"""
        payload = {
            "type": "purchase_order",
            "reference_name": f"TEST_PO_{uuid.uuid4().hex[:6]}",
            "amount": 75000,
            "requester_name": "Test User",
            "comments": "Test approval request"
        }
        response = api_client.post(f"{BASE_URL}/api/approvals/requests", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert data["amount"] == 75000
        TestApprovalsModule.request_id = data["id"]
        print(f"✓ Created request: {data['id']}")
    
    def test_approve_request(self, api_client):
        """POST /api/approvals/requests/{id}/approve approves a request"""
        if not TestApprovalsModule.request_id:
            pytest.skip("No request to approve")
        payload = {"approved_by": "admin", "comments": "Approved for testing"}
        response = api_client.post(f"{BASE_URL}/api/approvals/requests/{TestApprovalsModule.request_id}/approve", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Check step was approved
        assert data["steps"][0]["status"] == "approved"
        print(f"✓ Approved request step: {data['id']}")
    
    def test_approval_stats(self, api_client):
        """GET /api/approvals/stats returns statistics"""
        response = api_client.get(f"{BASE_URL}/api/approvals/stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Approval stats: {data}")


# ==================== BUDGETS MODULE ====================
class TestBudgetsModule:
    """Tests for Budget Management module"""
    
    budget_id = None
    
    def test_list_budgets(self, api_client):
        """GET /api/budgets returns list"""
        response = api_client.get(f"{BASE_URL}/api/budgets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List budgets: {len(data)} budgets found")
    
    def test_create_budget(self, api_client):
        """POST /api/budgets creates a budget"""
        payload = {
            "name": f"TEST_IT_Budget_{uuid.uuid4().hex[:6]}",
            "type": "department",
            "department": "IT",
            "fiscal_year": "2025-26",
            "line_items": [
                {"category": "Software", "amount": 500000},
                {"category": "Hardware", "amount": 300000},
                {"category": "Training", "amount": 100000}
            ]
        }
        response = api_client.post(f"{BASE_URL}/api/budgets", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["total_budget"] == 900000
        assert data["department"] == "IT"
        TestBudgetsModule.budget_id = data["id"]
        print(f"✓ Created budget: {data['id']} with total {data['total_budget']}")
    
    def test_budget_variance(self, api_client):
        """GET /api/budgets/variance returns variance data"""
        response = api_client.get(f"{BASE_URL}/api/budgets/variance")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Budget variance: {len(data)} budgets with variance data")
    
    def test_budget_alerts(self, api_client):
        """GET /api/budgets/alerts returns budget alerts"""
        response = api_client.get(f"{BASE_URL}/api/budgets/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Budget alerts: {len(data)} alerts")


# ==================== CONTRACTS MODULE ====================
class TestContractsModule:
    """Tests for Contract Management module"""
    
    contract_id = None
    
    def test_list_contracts(self, api_client):
        """GET /api/contracts returns list"""
        response = api_client.get(f"{BASE_URL}/api/contracts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List contracts: {len(data)} contracts found")
    
    def test_create_contract(self, api_client):
        """POST /api/contracts creates a contract"""
        payload = {
            "title": f"TEST_MSA_{uuid.uuid4().hex[:6]}",
            "type": "msa",
            "client_name": "Test Client Corp",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "value": 1000000,
            "currency": "INR",
            "billing_type": "fixed",
            "milestones": [
                {"name": "Phase 1", "amount": 300000, "due_date": "2025-03-31"},
                {"name": "Phase 2", "amount": 400000, "due_date": "2025-06-30"},
                {"name": "Phase 3", "amount": 300000, "due_date": "2025-09-30"}
            ],
            "auto_renew": True,
            "notice_period_days": 30
        }
        response = api_client.post(f"{BASE_URL}/api/contracts", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["value"] == 1000000
        assert len(data["milestones"]) == 3
        TestContractsModule.contract_id = data["id"]
        print(f"✓ Created contract: {data['id']}")
    
    def test_renewal_alerts(self, api_client):
        """GET /api/contracts/alerts/renewals returns renewal alerts"""
        response = api_client.get(f"{BASE_URL}/api/contracts/alerts/renewals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Renewal alerts: {len(data)} contracts expiring soon")
    
    def test_contract_stats(self, api_client):
        """GET /api/contracts/stats/summary returns contract stats"""
        response = api_client.get(f"{BASE_URL}/api/contracts/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Contract stats: {data}")


# ==================== RESOURCES MODULE ====================
class TestResourcesModule:
    """Tests for Resource Planning module"""
    
    allocation_id = None
    
    def test_list_allocations(self, api_client):
        """GET /api/resources/allocations returns list"""
        response = api_client.get(f"{BASE_URL}/api/resources/allocations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List allocations: {len(data)} allocations found")
    
    def test_create_allocation(self, api_client):
        """POST /api/resources/allocations creates allocation"""
        payload = {
            "employee_id": f"TEST_EMP_{uuid.uuid4().hex[:6]}",
            "employee_name": "Test Employee",
            "project_id": f"TEST_PROJ_{uuid.uuid4().hex[:6]}",
            "project_name": "Test Project",
            "role": "Developer",
            "allocation_pct": 80,
            "start_date": "2025-01-01",
            "end_date": "2025-06-30",
            "billable": True,
            "bill_rate": 5000
        }
        response = api_client.post(f"{BASE_URL}/api/resources/allocations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["allocation_pct"] == 80
        assert data["billable"] == True
        TestResourcesModule.allocation_id = data["id"]
        print(f"✓ Created allocation: {data['id']}")
    
    def test_get_bench(self, api_client):
        """GET /api/resources/bench returns bench data"""
        response = api_client.get(f"{BASE_URL}/api/resources/bench")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Bench data: {len(data)} employees on bench")
    
    def test_resource_utilization(self, api_client):
        """GET /api/resources/utilization returns utilization stats"""
        response = api_client.get(f"{BASE_URL}/api/resources/utilization")
        assert response.status_code == 200
        data = response.json()
        assert "total_employees" in data
        assert "avg_utilization" in data
        print(f"✓ Utilization: {data['avg_utilization']}% average")
    
    def test_staffing_forecast(self, api_client):
        """GET /api/resources/forecast returns staffing forecast"""
        response = api_client.get(f"{BASE_URL}/api/resources/forecast")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Staffing forecast: {len(data)} projects")


# ==================== FOREX MODULE ====================
class TestForexModule:
    """Tests for Multi-Currency & Forex module"""
    
    transaction_id = None
    
    def test_get_rates(self, api_client):
        """GET /api/forex/rates returns exchange rates"""
        response = api_client.get(f"{BASE_URL}/api/forex/rates")
        assert response.status_code == 200
        data = response.json()
        assert "rates" in data
        assert "USD" in data["rates"]
        print(f"✓ Forex rates: USD={data['rates']['USD']}")
    
    def test_create_forex_transaction(self, api_client):
        """POST /api/forex/transactions creates forex transaction"""
        payload = {
            "type": "invoice",
            "reference_name": f"TEST_INV_{uuid.uuid4().hex[:6]}",
            "currency": "USD",
            "foreign_amount": 10000,
            "booking_rate": 84.50,
            "date": "2025-01-15"
        }
        response = api_client.post(f"{BASE_URL}/api/forex/transactions", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["booking_inr"] == 845000  # 10000 * 84.50
        assert data["settled"] == False
        TestForexModule.transaction_id = data["id"]
        print(f"✓ Created forex transaction: {data['id']}")
    
    def test_list_forex_transactions(self, api_client):
        """GET /api/forex/transactions returns list"""
        response = api_client.get(f"{BASE_URL}/api/forex/transactions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Forex transactions: {len(data)} transactions")
    
    def test_fetch_live_rates(self, api_client):
        """POST /api/forex/rates/fetch-live fetches live rates"""
        response = api_client.post(f"{BASE_URL}/api/forex/rates/fetch-live")
        assert response.status_code == 200
        data = response.json()
        # Either returns live rates or fallback
        assert "rates" in data or "status" in data
        print(f"✓ Live rates fetch: source={data.get('source', 'unknown')}")
    
    def test_revaluation(self, api_client):
        """GET /api/forex/revaluation returns unrealized gain/loss"""
        response = api_client.get(f"{BASE_URL}/api/forex/revaluation")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total_unrealized_gain_loss" in data
        print(f"✓ Revaluation: {data['total_unrealized_gain_loss']} unrealized")


# ==================== BILLING MODULE ====================
class TestBillingModule:
    """Tests for Billing Automation module"""
    
    def test_get_unbilled(self, api_client):
        """GET /api/billing/unbilled returns unbilled timesheets"""
        response = api_client.get(f"{BASE_URL}/api/billing/unbilled")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Unbilled: {len(data)} projects with unbilled time")
    
    def test_billing_stats(self, api_client):
        """GET /api/billing/stats returns billing stats"""
        response = api_client.get(f"{BASE_URL}/api/billing/stats")
        assert response.status_code == 200
        data = response.json()
        assert "unbilled_timesheets" in data
        assert "draft_invoices" in data
        print(f"✓ Billing stats: {data['unbilled_timesheets']} unbilled, {data['draft_invoices']} drafts")
    
    def test_milestone_invoices(self, api_client):
        """GET /api/billing/milestone-invoices returns invoiceable milestones"""
        response = api_client.get(f"{BASE_URL}/api/billing/milestone-invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Milestone invoices: {len(data)} invoiceable milestones")


# ==================== DOCUMENTS MODULE ====================
class TestDocumentsModule:
    """Tests for Document Management module"""
    
    def test_list_documents(self, api_client):
        """GET /api/documents returns document list"""
        response = api_client.get(f"{BASE_URL}/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Documents: {len(data)} documents found")
    
    def test_get_categories(self, api_client):
        """GET /api/documents/categories returns document categories"""
        response = api_client.get(f"{BASE_URL}/api/documents/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "contract" in data
        assert "invoice" in data
        print(f"✓ Document categories: {len(data)} categories")
    
    def test_document_stats(self, api_client):
        """GET /api/documents/stats returns document stats"""
        response = api_client.get(f"{BASE_URL}/api/documents/stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Document stats: {data}")


# ==================== NOTIFICATIONS MODULE ====================
class TestNotificationsModule:
    """Tests for Notifications module"""
    
    notification_id = None
    
    def test_list_notifications(self, api_client):
        """GET /api/notifications returns notification list"""
        response = api_client.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notifications: {len(data)} notifications found")
    
    def test_create_notification(self, api_client):
        """POST /api/notifications creates a notification"""
        payload = {
            "type": "info",
            "title": f"TEST_Notification_{uuid.uuid4().hex[:6]}",
            "message": "This is a test notification",
            "priority": "normal",
            "role": "admin"
        }
        response = api_client.post(f"{BASE_URL}/api/notifications", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["read"] == False
        TestNotificationsModule.notification_id = data["id"]
        print(f"✓ Created notification: {data['id']}")
    
    def test_generate_reminders(self, api_client):
        """POST /api/notifications/generate-reminders generates reminders"""
        response = api_client.post(f"{BASE_URL}/api/notifications/generate-reminders")
        assert response.status_code == 200
        data = response.json()
        assert "generated" in data
        print(f"✓ Generated reminders: {data['generated']} new reminders")
    
    def test_unread_count(self, api_client):
        """GET /api/notifications/unread-count returns unread count"""
        response = api_client.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert "unread" in data
        print(f"✓ Unread count: {data['unread']}")


# ==================== COMPLIANCE MODULE ====================
class TestComplianceModule:
    """Tests for Audit & Compliance Dashboard module"""
    
    def test_get_frameworks(self, api_client):
        """GET /api/compliance/frameworks returns SOC2/ISO data"""
        response = api_client.get(f"{BASE_URL}/api/compliance/frameworks")
        assert response.status_code == 200
        data = response.json()
        assert "soc2" in data
        assert "iso27001" in data
        assert "readiness_pct" in data["soc2"]
        print(f"✓ Compliance frameworks: SOC2={data['soc2']['readiness_pct']}%, ISO27001={data['iso27001']['readiness_pct']}%")
    
    def test_compliance_dashboard(self, api_client):
        """GET /api/compliance/dashboard returns compliance dashboard"""
        response = api_client.get(f"{BASE_URL}/api/compliance/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "frameworks" in data
        assert "user_stats" in data
        assert "rbac_enabled" in data
        print(f"✓ Compliance dashboard: RBAC={data['rbac_enabled']}, Audit={data['audit_trail_enabled']}")
    
    def test_access_logs(self, api_client):
        """GET /api/compliance/access-logs returns access logs"""
        response = api_client.get(f"{BASE_URL}/api/compliance/access-logs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Access logs: {len(data)} logs")


# ==================== PORTAL MODULE ====================
class TestPortalModule:
    """Tests for Client Portal module"""
    
    portal_client_id = None
    portal_token = None
    
    def test_list_portal_clients(self, api_client):
        """GET /api/portal/clients returns portal client list"""
        response = api_client.get(f"{BASE_URL}/api/portal/clients")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Portal clients: {len(data)} clients")
    
    def test_create_portal_client(self, api_client):
        """POST /api/portal/clients creates portal client with JWT token"""
        payload = {
            "client_id": f"TEST_CLIENT_{uuid.uuid4().hex[:6]}",
            "client_name": "Test Portal Client",
            "contact_name": "John Doe",
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
            "projects": []
        }
        response = api_client.post(f"{BASE_URL}/api/portal/clients", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "portal_token" in data
        assert data["is_active"] == True
        TestPortalModule.portal_client_id = data["id"]
        TestPortalModule.portal_token = data["portal_token"]
        print(f"✓ Created portal client: {data['id']} with token")
    
    def test_portal_token_access(self, api_client):
        """Test portal endpoints with X-Portal-Token header"""
        if not TestPortalModule.portal_token:
            pytest.skip("No portal token available")
        
        headers = {"X-Portal-Token": TestPortalModule.portal_token}
        
        # Test /my/projects
        response = requests.get(f"{BASE_URL}/api/portal/my/projects", headers=headers)
        assert response.status_code == 200
        print(f"✓ Portal /my/projects accessible with token")
        
        # Test /my/invoices
        response = requests.get(f"{BASE_URL}/api/portal/my/invoices", headers=headers)
        assert response.status_code == 200
        print(f"✓ Portal /my/invoices accessible with token")
        
        # Test /my/dashboard
        response = requests.get(f"{BASE_URL}/api/portal/my/dashboard", headers=headers)
        assert response.status_code == 200
        print(f"✓ Portal /my/dashboard accessible with token")
    
    def test_portal_without_token_fails(self):
        """Test portal endpoints fail without token"""
        response = requests.get(f"{BASE_URL}/api/portal/my/projects")
        assert response.status_code == 401
        print(f"✓ Portal correctly rejects requests without token")


# ==================== CLEANUP ====================
class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_data(self, api_client):
        """Delete test-created data"""
        # Cleanup workflow
        if TestApprovalsModule.workflow_id:
            api_client.delete(f"{BASE_URL}/api/approvals/workflows/{TestApprovalsModule.workflow_id}")
        
        # Cleanup budget
        if TestBudgetsModule.budget_id:
            api_client.delete(f"{BASE_URL}/api/budgets/{TestBudgetsModule.budget_id}")
        
        # Cleanup allocation
        if TestResourcesModule.allocation_id:
            api_client.delete(f"{BASE_URL}/api/resources/allocations/{TestResourcesModule.allocation_id}")
        
        # Cleanup notification
        if TestNotificationsModule.notification_id:
            api_client.delete(f"{BASE_URL}/api/notifications/{TestNotificationsModule.notification_id}")
        
        # Cleanup portal client
        if TestPortalModule.portal_client_id:
            api_client.delete(f"{BASE_URL}/api/portal/clients/{TestPortalModule.portal_client_id}")
        
        print("✓ Test data cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
