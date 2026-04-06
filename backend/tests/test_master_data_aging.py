# Test Master Data (Vendors, Customers, Items) and AP/AR Aging APIs
# Iteration 14: P0 completion testing

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestVendorsAPI:
    """Test Vendors CRUD operations"""
    
    def test_get_vendors_returns_200(self):
        """GET /api/entities?entity_type=vendor returns 200"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET vendors: {len(data)} vendors found")
    
    def test_vendors_have_required_fields(self):
        """Vendors have name, entity_type, status fields"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        assert response.status_code == 200
        vendors = response.json()
        if len(vendors) > 0:
            vendor = vendors[0]
            assert "name" in vendor
            assert "entity_type" in vendor
            assert vendor["entity_type"] == "vendor"
            print(f"✓ Vendor fields verified: {vendor['name']}")
    
    def test_create_vendor_success(self):
        """POST /api/entities creates vendor successfully"""
        test_vendor = {
            "entity_type": "vendor",
            "name": f"TEST_Vendor_{uuid.uuid4().hex[:6]}",
            "gstin": "27AABCT1234A1Z5",
            "state": "Maharashtra",
            "payment_terms": "Net 30",
            "status": "Active"
        }
        response = requests.post(f"{BASE_URL}/api/entities", json=test_vendor)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_vendor["name"]
        assert data["entity_type"] == "vendor"
        print(f"✓ Created vendor: {data['name']}")
    
    def test_create_vendor_with_gstin_validation(self):
        """POST /api/entities validates GSTIN and enriches data"""
        test_vendor = {
            "entity_type": "vendor",
            "name": f"TEST_GSTIN_Vendor_{uuid.uuid4().hex[:6]}",
            "gstin": "24AABCI1234A1Z5",  # Gujarat GSTIN
        }
        response = requests.post(f"{BASE_URL}/api/entities", json=test_vendor)
        assert response.status_code == 200
        data = response.json()
        # GSTIN validation should enrich state info
        assert "gst_state_code" in data or "state" in data
        print(f"✓ GSTIN validation: state={data.get('state', data.get('gst_state_code'))}")


class TestCustomersAPI:
    """Test Customers CRUD operations"""
    
    def test_get_customers_returns_200(self):
        """GET /api/entities?entity_type=customer returns 200"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=customer")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET customers: {len(data)} customers found")
    
    def test_customers_have_required_fields(self):
        """Customers have name, entity_type fields"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=customer")
        assert response.status_code == 200
        customers = response.json()
        if len(customers) > 0:
            customer = customers[0]
            assert "name" in customer
            assert "entity_type" in customer
            assert customer["entity_type"] == "customer"
            print(f"✓ Customer fields verified: {customer['name']}")
    
    def test_create_customer_success(self):
        """POST /api/entities creates customer successfully"""
        test_customer = {
            "entity_type": "customer",
            "name": f"TEST_Customer_{uuid.uuid4().hex[:6]}",
            "gstin": "27AABCC5678B1Z2",
            "state": "Maharashtra",
            "credit_limit": 500000,
            "status": "Active"
        }
        response = requests.post(f"{BASE_URL}/api/entities", json=test_customer)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_customer["name"]
        assert data["entity_type"] == "customer"
        print(f"✓ Created customer: {data['name']}")


class TestItemsAPI:
    """Test Items/Stock CRUD operations"""
    
    def test_get_items_returns_200(self):
        """GET /api/stock/items returns 200"""
        response = requests.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET items: {len(data)} items found")
    
    def test_items_have_required_fields(self):
        """Items have item_code, item_name, hsn_sac, gst_rate, uom"""
        response = requests.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        items = response.json()
        if len(items) > 0:
            item = items[0]
            assert "item_code" in item
            assert "item_name" in item
            # hsn_sac or hsn should exist
            assert "hsn_sac" in item or "hsn" in item
            assert "gst_rate" in item
            assert "uom" in item
            print(f"✓ Item fields verified: {item['item_code']} - {item['item_name']}")
    
    def test_create_item_success(self):
        """POST /api/stock/items creates item successfully"""
        test_item = {
            "item_code": f"TEST-{uuid.uuid4().hex[:6]}",
            "item_name": f"Test Item {uuid.uuid4().hex[:6]}",
            "hsn_sac": "3901",
            "gst_rate": 18,
            "uom": "KG",
            "valuation_method": "FIFO",
            "opening_stock": 100
        }
        response = requests.post(f"{BASE_URL}/api/stock/items", json=test_item)
        assert response.status_code == 200
        data = response.json()
        assert data["item_code"] == test_item["item_code"]
        assert data["item_name"] == test_item["item_name"]
        print(f"✓ Created item: {data['item_code']}")


class TestAgingPayablesAPI:
    """Test AP Aging Report API"""
    
    def test_ap_aging_returns_200(self):
        """GET /api/aging/payables returns 200"""
        response = requests.get(f"{BASE_URL}/api/aging/payables")
        assert response.status_code == 200
        data = response.json()
        assert "report_type" in data
        assert data["report_type"] == "Accounts Payable Aging"
        print(f"✓ AP Aging report loaded")
    
    def test_ap_aging_has_buckets(self):
        """AP Aging has 0-30, 30-60, 60-90, 90+ buckets"""
        response = requests.get(f"{BASE_URL}/api/aging/payables")
        assert response.status_code == 200
        data = response.json()
        assert "buckets" in data
        buckets = data["buckets"]
        assert "0-30" in buckets
        assert "30-60" in buckets
        assert "60-90" in buckets
        assert "90+" in buckets
        print(f"✓ AP buckets: 0-30={buckets['0-30']}, 30-60={buckets['30-60']}, 60-90={buckets['60-90']}, 90+={buckets['90+']}")
    
    def test_ap_aging_has_total_outstanding(self):
        """AP Aging has total_outstanding field"""
        response = requests.get(f"{BASE_URL}/api/aging/payables")
        assert response.status_code == 200
        data = response.json()
        assert "total_outstanding" in data
        assert isinstance(data["total_outstanding"], (int, float))
        print(f"✓ AP total outstanding: {data['total_outstanding']}")
    
    def test_ap_aging_has_vendor_breakdown(self):
        """AP Aging has by_vendor breakdown"""
        response = requests.get(f"{BASE_URL}/api/aging/payables")
        assert response.status_code == 200
        data = response.json()
        assert "by_vendor" in data
        assert isinstance(data["by_vendor"], list)
        if len(data["by_vendor"]) > 0:
            vendor = data["by_vendor"][0]
            assert "vendor" in vendor
            assert "total" in vendor
            print(f"✓ AP by_vendor: {len(data['by_vendor'])} vendors, top={vendor['vendor']}")
    
    def test_ap_aging_has_details(self):
        """AP Aging has invoice details"""
        response = requests.get(f"{BASE_URL}/api/aging/payables")
        assert response.status_code == 200
        data = response.json()
        assert "details" in data
        if len(data["details"]) > 0:
            detail = data["details"][0]
            assert "invoice_number" in detail
            assert "outstanding" in detail
            assert "bucket" in detail
            print(f"✓ AP details: {len(data['details'])} invoices")


class TestAgingReceivablesAPI:
    """Test AR Aging Report API"""
    
    def test_ar_aging_returns_200(self):
        """GET /api/aging/receivables returns 200"""
        response = requests.get(f"{BASE_URL}/api/aging/receivables")
        assert response.status_code == 200
        data = response.json()
        assert "report_type" in data
        assert data["report_type"] == "Accounts Receivable Aging"
        print(f"✓ AR Aging report loaded")
    
    def test_ar_aging_has_buckets(self):
        """AR Aging has 0-30, 30-60, 60-90, 90+ buckets"""
        response = requests.get(f"{BASE_URL}/api/aging/receivables")
        assert response.status_code == 200
        data = response.json()
        assert "buckets" in data
        buckets = data["buckets"]
        assert "0-30" in buckets
        assert "30-60" in buckets
        assert "60-90" in buckets
        assert "90+" in buckets
        print(f"✓ AR buckets: 0-30={buckets['0-30']}, 30-60={buckets['30-60']}, 60-90={buckets['60-90']}, 90+={buckets['90+']}")
    
    def test_ar_aging_has_total_outstanding(self):
        """AR Aging has total_outstanding field"""
        response = requests.get(f"{BASE_URL}/api/aging/receivables")
        assert response.status_code == 200
        data = response.json()
        assert "total_outstanding" in data
        assert isinstance(data["total_outstanding"], (int, float))
        print(f"✓ AR total outstanding: {data['total_outstanding']}")
    
    def test_ar_aging_has_customer_breakdown(self):
        """AR Aging has by_customer breakdown"""
        response = requests.get(f"{BASE_URL}/api/aging/receivables")
        assert response.status_code == 200
        data = response.json()
        assert "by_customer" in data
        assert isinstance(data["by_customer"], list)
        if len(data["by_customer"]) > 0:
            customer = data["by_customer"][0]
            assert "customer" in customer
            assert "total" in customer
            print(f"✓ AR by_customer: {len(data['by_customer'])} customers, top={customer['customer']}")


class TestCompanySettingsAPI:
    """Test Company Settings API"""
    
    def test_company_settings_returns_200(self):
        """GET /api/company/settings returns 200"""
        response = requests.get(f"{BASE_URL}/api/company/settings")
        assert response.status_code == 200
        data = response.json()
        assert "exists" in data
        print(f"✓ Company settings loaded")
    
    def test_company_settings_has_name(self):
        """Company settings has legal_name or company_name"""
        response = requests.get(f"{BASE_URL}/api/company/settings")
        assert response.status_code == 200
        data = response.json()
        assert "legal_name" in data or "company_name" in data
        name = data.get("legal_name") or data.get("company_name")
        print(f"✓ Company name: {name}")
    
    def test_company_settings_has_logo_url(self):
        """Company settings has logo_url"""
        response = requests.get(f"{BASE_URL}/api/company/settings")
        assert response.status_code == 200
        data = response.json()
        assert "logo_url" in data
        print(f"✓ Logo URL: {data['logo_url']}")
    
    def test_company_logo_accessible(self):
        """Company logo file is accessible"""
        settings = requests.get(f"{BASE_URL}/api/company/settings").json()
        logo_url = settings.get("logo_url")
        if logo_url:
            response = requests.get(f"{BASE_URL}{logo_url}")
            assert response.status_code == 200
            assert "image" in response.headers.get("content-type", "")
            print(f"✓ Logo accessible: {logo_url}")


class TestGSTStatesAPI:
    """Test GST States API for dropdown"""
    
    def test_gst_states_returns_200(self):
        """GET /api/gst/states returns 200"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✓ GST states: {len(data)} states")
    
    def test_gst_states_have_code_and_name(self):
        """GST states have code and name fields"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200
        states = response.json()
        if len(states) > 0:
            state = states[0]
            assert "code" in state
            assert "name" in state
            print(f"✓ State fields: code={state['code']}, name={state['name']}")


class TestHSNSuggestAPI:
    """Test AI HSN Suggest API"""
    
    def test_hsn_suggest_endpoint_exists(self):
        """POST /api/gst/suggest-hsn endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/gst/suggest-hsn", json={"description": "test"})
        # Should not be 404
        assert response.status_code != 404
        print(f"✓ HSN suggest endpoint exists (status: {response.status_code})")
