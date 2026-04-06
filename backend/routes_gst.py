# GST Rules API - State-wise tax computation, HSN/SAC validation & AI suggest
from fastapi import APIRouter, HTTPException
from typing import Optional
import gst_rules
import os, json, logging

router = APIRouter(prefix="/gst", tags=["gst"])
EMERGENT_KEY = None

def set_key(key):
    global EMERGENT_KEY
    EMERGENT_KEY = key


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


@router.post("/suggest-hsn")
async def suggest_hsn(data: dict):
    """
    AI-powered HSN/SAC code suggestion.
    Takes item description and returns suggested HSN/SAC code with GST rate.
    """
    item_description = data.get("description", "")
    item_name = data.get("item_name", "")
    query = item_description or item_name

    if not query:
        raise HTTPException(status_code=400, detail="item description or item_name is required")

    if not EMERGENT_KEY:
        raise HTTPException(status_code=500, detail="LLM key not configured")

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        system_prompt = """You are an Indian GST HSN/SAC code expert. Given an item description, suggest the most accurate HSN or SAC code.

Rules:
- HSN codes are for GOODS (2-8 digits). Common chapters: 28 (chemicals), 29 (organic chemicals), 39 (plastics), 72 (iron/steel), 84 (machinery), 85 (electrical)
- SAC codes are for SERVICES (start with 99). Common: 9954 (construction), 9971 (financial), 9983 (IT)
- Return the most specific code possible (4-8 digits for HSN, 4-6 for SAC)
- Include the correct GST rate slab (0, 5, 12, 18, or 28%)

Return ONLY a valid JSON object (no markdown, no explanation):
{"hsn_sac": "2907", "type": "HSN", "gst_rate": 18, "description": "Phenols; phenol-alcohols", "chapter": "29 - Organic chemicals", "confidence": "high"}

confidence must be "high", "medium", or "low".
"""

        llm = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"hsn-suggest-{query[:20]}",
            system_message=system_prompt,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        response = await llm.send_message(
            UserMessage(text=f"Suggest HSN/SAC code for: {query}")
        )

        text = response if isinstance(response, str) else str(response)
        text = text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        suggestion = json.loads(text)

        # Validate the suggestion
        validation = gst_rules.validate_hsn_sac(suggestion.get("hsn_sac", ""))
        suggestion["validation"] = validation

        return suggestion

    except json.JSONDecodeError:
        return {"hsn_sac": "", "error": "Could not parse AI response", "raw": text[:200]}
    except Exception as e:
        logging.error(f"HSN suggest error: {e}")
        raise HTTPException(status_code=500, detail=f"HSN suggestion failed: {str(e)}")
