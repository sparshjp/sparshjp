"""
Test Linked Document Flow for Kairos Advisory ERP
Purchase: PO → GRN (from PO) → Invoice (from GRN) → Payment (for Invoice)
Selling: SO → DN (from SO) → Invoice (from DN) → Payment (for Invoice)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPurchaseLinkedFlow:
    """Test Purchase Linked Document Flow: PO → GRN → Invoice → Payment"""
    
    def test_01_api_health(self):
        """Verify API is running"""
        r = requests.get(f"{BASE_URL}/api/")
        assert r.status_code == 200
        data = r.json()
        assert "Kairos" in data.get("message", "")
        print(f"API Health: {data}")
    
    def test_02_create_purchase_order(self):
        """Create a new PO and verify response structure"""
        payload = {
            "vendor": "TEST_LinkedFlow_Vendor",
            "transaction_date": "2026-01-06",
            "delivery_date": "2026-01-15",
            "items": [
                {"item_code": "TEST-RM-001", "item_name": "Test Raw Material", "qty": 10, "rate": 500, "amount": 5000}
            ],
            "gst_rate": 18,
            "cost_center": "Manufacturing"
        }
        r = requests.post(f"{BASE_URL}/api/purchase/orders", json=payload)
        assert r.status_code == 200, f"Failed to create PO: {r.text}"
        data = r.json()
        
        # Verify PO structure
        assert "po_number" in data, "Missing po_number"
        assert data["po_number"].startswith("PO-"), f"Invalid PO number format: {data['po_number']}"
        assert data["vendor"] == "TEST_LinkedFlow_Vendor"
        assert data["subtotal"] == 5000
        assert data["gst_amount"] == 900  # 18% of 5000
        assert data["grand_total"] == 5900
        assert data["status"] == "Submitted"
        assert data["grn_status"] == "Pending"
        assert data["invoice_status"] == "Pending"
        
        # Store for next tests
        pytest.po_id = data["id"]
        pytest.po_number = data["po_number"]
        print(f"Created PO: {data['po_number']} | Total: {data['grand_total']}")
    
    def test_03_list_pending_grn(self):
        """Verify PO appears in pending GRN list"""
        r = requests.get(f"{BASE_URL}/api/purchase/grn/pending")
        assert r.status_code == 200
        data = r.json()
        
        # Find our PO in pending list
        our_po = next((po for po in data if po.get("id") == pytest.po_id), None)
        assert our_po is not None, f"PO {pytest.po_number} not found in pending GRN list"
        assert our_po["grn_status"] == "Pending"
        print(f"Pending GRN count: {len(data)} | Our PO found: {pytest.po_number}")
    
    def test_04_confirm_receipt_creates_grn(self):
        """Confirm receipt from PO - creates GRN with JE"""
        r = requests.post(f"{BASE_URL}/api/purchase/grn/from-po/{pytest.po_id}")
        assert r.status_code == 200, f"Failed to create GRN: {r.text}"
        data = r.json()
        
        # Verify GRN structure
        assert "grn_number" in data, "Missing grn_number"
        assert data["grn_number"].startswith("GRN-"), f"Invalid GRN number: {data['grn_number']}"
        assert data["po_id"] == pytest.po_id
        assert data["po_number"] == pytest.po_number
        assert data["vendor"] == "TEST_LinkedFlow_Vendor"
        assert data["grand_total"] == 5900
        assert data["status"] == "Received"
        assert data["invoice_status"] == "Pending"
        assert "journal_entry_id" in data, "Missing journal_entry_id - JE not posted"
        
        pytest.grn_id = data["id"]
        pytest.grn_number = data["grn_number"]
        print(f"Created GRN: {data['grn_number']} | JE posted: {data.get('journal_entry_id', 'N/A')}")
    
    def test_05_po_status_updated_after_grn(self):
        """Verify PO status changed to 'To Invoice' and grn_status to 'Received'"""
        r = requests.get(f"{BASE_URL}/api/purchase/orders")
        assert r.status_code == 200
        data = r.json()
        
        our_po = next((po for po in data if po.get("id") == pytest.po_id), None)
        assert our_po is not None, "PO not found"
        assert our_po["status"] == "To Invoice", f"Expected 'To Invoice', got '{our_po['status']}'"
        assert our_po["grn_status"] == "Received", f"Expected 'Received', got '{our_po['grn_status']}'"
        print(f"PO {pytest.po_number} status: {our_po['status']} | GRN status: {our_po['grn_status']}")
    
    def test_06_list_pending_invoices(self):
        """Verify GRN appears in pending invoice list"""
        r = requests.get(f"{BASE_URL}/api/purchase/invoices/pending")
        assert r.status_code == 200
        data = r.json()
        
        our_grn = next((grn for grn in data if grn.get("id") == pytest.grn_id), None)
        assert our_grn is not None, f"GRN {pytest.grn_number} not found in pending invoice list"
        assert our_grn["invoice_status"] == "Pending"
        print(f"Pending Invoice count: {len(data)} | Our GRN found: {pytest.grn_number}")
    
    def test_07_create_invoice_from_grn(self):
        """Create purchase invoice from GRN"""
        payload = {"vendor_invoice_no": "VINV-TEST-001"}
        r = requests.post(f"{BASE_URL}/api/purchase/invoices/from-grn/{pytest.grn_id}", json=payload)
        assert r.status_code == 200, f"Failed to create invoice: {r.text}"
        data = r.json()
        
        # Verify Invoice structure
        assert "invoice_number" in data, "Missing invoice_number"
        assert data["invoice_number"].startswith("PI-"), f"Invalid invoice number: {data['invoice_number']}"
        assert data["grn_id"] == pytest.grn_id
        assert data["grn_number"] == pytest.grn_number
        assert data["po_id"] == pytest.po_id
        assert data["po_number"] == pytest.po_number
        assert data["vendor"] == "TEST_LinkedFlow_Vendor"
        assert data["grand_total"] == 5900
        assert data["status"] == "Unpaid"
        assert data["amount_paid"] == 0
        
        pytest.invoice_id = data["id"]
        pytest.invoice_number = data["invoice_number"]
        print(f"Created Invoice: {data['invoice_number']} | Status: {data['status']}")
    
    def test_08_list_outstanding_invoices(self):
        """Verify invoice appears in outstanding list with aging"""
        r = requests.get(f"{BASE_URL}/api/purchase/payments/outstanding")
        assert r.status_code == 200
        data = r.json()
        
        our_inv = next((inv for inv in data if inv.get("id") == pytest.invoice_id), None)
        assert our_inv is not None, f"Invoice {pytest.invoice_number} not found in outstanding list"
        assert "days_outstanding" in our_inv, "Missing days_outstanding"
        assert "balance_due" in our_inv, "Missing balance_due"
        assert our_inv["balance_due"] == 5900
        print(f"Outstanding count: {len(data)} | Invoice {pytest.invoice_number} | Days: {our_inv['days_outstanding']} | Balance: {our_inv['balance_due']}")
    
    def test_09_pay_invoice(self):
        """Pay the invoice and verify JE posted"""
        payload = {"payment_mode": "Bank Transfer"}
        r = requests.post(f"{BASE_URL}/api/purchase/payments/for-invoice/{pytest.invoice_id}", json=payload)
        assert r.status_code == 200, f"Failed to pay invoice: {r.text}"
        data = r.json()
        
        # Verify Payment structure
        assert "payment_number" in data, "Missing payment_number"
        assert data["payment_number"].startswith("VP-"), f"Invalid payment number: {data['payment_number']}"
        assert data["invoice_id"] == pytest.invoice_id
        assert data["invoice_number"] == pytest.invoice_number
        assert data["vendor"] == "TEST_LinkedFlow_Vendor"
        assert data["amount"] == 5900
        assert "journal_entry_id" in data, "Missing journal_entry_id - JE not posted"
        
        pytest.payment_id = data["id"]
        pytest.payment_number = data["payment_number"]
        print(f"Created Payment: {data['payment_number']} | Amount: {data['amount']} | JE: {data.get('journal_entry_id', 'N/A')}")
    
    def test_10_invoice_marked_paid(self):
        """Verify invoice status changed to Paid"""
        r = requests.get(f"{BASE_URL}/api/purchase/invoices")
        assert r.status_code == 200
        data = r.json()
        
        our_inv = next((inv for inv in data if inv.get("id") == pytest.invoice_id), None)
        assert our_inv is not None, "Invoice not found"
        assert our_inv["status"] == "Paid", f"Expected 'Paid', got '{our_inv['status']}'"
        assert our_inv["amount_paid"] == 5900
        print(f"Invoice {pytest.invoice_number} status: {our_inv['status']} | Paid: {our_inv['amount_paid']}")


class TestSellingLinkedFlow:
    """Test Selling Linked Document Flow: SO → DN → Invoice → Payment"""
    
    def test_11_create_sales_order(self):
        """Create a new SO and verify response structure"""
        payload = {
            "customer": "TEST_LinkedFlow_Customer",
            "transaction_date": "2026-01-06",
            "delivery_date": "2026-01-10",
            "items": [
                {"item_code": "TEST-FG-001", "item_name": "Test Finished Good", "qty": 5, "rate": 2000, "amount": 10000}
            ],
            "gst_rate": 18,
            "cost_center": "Sales & Marketing"
        }
        r = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=payload)
        assert r.status_code == 200, f"Failed to create SO: {r.text}"
        data = r.json()
        
        # Verify SO structure
        assert "so_number" in data, "Missing so_number"
        assert data["so_number"].startswith("SO-"), f"Invalid SO number format: {data['so_number']}"
        assert data["customer"] == "TEST_LinkedFlow_Customer"
        assert data["subtotal"] == 10000
        assert data["gst_amount"] == 1800  # 18% of 10000
        assert data["grand_total"] == 11800
        assert data["status"] == "Submitted"
        assert data["delivery_status"] == "Not Delivered"
        assert data["billing_status"] == "Not Billed"
        
        pytest.so_id = data["id"]
        pytest.so_number = data["so_number"]
        print(f"Created SO: {data['so_number']} | Total: {data['grand_total']}")
    
    def test_12_list_pending_delivery(self):
        """Verify SO appears in pending delivery list"""
        r = requests.get(f"{BASE_URL}/api/selling/delivery-notes/pending")
        assert r.status_code == 200
        data = r.json()
        
        our_so = next((so for so in data if so.get("id") == pytest.so_id), None)
        assert our_so is not None, f"SO {pytest.so_number} not found in pending delivery list"
        assert our_so["delivery_status"] == "Not Delivered"
        print(f"Pending Delivery count: {len(data)} | Our SO found: {pytest.so_number}")
    
    def test_13_confirm_delivery_creates_dn(self):
        """Confirm delivery from SO - creates DN"""
        r = requests.post(f"{BASE_URL}/api/selling/delivery-notes/from-so/{pytest.so_id}")
        assert r.status_code == 200, f"Failed to create DN: {r.text}"
        data = r.json()
        
        # Verify DN structure
        assert "dn_number" in data, "Missing dn_number"
        assert data["dn_number"].startswith("DN-"), f"Invalid DN number: {data['dn_number']}"
        assert data["so_id"] == pytest.so_id
        assert data["so_number"] == pytest.so_number
        assert data["customer"] == "TEST_LinkedFlow_Customer"
        assert data["grand_total"] == 11800
        assert data["status"] == "Delivered"
        assert data["invoice_status"] == "Pending"
        
        pytest.dn_id = data["id"]
        pytest.dn_number = data["dn_number"]
        print(f"Created DN: {data['dn_number']} | Status: {data['status']}")
    
    def test_14_so_status_updated_after_dn(self):
        """Verify SO status changed to 'To Invoice' and delivery_status to 'Fully Delivered'"""
        r = requests.get(f"{BASE_URL}/api/selling/sales-orders")
        assert r.status_code == 200
        data = r.json()
        
        our_so = next((so for so in data if so.get("id") == pytest.so_id), None)
        assert our_so is not None, "SO not found"
        assert our_so["status"] == "To Invoice", f"Expected 'To Invoice', got '{our_so['status']}'"
        assert our_so["delivery_status"] == "Fully Delivered", f"Expected 'Fully Delivered', got '{our_so['delivery_status']}'"
        print(f"SO {pytest.so_number} status: {our_so['status']} | Delivery: {our_so['delivery_status']}")
    
    def test_15_list_pending_sales_invoices(self):
        """Verify DN appears in pending invoice list"""
        r = requests.get(f"{BASE_URL}/api/selling/invoices/pending")
        assert r.status_code == 200
        data = r.json()
        
        our_dn = next((dn for dn in data if dn.get("id") == pytest.dn_id), None)
        assert our_dn is not None, f"DN {pytest.dn_number} not found in pending invoice list"
        assert our_dn["invoice_status"] == "Pending"
        print(f"Pending Sales Invoice count: {len(data)} | Our DN found: {pytest.dn_number}")
    
    def test_16_create_sales_invoice_from_dn(self):
        """Create sales invoice from DN - posts Revenue + COGS JE"""
        r = requests.post(f"{BASE_URL}/api/selling/invoices/from-dn/{pytest.dn_id}", json={})
        assert r.status_code == 200, f"Failed to create sales invoice: {r.text}"
        data = r.json()
        
        # Verify Invoice structure
        assert "invoice_number" in data, "Missing invoice_number"
        assert data["invoice_number"].startswith("SI-"), f"Invalid invoice number: {data['invoice_number']}"
        assert data["dn_id"] == pytest.dn_id
        assert data["dn_number"] == pytest.dn_number
        assert data["so_id"] == pytest.so_id
        assert data["so_number"] == pytest.so_number
        assert data["customer"] == "TEST_LinkedFlow_Customer"
        assert data["grand_total"] == 11800
        assert data["status"] == "Unpaid"
        assert data["amount_paid"] == 0
        assert "cogs_total" in data, "Missing cogs_total"
        assert "journal_entry_id" in data, "Missing journal_entry_id - JE not posted"
        
        pytest.sales_invoice_id = data["id"]
        pytest.sales_invoice_number = data["invoice_number"]
        print(f"Created Sales Invoice: {data['invoice_number']} | COGS: {data['cogs_total']} | JE: {data.get('journal_entry_id', 'N/A')}")
    
    def test_17_list_outstanding_ar(self):
        """Verify sales invoice appears in outstanding AR list with aging"""
        r = requests.get(f"{BASE_URL}/api/selling/payments/outstanding")
        assert r.status_code == 200
        data = r.json()
        
        our_inv = next((inv for inv in data if inv.get("id") == pytest.sales_invoice_id), None)
        assert our_inv is not None, f"Invoice {pytest.sales_invoice_number} not found in outstanding AR list"
        assert "days_outstanding" in our_inv, "Missing days_outstanding"
        assert "balance_due" in our_inv, "Missing balance_due"
        assert our_inv["balance_due"] == 11800
        print(f"Outstanding AR count: {len(data)} | Invoice {pytest.sales_invoice_number} | Days: {our_inv['days_outstanding']} | Balance: {our_inv['balance_due']}")
    
    def test_18_receive_payment(self):
        """Receive payment for sales invoice and verify JE posted"""
        payload = {"payment_mode": "Bank Transfer"}
        r = requests.post(f"{BASE_URL}/api/selling/payments/for-invoice/{pytest.sales_invoice_id}", json=payload)
        assert r.status_code == 200, f"Failed to receive payment: {r.text}"
        data = r.json()
        
        # Verify Payment structure
        assert "payment_number" in data, "Missing payment_number"
        assert data["payment_number"].startswith("CR-"), f"Invalid payment number: {data['payment_number']}"
        assert data["invoice_id"] == pytest.sales_invoice_id
        assert data["invoice_number"] == pytest.sales_invoice_number
        assert data["customer"] == "TEST_LinkedFlow_Customer"
        assert data["amount"] == 11800
        assert "journal_entry_id" in data, "Missing journal_entry_id - JE not posted"
        
        pytest.customer_payment_id = data["id"]
        pytest.customer_payment_number = data["payment_number"]
        print(f"Received Payment: {data['payment_number']} | Amount: {data['amount']} | JE: {data.get('journal_entry_id', 'N/A')}")
    
    def test_19_sales_invoice_marked_paid(self):
        """Verify sales invoice status changed to Paid"""
        r = requests.get(f"{BASE_URL}/api/selling/invoices")
        assert r.status_code == 200
        data = r.json()
        
        our_inv = next((inv for inv in data if inv.get("id") == pytest.sales_invoice_id), None)
        assert our_inv is not None, "Sales Invoice not found"
        assert our_inv["status"] == "Paid", f"Expected 'Paid', got '{our_inv['status']}'"
        assert our_inv["amount_paid"] == 11800
        print(f"Sales Invoice {pytest.sales_invoice_number} status: {our_inv['status']} | Paid: {our_inv['amount_paid']}")
    
    def test_20_so_status_completed(self):
        """Verify SO status changed to Completed after full lifecycle"""
        r = requests.get(f"{BASE_URL}/api/selling/sales-orders")
        assert r.status_code == 200
        data = r.json()
        
        our_so = next((so for so in data if so.get("id") == pytest.so_id), None)
        assert our_so is not None, "SO not found"
        assert our_so["status"] == "Completed", f"Expected 'Completed', got '{our_so['status']}'"
        assert our_so["billing_status"] == "Fully Billed", f"Expected 'Fully Billed', got '{our_so['billing_status']}'"
        print(f"SO {pytest.so_number} final status: {our_so['status']} | Billing: {our_so['billing_status']}")


class TestExistingPOFlow:
    """Test the existing PO (PO-20260406-8022) mentioned in context"""
    
    def test_21_check_existing_po(self):
        """Check if existing PO is in pending GRN list"""
        r = requests.get(f"{BASE_URL}/api/purchase/grn/pending")
        assert r.status_code == 200
        data = r.json()
        
        existing_po = next((po for po in data if "8022" in po.get("po_number", "")), None)
        if existing_po:
            print(f"Found existing PO: {existing_po['po_number']} | Vendor: {existing_po['vendor']} | Total: {existing_po['grand_total']}")
            pytest.existing_po_id = existing_po["id"]
            pytest.existing_po_number = existing_po["po_number"]
        else:
            # Check if it was already processed
            r2 = requests.get(f"{BASE_URL}/api/purchase/orders")
            all_pos = r2.json()
            existing_po = next((po for po in all_pos if "8022" in po.get("po_number", "")), None)
            if existing_po:
                print(f"Existing PO already processed: {existing_po['po_number']} | Status: {existing_po['status']} | GRN: {existing_po['grn_status']}")
                pytest.existing_po_id = None  # Already processed
            else:
                print("Existing PO (8022) not found in database")
                pytest.existing_po_id = None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
