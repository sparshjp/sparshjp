"""
Test GSTIN/PAN Validation Intelligence and Enhanced CSV Import Validation
Tests for Kairos Advisory ERP - P0 Items

Modules tested:
- GSTIN validation: format, PAN extraction, state mapping, entity type
- PAN validation: format, entity type extraction
- Entity creation with GSTIN auto-enrichment
- CSV validation: headers, numeric fields, journal balance, CoA cross-check
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGSTINValidation:
    """GSTIN validation endpoint tests"""
    
    def test_valid_gstin_maharashtra_company(self):
        """Test valid GSTIN 27AABCU9603R1ZM - Maharashtra, Company"""
        response = requests.get(f"{BASE_URL}/api/validate/gstin/27AABCU9603R1ZM")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["pan"] == "AABCU9603R"
        assert data["state_code"] == "27"
        assert data["state_name"] == "Maharashtra"
        assert data["entity_type"] == "Company"
        print(f"✓ Valid GSTIN (Maharashtra, Company): {data}")
    
    def test_valid_gstin_delhi_company(self):
        """Test valid GSTIN 07AAACI1681G1ZP - Delhi, Company"""
        response = requests.get(f"{BASE_URL}/api/validate/gstin/07AAACI1681G1ZP")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["pan"] == "AAACI1681G"
        assert data["state_code"] == "07"
        assert data["state_name"] == "Delhi"
        assert data["entity_type"] == "Company"
        print(f"✓ Valid GSTIN (Delhi, Company): {data}")
    
    def test_invalid_gstin_format(self):
        """Test invalid GSTIN returns valid=false with error"""
        response = requests.get(f"{BASE_URL}/api/validate/gstin/INVALID")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        assert "errors" in data
        assert len(data["errors"]) > 0
        print(f"✓ Invalid GSTIN rejected: {data['errors']}")
    
    def test_invalid_gstin_wrong_length(self):
        """Test GSTIN with wrong length"""
        response = requests.get(f"{BASE_URL}/api/validate/gstin/27AABCU9603R1Z")  # 14 chars
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        assert any("15 characters" in err for err in data["errors"])
        print(f"✓ Wrong length GSTIN rejected: {data['errors']}")
    
    def test_invalid_gstin_bad_state_code(self):
        """Test GSTIN with invalid state code"""
        response = requests.get(f"{BASE_URL}/api/validate/gstin/99AABCU9603R1ZM")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        print(f"✓ Invalid state code rejected: {data}")


class TestPANValidation:
    """PAN validation endpoint tests"""
    
    def test_valid_pan_company(self):
        """Test valid PAN AABCU9603R - Company (4th char = C)"""
        response = requests.get(f"{BASE_URL}/api/validate/pan/AABCU9603R")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["entity_type"] == "Company"
        print(f"✓ Valid PAN (Company): {data}")
    
    def test_valid_pan_individual(self):
        """Test valid PAN BBBPP1234A - Individual/Proprietor (4th char = P)"""
        response = requests.get(f"{BASE_URL}/api/validate/pan/BBBPP1234A")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert "Individual" in data["entity_type"] or "Proprietor" in data["entity_type"]
        print(f"✓ Valid PAN (Individual): {data}")
    
    def test_valid_pan_firm(self):
        """Test valid PAN with F (Firm/LLP)"""
        response = requests.get(f"{BASE_URL}/api/validate/pan/AAAFB1234C")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert "Firm" in data["entity_type"] or "LLP" in data["entity_type"]
        print(f"✓ Valid PAN (Firm): {data}")
    
    def test_invalid_pan_format(self):
        """Test invalid PAN returns valid=false"""
        response = requests.get(f"{BASE_URL}/api/validate/pan/INVALID")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        assert "errors" in data
        print(f"✓ Invalid PAN rejected: {data['errors']}")
    
    def test_invalid_pan_wrong_length(self):
        """Test PAN with wrong length"""
        response = requests.get(f"{BASE_URL}/api/validate/pan/AABCU960")  # 8 chars
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        assert any("10 characters" in err for err in data["errors"])
        print(f"✓ Wrong length PAN rejected: {data['errors']}")


class TestEntityCreationWithGSTIN:
    """Entity creation with GSTIN auto-enrichment tests"""
    
    def test_create_entity_with_valid_gstin_extracts_pan(self):
        """POST /api/entities with GSTIN auto-extracts PAN, state, constitution"""
        payload = {
            "entity_type": "vendor",
            "name": "TEST_GSTIN_Vendor_001",
            "gstin": "27AABCU9603R1ZM"
        }
        response = requests.post(f"{BASE_URL}/api/entities", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Verify auto-extraction
        assert data["pan"] == "AABCU9603R", f"PAN should be extracted from GSTIN, got {data.get('pan')}"
        assert data["state_name"] == "Maharashtra", f"State should be Maharashtra, got {data.get('state_name')}"
        assert data["constitution"] == "Company", f"Constitution should be Company, got {data.get('constitution')}"
        assert data["gstin_valid"] == True
        print(f"✓ Entity created with GSTIN enrichment: PAN={data['pan']}, State={data['state_name']}, Constitution={data['constitution']}")
    
    def test_create_entity_with_invalid_gstin(self):
        """POST /api/entities with invalid GSTIN marks gstin_valid=false"""
        payload = {
            "entity_type": "vendor",
            "name": "TEST_Invalid_GSTIN_Vendor",
            "gstin": "INVALIDGSTIN123"
        }
        response = requests.post(f"{BASE_URL}/api/entities", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["gstin_valid"] == False
        assert "gstin_errors" in data
        print(f"✓ Entity created with invalid GSTIN flagged: {data.get('gstin_errors')}")
    
    def test_create_entity_with_pan_only(self):
        """POST /api/entities with PAN extracts entity type"""
        payload = {
            "entity_type": "client",
            "name": "TEST_PAN_Client_001",
            "pan": "BBBPP1234A"
        }
        response = requests.post(f"{BASE_URL}/api/entities", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "Individual" in data.get("constitution", "") or "Proprietor" in data.get("constitution", "")
        print(f"✓ Entity created with PAN enrichment: Constitution={data.get('constitution')}")


class TestCSVValidation:
    """Enhanced CSV validation tests"""
    
    def test_csv_validation_unbalanced_journals(self):
        """POST /api/import/validate with unbalanced journals returns valid=false"""
        csv_data = """Date,Ledger,Debit,Credit,Description
2025-01-15,Cash,1000,0,Cash receipt
2025-01-15,Sales,0,500,Sales revenue"""  # Unbalanced: 1000 debit vs 500 credit
        
        payload = {"module": "journals", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        # Check for balance error
        balance_error = any("not balanced" in err.lower() or "debit" in err.lower() and "credit" in err.lower() 
                          for err in data.get("errors", []))
        assert balance_error, f"Should have balance error, got: {data.get('errors')}"
        print(f"✓ Unbalanced journal rejected: {data['errors']}")
    
    def test_csv_validation_missing_headers(self):
        """POST /api/import/validate with missing headers returns errors"""
        csv_data = """Date,Ledger,Description
2025-01-15,Cash,Test entry"""  # Missing Debit and Credit headers
        
        payload = {"module": "journals", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        # Check for missing header errors
        missing_header_error = any("missing" in err.lower() and "header" in err.lower() 
                                   for err in data.get("errors", []))
        assert missing_header_error, f"Should have missing header error, got: {data.get('errors')}"
        print(f"✓ Missing headers rejected: {data['errors']}")
    
    def test_csv_validation_non_numeric_values(self):
        """POST /api/import/validate with non-numeric values returns errors"""
        csv_data = """Date,Ledger,Debit,Credit,Description
2025-01-15,Cash,ABC,0,Invalid debit
2025-01-15,Sales,0,XYZ,Invalid credit"""
        
        payload = {"module": "journals", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        # Check for numeric validation errors (could be "number", "numeric", or "convert string to float")
        numeric_error = any("number" in err.lower() or "numeric" in err.lower() or "float" in err.lower()
                          for err in data.get("errors", []))
        assert numeric_error, f"Should have numeric validation error, got: {data.get('errors')}"
        print(f"✓ Non-numeric values rejected: {data['errors']}")
    
    def test_csv_validation_invalid_date_format(self):
        """POST /api/import/validate with invalid date format returns errors"""
        csv_data = """Date,Ledger,Debit,Credit,Description
15-01-2025,Cash,1000,0,Wrong date format
2025-01-15,Sales,0,1000,Correct format"""
        
        payload = {"module": "journals", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Should have date format error
        date_error = any("date" in err.lower() and "format" in err.lower() 
                        for err in data.get("errors", []))
        assert date_error, f"Should have date format error, got: {data.get('errors')}"
        print(f"✓ Invalid date format flagged: {data['errors']}")
    
    def test_csv_validation_valid_balanced_journals(self):
        """POST /api/import/validate with valid balanced journals returns valid=true"""
        csv_data = """Date,Ledger,Debit,Credit,Description
2025-01-15,Cash,1000,0,Cash receipt
2025-01-15,Sales,0,1000,Sales revenue"""  # Balanced: 1000 = 1000
        
        payload = {"module": "journals", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True, f"Should be valid, got errors: {data.get('errors')}"
        assert data["row_count"] == 2
        print(f"✓ Valid balanced journal accepted: row_count={data['row_count']}")
    
    def test_csv_validation_purchases_module(self):
        """POST /api/import/validate for purchases module"""
        csv_data = """Date,Entity Name,Item/Service,Rate,GST Rate,Total
2025-01-15,Test Vendor,Office Supplies,1000,18,1180"""
        
        payload = {"module": "purchases", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True, f"Should be valid, got errors: {data.get('errors')}"
        print(f"✓ Valid purchases CSV accepted: {data}")
    
    def test_csv_validation_empty_csv(self):
        """POST /api/import/validate with empty CSV returns error"""
        csv_data = ""
        
        payload = {"module": "journals", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
        print(f"✓ Empty CSV rejected: {data.get('errors')}")
    
    def test_csv_validation_coa_cross_check_warning(self):
        """POST /api/import/validate warns about ledgers not in CoA"""
        csv_data = """Date,Ledger,Debit,Credit,Description
2025-01-15,NonExistentLedger123,1000,0,Test
2025-01-15,AnotherFakeLedger456,0,1000,Test"""
        
        payload = {"module": "journals", "csv_data": csv_data}
        response = requests.post(f"{BASE_URL}/api/import/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Should have warnings about ledgers not in CoA
        coa_warning = any("not in chart of accounts" in warn.lower() or "not in coa" in warn.lower()
                         for warn in data.get("warnings", []))
        assert coa_warning, f"Should warn about ledgers not in CoA, got warnings: {data.get('warnings')}"
        print(f"✓ CoA cross-check warning: {data.get('warnings')}")


class TestAPIHealth:
    """Basic API health check"""
    
    def test_api_health(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "Kairos" in data.get("message", "")
        print(f"✓ API Health: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
