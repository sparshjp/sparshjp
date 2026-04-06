# GST Rules API - State-wise tax computation and HSN/SAC validation
from fastapi import APIRouter, HTTPException
from typing import Optional
import gst_rules

router = APIRouter(prefix="/gst", tags=["gst"])


@router.get("/states")
async def get_states():
    """Get all Indian states/UTs with GST codes and tax regimes"""
    return gst_rules.get_all_states()


@router.get("/state/{state_input}")
async def get_state(state_input: str):
    """Resolve a state name/code/alpha to full state info"""
    code = gst_rules.resolve_state_code(state_input)
    if not code:
        raise HTTPException(status_code=404, detail=f"State not found: {state_input}")
    return gst_rules.get_state_info(code)


@router.post("/compute-tax")
async def compute_tax(data: dict):
    """
    Compute GST components for a transaction.
    Body: {supplier_state, recipient_state, gst_rate, taxable_value}
    Returns: tax_type (CGST+SGST / CGST+UTGST / IGST), components, totals
    """
    supplier = data.get("supplier_state")
    recipient = data.get("recipient_state")
    gst_rate = data.get("gst_rate", 18)
    taxable_value = data.get("taxable_value", 0)

    if not supplier or not recipient:
        raise HTTPException(status_code=400, detail="supplier_state and recipient_state are required")

    result = gst_rules.compute_tax(supplier, recipient, gst_rate, taxable_value)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/compute-line-items")
async def compute_line_items(data: dict):
    """
    Compute GST for multiple line items with different HSN/rates.
    Body: {supplier_state, recipient_state, items: [{hsn_sac, gst_rate, taxable_value, item}, ...]}
    """
    supplier = data.get("supplier_state")
    recipient = data.get("recipient_state")
    items = data.get("items", [])

    if not supplier or not recipient:
        raise HTTPException(status_code=400, detail="supplier_state and recipient_state are required")
    if not items:
        raise HTTPException(status_code=400, detail="items array is required")

    result = gst_rules.compute_line_item_tax(supplier, recipient, items)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/validate-hsn")
async def validate_hsn(data: dict):
    """Validate HSN/SAC code format"""
    code = data.get("code", "")
    return gst_rules.validate_hsn_sac(code)


@router.get("/rate-slabs")
async def get_rate_slabs():
    """Get standard GST rate slabs"""
    return {
        "slabs": gst_rules.GST_RATE_SLABS,
        "common_rates": [
            {"rate": 0, "description": "Essential goods (fresh food, healthcare)"},
            {"rate": 5, "description": "Basic necessities, economy transport"},
            {"rate": 12, "description": "Standard goods, processed food"},
            {"rate": 18, "description": "Most goods and services (default)"},
            {"rate": 28, "description": "Luxury goods, sin goods, automobiles"},
        ]
    }
