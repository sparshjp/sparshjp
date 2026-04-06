"""
PolyMerx Specialty Chemicals - Seeded Data Verification Tests
Tests the 200-transaction dataset with linked document flows
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://prompt-to-post-4.preview.emergentagent.com')


class TestAPIHealth:
    """Basic API health checks"""
    
    def test_api_root(self):
        """API root returns correct version"""
        r = requests.get(f"{BASE_URL}/api/")
        assert r.status_code == 200
        data = r.json()
        assert data["message"] == "Kairos Accounting API"
        assert data["version"] == "2.0.0"


class TestChartOfAccounts:
    """Chart of Accounts verification"""
    
    def test_coa_count(self):
        """CoA should have 77 ledger accounts"""
        r = requests.get(f"{BASE_URL}/api/coa")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 77, f"Expected 77 CoA accounts, got {len(data)}"
    
    def test_coa_has_required_accounts(self):
        """CoA should have key accounts for ERP operations"""
        r = requests.get(f"{BASE_URL}/api/coa")
        assert r.status_code == 200
        data = r.json()
        account_names = [a["ledger_name"] for a in data]
        
        required_accounts = [
            "Cash & Bank (HDFC Current)",
            "Accounts Receivable",
            "Accounts Payable",
            "Sales Revenue",
            "GST Input",
            "GST Output",
        ]
        for acc in required_accounts:
            assert acc in account_names, f"Missing required account: {acc}"


class TestDashboardStats:
    """Dashboard module statistics verification"""
    
    def test_crm_leads_count(self):
        """CRM should have 7 leads"""
        r = requests.get(f"{BASE_URL}/api/crm/leads")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 7, f"Expected 7 leads, got {len(data)}"
    
    def test_crm_customers_count(self):
        """CRM should have 10 customers"""
        r = requests.get(f"{BASE_URL}/api/crm/customers")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 10, f"Expected 10 customers, got {len(data)}"
    
    def test_selling_sales_orders_count(self):
        """Selling should have 8 SOs"""
        r = requests.get(f"{BASE_URL}/api/selling/sales-orders")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 8, f"Expected 8 SOs, got {len(data)}"
    
    def test_selling_invoices_count(self):
        """Selling should have 8 invoices"""
        r = requests.get(f"{BASE_URL}/api/selling/invoices")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 8, f"Expected 8 sales invoices, got {len(data)}"
    
    def test_buying_purchase_orders_count(self):
        """Buying should have 10 POs"""
        r = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 10, f"Expected 10 POs, got {len(data)}"
    
    def test_buying_invoices_count(self):
        """Buying should have 6 invoices"""
        r = requests.get(f"{BASE_URL}/api/purchase/invoices")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 6, f"Expected 6 purchase invoices, got {len(data)}"
    
    def test_buying_grn_count(self):
        """Buying should have 9 GRNs"""
        r = requests.get(f"{BASE_URL}/api/purchase/grn")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 9, f"Expected 9 GRNs, got {len(data)}"
    
    def test_stock_items_count(self):
        """Stock should have 18 items"""
        r = requests.get(f"{BASE_URL}/api/stock/items")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 18, f"Expected 18 items, got {len(data)}"
    
    def test_hr_employees_count(self):
        """HR should have 8 employees"""
        r = requests.get(f"{BASE_URL}/api/hr/employees")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 8, f"Expected 8 employees, got {len(data)}"


class TestManufacturing:
    """Manufacturing module verification"""
    
    def test_work_orders_count(self):
        """Manufacturing should have 8 WOs"""
        r = requests.get(f"{BASE_URL}/api/manufacturing/work-orders")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 8, f"Expected 8 WOs, got {len(data)}"
    
    def test_work_orders_status_distribution(self):
        """WOs should have 7 Completed + 1 In Progress"""
        r = requests.get(f"{BASE_URL}/api/manufacturing/work-orders")
        assert r.status_code == 200
        data = r.json()
        
        completed = len([w for w in data if w.get("status") == "Completed"])
        in_progress = len([w for w in data if w.get("status") == "In Progress"])
        
        assert completed == 7, f"Expected 7 Completed WOs, got {completed}"
        assert in_progress == 1, f"Expected 1 In Progress WO, got {in_progress}"


class TestFinancialStatements:
    """Financial Statements verification - Schedule III format"""
    
    def test_balance_sheet_balanced(self):
        """Balance Sheet should be balanced"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert r.status_code == 200
        data = r.json()
        
        assert data["is_balanced"] == True, "Balance Sheet is not balanced"
        assert data["difference"] == 0.0, f"Balance Sheet difference: {data['difference']}"
    
    def test_balance_sheet_total_assets(self):
        """Balance Sheet total assets should be ~9.67 Cr"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert r.status_code == 200
        data = r.json()
        
        total_assets = data["assets"]["total"]
        # ~9.67 Cr = 96,700,000 (allowing some variance)
        assert 90000000 < total_assets < 100000000, f"Total assets {total_assets} not in expected range (~9.67 Cr)"
    
    def test_balance_sheet_equity_equals_assets(self):
        """Total Equity+Liabilities should equal Total Assets"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert r.status_code == 200
        data = r.json()
        
        total_assets = data["assets"]["total"]
        total_equity_liab = data["equity_and_liabilities"]["total"]
        
        assert abs(total_assets - total_equity_liab) < 1, f"Assets ({total_assets}) != Equity+Liab ({total_equity_liab})"
    
    def test_balance_sheet_company_name(self):
        """Balance Sheet should show PolyMerx company name"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert r.status_code == 200
        data = r.json()
        
        assert "PolyMerx" in data["company_name"], f"Company name should contain PolyMerx, got {data['company_name']}"
    
    def test_profit_and_loss_has_revenue(self):
        """P&L should show revenue and expenses"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/profit-and-loss")
        assert r.status_code == 200
        data = r.json()
        
        summary = data.get("summary", {})
        assert summary.get("total_revenue", 0) > 0, "P&L should have revenue"
        assert summary.get("total_expenses", 0) > 0, "P&L should have expenses"
        assert "net_profit" in summary, "P&L should have net profit"
    
    def test_trial_balance_balanced(self):
        """Trial Balance should be balanced"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/trial-balance")
        assert r.status_code == 200
        data = r.json()
        
        assert data["in_balance"] == True, "Trial Balance is not balanced"
        assert abs(data["total_debit"] - data["total_credit"]) < 1, "TB debit != credit"
    
    def test_trial_balance_entry_count(self):
        """Trial Balance should have 56+ entries"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/trial-balance")
        assert r.status_code == 200
        data = r.json()
        
        entry_count = len(data.get("entries", []))
        assert entry_count >= 56, f"Expected 56+ TB entries, got {entry_count}"


class TestBuyingLinkedFlow:
    """Buying module linked flow verification"""
    
    def test_po_status_distribution(self):
        """POs should have correct linked status"""
        r = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert r.status_code == 200
        data = r.json()
        
        # Check for PO-CAPEX-2026-001 which should be Submitted with GRN Pending
        capex_po = next((p for p in data if p.get("po_number") == "PO-CAPEX-2026-001"), None)
        assert capex_po is not None, "PO-CAPEX-2026-001 not found"
        assert capex_po.get("status") == "Submitted", f"CAPEX PO status should be Submitted, got {capex_po.get('status')}"
        assert capex_po.get("grn_status") == "Pending", f"CAPEX PO GRN status should be Pending, got {capex_po.get('grn_status')}"
    
    def test_pending_grn_list(self):
        """Pending GRN list should include PO-CAPEX-2026-001"""
        r = requests.get(f"{BASE_URL}/api/purchase/grn/pending")
        assert r.status_code == 200
        data = r.json()
        
        po_numbers = [p.get("po_number") for p in data]
        assert "PO-CAPEX-2026-001" in po_numbers, "PO-CAPEX-2026-001 should be in pending GRN list"
    
    def test_vendor_payments_endpoint(self):
        """Vendor payments endpoint should work"""
        r = requests.get(f"{BASE_URL}/api/purchase/payments")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list), "Payments should return a list"


class TestSellingLinkedFlow:
    """Selling module linked flow verification"""
    
    def test_delivery_notes_endpoint(self):
        """Delivery notes endpoint should work"""
        r = requests.get(f"{BASE_URL}/api/selling/delivery-notes")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list), "Delivery notes should return a list"
    
    def test_customer_payments_endpoint(self):
        """Customer payments endpoint should work"""
        r = requests.get(f"{BASE_URL}/api/selling/payments")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list), "Payments should return a list"


class TestExcelExport:
    """Excel export functionality"""
    
    def test_trial_balance_excel_export(self):
        """Trial Balance Excel export should return xlsx file"""
        r = requests.get(f"{BASE_URL}/api/financial-statements/trial-balance/export/excel")
        assert r.status_code == 200
        assert "spreadsheet" in r.headers.get("Content-Type", ""), "Should return Excel file"
        assert len(r.content) > 1000, "Excel file should have content"


class TestLinkedFlowAction:
    """Test linked flow action - Confirm GRN from PO"""
    
    def test_confirm_grn_from_capex_po(self):
        """Clicking GRN pending on PO-CAPEX-2026-001 should allow confirming receipt"""
        # First get the PO ID
        r = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert r.status_code == 200
        data = r.json()
        
        capex_po = next((p for p in data if p.get("po_number") == "PO-CAPEX-2026-001"), None)
        assert capex_po is not None, "PO-CAPEX-2026-001 not found"
        
        po_id = capex_po.get("id")
        
        # Confirm receipt (create GRN from PO)
        r = requests.post(f"{BASE_URL}/api/purchase/grn/from-po/{po_id}")
        assert r.status_code == 200, f"Failed to create GRN: {r.text}"
        
        grn_data = r.json()
        assert "grn_number" in grn_data, "GRN should have grn_number"
        assert grn_data.get("po_id") == po_id, "GRN should reference the PO"
        assert grn_data.get("vendor") == capex_po.get("vendor"), "GRN vendor should match PO vendor"
        
        # Verify PO status updated
        r = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert r.status_code == 200
        updated_po = next((p for p in r.json() if p.get("id") == po_id), None)
        assert updated_po.get("grn_status") == "Received", "PO GRN status should be Received after GRN creation"
        assert updated_po.get("status") == "To Invoice", "PO status should be To Invoice after GRN creation"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
