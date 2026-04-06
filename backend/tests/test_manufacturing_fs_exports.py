"""
Test Manufacturing Module and Financial Statement Excel Exports
Tests for Kairos Accounting ERP - Iteration 5
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAPIHealth:
    """Basic API health check"""
    
    def test_api_root(self):
        """Test API is running"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Kairos Accounting API"
        assert data["version"] == "2.0.0"
        print(f"✓ API Health: {data['message']} v{data['version']}")


class TestManufacturingModule:
    """Manufacturing Module - Work Order CRUD and Lifecycle"""
    
    def test_list_work_orders_empty(self):
        """GET /api/manufacturing/work-orders returns empty array when DB is empty"""
        response = requests.get(f"{BASE_URL}/api/manufacturing/work-orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Work Orders List: {len(data)} work orders found")
    
    def test_create_work_order(self):
        """POST /api/manufacturing/work-orders creates a work order with BOM"""
        payload = {
            "production_item": "TEST-FG-CHIP-001",
            "production_item_name": "Test NanoChip X1",
            "qty_to_produce": 100,
            "additional_costs": 5000,
            "planned_start": "2026-01-15",
            "planned_end": "2026-01-20",
            "cost_center": "Manufacturing",
            "bom_items": [
                {"item_code": "RM-SILICON-001", "item_name": "Silicon Wafer", "qty": 50, "rate": 200},
                {"item_code": "RM-COPPER-001", "item_name": "Copper Wire", "qty": 100, "rate": 50}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/manufacturing/work-orders", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "id" in data
        assert "wo_number" in data
        assert data["production_item"] == "TEST-FG-CHIP-001"
        assert data["production_item_name"] == "Test NanoChip X1"
        assert data["qty_to_produce"] == 100
        assert data["status"] == "Draft"
        assert len(data["bom_items"]) == 2
        
        # Validate cost calculations
        expected_rm_cost = (50 * 200) + (100 * 50)  # 10000 + 5000 = 15000
        assert data["total_rm_cost"] == expected_rm_cost
        expected_cost_per_unit = (expected_rm_cost + 5000) / 100  # 20000 / 100 = 200
        assert data["cost_per_unit"] == expected_cost_per_unit
        
        print(f"✓ Work Order Created: {data['wo_number']} | RM Cost: {data['total_rm_cost']} | Cost/Unit: {data['cost_per_unit']}")
        
        # Store for subsequent tests
        pytest.wo_id = data["id"]
        pytest.wo_number = data["wo_number"]
    
    def test_get_work_order_by_id(self):
        """GET /api/manufacturing/work-orders/{id} returns the work order"""
        if not hasattr(pytest, 'wo_id'):
            pytest.skip("No work order created")
        
        response = requests.get(f"{BASE_URL}/api/manufacturing/work-orders/{pytest.wo_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pytest.wo_id
        assert data["status"] == "Draft"
        print(f"✓ Work Order Retrieved: {data['wo_number']} - Status: {data['status']}")
    
    def test_start_work_order(self):
        """POST /api/manufacturing/work-orders/{id}/start transitions to In Progress"""
        if not hasattr(pytest, 'wo_id'):
            pytest.skip("No work order created")
        
        response = requests.post(f"{BASE_URL}/api/manufacturing/work-orders/{pytest.wo_id}/start")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "started" in data["message"].lower() or "materials issued" in data["message"].lower()
        
        # Verify status changed
        verify_response = requests.get(f"{BASE_URL}/api/manufacturing/work-orders/{pytest.wo_id}")
        verify_data = verify_response.json()
        assert verify_data["status"] == "In Progress"
        assert verify_data["actual_start"] is not None
        
        print(f"✓ Work Order Started: {pytest.wo_number} - Status: In Progress")
    
    def test_complete_work_order(self):
        """POST /api/manufacturing/work-orders/{id}/complete transitions to Completed"""
        if not hasattr(pytest, 'wo_id'):
            pytest.skip("No work order created")
        
        payload = {
            "qty_produced": 95,
            "qty_rejected": 5,
            "scrap_reason": "Quality defects"
        }
        response = requests.post(f"{BASE_URL}/api/manufacturing/work-orders/{pytest.wo_id}/complete", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "completed" in data["message"].lower()
        
        # Verify status and quantities
        verify_response = requests.get(f"{BASE_URL}/api/manufacturing/work-orders/{pytest.wo_id}")
        verify_data = verify_response.json()
        assert verify_data["status"] == "Completed"
        assert verify_data["qty_produced"] == 95
        assert verify_data["qty_rejected"] == 5
        assert verify_data["actual_end"] is not None
        
        print(f"✓ Work Order Completed: {pytest.wo_number} - Produced: 95, Rejected: 5")
    
    def test_create_and_cancel_work_order(self):
        """Test cancel workflow: Create → Cancel"""
        # Create a new WO
        payload = {
            "production_item": "TEST-FG-CANCEL-001",
            "production_item_name": "Test Cancel Item",
            "qty_to_produce": 10,
            "bom_items": []
        }
        create_response = requests.post(f"{BASE_URL}/api/manufacturing/work-orders", json=payload)
        assert create_response.status_code == 200
        wo_id = create_response.json()["id"]
        
        # Cancel it
        cancel_response = requests.post(f"{BASE_URL}/api/manufacturing/work-orders/{wo_id}/cancel")
        assert cancel_response.status_code == 200
        
        # Verify cancelled
        verify_response = requests.get(f"{BASE_URL}/api/manufacturing/work-orders/{wo_id}")
        assert verify_response.json()["status"] == "Cancelled"
        
        print(f"✓ Work Order Cancel Flow: Created → Cancelled")


class TestFinancialStatementExports:
    """Financial Statement Excel Export Tests"""
    
    def test_balance_sheet_excel_export(self):
        """GET /api/financial-statements/balance-sheet/export/excel returns Excel file"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet/export/excel")
        assert response.status_code == 200
        
        # Verify content type
        content_type = response.headers.get('Content-Type', '')
        assert 'spreadsheetml' in content_type or 'application/vnd' in content_type
        
        # Verify content disposition
        content_disp = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disp
        assert 'Balance_Sheet' in content_disp or 'balance' in content_disp.lower()
        
        # Verify file size (should be > 1KB for valid Excel)
        assert len(response.content) > 1000
        
        # Verify Excel magic bytes (PK for ZIP-based xlsx)
        assert response.content[:2] == b'PK'
        
        print(f"✓ Balance Sheet Excel Export: {len(response.content)} bytes")
    
    def test_profit_loss_excel_export(self):
        """GET /api/financial-statements/profit-and-loss/export/excel returns Excel file"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/profit-and-loss/export/excel")
        assert response.status_code == 200
        
        content_type = response.headers.get('Content-Type', '')
        assert 'spreadsheetml' in content_type or 'application/vnd' in content_type
        
        content_disp = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disp
        assert 'Profit_Loss' in content_disp or 'profit' in content_disp.lower()
        
        assert len(response.content) > 1000
        assert response.content[:2] == b'PK'
        
        print(f"✓ Profit & Loss Excel Export: {len(response.content)} bytes")
    
    def test_trial_balance_excel_export(self):
        """GET /api/financial-statements/trial-balance/export/excel returns Excel file"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/trial-balance/export/excel")
        assert response.status_code == 200
        
        content_type = response.headers.get('Content-Type', '')
        assert 'spreadsheetml' in content_type or 'application/vnd' in content_type
        
        content_disp = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disp
        assert 'Trial_Balance' in content_disp or 'trial' in content_disp.lower()
        
        assert len(response.content) > 1000
        assert response.content[:2] == b'PK'
        
        print(f"✓ Trial Balance Excel Export: {len(response.content)} bytes")


class TestFinancialStatementData:
    """Financial Statement JSON Data Tests"""
    
    def test_balance_sheet_schedule_iii_format(self):
        """GET /api/financial-statements/balance-sheet returns Schedule III format"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        
        # Verify Schedule III structure
        assert data["format"] == "Schedule III - Companies Act 2013 (Division I)"
        assert "equity_and_liabilities" in data
        assert "assets" in data
        assert "is_balanced" in data
        
        # Verify equity structure
        el = data["equity_and_liabilities"]
        assert "shareholders_funds" in el
        assert "non_current_liabilities" in el
        assert "current_liabilities" in el
        
        # Verify assets structure
        assets = data["assets"]
        assert "non_current_assets" in assets
        assert "current_assets" in assets
        
        print(f"✓ Balance Sheet Schedule III: Balanced={data['is_balanced']}, Total={data['equity_and_liabilities']['total']}")
    
    def test_profit_loss_schedule_iii_format(self):
        """GET /api/financial-statements/profit-and-loss returns Schedule III format"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/profit-and-loss")
        assert response.status_code == 200
        data = response.json()
        
        assert data["format"] == "Schedule III - Companies Act 2013 (Division I)"
        assert "line_items" in data
        assert "summary" in data
        
        # Verify summary has key metrics
        summary = data["summary"]
        assert "total_revenue" in summary
        assert "total_expenses" in summary
        assert "net_profit" in summary
        
        print(f"✓ P&L Schedule III: Revenue={summary['total_revenue']}, Expenses={summary['total_expenses']}, Net={summary['net_profit']}")
    
    def test_trial_balance_data(self):
        """GET /api/financial-statements/trial-balance returns proper TB"""
        response = requests.get(f"{BASE_URL}/api/financial-statements/trial-balance")
        assert response.status_code == 200
        data = response.json()
        
        assert "entries" in data
        assert "total_debit" in data
        assert "total_credit" in data
        assert "in_balance" in data
        
        print(f"✓ Trial Balance: Debit={data['total_debit']}, Credit={data['total_credit']}, InBalance={data['in_balance']}")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_work_orders(self):
        """Clean up TEST_ prefixed work orders"""
        response = requests.get(f"{BASE_URL}/api/manufacturing/work-orders")
        if response.status_code == 200:
            work_orders = response.json()
            test_wos = [wo for wo in work_orders if wo.get("production_item", "").startswith("TEST-")]
            print(f"✓ Found {len(test_wos)} test work orders (cleanup would delete these)")
        else:
            print("✓ Cleanup check completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
