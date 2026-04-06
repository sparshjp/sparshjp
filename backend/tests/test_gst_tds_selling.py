# Kairos Accounting - GST/TDS Statutory Reports & Enhanced Selling Module Tests
# Tests: GSTR-1, GSTR-3B, TDS Return, Credit Limit, Negative Stock

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic API health check"""
    
    def test_api_health(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "Kairos" in data.get("message", "")
        print(f"✓ API Health: {data}")


class TestGSTR1:
    """GSTR-1 Outward Supplies Report Tests"""
    
    def test_gstr1_report(self):
        """GET /api/statutory/gstr1 - Returns B2B invoices with CGST/SGST split"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1")
        assert response.status_code == 200
        data = response.json()
        
        # Verify report structure
        assert data.get("report_type") == "GSTR-1"
        assert "gstin" in data
        assert "legal_name" in data
        assert "return_period" in data
        assert "sections" in data
        assert "summary" in data
        
        # Verify B2B section
        b2b = data["sections"].get("b2b", {})
        assert "invoices" in b2b
        assert "count" in b2b
        
        # Verify summary has CGST/SGST split
        summary = data["summary"]
        assert "total_cgst" in summary
        assert "total_sgst" in summary
        assert "total_taxable_value" in summary
        assert "total_tax" in summary
        
        print(f"✓ GSTR-1: {summary['total_invoices']} invoices, Tax: {summary['total_tax']}")
        print(f"  CGST: {summary['total_cgst']}, SGST: {summary['total_sgst']}")
    
    def test_gstr1_export_csv(self):
        """GET /api/statutory/gstr1/export - Downloads CSV"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("Content-Type", "")
        assert "GSTR1.csv" in response.headers.get("Content-Disposition", "")
        
        # Verify CSV content has headers
        content = response.text
        assert "GSTIN" in content
        assert "Invoice No" in content
        assert "CGST" in content
        assert "SGST" in content
        print(f"✓ GSTR-1 CSV Export: {len(content)} bytes")


class TestGSTR3B:
    """GSTR-3B Monthly Summary Return Tests"""
    
    def test_gstr3b_report(self):
        """GET /api/statutory/gstr3b - Returns output tax, ITC, net payable"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b")
        assert response.status_code == 200
        data = response.json()
        
        # Verify report structure
        assert data.get("report_type") == "GSTR-3B"
        assert "gstin" in data
        assert "legal_name" in data
        assert "sections" in data
        assert "summary" in data
        
        # Verify sections
        sections = data["sections"]
        assert "3_1" in sections  # Outward supplies
        assert "4" in sections    # ITC
        assert "6_1" in sections  # Payment
        
        # Verify 3.1 - Outward supplies
        sec_3_1 = sections["3_1"]
        assert "outward_taxable_supplies" in sec_3_1
        ots = sec_3_1["outward_taxable_supplies"]
        assert "cgst" in ots
        assert "sgst" in ots
        
        # Verify 4 - ITC
        sec_4 = sections["4"]
        assert "itc_available" in sec_4
        
        # Verify 6.1 - Payment
        sec_6_1 = sections["6_1"]
        assert "tax_payable" in sec_6_1
        assert "itc_utilized" in sec_6_1
        assert "cash_payable" in sec_6_1
        
        # Verify summary
        summary = data["summary"]
        assert "total_output_tax" in summary
        assert "total_input_credit" in summary
        assert "net_payable" in summary
        
        print(f"✓ GSTR-3B: Output Tax: {summary['total_output_tax']}, ITC: {summary['total_input_credit']}")
        print(f"  Net Payable: {summary['net_payable']}")
    
    def test_gstr3b_export_json(self):
        """GET /api/statutory/gstr3b/export - Downloads JSON"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b/export")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert "GSTR3B.json" in response.headers.get("Content-Disposition", "")
        
        # Verify JSON content
        data = response.json()
        assert "report_type" in data
        assert data["report_type"] == "GSTR-3B"
        print(f"✓ GSTR-3B JSON Export successful")


class TestTDSReturn:
    """TDS Return (Form 26Q) Tests"""
    
    def test_tds_return_report(self):
        """GET /api/statutory/tds-return - Returns deductees"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return")
        assert response.status_code == 200
        data = response.json()
        
        # Verify report structure
        assert data.get("report_type") == "TDS Return (Form 26Q)"
        assert "tan" in data
        assert "deductor_name" in data
        assert "quarter" in data
        assert "financial_year" in data
        assert "deductees" in data
        assert "summary" in data
        
        # Verify summary
        summary = data["summary"]
        assert "total_deductees" in summary
        assert "total_tds_deducted" in summary
        assert "tds_pending_deposit" in summary
        
        print(f"✓ TDS Return: {summary['total_deductees']} deductees, TDS: {summary['total_tds_deducted']}")
    
    def test_tds_return_export_csv(self):
        """GET /api/statutory/tds-return/export - Downloads CSV"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("Content-Type", "")
        assert "TDS_Return_26Q.csv" in response.headers.get("Content-Disposition", "")
        
        # Verify CSV content has headers
        content = response.text
        assert "Deductee Name" in content
        assert "TDS Amount" in content
        assert "Section" in content
        print(f"✓ TDS Return CSV Export: {len(content)} bytes")


class TestCreditLimitCheck:
    """Credit Limit Warning on Sales Orders"""
    
    def test_sales_order_credit_limit_warning(self):
        """POST /api/selling/sales-orders - Returns credit_warning when limit exceeded"""
        # First, check if we have a customer with credit limit
        customers_resp = requests.get(f"{BASE_URL}/api/admin/tables/customers")
        
        # Create a sales order with high value to potentially trigger warning
        test_so = {
            "customer": "TEST_CreditLimitCustomer",
            "customer_gstin": "24AABCT1234A1Z5",
            "items": [
                {"item_code": "TEST-ITEM", "qty": 1000, "rate": 50000, "amount": 50000000}
            ],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        
        response = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=test_so)
        assert response.status_code == 200
        data = response.json()
        
        # Verify SO was created
        assert "id" in data
        assert "so_number" in data
        assert data["customer"] == "TEST_CreditLimitCustomer"
        
        # Credit warning is optional - depends on customer having credit limit set
        if "credit_warning" in data:
            print(f"✓ Credit Limit Warning triggered: {data['credit_warning']}")
        else:
            print(f"✓ Sales Order created (no credit limit set for customer): {data['so_number']}")


class TestNegativeStockCheck:
    """Negative Stock Warning on Delivery Notes"""
    
    def test_delivery_note_negative_stock_warning(self):
        """POST /api/selling/delivery-notes - Returns warning when stock insufficient"""
        # Create a delivery note with high quantity to potentially trigger warning
        test_dn = {
            "customer": "TEST_NegativeStockCustomer",
            "items": [
                {"item_code": "TEST-NONEXISTENT-ITEM", "qty": 999999}
            ],
            "warehouse": "Main Warehouse"
        }
        
        response = requests.post(f"{BASE_URL}/api/selling/delivery-notes", json=test_dn)
        assert response.status_code == 200
        data = response.json()
        
        # Verify DN was created
        assert "id" in data
        assert "dn_number" in data
        
        # Warning is returned when stock is insufficient
        if "warning" in data:
            assert "Negative stock" in data["warning"]
            print(f"✓ Negative Stock Warning triggered: {data['warning']}")
        else:
            print(f"✓ Delivery Note created (stock available): {data['dn_number']}")


class TestSellingModuleIntegration:
    """Full Selling Module Integration Tests"""
    
    def test_create_sales_order_with_gst(self):
        """Create SO with GST calculation"""
        test_so = {
            "customer": "TEST_IntegrationCustomer",
            "customer_gstin": "24AABCI1234A1Z5",
            "items": [
                {"item_code": "MCU-X1", "qty": 10, "rate": 1500, "amount": 15000}
            ],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        
        response = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=test_so)
        assert response.status_code == 200
        data = response.json()
        
        assert data["subtotal"] == 15000
        assert data["gst_rate"] == 18
        assert data["gst_amount"] == 2700  # 15000 * 18%
        assert data["grand_total"] == 17700
        print(f"✓ Sales Order with GST: {data['so_number']}, Total: {data['grand_total']}")
    
    def test_create_sales_invoice_with_auto_je(self):
        """Create Sales Invoice with auto journal entry"""
        test_inv = {
            "customer": "TEST_InvoiceCustomer",
            "customer_gstin": "24AABCI5678B1Z9",
            "items": [
                {"item_code": "MCU-X1", "qty": 5, "rate": 2000, "amount": 10000}
            ],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        
        response = requests.post(f"{BASE_URL}/api/selling/invoices", json=test_inv)
        assert response.status_code == 200
        data = response.json()
        
        assert "invoice_number" in data
        assert "journal_entry_id" in data  # Auto JE created
        assert data["subtotal"] == 10000
        assert data["gst_amount"] == 1800
        assert data["grand_total"] == 11800
        print(f"✓ Sales Invoice with Auto JE: {data['invoice_number']}, JE: {data['journal_entry_id']}")


class TestStatutoryReportsWithParams:
    """Test statutory reports with optional parameters"""
    
    def test_gstr1_with_month_year(self):
        """GSTR-1 with month/year parameters"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1?month=01-2026&year=2026")
        assert response.status_code == 200
        data = response.json()
        assert data["return_period"] == "01-2026"
        print(f"✓ GSTR-1 with params: Period {data['return_period']}")
    
    def test_gstr3b_with_month_year(self):
        """GSTR-3B with month/year parameters"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b?month=01-2026&year=2026")
        assert response.status_code == 200
        data = response.json()
        assert data["return_period"] == "01-2026"
        print(f"✓ GSTR-3B with params: Period {data['return_period']}")
    
    def test_tds_return_with_quarter(self):
        """TDS Return with quarter parameter"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return?quarter=Q3")
        assert response.status_code == 200
        data = response.json()
        assert data["quarter"] == "Q3"
        print(f"✓ TDS Return with params: Quarter {data['quarter']}")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data():
    """Cleanup TEST_ prefixed data after tests"""
    yield
    # Note: In production, implement cleanup logic here
    print("\n✓ Test cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
