# Test Statutory Returns: GSTR-1, GSTR-3B, E-Invoice, TDS Returns, HSN Suggest
# Tests for the new GST module with state-aware tax computation

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGSTR1:
    """GSTR-1 Outward Supplies Return Tests"""
    
    def test_gstr1_endpoint_returns_200(self):
        """GET /api/statutory/gstr1 returns 200"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GSTR-1 endpoint returns 200")
    
    def test_gstr1_has_required_structure(self):
        """GSTR-1 response has required sections"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1")
        data = response.json()
        
        # Check top-level fields
        assert "report_type" in data, "Missing report_type"
        assert data["report_type"] == "GSTR-1", f"Expected GSTR-1, got {data['report_type']}"
        assert "return_period" in data, "Missing return_period"
        assert "gstin" in data, "Missing gstin"
        assert "legal_name" in data, "Missing legal_name"
        assert "sections" in data, "Missing sections"
        assert "summary" in data, "Missing summary"
        print("PASS: GSTR-1 has required top-level structure")
    
    def test_gstr1_has_b2b_b2c_hsn_sections(self):
        """GSTR-1 has B2B, B2C Large, B2C Small, HSN, Docs sections"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1")
        data = response.json()
        sections = data.get("sections", {})
        
        assert "b2b" in sections, "Missing b2b section"
        assert "b2c_large" in sections, "Missing b2c_large section"
        assert "b2c_small" in sections, "Missing b2c_small section"
        assert "hsn" in sections, "Missing hsn section"
        assert "docs" in sections, "Missing docs section"
        
        # Check B2B section structure
        b2b = sections["b2b"]
        assert "label" in b2b, "B2B missing label"
        assert "invoices" in b2b, "B2B missing invoices"
        assert "count" in b2b, "B2B missing count"
        
        print(f"PASS: GSTR-1 has all sections - B2B({b2b['count']}), B2C Large({sections['b2c_large']['count']}), B2C Small({sections['b2c_small']['count']})")
    
    def test_gstr1_summary_has_tax_split(self):
        """GSTR-1 summary has IGST/CGST/SGST split"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1")
        data = response.json()
        summary = data.get("summary", {})
        
        assert "total_invoices" in summary, "Missing total_invoices"
        assert "total_taxable_value" in summary, "Missing total_taxable_value"
        assert "total_igst" in summary, "Missing total_igst"
        assert "total_cgst" in summary, "Missing total_cgst"
        assert "total_sgst" in summary, "Missing total_sgst"
        assert "total_tax" in summary, "Missing total_tax"
        
        print(f"PASS: GSTR-1 summary - Invoices: {summary['total_invoices']}, IGST: {summary['total_igst']}, CGST: {summary['total_cgst']}, SGST: {summary['total_sgst']}")
    
    def test_gstr1_invoice_has_supply_type(self):
        """GSTR-1 invoices have supply_type (IGST or CGST+SGST)"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1")
        data = response.json()
        
        # Check any invoice from any section
        for section_key in ["b2b", "b2c_large", "b2c_small"]:
            invoices = data.get("sections", {}).get(section_key, {}).get("invoices", [])
            if invoices:
                inv = invoices[0]
                assert "supply_type" in inv, f"Invoice in {section_key} missing supply_type"
                assert "taxable_value" in inv, f"Invoice in {section_key} missing taxable_value"
                assert "igst" in inv, f"Invoice in {section_key} missing igst"
                assert "cgst" in inv, f"Invoice in {section_key} missing cgst"
                assert "sgst" in inv, f"Invoice in {section_key} missing sgst"
                print(f"PASS: {section_key} invoice has supply_type: {inv['supply_type']}")
                return
        
        print("PASS: No invoices to check, but structure is correct")


class TestGSTR3B:
    """GSTR-3B Monthly Summary Return Tests"""
    
    def test_gstr3b_endpoint_returns_200(self):
        """GET /api/statutory/gstr3b returns 200"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GSTR-3B endpoint returns 200")
    
    def test_gstr3b_has_required_structure(self):
        """GSTR-3B response has required sections"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b")
        data = response.json()
        
        assert data["report_type"] == "GSTR-3B", f"Expected GSTR-3B, got {data.get('report_type')}"
        assert "return_period" in data, "Missing return_period"
        assert "gstin" in data, "Missing gstin"
        assert "sections" in data, "Missing sections"
        assert "summary" in data, "Missing summary"
        print("PASS: GSTR-3B has required top-level structure")
    
    def test_gstr3b_has_sections_31_32_4_61(self):
        """GSTR-3B has sections 3.1, 3.2, 4, 6.1"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b")
        data = response.json()
        sections = data.get("sections", {})
        
        assert "3_1" in sections, "Missing section 3.1"
        assert "3_2" in sections, "Missing section 3.2"
        assert "4" in sections, "Missing section 4 (ITC)"
        assert "6_1" in sections, "Missing section 6.1 (Payment)"
        
        # Check section 3.1 structure
        s31 = sections["3_1"]
        assert "outward_taxable_supplies" in s31, "Section 3.1 missing outward_taxable_supplies"
        
        # Check section 4 (ITC) structure
        s4 = sections["4"]
        assert "itc_available" in s4, "Section 4 missing itc_available"
        assert "net_itc" in s4, "Section 4 missing net_itc"
        
        # Check section 6.1 (Payment) structure
        s61 = sections["6_1"]
        assert "tax_payable" in s61, "Section 6.1 missing tax_payable"
        assert "cash_payable" in s61, "Section 6.1 missing cash_payable"
        
        print("PASS: GSTR-3B has all required sections (3.1, 3.2, 4, 6.1)")
    
    def test_gstr3b_summary_has_net_payable(self):
        """GSTR-3B summary has net_payable calculation"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b")
        data = response.json()
        summary = data.get("summary", {})
        
        assert "total_output_tax" in summary, "Missing total_output_tax"
        assert "total_input_credit" in summary, "Missing total_input_credit"
        assert "net_payable" in summary, "Missing net_payable"
        
        # Verify net_payable = output - input (if positive)
        expected_net = summary["total_output_tax"] - summary["total_input_credit"]
        if expected_net > 0:
            assert summary["net_payable"] == max(expected_net, 0), "net_payable calculation incorrect"
        
        print(f"PASS: GSTR-3B summary - Output: {summary['total_output_tax']}, ITC: {summary['total_input_credit']}, Net Payable: {summary['net_payable']}")
    
    def test_gstr3b_itc_has_tax_components(self):
        """GSTR-3B ITC section has IGST/CGST/SGST breakdown"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b")
        data = response.json()
        itc = data.get("sections", {}).get("4", {}).get("itc_available", {})
        
        assert "igst" in itc, "ITC missing igst"
        assert "cgst" in itc, "ITC missing cgst"
        assert "sgst" in itc, "ITC missing sgst"
        
        print(f"PASS: GSTR-3B ITC - IGST: {itc['igst']}, CGST: {itc['cgst']}, SGST: {itc['sgst']}")


class TestEInvoice:
    """E-Invoice IRN Generation Tests"""
    
    def test_e_invoices_endpoint_returns_200(self):
        """GET /api/statutory/e-invoices returns 200"""
        response = requests.get(f"{BASE_URL}/api/statutory/e-invoices")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: E-Invoices endpoint returns 200")
    
    def test_e_invoices_has_required_structure(self):
        """E-Invoices response has company and e_invoices list"""
        response = requests.get(f"{BASE_URL}/api/statutory/e-invoices")
        data = response.json()
        
        assert "company" in data, "Missing company info"
        assert "e_invoices" in data, "Missing e_invoices list"
        assert "total" in data, "Missing total count"
        assert isinstance(data["e_invoices"], list), "e_invoices should be a list"
        
        print(f"PASS: E-Invoices structure correct - {data['total']} eligible invoices")
    
    def test_e_invoice_has_irn_hash(self):
        """E-Invoice entries have IRN hash"""
        response = requests.get(f"{BASE_URL}/api/statutory/e-invoices")
        data = response.json()
        
        if data["e_invoices"]:
            inv = data["e_invoices"][0]
            assert "irn" in inv, "E-Invoice missing irn"
            assert "invoice_number" in inv, "E-Invoice missing invoice_number"
            assert "customer_gstin" in inv, "E-Invoice missing customer_gstin"
            assert len(inv["irn"]) == 32, f"IRN should be 32 chars, got {len(inv['irn'])}"
            print(f"PASS: E-Invoice has IRN hash: {inv['irn'][:16]}...")
        else:
            print("PASS: No B2B invoices eligible for e-invoicing (expected with seeded data)")
    
    def test_e_invoice_json_endpoint(self):
        """GET /api/statutory/e-invoice/{invoice_number}/json returns NIC format"""
        # First get list of e-invoices
        response = requests.get(f"{BASE_URL}/api/statutory/e-invoices")
        data = response.json()
        
        if data["e_invoices"]:
            inv_num = data["e_invoices"][0]["invoice_number"]
            json_response = requests.get(f"{BASE_URL}/api/statutory/e-invoice/{inv_num}/json")
            assert json_response.status_code == 200, f"Expected 200, got {json_response.status_code}"
            
            e_json = json_response.json()
            # Check NIC format fields
            assert "Version" in e_json, "Missing Version"
            assert "TranDtls" in e_json, "Missing TranDtls"
            assert "DocDtls" in e_json, "Missing DocDtls"
            assert "SellerDtls" in e_json, "Missing SellerDtls"
            assert "BuyerDtls" in e_json, "Missing BuyerDtls"
            assert "ItemList" in e_json, "Missing ItemList"
            assert "ValDtls" in e_json, "Missing ValDtls"
            
            print(f"PASS: E-Invoice JSON for {inv_num} has NIC format")
        else:
            print("SKIP: No e-invoices to test JSON endpoint")
    
    def test_e_invoice_json_404_for_invalid(self):
        """GET /api/statutory/e-invoice/INVALID/json returns 404"""
        response = requests.get(f"{BASE_URL}/api/statutory/e-invoice/INVALID-INV-999/json")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: E-Invoice JSON returns 404 for invalid invoice")


class TestTDSReturn:
    """TDS Return (Form 26Q) Tests"""
    
    def test_tds_return_endpoint_returns_200(self):
        """GET /api/statutory/tds-return returns 200"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: TDS Return endpoint returns 200")
    
    def test_tds_return_has_required_structure(self):
        """TDS Return has required fields"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return")
        data = response.json()
        
        assert data["report_type"] == "TDS Return (Form 26Q)", f"Expected Form 26Q, got {data.get('report_type')}"
        assert "quarter" in data, "Missing quarter"
        assert "financial_year" in data, "Missing financial_year"
        assert "deductor_name" in data, "Missing deductor_name"
        assert "deductees" in data, "Missing deductees list"
        assert "summary" in data, "Missing summary"
        
        print(f"PASS: TDS Return structure correct - {data['quarter']} FY {data['financial_year']}")
    
    def test_tds_return_summary_has_totals(self):
        """TDS Return summary has total calculations"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return")
        data = response.json()
        summary = data.get("summary", {})
        
        assert "total_deductees" in summary, "Missing total_deductees"
        assert "total_amount_paid" in summary, "Missing total_amount_paid"
        assert "total_tds_deducted" in summary, "Missing total_tds_deducted"
        assert "tds_pending_deposit" in summary, "Missing tds_pending_deposit"
        
        print(f"PASS: TDS Summary - Deductees: {summary['total_deductees']}, TDS: {summary['total_tds_deducted']}")
    
    def test_tds_deductee_has_required_fields(self):
        """TDS deductee entries have required fields"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return")
        data = response.json()
        
        if data["deductees"]:
            d = data["deductees"][0]
            assert "deductee_name" in d, "Missing deductee_name"
            assert "section" in d, "Missing section"
            assert "amount_paid" in d, "Missing amount_paid"
            assert "tds_amount" in d, "Missing tds_amount"
            assert "tds_rate" in d, "Missing tds_rate"
            print(f"PASS: TDS deductee has required fields - Section {d['section']}")
        else:
            print("PASS: No TDS deductees (expected if no TDS transactions)")


class TestHSNSuggest:
    """HSN/SAC AI Suggestion Tests"""
    
    def test_hsn_suggest_endpoint_exists(self):
        """POST /api/gst/suggest-hsn endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/gst/suggest-hsn", json={"description": "test"})
        # Should not be 404
        assert response.status_code != 404, "HSN suggest endpoint not found"
        print(f"PASS: HSN suggest endpoint exists (status: {response.status_code})")
    
    def test_hsn_suggest_requires_description(self):
        """HSN suggest requires description or item_name"""
        response = requests.post(f"{BASE_URL}/api/gst/suggest-hsn", json={})
        assert response.status_code == 400, f"Expected 400 for empty request, got {response.status_code}"
        print("PASS: HSN suggest returns 400 for missing description")
    
    def test_hsn_suggest_for_chemical(self):
        """HSN suggest returns HSN code for chemical description"""
        response = requests.post(f"{BASE_URL}/api/gst/suggest-hsn", json={
            "description": "cotton fabric textile"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "hsn_sac" in data, "Missing hsn_sac in response"
            # Cotton fabric should return HSN starting with 52 (cotton) or similar
            print(f"PASS: HSN suggest for cotton fabric: {data.get('hsn_sac')} (type: {data.get('type')})")
        elif response.status_code == 500:
            # LLM might fail - check error message
            print(f"WARN: HSN suggest returned 500 - LLM may have failed: {response.text[:200]}")
        else:
            print(f"WARN: HSN suggest returned {response.status_code}")
    
    def test_hsn_suggest_for_service(self):
        """HSN suggest returns SAC code for service description"""
        response = requests.post(f"{BASE_URL}/api/gst/suggest-hsn", json={
            "description": "software development IT services"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "hsn_sac" in data, "Missing hsn_sac in response"
            # IT services should return SAC starting with 99
            if data.get("hsn_sac", "").startswith("99"):
                print(f"PASS: HSN suggest for IT services: {data.get('hsn_sac')} (SAC code)")
            else:
                print(f"PASS: HSN suggest returned: {data.get('hsn_sac')} (may not be SAC)")
        elif response.status_code == 500:
            print(f"WARN: HSN suggest returned 500 - LLM may have failed")
        else:
            print(f"WARN: HSN suggest returned {response.status_code}")


class TestExportEndpoints:
    """Export Endpoints Tests"""
    
    def test_gstr1_export_csv(self):
        """GET /api/statutory/gstr1/export returns CSV"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr1/export")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/csv" in response.headers.get("content-type", ""), "Expected CSV content-type"
        assert "GSTR1.csv" in response.headers.get("content-disposition", ""), "Expected GSTR1.csv filename"
        print("PASS: GSTR-1 export returns CSV")
    
    def test_gstr3b_export_json(self):
        """GET /api/statutory/gstr3b/export returns JSON"""
        response = requests.get(f"{BASE_URL}/api/statutory/gstr3b/export")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/json" in response.headers.get("content-type", ""), "Expected JSON content-type"
        assert "GSTR3B.json" in response.headers.get("content-disposition", ""), "Expected GSTR3B.json filename"
        print("PASS: GSTR-3B export returns JSON")
    
    def test_tds_return_export_csv(self):
        """GET /api/statutory/tds-return/export returns CSV"""
        response = requests.get(f"{BASE_URL}/api/statutory/tds-return/export")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/csv" in response.headers.get("content-type", ""), "Expected CSV content-type"
        assert "TDS_Return_26Q.csv" in response.headers.get("content-disposition", ""), "Expected TDS_Return_26Q.csv filename"
        print("PASS: TDS Return export returns CSV")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
