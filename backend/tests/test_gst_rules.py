"""
GST Rules Engine Tests - Kairos AI ERP
Tests for India GST localization: CGST+SGST, CGST+UTGST, IGST computation
Tests state resolution, HSN/SAC validation, and integration with PO/SO
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGSTStates:
    """Tests for GET /api/gst/states - All 36 Indian states/UTs"""
    
    def test_get_all_states_returns_36_entries(self):
        """Verify all 36 states/UTs are returned"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        states = response.json()
        assert isinstance(states, list), "Response should be a list"
        assert len(states) == 36, f"Expected 36 states/UTs, got {len(states)}"
    
    def test_states_have_required_fields(self):
        """Each state should have code, name, alpha, is_ut, utgst, tax_regime"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200
        
        states = response.json()
        required_fields = ["code", "name", "alpha", "is_ut", "utgst", "tax_regime"]
        
        for state in states:
            for field in required_fields:
                assert field in state, f"State {state.get('name', 'unknown')} missing field: {field}"
    
    def test_maharashtra_state_code_27(self):
        """Maharashtra should have code 27"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200
        
        states = response.json()
        mh = next((s for s in states if s["code"] == "27"), None)
        assert mh is not None, "Maharashtra (code 27) not found"
        assert mh["name"] == "Maharashtra"
        assert mh["alpha"] == "MH"
        assert mh["is_ut"] == False
        assert mh["utgst"] == False
        assert mh["tax_regime"] == "CGST + SGST"
    
    def test_chandigarh_is_ut_with_utgst(self):
        """Chandigarh (04) should be UT with UTGST"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200
        
        states = response.json()
        ch = next((s for s in states if s["code"] == "04"), None)
        assert ch is not None, "Chandigarh (code 04) not found"
        assert ch["name"] == "Chandigarh"
        assert ch["is_ut"] == True
        assert ch["utgst"] == True
        assert ch["tax_regime"] == "CGST + UTGST"
    
    def test_delhi_is_ut_without_utgst(self):
        """Delhi (07) is UT with legislature, uses SGST not UTGST"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200
        
        states = response.json()
        dl = next((s for s in states if s["code"] == "07"), None)
        assert dl is not None, "Delhi (code 07) not found"
        assert dl["name"] == "Delhi"
        assert dl["is_ut"] == True
        assert dl["utgst"] == False  # Has legislature, uses SGST
        assert dl["tax_regime"] == "CGST + SGST"
    
    def test_ladakh_is_ut_with_utgst(self):
        """Ladakh (38) should be UT with UTGST"""
        response = requests.get(f"{BASE_URL}/api/gst/states")
        assert response.status_code == 200
        
        states = response.json()
        la = next((s for s in states if s["code"] == "38"), None)
        assert la is not None, "Ladakh (code 38) not found"
        assert la["name"] == "Ladakh"
        assert la["is_ut"] == True
        assert la["utgst"] == True
        assert la["tax_regime"] == "CGST + UTGST"


class TestGSTStateResolution:
    """Tests for GET /api/gst/state/{state} - State resolution by name/code/alpha"""
    
    def test_resolve_by_gst_code(self):
        """Resolve state by GST code (27 -> Maharashtra)"""
        response = requests.get(f"{BASE_URL}/api/gst/state/27")
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == "27"
        assert data["name"] == "Maharashtra"
    
    def test_resolve_by_name(self):
        """Resolve state by full name"""
        response = requests.get(f"{BASE_URL}/api/gst/state/Gujarat")
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == "24"
        assert data["name"] == "Gujarat"
    
    def test_resolve_by_alpha_code(self):
        """Resolve state by alpha code (MH -> Maharashtra)"""
        response = requests.get(f"{BASE_URL}/api/gst/state/MH")
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == "27"
        assert data["name"] == "Maharashtra"
    
    def test_resolve_by_lowercase_name(self):
        """Resolve state by lowercase name"""
        response = requests.get(f"{BASE_URL}/api/gst/state/maharashtra")
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == "27"
    
    def test_resolve_invalid_state_returns_404(self):
        """Invalid state should return 404"""
        response = requests.get(f"{BASE_URL}/api/gst/state/InvalidState")
        assert response.status_code == 404


class TestGSTComputeTax:
    """Tests for POST /api/gst/compute-tax - Tax computation"""
    
    def test_intra_state_maharashtra_cgst_sgst(self):
        """Intra-state Maharashtra -> Maharashtra returns CGST+SGST (9%+9% for 18%)"""
        payload = {
            "supplier_state": "Maharashtra",
            "recipient_state": "Maharashtra",
            "gst_rate": 18,
            "taxable_value": 10000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["supply_type"] == "intra_state"
        assert data["tax_type"] == "CGST + SGST"
        
        comp = data["components"]
        assert comp["cgst_rate"] == 9
        assert comp["sgst_rate"] == 9
        assert comp["cgst_amount"] == 900
        assert comp["sgst_amount"] == 900
        assert comp["igst_rate"] == 0
        assert comp["igst_amount"] == 0
        
        assert data["total_tax"] == 1800
        assert data["grand_total"] == 11800
    
    def test_inter_state_maharashtra_to_gujarat_igst(self):
        """Inter-state Maharashtra -> Gujarat returns IGST (18%)"""
        payload = {
            "supplier_state": "Maharashtra",
            "recipient_state": "Gujarat",
            "gst_rate": 18,
            "taxable_value": 10000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["supply_type"] == "inter_state"
        assert data["tax_type"] == "IGST"
        
        comp = data["components"]
        assert comp["igst_rate"] == 18
        assert comp["igst_amount"] == 1800
        assert comp["cgst_rate"] == 0
        assert comp["cgst_amount"] == 0
        assert comp["sgst_rate"] == 0
        assert comp["sgst_amount"] == 0
        
        assert data["total_tax"] == 1800
        assert data["grand_total"] == 11800
    
    def test_intra_ut_chandigarh_cgst_utgst(self):
        """Intra-UT Chandigarh -> Chandigarh returns CGST+UTGST"""
        payload = {
            "supplier_state": "Chandigarh",
            "recipient_state": "Chandigarh",
            "gst_rate": 18,
            "taxable_value": 10000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["supply_type"] == "intra_state"
        assert data["tax_type"] == "CGST + UTGST"
        
        comp = data["components"]
        assert comp["cgst_rate"] == 9
        assert comp["utgst_rate"] == 9
        assert comp["cgst_amount"] == 900
        assert comp["utgst_amount"] == 900
        assert comp["sgst_rate"] == 0
        assert comp["sgst_amount"] == 0
        assert comp["igst_rate"] == 0
        assert comp["igst_amount"] == 0
        
        assert data["total_tax"] == 1800
    
    def test_inter_state_from_ut_chandigarh_to_maharashtra_igst(self):
        """Inter-state from UT (Chandigarh -> Maharashtra) returns IGST"""
        payload = {
            "supplier_state": "Chandigarh",
            "recipient_state": "Maharashtra",
            "gst_rate": 18,
            "taxable_value": 10000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["supply_type"] == "inter_state"
        assert data["tax_type"] == "IGST"
        
        comp = data["components"]
        assert comp["igst_rate"] == 18
        assert comp["igst_amount"] == 1800
    
    def test_intra_ut_ladakh_cgst_utgst(self):
        """Intra-UT Ladakh -> Ladakh returns CGST+UTGST"""
        payload = {
            "supplier_state": "Ladakh",
            "recipient_state": "Ladakh",
            "gst_rate": 12,
            "taxable_value": 5000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tax_type"] == "CGST + UTGST"
        assert data["components"]["cgst_rate"] == 6
        assert data["components"]["utgst_rate"] == 6
        assert data["total_tax"] == 600
    
    def test_intra_ut_delhi_cgst_sgst(self):
        """Delhi (UT with legislature) uses CGST+SGST, not UTGST"""
        payload = {
            "supplier_state": "Delhi",
            "recipient_state": "Delhi",
            "gst_rate": 18,
            "taxable_value": 10000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tax_type"] == "CGST + SGST"  # Not UTGST
        assert data["components"]["sgst_rate"] == 9
        assert data["components"]["utgst_rate"] == 0
    
    def test_compute_tax_missing_states_returns_400(self):
        """Missing supplier/recipient state should return 400"""
        payload = {
            "gst_rate": 18,
            "taxable_value": 10000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 400
    
    def test_compute_tax_with_state_codes(self):
        """Compute tax using GST state codes instead of names"""
        payload = {
            "supplier_state": "27",  # Maharashtra
            "recipient_state": "24",  # Gujarat
            "gst_rate": 18,
            "taxable_value": 10000
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-tax", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["tax_type"] == "IGST"
        assert data["supplier_state"]["code"] == "27"
        assert data["recipient_state"]["code"] == "24"


class TestGSTComputeLineItems:
    """Tests for POST /api/gst/compute-line-items - Multi-item tax computation"""
    
    def test_multi_item_tax_computation(self):
        """Compute tax for multiple items with different HSN/rates"""
        payload = {
            "supplier_state": "Maharashtra",
            "recipient_state": "Gujarat",
            "items": [
                {"hsn_sac": "2907", "item": "RM-BPA", "gst_rate": 18, "taxable_value": 50000},
                {"hsn_sac": "2929", "item": "RM-MDI", "gst_rate": 18, "taxable_value": 30000},
                {"hsn_sac": "3907", "item": "EP-1000", "gst_rate": 12, "taxable_value": 20000}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-line-items", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "line_items" in data
        assert len(data["line_items"]) == 3
        
        # All should be IGST (inter-state)
        for item in data["line_items"]:
            assert item["tax_type"] == "IGST"
        
        # Check totals
        totals = data["totals"]
        assert totals["taxable_value"] == 100000
        # IGST: 50000*0.18 + 30000*0.18 + 20000*0.12 = 9000 + 5400 + 2400 = 16800
        assert totals["igst"] == 16800
        assert totals["cgst"] == 0
        assert totals["sgst"] == 0
        assert totals["total_tax"] == 16800
        assert totals["grand_total"] == 116800
    
    def test_multi_item_intra_state(self):
        """Multi-item intra-state should have CGST+SGST"""
        payload = {
            "supplier_state": "Maharashtra",
            "recipient_state": "Maharashtra",
            "items": [
                {"hsn_sac": "2907", "item": "RM-BPA", "gst_rate": 18, "taxable_value": 10000},
                {"hsn_sac": "2929", "item": "RM-MDI", "gst_rate": 18, "taxable_value": 10000}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-line-items", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        totals = data["totals"]
        
        # CGST+SGST: 20000 * 0.18 = 3600, split 1800+1800
        assert totals["cgst"] == 1800
        assert totals["sgst"] == 1800
        assert totals["igst"] == 0
        assert totals["total_tax"] == 3600
    
    def test_compute_line_items_missing_items_returns_400(self):
        """Missing items array should return 400"""
        payload = {
            "supplier_state": "Maharashtra",
            "recipient_state": "Gujarat"
        }
        response = requests.post(f"{BASE_URL}/api/gst/compute-line-items", json=payload)
        assert response.status_code == 400


class TestGSTValidateHSN:
    """Tests for POST /api/gst/validate-hsn - HSN/SAC validation"""
    
    def test_valid_hsn_2_digit(self):
        """2-digit HSN code is valid"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "29"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["type"] == "HSN"
        assert data["category"] == "Goods"
    
    def test_valid_hsn_4_digit(self):
        """4-digit HSN code is valid"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "2907"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["type"] == "HSN"
    
    def test_valid_hsn_8_digit(self):
        """8-digit HSN code is valid"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "29071100"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["type"] == "HSN"
    
    def test_valid_sac_code(self):
        """SAC code starting with 99 is valid for services"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "9954"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["type"] == "SAC"
        assert data["category"] == "Services"
    
    def test_valid_sac_6_digit(self):
        """6-digit SAC code is valid"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "995411"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["type"] == "SAC"
    
    def test_invalid_hsn_1_digit(self):
        """1-digit code is invalid"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "2"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
    
    def test_invalid_hsn_9_digit(self):
        """9-digit HSN code is invalid (max 8)"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "290711001"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
    
    def test_invalid_hsn_non_numeric(self):
        """Non-numeric code is invalid"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": "29AB"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False
    
    def test_empty_hsn_code(self):
        """Empty code is invalid"""
        response = requests.post(f"{BASE_URL}/api/gst/validate-hsn", json={"code": ""})
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == False


class TestGSTRateSlabs:
    """Tests for GET /api/gst/rate-slabs"""
    
    def test_get_rate_slabs(self):
        """Get standard GST rate slabs"""
        response = requests.get(f"{BASE_URL}/api/gst/rate-slabs")
        assert response.status_code == 200
        
        data = response.json()
        assert "slabs" in data
        assert data["slabs"] == [0, 0.25, 3, 5, 12, 18, 28]
    
    def test_rate_slabs_have_descriptions(self):
        """Rate slabs should have common_rates with descriptions"""
        response = requests.get(f"{BASE_URL}/api/gst/rate-slabs")
        assert response.status_code == 200
        
        data = response.json()
        assert "common_rates" in data
        assert len(data["common_rates"]) >= 5
        
        # Check 18% rate exists
        rate_18 = next((r for r in data["common_rates"] if r["rate"] == 18), None)
        assert rate_18 is not None
        assert "description" in rate_18


class TestPurchaseOrderGSTIntegration:
    """Tests for PO creation with GST rules integration"""
    
    def test_po_with_gujarat_vendor_from_maharashtra_igst(self):
        """PO with Gujarat vendor from Maharashtra company -> IGST in tax_breakdown"""
        payload = {
            "vendor": "INEOS India",  # Gujarat vendor (code 24)
            "items": [
                {"item_code": "RM-BPA", "qty": 100, "rate": 500, "amount": 50000}
            ],
            "cost_center": "Production"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/orders", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "tax_breakdown" in data
        
        tb = data["tax_breakdown"]
        assert tb["supply_type"] == "IGST" or "inter" in tb.get("supply_type", "").lower()
        assert tb["igst"] > 0
        assert tb["cgst"] == 0
        assert tb["sgst"] == 0
    
    def test_po_with_maharashtra_vendor_from_maharashtra_cgst_sgst(self):
        """PO with Maharashtra vendor from Maharashtra company -> CGST+SGST"""
        payload = {
            "vendor": "LANXESS India",  # Maharashtra vendor (code 27)
            "items": [
                {"item_code": "RM-MDI", "qty": 50, "rate": 600, "amount": 30000}
            ],
            "cost_center": "Production"
        }
        response = requests.post(f"{BASE_URL}/api/purchase/orders", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "tax_breakdown" in data
        
        tb = data["tax_breakdown"]
        assert "CGST" in tb.get("supply_type", "") or "intra" in tb.get("supply_type", "").lower()
        assert tb["cgst"] > 0
        assert tb["sgst"] > 0
        assert tb["igst"] == 0


class TestSalesOrderGSTIntegration:
    """Tests for SO creation with GST rules integration"""
    
    def test_so_with_inter_state_customer_igst(self):
        """SO with inter-state customer -> IGST in tax_breakdown"""
        # First, check if we have an inter-state customer
        entities_resp = requests.get(f"{BASE_URL}/api/entities?entity_type=customer")
        if entities_resp.status_code != 200:
            pytest.skip("Cannot fetch customers")
        
        customers = entities_resp.json()
        # Find a customer not in Maharashtra
        inter_state_customer = next(
            (c for c in customers if c.get("state") and c.get("state") != "Maharashtra"),
            None
        )
        
        if not inter_state_customer:
            pytest.skip("No inter-state customer found in master data")
        
        payload = {
            "customer": inter_state_customer["name"],
            "items": [
                {"item_code": "EP-1000", "qty": 10, "rate": 1000, "amount": 10000}
            ],
            "cost_center": "Sales & Marketing"
        }
        response = requests.post(f"{BASE_URL}/api/selling/sales-orders", json=payload)
        
        if response.status_code == 400:
            # Customer or item might not exist
            pytest.skip(f"SO creation failed: {response.json()}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "tax_breakdown" in data
        
        tb = data["tax_breakdown"]
        # Should be IGST for inter-state
        assert tb["igst"] > 0 or "IGST" in tb.get("supply_type", "")


class TestMasterDataGSTFields:
    """Tests for GST fields in master data after migration"""
    
    def test_items_have_hsn_sac_and_gst_rate(self):
        """Items in DB should have hsn_sac and gst_rate fields"""
        response = requests.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        
        items = response.json()
        if not items:
            pytest.skip("No items in database")
        
        # Check seeded items have HSN/SAC
        for item in items[:5]:  # Check first 5
            # hsn_sac should exist (may be empty for some)
            assert "hsn_sac" in item or "hsn_code" in item, f"Item {item.get('item_code')} missing hsn_sac"
            assert "gst_rate" in item, f"Item {item.get('item_code')} missing gst_rate"
    
    def test_entities_have_gst_state_code(self):
        """Entities (vendors/customers) with Indian GSTIN should have gst_state_code and state fields"""
        response = requests.get(f"{BASE_URL}/api/entities")
        assert response.status_code == 200
        
        entities = response.json()
        if not entities:
            pytest.skip("No entities in database")
        
        # Check entities with valid Indian GSTIN (15 chars) have state info
        # Foreign entities may not have GSTIN or state info
        entities_with_gstin = [e for e in entities if e.get("gstin") and len(e.get("gstin", "")) == 15]
        
        if not entities_with_gstin:
            pytest.skip("No entities with valid Indian GSTIN found")
        
        for entity in entities_with_gstin[:5]:  # Check first 5
            # Should have state info derived from GSTIN
            has_state_info = (
                entity.get("gst_state_code") or 
                entity.get("state_code") or 
                entity.get("state")
            )
            assert has_state_info, f"Entity {entity.get('name')} with GSTIN {entity.get('gstin')} missing state info"


class TestSpecificVendorStates:
    """Tests for specific seeded vendor states"""
    
    def test_ineos_india_is_gujarat(self):
        """INEOS India should be in Gujarat (code 24)"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        assert response.status_code == 200
        
        vendors = response.json()
        ineos = next((v for v in vendors if "INEOS" in v.get("name", "")), None)
        
        if not ineos:
            pytest.skip("INEOS India vendor not found")
        
        # Check state is Gujarat
        state = ineos.get("state") or ineos.get("state_name")
        state_code = ineos.get("gst_state_code") or ineos.get("state_code")
        
        assert state == "Gujarat" or state_code == "24", f"INEOS India state: {state}, code: {state_code}"
    
    def test_lanxess_india_is_maharashtra(self):
        """LANXESS India should be in Maharashtra (code 27)"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        assert response.status_code == 200
        
        vendors = response.json()
        lanxess = next((v for v in vendors if "LANXESS" in v.get("name", "")), None)
        
        if not lanxess:
            pytest.skip("LANXESS India vendor not found")
        
        state = lanxess.get("state") or lanxess.get("state_name")
        state_code = lanxess.get("gst_state_code") or lanxess.get("state_code")
        
        assert state == "Maharashtra" or state_code == "27", f"LANXESS India state: {state}, code: {state_code}"
    
    def test_motherson_sumi_is_uttar_pradesh(self):
        """Motherson Sumi Systems should be in Uttar Pradesh (code 09)"""
        response = requests.get(f"{BASE_URL}/api/entities?entity_type=vendor")
        assert response.status_code == 200
        
        vendors = response.json()
        motherson = next((v for v in vendors if "Motherson" in v.get("name", "")), None)
        
        if not motherson:
            pytest.skip("Motherson Sumi Systems vendor not found")
        
        state = motherson.get("state") or motherson.get("state_name")
        state_code = motherson.get("gst_state_code") or motherson.get("state_code")
        
        assert state == "Uttar Pradesh" or state_code == "09", f"Motherson state: {state}, code: {state_code}"


class TestSpecificItemHSN:
    """Tests for specific seeded item HSN codes"""
    
    def test_rm_bpa_has_hsn_2907(self):
        """RM-BPA should have HSN 2907"""
        response = requests.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        
        items = response.json()
        bpa = next((i for i in items if i.get("item_code") == "RM-BPA"), None)
        
        if not bpa:
            pytest.skip("RM-BPA item not found")
        
        hsn = bpa.get("hsn_sac") or bpa.get("hsn_code")
        assert hsn == "2907", f"RM-BPA HSN: {hsn}"
    
    def test_rm_mdi_has_hsn_2929(self):
        """RM-MDI should have HSN 2929"""
        response = requests.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        
        items = response.json()
        mdi = next((i for i in items if i.get("item_code") == "RM-MDI"), None)
        
        if not mdi:
            pytest.skip("RM-MDI item not found")
        
        hsn = mdi.get("hsn_sac") or mdi.get("hsn_code")
        assert hsn == "2929", f"RM-MDI HSN: {hsn}"
    
    def test_ep_1000_has_hsn_3907(self):
        """EP-1000 should have HSN 3907"""
        response = requests.get(f"{BASE_URL}/api/stock/items")
        assert response.status_code == 200
        
        items = response.json()
        ep = next((i for i in items if i.get("item_code") == "EP-1000"), None)
        
        if not ep:
            pytest.skip("EP-1000 item not found")
        
        hsn = ep.get("hsn_sac") or ep.get("hsn_code")
        assert hsn == "3907", f"EP-1000 HSN: {hsn}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
