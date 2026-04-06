"""
Test AI Parse Prompt API - Zero-Touch UI Feature
Tests the /api/ai/parse-prompt endpoint for various intents:
- Purchase Order
- Sales Order
- Work Order
- Journal Entry
- Goods Receipt
- Delivery Note
- CRM Lead
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAIParsePrompt:
    """Test AI Parse Prompt endpoint for various intents"""
    
    def test_health_check(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API health check passed: {data}")
    
    def test_parse_purchase_order_prompt(self):
        """Test parsing a Purchase Order prompt"""
        prompt = "Create PO for 5000 KG EP-1000 from Aditya Birla Chemicals at 195 per KG"
        
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-prompt",
            json={"prompt": prompt},
            timeout=30  # AI parsing can take 3-8 seconds
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify intent
        assert "intent" in data, f"Missing 'intent' in response: {data}"
        assert data["intent"] == "purchase_order", f"Expected intent=purchase_order, got {data['intent']}"
        
        # Verify confidence
        assert "confidence" in data, f"Missing 'confidence' in response"
        assert data["confidence"] >= 0.5, f"Low confidence: {data['confidence']}"
        
        # Verify extracted data
        assert "extracted" in data, f"Missing 'extracted' in response"
        extracted = data["extracted"]
        
        # Check for vendor extraction (fuzzy match to Aditya Birla)
        if "vendor" in extracted:
            print(f"  Vendor extracted: {extracted['vendor']}")
        
        # Check for items extraction
        if "items" in extracted:
            print(f"  Items extracted: {extracted['items']}")
            assert len(extracted["items"]) > 0, "No items extracted"
        
        # Verify master_data is included
        assert "master_data" in data, f"Missing 'master_data' in response"
        master_data = data["master_data"]
        assert "vendors" in master_data, "Missing vendors in master_data"
        assert "items" in master_data, "Missing items in master_data"
        
        print(f"✓ Purchase Order prompt parsed successfully")
        print(f"  Intent: {data['intent']}, Confidence: {data['confidence']}")
        print(f"  Summary: {data.get('summary', 'N/A')}")
        print(f"  Missing fields: {data.get('missing', [])}")
    
    def test_parse_sales_order_prompt(self):
        """Test parsing a Sales Order prompt"""
        prompt = "Raise sales order for Asian Paints - 2000 KG EP-2500 at 520/KG"
        
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-prompt",
            json={"prompt": prompt},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify intent
        assert "intent" in data
        assert data["intent"] == "sales_order", f"Expected intent=sales_order, got {data['intent']}"
        
        # Verify extracted data
        assert "extracted" in data
        extracted = data["extracted"]
        
        # Check for customer extraction
        if "customer" in extracted:
            print(f"  Customer extracted: {extracted['customer']}")
        
        # Check for items
        if "items" in extracted:
            print(f"  Items extracted: {extracted['items']}")
        
        # Verify master_data
        assert "master_data" in data
        assert "customers" in data["master_data"]
        
        print(f"✓ Sales Order prompt parsed successfully")
        print(f"  Intent: {data['intent']}, Confidence: {data['confidence']}")
        print(f"  Summary: {data.get('summary', 'N/A')}")
    
    def test_parse_journal_entry_prompt(self):
        """Test parsing a Journal Entry prompt"""
        prompt = "Record salary expense 200000 - debit Salary Expense, credit Salary Payable"
        
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-prompt",
            json={"prompt": prompt},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify intent
        assert "intent" in data
        assert data["intent"] == "journal_entry", f"Expected intent=journal_entry, got {data['intent']}"
        
        # Verify extracted data has entries
        assert "extracted" in data
        extracted = data["extracted"]
        
        if "entries" in extracted:
            print(f"  Journal entries extracted: {extracted['entries']}")
            # Verify debit/credit structure
            for entry in extracted["entries"]:
                assert "account" in entry or "ledger" in entry, "Entry missing account"
        
        # Verify master_data has ledgers
        assert "master_data" in data
        assert "ledgers" in data["master_data"]
        
        print(f"✓ Journal Entry prompt parsed successfully")
        print(f"  Intent: {data['intent']}, Confidence: {data['confidence']}")
        print(f"  Summary: {data.get('summary', 'N/A')}")
    
    def test_parse_work_order_prompt(self):
        """Test parsing a Work Order prompt"""
        prompt = "Start work order for 1000 KG PU-C450"
        
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-prompt",
            json={"prompt": prompt},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify intent
        assert "intent" in data
        assert data["intent"] == "work_order", f"Expected intent=work_order, got {data['intent']}"
        
        # Verify extracted data
        assert "extracted" in data
        extracted = data["extracted"]
        
        # Check for production item
        if "production_item" in extracted:
            print(f"  Production item: {extracted['production_item']}")
        
        # Check for quantity
        if "qty_to_produce" in extracted:
            print(f"  Qty to produce: {extracted['qty_to_produce']}")
        
        print(f"✓ Work Order prompt parsed successfully")
        print(f"  Intent: {data['intent']}, Confidence: {data['confidence']}")
        print(f"  Summary: {data.get('summary', 'N/A')}")
    
    def test_parse_crm_lead_prompt(self):
        """Test parsing a CRM Lead prompt"""
        prompt = "New lead from Reliance Industries, contact Mukesh Shah, phone 9876543210, interested in bulk epoxy resins"
        
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-prompt",
            json={"prompt": prompt},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify intent
        assert "intent" in data
        assert data["intent"] == "crm_lead", f"Expected intent=crm_lead, got {data['intent']}"
        
        # Verify extracted data
        assert "extracted" in data
        extracted = data["extracted"]
        
        # Check for company
        if "company" in extracted:
            print(f"  Company: {extracted['company']}")
        
        # Check for contact name
        if "contact_name" in extracted:
            print(f"  Contact: {extracted['contact_name']}")
        
        print(f"✓ CRM Lead prompt parsed successfully")
        print(f"  Intent: {data['intent']}, Confidence: {data['confidence']}")
        print(f"  Summary: {data.get('summary', 'N/A')}")
    
    def test_parse_empty_prompt_returns_error(self):
        """Test that empty prompt returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-prompt",
            json={"prompt": ""},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for empty prompt, got {response.status_code}"
        print(f"✓ Empty prompt correctly returns 400 error")
    
    def test_master_data_in_response(self):
        """Verify master_data object contains all required lists"""
        prompt = "Create a purchase order"
        
        response = requests.post(
            f"{BASE_URL}/api/ai/parse-prompt",
            json={"prompt": prompt},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "master_data" in data
        md = data["master_data"]
        
        # Check all required master data lists
        required_keys = ["vendors", "customers", "items", "cost_centers", "ledgers", "pending_pos", "pending_sos"]
        for key in required_keys:
            assert key in md, f"Missing '{key}' in master_data"
            print(f"  {key}: {len(md[key])} items")
        
        print(f"✓ Master data contains all required lists")


class TestExistingSeededData:
    """Verify existing seeded data is still intact"""
    
    def test_purchase_orders_count(self):
        """Verify PO count (should be 11: 10 seeded + 1 from AI test)"""
        response = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert response.status_code == 200
        data = response.json()
        
        # Should be at least 10 (original seeded) or 11 (with AI-created PO)
        assert len(data) >= 10, f"Expected at least 10 POs, got {len(data)}"
        print(f"✓ Purchase Orders count: {len(data)}")
    
    def test_sales_orders_count(self):
        """Verify SO count (should be 8)"""
        response = requests.get(f"{BASE_URL}/api/selling/sales-orders")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) >= 8, f"Expected at least 8 SOs, got {len(data)}"
        print(f"✓ Sales Orders count: {len(data)}")
    
    def test_trial_balance_is_balanced(self):
        """Verify Trial Balance is still balanced"""
        response = requests.get(f"{BASE_URL}/api/reports/trial-balance")
        assert response.status_code == 200
        data = response.json()
        
        assert "in_balance" in data
        assert data["in_balance"] == True, f"Trial Balance not balanced! Diff: {data.get('difference', 'N/A')}"
        print(f"✓ Trial Balance is balanced (Debit: {data['total_debit']}, Credit: {data['total_credit']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
