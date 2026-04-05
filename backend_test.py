#!/usr/bin/env python3
"""
AI-Native ERP Backend API Testing
Tests all endpoints including AI integrations, document upload, and financial reporting
"""

import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import io
from PIL import Image

class ERPAPITester:
    def __init__(self, base_url="https://prompt-to-post-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_api_health(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'N/A')}"
            self.log_test("API Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
            return False

    def test_document_upload(self):
        """Test document upload and OCR extraction"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            files = {'file': ('test_invoice.png', img_buffer, 'image/png')}
            response = requests.post(f"{self.api_url}/documents/upload", files=files, timeout=30)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.document_id = data.get('document_id')
                details += f", Document ID: {self.document_id}"
                # Check if OCR data is present
                if 'extracted_data' in data:
                    details += ", OCR: ✓"
                else:
                    details += ", OCR: ✗"
            
            self.log_test("Document Upload & OCR", success, details)
            return success, getattr(self, 'document_id', None)
        except Exception as e:
            self.log_test("Document Upload & OCR", False, str(e))
            return False, None

    def test_prompt_processing(self, document_id=None):
        """Test AI prompt processing with Claude Sonnet 4.5"""
        try:
            prompt_data = {
                "prompt": "Record electricity expense of ₹15,000 for Gujarat plant for December 2025, paid to ABC Power Corp. Posting date: 2025-01-02",
                "module": "purchase-to-pay",
                "user_id": "test_user"
            }
            
            if document_id:
                prompt_data["document_id"] = document_id
            
            response = requests.post(f"{self.api_url}/transactions/prompt", json=prompt_data, timeout=60)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.transaction_id = data.get('id')
                details += f", Transaction ID: {self.transaction_id}"
                
                # Check if journal entries were generated
                if data.get('journal_entries'):
                    details += f", Journal Entries: {len(data['journal_entries'])}"
                else:
                    details += ", Journal Entries: 0"
                    
                # Check AI parsing results
                if data.get('posting_date'):
                    details += ", AI Parsing: ✓"
                else:
                    details += ", AI Parsing: ✗"
            
            self.log_test("AI Prompt Processing (Claude)", success, details)
            return success, getattr(self, 'transaction_id', None)
        except Exception as e:
            self.log_test("AI Prompt Processing (Claude)", False, str(e))
            return False, None

    def test_get_drafts(self):
        """Test retrieving draft transactions"""
        try:
            response = requests.get(f"{self.api_url}/transactions/drafts", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Draft Count: {len(data)}"
            
            self.log_test("Get Draft Transactions", success, details)
            return success
        except Exception as e:
            self.log_test("Get Draft Transactions", False, str(e))
            return False

    def test_post_transaction(self, transaction_id):
        """Test posting a draft transaction"""
        if not transaction_id:
            self.log_test("Post Transaction", False, "No transaction ID available")
            return False
            
        try:
            post_data = {"transaction_id": transaction_id}
            response = requests.post(f"{self.api_url}/transactions/post", json=post_data, timeout=10)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'N/A')}"
            
            self.log_test("Post Transaction", success, details)
            return success
        except Exception as e:
            self.log_test("Post Transaction", False, str(e))
            return False

    def test_get_posted_transactions(self):
        """Test retrieving posted transactions"""
        try:
            response = requests.get(f"{self.api_url}/transactions/posted", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Posted Count: {len(data)}"
            
            self.log_test("Get Posted Transactions", success, details)
            return success
        except Exception as e:
            self.log_test("Get Posted Transactions", False, str(e))
            return False

    def test_conversational_reporting(self):
        """Test AI-powered conversational reporting"""
        try:
            query_data = {
                "query": "Show me total expenses for this month",
                "start_date": "2025-01-01",
                "end_date": "2025-01-31"
            }
            
            response = requests.post(f"{self.api_url}/reports/query", json=query_data, timeout=60)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Data Points: {data.get('data_points', 0)}"
                if data.get('answer'):
                    details += ", AI Response: ✓"
                else:
                    details += ", AI Response: ✗"
            
            self.log_test("Conversational Reporting (AI)", success, details)
            return success
        except Exception as e:
            self.log_test("Conversational Reporting (AI)", False, str(e))
            return False

    def test_balance_sheet(self):
        """Test balance sheet generation"""
        try:
            response = requests.get(f"{self.api_url}/reports/balance-sheet", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Entries: {data.get('total_entries', 0)}"
                details += f", Date: {data.get('as_of_date', 'N/A')}"
            
            self.log_test("Balance Sheet Report", success, details)
            return success
        except Exception as e:
            self.log_test("Balance Sheet Report", False, str(e))
            return False

    def test_profit_loss(self):
        """Test profit & loss statement"""
        try:
            params = {
                "start_date": "2025-01-01",
                "end_date": "2025-01-31"
            }
            response = requests.get(f"{self.api_url}/reports/profit-loss", params=params, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Revenue: ₹{data.get('total_revenue', 0)}"
                details += f", Expenses: ₹{data.get('total_expenses', 0)}"
                details += f", Net: ₹{data.get('net_profit', 0)}"
            
            self.log_test("Profit & Loss Report", success, details)
            return success
        except Exception as e:
            self.log_test("Profit & Loss Report", False, str(e))
            return False

    def test_trial_balance(self):
        """Test trial balance report"""
        try:
            response = requests.get(f"{self.api_url}/reports/trial-balance", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Accounts: {len(data.get('accounts', {}))}"
                details += f", Total Dr: ₹{data.get('total_debit', 0)}"
                details += f", Total Cr: ₹{data.get('total_credit', 0)}"
                
                # Check if trial balance is balanced
                diff = data.get('difference', 0)
                if abs(diff) < 0.01:  # Allow for small rounding differences
                    details += ", Balanced: ✓"
                else:
                    details += f", Difference: ₹{diff}"
            
            self.log_test("Trial Balance Report", success, details)
            return success
        except Exception as e:
            self.log_test("Trial Balance Report", False, str(e))
            return False

    def test_vendors_crud(self):
        """Test vendor CRUD operations"""
        try:
            # Create vendor
            vendor_data = {
                "name": "Test Vendor Ltd",
                "gstin": "24ABCDE1234F1Z5",
                "contact": "+91-9876543210",
                "address": "Test Address, Mumbai"
            }
            
            response = requests.post(f"{self.api_url}/vendors", json=vendor_data, timeout=10)
            create_success = response.status_code == 200
            
            # Get vendors
            response = requests.get(f"{self.api_url}/vendors", timeout=10)
            get_success = response.status_code == 200
            
            success = create_success and get_success
            details = f"Create: {response.status_code if create_success else 'Failed'}, Get: {response.status_code if get_success else 'Failed'}"
            
            if get_success:
                vendors = response.json()
                details += f", Count: {len(vendors)}"
            
            self.log_test("Vendor CRUD Operations", success, details)
            return success
        except Exception as e:
            self.log_test("Vendor CRUD Operations", False, str(e))
            return False

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting AI-Native ERP Backend API Tests")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # Document upload and OCR
        doc_success, document_id = self.test_document_upload()
        
        # AI prompt processing
        prompt_success, transaction_id = self.test_prompt_processing(document_id)
        
        # Transaction management
        self.test_get_drafts()
        if transaction_id:
            self.test_post_transaction(transaction_id)
        self.test_get_posted_transactions()
        
        # AI reporting
        self.test_conversational_reporting()
        
        # Financial reports
        self.test_balance_sheet()
        self.test_profit_loss()
        self.test_trial_balance()
        
        # Vendor management
        self.test_vendors_crud()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = ERPAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())