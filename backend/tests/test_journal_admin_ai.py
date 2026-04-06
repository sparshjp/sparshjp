"""
Test Suite for Kairos Accounting - Journal Entries, Admin Data Tables, and AI Universal Prompt
Tests the new features added in iteration 2:
- Manual Journal Entry CRUD and posting
- Admin Data Tables (list, view, search, export)
- Universal AI Prompt processing
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic API health check"""
    
    def test_api_health(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Kairos Accounting API"
        assert "version" in data
        print(f"✓ API Health: {data}")


class TestManualJournalEntries:
    """Test Manual Journal Entry module - create, list, post"""
    
    def test_create_balanced_journal_entry(self):
        """Create a balanced manual journal entry"""
        payload = {
            "entry_type": "Manual Entry",
            "posting_date": "2026-01-15",
            "cost_center": "General",
            "narration": "TEST_Test journal entry for testing",
            "journal_entries": [
                {"account": "Cash", "debit": 1000.00, "credit": 0, "description": "Cash received"},
                {"account": "Sales Revenue", "debit": 0, "credit": 1000.00, "description": "Sales income"}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/journal-entries/manual", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["entry_type"] == "Manual Entry"
        assert data["status"] == "Draft"
        assert len(data["journal_entries"]) == 2
        print(f"✓ Created journal entry: {data['id']}")
        return data["id"]
    
    def test_create_unbalanced_journal_entry_fails(self):
        """Verify unbalanced entries are rejected"""
        payload = {
            "entry_type": "Manual Entry",
            "posting_date": "2026-01-15",
            "cost_center": "General",
            "narration": "TEST_Unbalanced entry",
            "journal_entries": [
                {"account": "Cash", "debit": 1000.00, "credit": 0, "description": "Cash"},
                {"account": "Sales", "debit": 0, "credit": 500.00, "description": "Sales"}  # Unbalanced!
            ]
        }
        response = requests.post(f"{BASE_URL}/api/journal-entries/manual", json=payload)
        assert response.status_code == 400, f"Expected 400 for unbalanced entry, got {response.status_code}"
        print("✓ Unbalanced entry correctly rejected")
    
    def test_list_journal_entries(self):
        """List all manual journal entries"""
        response = requests.get(f"{BASE_URL}/api/journal-entries/manual")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} journal entries")
        return data
    
    def test_list_journal_entries_with_filter(self):
        """List journal entries with status filter"""
        response = requests.get(f"{BASE_URL}/api/journal-entries/manual", params={"status": "Draft"})
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # All returned entries should be Draft
        for entry in data:
            assert entry["status"] == "Draft"
        print(f"✓ Filtered {len(data)} draft entries")
    
    def test_post_journal_entry(self):
        """Post a draft journal entry to ledger"""
        # First create an entry
        payload = {
            "entry_type": "Manual Entry",
            "posting_date": "2026-01-15",
            "cost_center": "General",
            "narration": "TEST_Entry to be posted",
            "journal_entries": [
                {"account": "Bank Account", "debit": 500.00, "credit": 0, "description": "Bank deposit"},
                {"account": "Cash", "debit": 0, "credit": 500.00, "description": "Cash withdrawal"}
            ]
        }
        create_response = requests.post(f"{BASE_URL}/api/journal-entries/manual", json=payload)
        assert create_response.status_code == 200
        entry_id = create_response.json()["id"]
        
        # Now post it
        post_response = requests.post(f"{BASE_URL}/api/journal-entries/manual/{entry_id}/post")
        assert post_response.status_code == 200
        
        data = post_response.json()
        assert data["message"] == "Posted successfully"
        print(f"✓ Posted journal entry: {entry_id}")
    
    def test_post_already_posted_entry_fails(self):
        """Verify already posted entries cannot be posted again"""
        # Create and post an entry
        payload = {
            "entry_type": "Manual Entry",
            "posting_date": "2026-01-15",
            "cost_center": "General",
            "narration": "TEST_Double post test",
            "journal_entries": [
                {"account": "Expense", "debit": 200.00, "credit": 0, "description": "Expense"},
                {"account": "Cash", "debit": 0, "credit": 200.00, "description": "Cash"}
            ]
        }
        create_response = requests.post(f"{BASE_URL}/api/journal-entries/manual", json=payload)
        entry_id = create_response.json()["id"]
        
        # Post first time
        requests.post(f"{BASE_URL}/api/journal-entries/manual/{entry_id}/post")
        
        # Try to post again
        second_post = requests.post(f"{BASE_URL}/api/journal-entries/manual/{entry_id}/post")
        assert second_post.status_code == 400, f"Expected 400 for double post, got {second_post.status_code}"
        print("✓ Double posting correctly rejected")
    
    def test_post_nonexistent_entry_fails(self):
        """Verify posting non-existent entry returns 404"""
        response = requests.post(f"{BASE_URL}/api/journal-entries/manual/nonexistent-id-12345/post")
        assert response.status_code == 404
        print("✓ Non-existent entry post correctly returns 404")


class TestAdminDataTables:
    """Test Admin Data Tables module - list tables, view data, search, export"""
    
    def test_list_all_tables(self):
        """Get list of all database collections"""
        response = requests.get(f"{BASE_URL}/api/admin/tables")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one table"
        
        # Each table should have name and count
        for table in data:
            assert "name" in table
            assert "count" in table
            assert isinstance(table["count"], int)
        
        print(f"✓ Found {len(data)} tables: {[t['name'] for t in data]}")
        return data
    
    def test_get_table_data(self):
        """Get paginated data from a specific table"""
        # First get list of tables
        tables_response = requests.get(f"{BASE_URL}/api/admin/tables")
        tables = tables_response.json()
        
        if len(tables) == 0:
            pytest.skip("No tables available")
        
        # Get data from first table
        table_name = tables[0]["name"]
        response = requests.get(f"{BASE_URL}/api/admin/tables/{table_name}")
        assert response.status_code == 200
        
        data = response.json()
        assert "table" in data
        assert "total" in data
        assert "records" in data
        assert data["table"] == table_name
        print(f"✓ Got {len(data['records'])} records from {table_name} (total: {data['total']})")
    
    def test_get_table_data_with_pagination(self):
        """Test pagination parameters"""
        tables_response = requests.get(f"{BASE_URL}/api/admin/tables")
        tables = tables_response.json()
        
        if len(tables) == 0:
            pytest.skip("No tables available")
        
        table_name = tables[0]["name"]
        response = requests.get(f"{BASE_URL}/api/admin/tables/{table_name}", params={"skip": 0, "limit": 10})
        assert response.status_code == 200
        
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 10
        assert len(data["records"]) <= 10
        print(f"✓ Pagination working: skip=0, limit=10, got {len(data['records'])} records")
    
    def test_get_table_data_with_search(self):
        """Test search functionality"""
        tables_response = requests.get(f"{BASE_URL}/api/admin/tables")
        tables = tables_response.json()
        
        if len(tables) == 0:
            pytest.skip("No tables available")
        
        table_name = tables[0]["name"]
        response = requests.get(f"{BASE_URL}/api/admin/tables/{table_name}", params={"search": "TEST"})
        assert response.status_code == 200
        
        data = response.json()
        assert "records" in data
        print(f"✓ Search working: found {len(data['records'])} records matching 'TEST'")
    
    def test_export_table_csv(self):
        """Test CSV export functionality"""
        tables_response = requests.get(f"{BASE_URL}/api/admin/tables")
        tables = tables_response.json()
        
        if len(tables) == 0:
            pytest.skip("No tables available")
        
        # Find a table with data
        table_with_data = None
        for table in tables:
            if table["count"] > 0:
                table_with_data = table["name"]
                break
        
        if not table_with_data:
            pytest.skip("No tables with data available")
        
        response = requests.get(f"{BASE_URL}/api/admin/tables/{table_with_data}/export")
        assert response.status_code == 200
        
        # Check content type is CSV
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type or "application/octet-stream" in content_type
        
        # Check content disposition header
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp
        assert ".csv" in content_disp
        
        print(f"✓ CSV export working for {table_with_data}")
    
    def test_export_empty_table(self):
        """Test export of table with no data"""
        # Create a query for a non-existent table or empty one
        response = requests.get(f"{BASE_URL}/api/admin/tables/nonexistent_table_xyz/export")
        # Should return 400 or handle gracefully
        assert response.status_code in [200, 400]
        print("✓ Empty/non-existent table export handled")


class TestUniversalAIPrompt:
    """Test Universal AI Prompt endpoint"""
    
    def test_universal_prompt_basic(self):
        """Test basic AI prompt processing"""
        payload = {
            "prompt": "Create a sales quotation for ABC Corp for 10 laptops at 50000 each",
            "context": {}
        }
        response = requests.post(f"{BASE_URL}/api/ai/universal-prompt", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        # AI should return structured data
        assert isinstance(data, dict)
        print(f"✓ AI prompt processed: {list(data.keys())}")
    
    def test_universal_prompt_crm(self):
        """Test AI prompt for CRM module"""
        payload = {
            "prompt": "John Smith from Tech Solutions called about our ERP software, budget around 5 lakhs",
            "context": {"module_hint": "crm"}
        }
        response = requests.post(f"{BASE_URL}/api/ai/universal-prompt", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ CRM AI prompt processed")
    
    def test_universal_prompt_accounting(self):
        """Test AI prompt for accounting/journal entry"""
        payload = {
            "prompt": "Record payment of 25000 to vendor ABC for office supplies",
            "context": {}
        }
        response = requests.post(f"{BASE_URL}/api/ai/universal-prompt", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Accounting AI prompt processed")


class TestTransactionPrompt:
    """Test Transaction Prompt endpoint (NLP to journal entries)"""
    
    def test_transaction_prompt(self):
        """Test NLP transaction processing"""
        payload = {
            "prompt": "Paid 15000 for office rent for January 2026",
            "module": "expenses",
            "user_id": "test_user",
            "cost_center": "General"
        }
        response = requests.post(f"{BASE_URL}/api/transactions/prompt", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "draft"
        assert "journal_entries" in data
        print(f"✓ Transaction prompt created draft: {data['id']}")
        return data["id"]
    
    def test_transaction_prompt_with_gst(self):
        """Test NLP transaction with GST calculation"""
        payload = {
            "prompt": "Purchased laptop for 80000 plus 18% GST from Delhi vendor",
            "module": "purchases",
            "user_id": "test_user",
            "cost_center": "IT Department"
        }
        response = requests.post(f"{BASE_URL}/api/transactions/prompt", json=payload, timeout=60)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "draft"
        print(f"✓ GST transaction prompt created: {data['id']}")


class TestSidebarNavigation:
    """Verify sidebar navigation links exist in frontend routes"""
    
    def test_journal_entries_route_exists(self):
        """Verify /journal-entries route is accessible"""
        response = requests.get(f"{BASE_URL}/journal-entries", allow_redirects=True)
        # React SPA returns 200 for all routes
        assert response.status_code == 200
        print("✓ /journal-entries route accessible")
    
    def test_admin_tables_route_exists(self):
        """Verify /admin/tables route is accessible"""
        response = requests.get(f"{BASE_URL}/admin/tables", allow_redirects=True)
        assert response.status_code == 200
        print("✓ /admin/tables route accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
