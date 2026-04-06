"""
Test AI-First Module Entry with Master Data Validation
Tests for:
1. AI prompt bar functionality in Buying, Selling, Manufacturing, Journal Entry modules
2. Strict master data validation (vendor/customer/item must exist)
3. Backend validation for PO/SO creation with non-existent entities
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMasterDataValidation:
    """Test strict master data validation for PO and SO creation"""
    
    def test_po_with_valid_vendor_and_item(self):
        """Create PO with valid vendor and item from master data"""
        payload = {
            "vendor": "LANXESS India",
            "items": [{"item_code": "RM-MDI", "item_name": "MDI", "qty": 3000, "rate": 262, "uom": "KG", "amount": 786000}],
            "gst_rate": 18,
            "cost_center": "Production-U1"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/orders", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "po_number" in data
        assert data["vendor"] == "LANXESS India"
        assert data["status"] == "Submitted"
        print(f"✓ PO created successfully: {data['po_number']}")
    
    def test_po_with_invalid_vendor_returns_400(self):
        """POST /api/purchase/orders with non-existent vendor should return 400"""
        payload = {
            "vendor": "Fake Vendor XYZ",
            "items": [{"item_code": "EP-1000", "item_name": "EP-1000", "qty": 100, "rate": 100, "uom": "KG", "amount": 10000}],
            "gst_rate": 18,
            "cost_center": "Manufacturing"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/orders", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid vendor, got {response.status_code}"
        data = response.json()
        assert "not found in master data" in data.get("detail", "").lower() or "vendor" in data.get("detail", "").lower()
        print(f"✓ Backend correctly rejected PO with invalid vendor: {data['detail']}")
    
    def test_po_with_invalid_item_returns_400(self):
        """POST /api/purchase/orders with non-existent item should return 400"""
        payload = {
            "vendor": "INEOS India",
            "items": [{"item_code": "FAKE-ITEM-999", "item_name": "Fake Item", "qty": 100, "rate": 100, "uom": "KG", "amount": 10000}],
            "gst_rate": 18,
            "cost_center": "Manufacturing"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/orders", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid item, got {response.status_code}"
        data = response.json()
        assert "not found in master data" in data.get("detail", "").lower() or "item" in data.get("detail", "").lower()
        print(f"✓ Backend correctly rejected PO with invalid item: {data['detail']}")
    
    def test_so_with_valid_customer_and_item(self):
        """Create SO with valid customer and item from master data"""
        payload = {
            "customer": "L&T Construction",
            "items": [{"item_code": "EP-1000", "item_name": "EP-1000 Epoxy Resin", "qty": 1000, "rate": 520, "uom": "KG", "amount": 520000}],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        response = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "so_number" in data
        assert data["customer"] == "L&T Construction"
        assert data["status"] == "Submitted"
        print(f"✓ SO created successfully: {data['so_number']}")
    
    def test_so_with_invalid_customer_returns_400(self):
        """POST /api/selling/sales-orders with non-existent customer should return 400"""
        payload = {
            "customer": "Non-Existent Customer Corp",
            "items": [{"item_code": "EP-1000", "item_name": "EP-1000", "qty": 100, "rate": 520, "uom": "KG", "amount": 52000}],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        response = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid customer, got {response.status_code}"
        data = response.json()
        assert "not found in master data" in data.get("detail", "").lower() or "customer" in data.get("detail", "").lower()
        print(f"✓ Backend correctly rejected SO with invalid customer: {data['detail']}")
    
    def test_so_with_invalid_item_returns_400(self):
        """POST /api/selling/sales-orders with non-existent item should return 400"""
        payload = {
            "customer": "Asian Paints Ltd.",
            "items": [{"item_code": "NONEXISTENT-ITEM", "item_name": "Fake Product", "qty": 100, "rate": 500, "uom": "KG", "amount": 50000}],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        response = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid item, got {response.status_code}"
        data = response.json()
        assert "not found in master data" in data.get("detail", "").lower() or "item" in data.get("detail", "").lower()
        print(f"✓ Backend correctly rejected SO with invalid item: {data['detail']}")


class TestAIParsePromptForModules:
    """Test AI parse-prompt endpoint for different module intents"""
    
    def test_ai_parse_purchase_order_prompt(self):
        """AI should parse PO prompt and return purchase_order intent"""
        payload = {"prompt": "PO for 3000 KG MDI-200 from LANXESS India at 262/KG"}
        response = requests.post(f"{BASE_URL}/api/ai/parse-prompt", json=payload, timeout=30)
        assert response.status_code == 200, f"AI parse failed: {response.text}"
        data = response.json()
        assert data.get("intent") == "purchase_order", f"Expected purchase_order intent, got {data.get('intent')}"
        assert data.get("confidence", 0) > 0.5, "Confidence should be > 0.5"
        assert "master_data" in data, "Response should include master_data"
        assert "vendors" in data["master_data"], "master_data should include vendors list"
        print(f"✓ AI parsed PO prompt: intent={data['intent']}, confidence={data['confidence']}")
    
    def test_ai_parse_sales_order_prompt(self):
        """AI should parse SO prompt and return sales_order intent"""
        payload = {"prompt": "SO for L&T Construction 1000 KG EP-1000 at 520/KG"}
        response = requests.post(f"{BASE_URL}/api/ai/parse-prompt", json=payload, timeout=30)
        assert response.status_code == 200, f"AI parse failed: {response.text}"
        data = response.json()
        assert data.get("intent") == "sales_order", f"Expected sales_order intent, got {data.get('intent')}"
        assert "master_data" in data
        assert "customers" in data["master_data"]
        print(f"✓ AI parsed SO prompt: intent={data['intent']}, confidence={data['confidence']}")
    
    def test_ai_parse_work_order_prompt(self):
        """AI should parse work order prompt and return work_order intent"""
        payload = {"prompt": "Produce 2000 KG PU-C450"}
        response = requests.post(f"{BASE_URL}/api/ai/parse-prompt", json=payload, timeout=30)
        assert response.status_code == 200, f"AI parse failed: {response.text}"
        data = response.json()
        assert data.get("intent") == "work_order", f"Expected work_order intent, got {data.get('intent')}"
        assert "master_data" in data
        print(f"✓ AI parsed work order prompt: intent={data['intent']}, confidence={data['confidence']}")
    
    def test_ai_parse_journal_entry_prompt(self):
        """AI should parse JE prompt and return journal_entry intent"""
        payload = {"prompt": "Debit Utility Expense 50000, Credit Cash & Bank (HDFC Current) 50000"}
        response = requests.post(f"{BASE_URL}/api/ai/parse-prompt", json=payload, timeout=30)
        assert response.status_code == 200, f"AI parse failed: {response.text}"
        data = response.json()
        assert data.get("intent") == "journal_entry", f"Expected journal_entry intent, got {data.get('intent')}"
        assert "master_data" in data
        assert "ledgers" in data["master_data"]
        print(f"✓ AI parsed JE prompt: intent={data['intent']}, confidence={data['confidence']}")
    
    def test_ai_parse_returns_master_data_for_dropdowns(self):
        """AI parse should return master data lists for strict dropdowns"""
        payload = {"prompt": "Create PO for 100 KG EP-1000 from INEOS India"}
        response = requests.post(f"{BASE_URL}/api/ai/parse-prompt", json=payload, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Verify master_data structure
        md = data.get("master_data", {})
        assert "vendors" in md, "Missing vendors in master_data"
        assert "customers" in md, "Missing customers in master_data"
        assert "items" in md, "Missing items in master_data"
        assert "cost_centers" in md, "Missing cost_centers in master_data"
        assert "ledgers" in md, "Missing ledgers in master_data"
        
        # Verify vendors list contains expected vendors
        assert "INEOS India" in md["vendors"], "INEOS India should be in vendors list"
        assert "LANXESS India" in md["vendors"], "LANXESS India should be in vendors list"
        
        # Verify items list structure
        assert len(md["items"]) > 0, "Items list should not be empty"
        assert any(i.get("code") == "EP-1000" for i in md["items"]), "EP-1000 should be in items list"
        
        print(f"✓ AI parse returns complete master_data: {len(md['vendors'])} vendors, {len(md['customers'])} customers, {len(md['items'])} items")


class TestSeededDataIntegrity:
    """Verify seeded data is intact"""
    
    def test_purchase_orders_count(self):
        """Should have 12+ POs (10 seeded + 2 AI-created from previous tests)"""
        response = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 12, f"Expected at least 12 POs, got {len(data)}"
        print(f"✓ Found {len(data)} purchase orders")
    
    def test_sales_orders_count(self):
        """Should have 8+ SOs"""
        response = requests.get(f"{BASE_URL}/api/selling/sales-orders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 8, f"Expected at least 8 SOs, got {len(data)}"
        print(f"✓ Found {len(data)} sales orders")
    
    def test_vendors_exist(self):
        """Verify master vendors exist"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        assert response.status_code == 200
        data = response.json()
        vendor_names = [v["name"] for v in data]
        expected_vendors = ["INEOS India", "LANXESS India", "Reliance Petrochemicals"]
        for v in expected_vendors:
            assert v in vendor_names, f"Expected vendor {v} not found"
        print(f"✓ Found {len(data)} vendors including expected ones")
    
    def test_customers_exist(self):
        """Verify master customers exist"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=customer")
        assert response.status_code == 200
        data = response.json()
        customer_names = [c["name"] for c in data]
        expected_customers = ["Asian Paints Ltd.", "L&T Construction", "Pidilite Industries"]
        for c in expected_customers:
            assert c in customer_names, f"Expected customer {c} not found"
        print(f"✓ Found {len(data)} customers including expected ones")
    
    def test_items_exist(self):
        """Verify master items exist"""
        response = requests.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        data = response.json()
        item_codes = [i["item_code"] for i in data]
        expected_items = ["EP-1000", "EP-2500", "PU-C450", "RM-MDI"]
        for i in expected_items:
            assert i in item_codes, f"Expected item {i} not found"
        print(f"✓ Found {len(data)} items including expected ones")


class TestManufacturingWorkOrders:
    """Test Manufacturing module work order creation"""
    
    def test_create_work_order(self):
        """Create work order for FG item"""
        payload = {
            "production_item": "PU-C450",
            "qty_to_produce": 500,
            "cost_center": "Production-U1",
            "bom_items": []
        }
        response = requests.post(f"{BASE_URL}/api/manufacturing/work-orders", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "wo_number" in data
        assert data["production_item"] == "PU-C450"
        assert data["status"] == "Draft"
        print(f"✓ Work order created: {data['wo_number']}")
    
    def test_list_work_orders(self):
        """List work orders"""
        response = requests.get(f"{BASE_URL}/api/manufacturing/work-orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Found {len(data)} work orders")


class TestJournalEntryCreation:
    """Test Journal Entry module"""
    
    def test_create_manual_journal_entry(self):
        """Create manual journal entry"""
        payload = {
            "posting_date": "2026-04-06",
            "cost_center": "General",
            "journal_entries": [
                {"account": "Utility Expense", "debit": 25000, "credit": 0, "description": "Test utility expense"},
                {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 25000, "description": "Payment"}
            ],
            "narration": "Test JE for utility expense"
        }
        response = requests.post(f"{BASE_URL}/api/journal-entries/manual", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["status"] == "Draft"
        print(f"✓ Journal entry created: {data['id']}")
    
    def test_list_manual_journal_entries(self):
        """List manual journal entries"""
        response = requests.get(f"{BASE_URL}/api/journal-entries/manual")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Found {len(data)} manual journal entries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
