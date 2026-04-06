"""
Kairos Accounting - Selling, Buying & Financial Statements Module Tests
Tests for:
- Selling Module: Sales Orders, Delivery Notes, Sales Invoices (auto JE), Customer Payments (auto JE)
- Buying Module: Purchase Orders, GRN (auto JE), Purchase Invoices (auto JE), Vendor Payments (auto JE)
- Financial Statements: Schedule III Balance Sheet, P&L, Trial Balance
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAPIHealth:
    """Basic API health check"""
    
    def test_api_health(self):
        """Test API is running"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "Kairos Accounting API" in data.get("message", "")
        print(f"PASS: API Health - {data}")


class TestSellingModule:
    """Selling Module Tests - Sales Orders, Delivery Notes, Invoices, Payments"""
    
    def test_create_sales_order(self):
        """Test POST /api/selling/sales-orders"""
        payload = {
            "customer": "TEST_AutoDrive Systems",
            "transaction_date": "2026-01-15",
            "delivery_date": "2026-01-20",
            "items": [
                {"item_code": "MCU-X1", "qty": 10, "rate": 1200, "amount": 12000}
            ],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        response = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "so_number" in data
        assert data["customer"] == "TEST_AutoDrive Systems"
        assert data["subtotal"] == 12000
        assert data["gst_amount"] == 2160  # 18% of 12000
        assert data["grand_total"] == 14160
        assert data["status"] == "Draft"
        assert data["delivery_status"] == "Not Delivered"
        assert data["billing_status"] == "Not Billed"
        print(f"PASS: Sales Order created - {data['so_number']}")
        return data
    
    def test_list_sales_orders(self):
        """Test GET /api/selling/sales-orders"""
        response = requests.get(f"{BASE_URL}/api/selling/sales-orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} sales orders")
    
    def test_create_delivery_note(self):
        """Test POST /api/selling/delivery-notes"""
        payload = {
            "customer": "TEST_IoTech Solutions",
            "posting_date": "2026-01-16",
            "items": [
                {"item_code": "MCU-X1", "qty": 5}
            ],
            "warehouse": "Main Warehouse"
        }
        response = requests.post(f"{BASE_URL}/api/selling/delivery-notes", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "dn_number" in data
        assert data["customer"] == "TEST_IoTech Solutions"
        assert data["total_qty"] == 5
        assert data["status"] == "Delivered"
        print(f"PASS: Delivery Note created - {data['dn_number']}")
        return data
    
    def test_list_delivery_notes(self):
        """Test GET /api/selling/delivery-notes"""
        response = requests.get(f"{BASE_URL}/api/selling/delivery-notes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} delivery notes")
    
    def test_create_sales_invoice_with_auto_je(self):
        """Test POST /api/selling/invoices - Auto-generates COGS & Revenue JE"""
        payload = {
            "customer": "TEST_SmartHome Devices",
            "posting_date": "2026-01-17",
            "items": [
                {"item_code": "MCU-X1", "qty": 20, "rate": 1200, "amount": 24000}
            ],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        response = requests.post(f"{BASE_URL}/api/selling/invoices", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify invoice structure
        assert "id" in data
        assert "invoice_number" in data
        assert data["customer"] == "TEST_SmartHome Devices"
        assert data["subtotal"] == 24000
        assert data["gst_amount"] == 4320  # 18% of 24000
        assert data["grand_total"] == 28320
        assert data["status"] == "Unpaid"
        
        # CRITICAL: Verify auto-generated journal entry ID
        assert "journal_entry_id" in data, "Sales Invoice should auto-create journal entry"
        assert data["journal_entry_id"] is not None
        print(f"PASS: Sales Invoice created with auto JE - {data['invoice_number']}, JE: {data['journal_entry_id']}")
        return data
    
    def test_list_sales_invoices(self):
        """Test GET /api/selling/invoices"""
        response = requests.get(f"{BASE_URL}/api/selling/invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} sales invoices")
    
    def test_create_customer_payment_with_auto_je(self):
        """Test POST /api/selling/payments - Auto-generates Bank+AR JE"""
        payload = {
            "customer": "TEST_AutoDrive Systems",
            "amount": 15000,
            "payment_date": "2026-01-18",
            "payment_mode": "Bank Transfer",
            "bank_account": "Cash & Bank (HDFC Current)",
            "is_advance": False,
            "cost_center": "Sales & Marketing"
        }
        response = requests.post(f"{BASE_URL}/api/selling/payments", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify payment structure
        assert "id" in data
        assert "payment_number" in data
        assert data["customer"] == "TEST_AutoDrive Systems"
        assert data["amount"] == 15000
        assert data["payment_mode"] == "Bank Transfer"
        
        # CRITICAL: Verify auto-generated journal entry ID
        assert "journal_entry_id" in data, "Customer Payment should auto-create journal entry"
        assert data["journal_entry_id"] is not None
        print(f"PASS: Customer Payment created with auto JE - {data['payment_number']}, JE: {data['journal_entry_id']}")
        return data
    
    def test_customer_payment_validation(self):
        """Test payment amount validation"""
        payload = {
            "customer": "TEST_Customer",
            "amount": 0,  # Invalid - must be positive
            "payment_date": "2026-01-18"
        }
        response = requests.post(f"{BASE_URL}/api/selling/payments", json=payload)
        assert response.status_code == 400, "Should reject zero amount"
        print("PASS: Payment validation - rejects zero amount")
    
    def test_list_customer_payments(self):
        """Test GET /api/selling/payments"""
        response = requests.get(f"{BASE_URL}/api/selling/payments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} customer payments")


class TestBuyingModule:
    """Buying Module Tests - Purchase Orders, GRN, Invoices, Payments"""
    
    def test_create_purchase_order(self):
        """Test POST /api/purchase/orders"""
        payload = {
            "vendor": "TEST_SiliconCore Semiconductors",
            "transaction_date": "2026-01-10",
            "delivery_date": "2026-01-15",
            "items": [
                {"item_code": "WAFER-6IN", "qty": 50, "rate": 3200, "amount": 160000}
            ],
            "gst_rate": 18,
            "payment_terms": "Net 30",
            "cost_center": "Manufacturing"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/orders", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify PO structure
        assert "id" in data
        assert "po_number" in data
        assert data["vendor"] == "TEST_SiliconCore Semiconductors"
        assert data["subtotal"] == 160000
        assert data["gst_amount"] == 28800  # 18% of 160000
        assert data["grand_total"] == 188800
        assert data["status"] == "Draft"
        assert data["grn_status"] == "Pending"
        print(f"PASS: Purchase Order created - {data['po_number']}")
        return data
    
    def test_list_purchase_orders(self):
        """Test GET /api/purchase/orders"""
        response = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} purchase orders")
    
    def test_create_grn_with_auto_je(self):
        """Test POST /api/purchase/grn - Auto-generates Inventory+AP JE"""
        payload = {
            "vendor": "TEST_Resistors & Co",
            "posting_date": "2026-01-12",
            "items": [
                {"item_code": "CAP-SMD-100", "qty": 20, "rate": 450, "amount": 9000},
                {"item_code": "RES-SMD-10K", "qty": 15, "rate": 380, "amount": 5700}
            ],
            "gst_rate": 18,
            "warehouse": "Main Warehouse",
            "qc_status": "Accepted",
            "cost_center": "Manufacturing"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/grn", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify GRN structure
        assert "id" in data
        assert "grn_number" in data
        assert data["vendor"] == "TEST_Resistors & Co"
        assert data["subtotal"] == 14700  # 9000 + 5700
        assert data["gst_amount"] == 2646  # 18% of 14700
        assert data["grand_total"] == 17346
        assert data["status"] == "Received"
        
        # CRITICAL: Verify auto-generated journal entry ID
        assert "journal_entry_id" in data, "GRN should auto-create journal entry"
        assert data["journal_entry_id"] is not None
        print(f"PASS: GRN created with auto JE - {data['grn_number']}, JE: {data['journal_entry_id']}")
        return data
    
    def test_list_grn(self):
        """Test GET /api/purchase/grn"""
        response = requests.get(f"{BASE_URL}/api/purchase/grn")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} GRNs")
    
    def test_create_purchase_invoice_with_auto_je(self):
        """Test POST /api/purchase/invoices - Auto-generates JE if no GRN ref"""
        payload = {
            "vendor": "TEST_Office Supplies Ltd",
            "posting_date": "2026-01-14",
            "vendor_invoice_no": "INV-2026-001",
            "items": [
                {"item_code": "OFFICE-SUPPLIES", "qty": 1, "rate": 5000, "amount": 5000}
            ],
            "gst_rate": 18,
            "expense_account": "Raw Material Inventory",
            "cost_center": "General"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/invoices", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify invoice structure
        assert "id" in data
        assert "invoice_number" in data
        assert data["vendor"] == "TEST_Office Supplies Ltd"
        assert data["subtotal"] == 5000
        assert data["gst_amount"] == 900  # 18% of 5000
        assert data["grand_total"] == 5900
        assert data["status"] == "Unpaid"
        
        # CRITICAL: Verify auto-generated journal entry ID (no GRN ref)
        assert "journal_entry_id" in data, "Purchase Invoice without GRN should auto-create JE"
        assert data["journal_entry_id"] is not None
        print(f"PASS: Purchase Invoice created with auto JE - {data['invoice_number']}, JE: {data['journal_entry_id']}")
        return data
    
    def test_list_purchase_invoices(self):
        """Test GET /api/purchase/invoices"""
        response = requests.get(f"{BASE_URL}/api/purchase/invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} purchase invoices")
    
    def test_create_vendor_payment_with_auto_je(self):
        """Test POST /api/purchase/payments - Auto-generates AP+Bank JE"""
        payload = {
            "vendor": "TEST_SiliconCore Semiconductors",
            "amount": 50000,
            "payment_date": "2026-01-20",
            "payment_mode": "Bank Transfer",
            "bank_account": "Cash & Bank (HDFC Current)",
            "cost_center": "Manufacturing"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/payments", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify payment structure
        assert "id" in data
        assert "payment_number" in data
        assert data["vendor"] == "TEST_SiliconCore Semiconductors"
        assert data["amount"] == 50000
        assert data["payment_mode"] == "Bank Transfer"
        
        # CRITICAL: Verify auto-generated journal entry ID
        assert "journal_entry_id" in data, "Vendor Payment should auto-create journal entry"
        assert data["journal_entry_id"] is not None
        print(f"PASS: Vendor Payment created with auto JE - {data['payment_number']}, JE: {data['journal_entry_id']}")
        return data
    
    def test_vendor_payment_validation(self):
        """Test payment amount validation"""
        payload = {
            "vendor": "TEST_Vendor",
            "amount": -100,  # Invalid - must be positive
            "payment_date": "2026-01-20"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/payments", json=payload)
        assert response.status_code == 400, "Should reject negative amount"
        print("PASS: Vendor Payment validation - rejects negative amount")
    
    def test_list_vendor_payments(self):
        """Test GET /api/purchase/payments"""
        response = requests.get(f"{BASE_URL}/api/purchase/payments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Listed {len(data)} vendor payments")


class TestFinancialStatements:
    """Financial Statements Tests - Schedule III Balance Sheet, P&L, Trial Balance"""
    
    def test_trial_balance(self):
        """Test GET /api/financial-statements/trial-balance"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/trial-balance")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert data["report_type"] == "Trial Balance"
        assert "company_name" in data
        assert "as_of_date" in data
        assert "entries" in data
        assert "total_debit" in data
        assert "total_credit" in data
        assert "difference" in data
        assert "in_balance" in data
        
        # CRITICAL: Trial Balance must be balanced
        assert data["in_balance"] == True, f"Trial Balance out of balance! Diff: {data['difference']}"
        print(f"PASS: Trial Balance - Debit: {data['total_debit']}, Credit: {data['total_credit']}, In Balance: {data['in_balance']}")
        return data
    
    def test_balance_sheet_schedule_iii(self):
        """Test GET /api/financial-statements/balance-sheet - Schedule III format"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        
        # Verify Schedule III structure
        assert data["report_type"] == "Balance Sheet"
        assert "Schedule III" in data["format"]
        assert "company_name" in data
        assert "as_of_date" in data
        assert "currency" in data
        
        # Verify Equity & Liabilities section
        assert "equity_and_liabilities" in data
        el = data["equity_and_liabilities"]
        assert "shareholders_funds" in el
        assert "non_current_liabilities" in el
        assert "current_liabilities" in el
        assert "total" in el
        
        # Verify Assets section
        assert "assets" in data
        assets = data["assets"]
        assert "non_current_assets" in assets
        assert "current_assets" in assets
        assert "total" in assets
        
        # CRITICAL: Balance Sheet must be balanced
        assert "is_balanced" in data
        assert data["is_balanced"] == True, f"Balance Sheet not balanced! Diff: {data.get('difference', 'N/A')}"
        
        print(f"PASS: Balance Sheet - E&L: {el['total']}, Assets: {assets['total']}, Balanced: {data['is_balanced']}")
        return data
    
    def test_profit_and_loss_schedule_iii(self):
        """Test GET /api/financial-statements/profit-and-loss - Schedule III format"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/profit-and-loss")
        assert response.status_code == 200
        data = response.json()
        
        # Verify Schedule III structure
        assert data["report_type"] == "Statement of Profit and Loss"
        assert "Schedule III" in data["format"]
        assert "company_name" in data
        assert "period" in data
        assert "currency" in data
        
        # Verify line items (Schedule III I-XVI)
        assert "line_items" in data
        line_items = data["line_items"]
        assert len(line_items) > 0
        
        # Check for key Schedule III line items
        sl_numbers = [item.get("sl", "") for item in line_items]
        assert "I" in sl_numbers, "Missing Revenue from Operations (I)"
        assert "II" in sl_numbers, "Missing Other Income (II)"
        assert "III" in sl_numbers, "Missing Total Revenue (III)"
        assert "IV" in sl_numbers, "Missing Expenses header (IV)"
        assert "IX" in sl_numbers, "Missing Profit before Tax (IX)"
        assert "XI" in sl_numbers, "Missing Profit for Period (XI)"
        
        # Verify summary
        assert "summary" in data
        summary = data["summary"]
        assert "total_revenue" in summary
        assert "total_expenses" in summary
        assert "net_profit" in summary
        
        print(f"PASS: P&L - Revenue: {summary['total_revenue']}, Expenses: {summary['total_expenses']}, Net: {summary['net_profit']}")
        return data
    
    def test_balance_sheet_with_date(self):
        """Test Balance Sheet with specific date parameter"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet?as_of_date=2026-01-31")
        assert response.status_code == 200
        data = response.json()
        assert data["as_of_date"] == "2026-01-31"
        print(f"PASS: Balance Sheet with date filter - {data['as_of_date']}")
    
    def test_profit_loss_with_date_range(self):
        """Test P&L with date range parameters"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/profit-and-loss?start_date=2026-01-01&end_date=2026-01-31")
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["from"] == "2026-01-01"
        assert data["period"]["to"] == "2026-01-31"
        print(f"PASS: P&L with date range - {data['period']}")


class TestAutoAccountingIntegration:
    """Integration tests for auto-accounting flows"""
    
    def test_sales_invoice_creates_cogs_entry(self):
        """Verify Sales Invoice auto-creates COGS journal entry"""
        # Create invoice with item that has valuation_rate
        payload = {
            "customer": "TEST_Integration_Customer",
            "posting_date": "2026-01-25",
            "items": [
                {"item_code": "MCU-X1", "qty": 5, "rate": 1500, "amount": 7500}
            ],
            "gst_rate": 18
        }
        response = requests.post(f"{BASE_URL}/api/selling/invoices", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify COGS was calculated
        assert "cogs_total" in data
        assert "journal_entry_id" in data
        
        # Verify the journal entry was created in manual_journal_entries
        je_response = requests.get(f"{BASE_URL}/api/journal-entries/manual")
        assert je_response.status_code == 200
        entries = je_response.json()
        
        # Find our entry
        our_entry = next((e for e in entries if e["id"] == data["journal_entry_id"]), None)
        assert our_entry is not None, "Journal entry not found in manual_journal_entries"
        assert our_entry["status"] == "Posted"
        assert our_entry["entry_type"] == "Auto Generated"
        
        print(f"PASS: Sales Invoice auto-accounting - Invoice: {data['invoice_number']}, COGS: {data['cogs_total']}, JE: {data['journal_entry_id']}")
    
    def test_grn_creates_inventory_ap_entry(self):
        """Verify GRN auto-creates Inventory+AP journal entry"""
        payload = {
            "vendor": "TEST_Integration_Vendor",
            "posting_date": "2026-01-26",
            "items": [
                {"item_code": "TEST-ITEM", "qty": 100, "rate": 50, "amount": 5000}
            ],
            "gst_rate": 18,
            "warehouse": "Main Warehouse"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/grn", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "journal_entry_id" in data
        
        # Verify the journal entry
        je_response = requests.get(f"{BASE_URL}/api/journal-entries/manual")
        entries = je_response.json()
        our_entry = next((e for e in entries if e["id"] == data["journal_entry_id"]), None)
        
        assert our_entry is not None
        assert our_entry["status"] == "Posted"
        
        # Verify journal entries contain correct accounts
        je_accounts = [je["account"] for je in our_entry["journal_entries"]]
        assert "Raw Material Inventory" in je_accounts, "Missing Raw Material Inventory debit"
        assert "GST Input" in je_accounts, "Missing GST Input debit"
        assert "Accounts Payable" in je_accounts, "Missing Accounts Payable credit"
        
        print(f"PASS: GRN auto-accounting - GRN: {data['grn_number']}, JE: {data['journal_entry_id']}")
    
    def test_vendor_payment_creates_ap_bank_entry(self):
        """Verify Vendor Payment auto-creates AP+Bank journal entry"""
        payload = {
            "vendor": "TEST_Integration_Vendor",
            "amount": 10000,
            "payment_date": "2026-01-27",
            "payment_mode": "Bank Transfer",
            "bank_account": "Cash & Bank (HDFC Current)"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/payments", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "journal_entry_id" in data
        
        # Verify the journal entry
        je_response = requests.get(f"{BASE_URL}/api/journal-entries/manual")
        entries = je_response.json()
        our_entry = next((e for e in entries if e["id"] == data["journal_entry_id"]), None)
        
        assert our_entry is not None
        
        # Verify journal entries contain correct accounts
        je_accounts = [je["account"] for je in our_entry["journal_entries"]]
        assert "Accounts Payable" in je_accounts, "Missing Accounts Payable debit"
        assert "Cash & Bank (HDFC Current)" in je_accounts, "Missing Bank credit"
        
        print(f"PASS: Vendor Payment auto-accounting - Payment: {data['payment_number']}, JE: {data['journal_entry_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
