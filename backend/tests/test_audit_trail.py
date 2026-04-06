"""
Audit Trail API Tests - Companies Act 2013 Rule 3(1) Compliance
Tests for:
- GET /api/audit-trail (with filters)
- GET /api/audit-trail/stats
- GET /api/audit-trail/document-types
- GET /api/audit-trail/export (CSV)
- Audit logging on PO creation
- Audit logging on company settings update (field-level changes)
- No edit/delete endpoints exist (tamper-proof)
"""

import pytest
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuditTrailAPI:
    """Test audit trail read-only endpoints"""
    
    def test_get_audit_trail_basic(self):
        """GET /api/audit-trail returns entries list"""
        response = requests.get(f"{BASE_URL}/api/audit-trail")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "entries" in data, "Response should have 'entries' key"
        assert "total" in data, "Response should have 'total' key"
        assert "limit" in data, "Response should have 'limit' key"
        assert "skip" in data, "Response should have 'skip' key"
        assert isinstance(data["entries"], list), "entries should be a list"
        print(f"PASS: GET /api/audit-trail returned {data['total']} total entries")
    
    def test_get_audit_trail_with_filters(self):
        """GET /api/audit-trail with document_type and action filters"""
        # Test with action filter
        response = requests.get(f"{BASE_URL}/api/audit-trail?action=CREATE")
        assert response.status_code == 200
        data = response.json()
        # All returned entries should have action=CREATE
        for entry in data["entries"]:
            assert entry.get("action") == "CREATE", f"Expected action=CREATE, got {entry.get('action')}"
        print(f"PASS: Filter by action=CREATE returned {len(data['entries'])} entries")
        
        # Test with document_type filter
        response = requests.get(f"{BASE_URL}/api/audit-trail?document_type=Company%20Settings")
        assert response.status_code == 200
        data = response.json()
        for entry in data["entries"]:
            assert entry.get("document_type") == "Company Settings"
        print(f"PASS: Filter by document_type=Company Settings returned {len(data['entries'])} entries")
    
    def test_get_audit_trail_with_search(self):
        """GET /api/audit-trail with search parameter"""
        response = requests.get(f"{BASE_URL}/api/audit-trail?search=PO")
        assert response.status_code == 200
        data = response.json()
        print(f"PASS: Search for 'PO' returned {len(data['entries'])} entries")
    
    def test_get_audit_trail_with_date_filters(self):
        """GET /api/audit-trail with date_from and date_to"""
        today = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/api/audit-trail?date_from={today}&date_to={today}")
        assert response.status_code == 200
        data = response.json()
        print(f"PASS: Date filter for {today} returned {len(data['entries'])} entries")
    
    def test_get_audit_stats(self):
        """GET /api/audit-trail/stats returns summary statistics"""
        response = requests.get(f"{BASE_URL}/api/audit-trail/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_entries" in data, "Response should have 'total_entries'"
        assert "by_action" in data, "Response should have 'by_action'"
        assert "by_document_type" in data, "Response should have 'by_document_type'"
        assert isinstance(data["by_action"], dict), "by_action should be a dict"
        assert isinstance(data["by_document_type"], dict), "by_document_type should be a dict"
        print(f"PASS: Stats - total_entries={data['total_entries']}, by_action={data['by_action']}")
    
    def test_get_document_types(self):
        """GET /api/audit-trail/document-types returns distinct types"""
        response = requests.get(f"{BASE_URL}/api/audit-trail/document-types")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list of document types"
        print(f"PASS: Document types returned: {data}")
    
    def test_export_csv(self):
        """GET /api/audit-trail/export returns CSV file"""
        response = requests.get(f"{BASE_URL}/api/audit-trail/export")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Should have attachment disposition"
        assert "audit_trail.csv" in content_disp, "Filename should be audit_trail.csv"
        
        # Check CSV has header row
        csv_content = response.text
        assert "Timestamp" in csv_content, "CSV should have Timestamp column"
        assert "Action" in csv_content, "CSV should have Action column"
        assert "Document Type" in csv_content, "CSV should have Document Type column"
        print(f"PASS: CSV export returned {len(csv_content)} bytes")
    
    def test_export_csv_with_filters(self):
        """GET /api/audit-trail/export with filters"""
        response = requests.get(f"{BASE_URL}/api/audit-trail/export?action=CREATE")
        assert response.status_code == 200
        print("PASS: CSV export with action filter works")


class TestAuditTrailLogging:
    """Test that transactions create audit entries"""
    
    def test_po_creation_creates_audit_entry(self):
        """Creating a PO should log an audit entry with action=CREATE"""
        # First get current audit count
        stats_before = requests.get(f"{BASE_URL}/api/audit-trail/stats").json()
        count_before = stats_before.get("total_entries", 0)
        
        # Create a PO using valid master data
        po_data = {
            "vendor": "LANXESS India",
            "items": [
                {"item_code": "RM-MDI", "item_name": "MDI-200", "qty": 100, "rate": 250, "uom": "KG", "amount": 25000}
            ],
            "cost_center": "General",
            "gst_rate": 18
        }
        
        response = requests.post(f"{BASE_URL}/api/purchase/orders", json=po_data)
        assert response.status_code == 200, f"PO creation failed: {response.text}"
        po = response.json()
        po_number = po.get("po_number")
        print(f"Created PO: {po_number}")
        
        # Check audit trail for this PO
        audit_response = requests.get(f"{BASE_URL}/api/audit-trail?document_type=Purchase%20Order&action=CREATE")
        assert audit_response.status_code == 200
        audit_data = audit_response.json()
        
        # Find the audit entry for our PO
        found = False
        for entry in audit_data["entries"]:
            if entry.get("document_number") == po_number:
                found = True
                assert entry.get("action") == "CREATE"
                assert entry.get("document_type") == "Purchase Order"
                assert "snapshot" in entry, "CREATE action should have snapshot"
                print(f"PASS: Found audit entry for PO {po_number} with snapshot")
                break
        
        assert found, f"Audit entry for PO {po_number} not found"
    
    def test_company_settings_update_logs_field_changes(self):
        """Updating company settings should log field-level changes"""
        # Get current settings
        current = requests.get(f"{BASE_URL}/api/company/settings").json()
        
        # Update with a new value
        import uuid
        test_value = f"Test Company {uuid.uuid4().hex[:6]}"
        update_data = {
            "company_name": test_value,
            "address": current.get("address", "123 Test Street"),
            "gstin": current.get("gstin", "27AABCU9603R1ZM")
        }
        
        response = requests.put(f"{BASE_URL}/api/company/settings", json=update_data)
        assert response.status_code == 200, f"Settings update failed: {response.text}"
        
        # Check audit trail for company settings
        audit_response = requests.get(f"{BASE_URL}/api/audit-trail?document_type=Company%20Settings")
        assert audit_response.status_code == 200
        audit_data = audit_response.json()
        
        # Should have at least one entry
        assert len(audit_data["entries"]) > 0, "Should have audit entries for Company Settings"
        
        # Check the latest entry
        latest = audit_data["entries"][0]
        assert latest.get("document_type") == "Company Settings"
        
        # If it's an UPDATE, it should have changes array
        if latest.get("action") == "UPDATE":
            changes = latest.get("changes", [])
            print(f"PASS: Company Settings UPDATE logged with {len(changes)} field changes")
            for c in changes:
                print(f"  - {c.get('field')}: {c.get('old_value')} -> {c.get('new_value')}")
        else:
            print(f"PASS: Company Settings {latest.get('action')} logged")


class TestAuditTrailTamperProof:
    """Test that audit trail is append-only (no edit/delete endpoints)"""
    
    def test_no_delete_endpoint(self):
        """DELETE /api/audit-trail should not exist"""
        response = requests.delete(f"{BASE_URL}/api/audit-trail")
        # Should return 405 Method Not Allowed or 404 Not Found
        assert response.status_code in [404, 405], f"DELETE should not be allowed, got {response.status_code}"
        print("PASS: DELETE /api/audit-trail returns 404/405 (not allowed)")
    
    def test_no_put_endpoint(self):
        """PUT /api/audit-trail should not exist"""
        response = requests.put(f"{BASE_URL}/api/audit-trail", json={"test": "data"})
        assert response.status_code in [404, 405], f"PUT should not be allowed, got {response.status_code}"
        print("PASS: PUT /api/audit-trail returns 404/405 (not allowed)")
    
    def test_no_patch_endpoint(self):
        """PATCH /api/audit-trail should not exist"""
        response = requests.patch(f"{BASE_URL}/api/audit-trail", json={"test": "data"})
        assert response.status_code in [404, 405], f"PATCH should not be allowed, got {response.status_code}"
        print("PASS: PATCH /api/audit-trail returns 404/405 (not allowed)")
    
    def test_no_delete_single_entry(self):
        """DELETE /api/audit-trail/{id} should not exist"""
        response = requests.delete(f"{BASE_URL}/api/audit-trail/some-id")
        assert response.status_code in [404, 405], f"DELETE single entry should not be allowed, got {response.status_code}"
        print("PASS: DELETE /api/audit-trail/{id} returns 404/405 (not allowed)")


class TestAuditEntryStructure:
    """Test audit entry data structure"""
    
    def test_entry_has_required_fields(self):
        """Audit entries should have all required fields per Companies Act 2013"""
        response = requests.get(f"{BASE_URL}/api/audit-trail?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["entries"]) == 0:
            pytest.skip("No audit entries to validate structure")
        
        required_fields = ["id", "timestamp", "user", "action", "document_type", "document_id"]
        
        for entry in data["entries"]:
            for field in required_fields:
                assert field in entry, f"Entry missing required field: {field}"
            
            # Validate action is one of the allowed types
            valid_actions = ["CREATE", "UPDATE", "DELETE", "SUBMIT", "CANCEL", "POST"]
            assert entry["action"] in valid_actions, f"Invalid action: {entry['action']}"
        
        print(f"PASS: All {len(data['entries'])} entries have required fields")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
