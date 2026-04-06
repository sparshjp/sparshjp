# GST Rules Engine - India Localization
# Implements CGST Act 2017, SGST Act 2017, IGST Act 2017, UTGST Act 2017
# Sections 7 & 8 of IGST Act determine inter-state vs intra-state supply

from typing import Optional

# ---------------------------------------------------------------------------
# All Indian States and Union Territories with GST State Codes
# Source: GSTN / CBIC Official Code List (updated post-2019 reorganization)
# ---------------------------------------------------------------------------

STATES = {
    "01": {"name": "Jammu & Kashmir", "alpha": "JK", "is_ut": False, "utgst": False},
    "02": {"name": "Himachal Pradesh", "alpha": "HP", "is_ut": False, "utgst": False},
    "03": {"name": "Punjab", "alpha": "PB", "is_ut": False, "utgst": False},
    "04": {"name": "Chandigarh", "alpha": "CH", "is_ut": True, "utgst": True},
    "05": {"name": "Uttarakhand", "alpha": "UK", "is_ut": False, "utgst": False},
    "06": {"name": "Haryana", "alpha": "HR", "is_ut": False, "utgst": False},
    "07": {"name": "Delhi", "alpha": "DL", "is_ut": True, "utgst": False},
    "08": {"name": "Rajasthan", "alpha": "RJ", "is_ut": False, "utgst": False},
    "09": {"name": "Uttar Pradesh", "alpha": "UP", "is_ut": False, "utgst": False},
    "10": {"name": "Bihar", "alpha": "BH", "is_ut": False, "utgst": False},
    "11": {"name": "Sikkim", "alpha": "SK", "is_ut": False, "utgst": False},
    "12": {"name": "Arunachal Pradesh", "alpha": "AR", "is_ut": False, "utgst": False},
    "13": {"name": "Nagaland", "alpha": "NL", "is_ut": False, "utgst": False},
    "14": {"name": "Manipur", "alpha": "MN", "is_ut": False, "utgst": False},
    "15": {"name": "Mizoram", "alpha": "MI", "is_ut": False, "utgst": False},
    "16": {"name": "Tripura", "alpha": "TR", "is_ut": False, "utgst": False},
    "17": {"name": "Meghalaya", "alpha": "ME", "is_ut": False, "utgst": False},
    "18": {"name": "Assam", "alpha": "AS", "is_ut": False, "utgst": False},
    "19": {"name": "West Bengal", "alpha": "WB", "is_ut": False, "utgst": False},
    "20": {"name": "Jharkhand", "alpha": "JH", "is_ut": False, "utgst": False},
    "21": {"name": "Odisha", "alpha": "OR", "is_ut": False, "utgst": False},
    "22": {"name": "Chhattisgarh", "alpha": "CT", "is_ut": False, "utgst": False},
    "23": {"name": "Madhya Pradesh", "alpha": "MP", "is_ut": False, "utgst": False},
    "24": {"name": "Gujarat", "alpha": "GJ", "is_ut": False, "utgst": False},
    "26": {"name": "Dadra & Nagar Haveli and Daman & Diu", "alpha": "DN", "is_ut": True, "utgst": True},
    "27": {"name": "Maharashtra", "alpha": "MH", "is_ut": False, "utgst": False},
    "29": {"name": "Karnataka", "alpha": "KA", "is_ut": False, "utgst": False},
    "30": {"name": "Goa", "alpha": "GA", "is_ut": False, "utgst": False},
    "31": {"name": "Lakshadweep", "alpha": "LD", "is_ut": True, "utgst": True},
    "32": {"name": "Kerala", "alpha": "KL", "is_ut": False, "utgst": False},
    "33": {"name": "Tamil Nadu", "alpha": "TN", "is_ut": False, "utgst": False},
    "34": {"name": "Puducherry", "alpha": "PY", "is_ut": True, "utgst": False},
    "35": {"name": "Andaman & Nicobar Islands", "alpha": "AN", "is_ut": True, "utgst": True},
    "36": {"name": "Telangana", "alpha": "TL", "is_ut": False, "utgst": False},
    "37": {"name": "Andhra Pradesh", "alpha": "AD", "is_ut": False, "utgst": False},
    "38": {"name": "Ladakh", "alpha": "LA", "is_ut": True, "utgst": True},
}

# Reverse lookup: state name -> code
STATE_NAME_TO_CODE = {}
for code, info in STATES.items():
    STATE_NAME_TO_CODE[info["name"].lower()] = code
    STATE_NAME_TO_CODE[info["alpha"].lower()] = code

# Common aliases
STATE_NAME_TO_CODE.update({
    "j&k": "01", "jammu and kashmir": "01", "jammu": "01",
    "hp": "02", "himachal": "02",
    "pb": "03",
    "ch": "04",
    "uk": "05", "uttaranchal": "05",
    "hr": "06",
    "dl": "07", "new delhi": "07",
    "rj": "08",
    "up": "09",
    "bh": "10",
    "sk": "11",
    "ar": "12",
    "nl": "13",
    "mn": "14",
    "mi": "15",
    "tr": "16",
    "me": "17",
    "as": "18",
    "wb": "19",
    "jh": "20",
    "or": "21", "orissa": "21",
    "ct": "22", "chattisgarh": "22",
    "mp": "23",
    "gj": "24",
    "dn": "26", "dadra": "26", "daman": "26", "daman and diu": "26", "daman & diu": "26",
    "dadra and nagar haveli": "26", "dadra & nagar haveli": "26",
    "mh": "27",
    "ka": "29",
    "ga": "30",
    "ld": "31",
    "kl": "32",
    "tn": "33",
    "py": "34", "pondicherry": "34",
    "an": "35", "andaman": "35", "andaman and nicobar": "35",
    "tl": "36", "ts": "36",
    "ad": "37", "ap": "37",
    "la": "38",
})

# Standard GST rate slabs
GST_RATE_SLABS = [0, 0.25, 3, 5, 12, 18, 28]


def resolve_state_code(state_input: str) -> Optional[str]:
    """
    Resolve a state name, alpha code, or GST code to the canonical 2-digit GST state code.
    Returns None if unresolvable.
    """
    if not state_input:
        return None
    s = state_input.strip()

    # Direct code match
    if s in STATES:
        return s
    # Zero-padded
    if len(s) == 1 and s.isdigit():
        padded = s.zfill(2)
        if padded in STATES:
            return padded

    # Name/alias lookup
    lower = s.lower()
    if lower in STATE_NAME_TO_CODE:
        return STATE_NAME_TO_CODE[lower]

    # Fuzzy: try partial match
    for name, code in STATE_NAME_TO_CODE.items():
        if lower in name or name in lower:
            return code

    return None


def extract_state_from_gstin(gstin: str) -> Optional[str]:
    """Extract state code from first 2 digits of GSTIN"""
    if gstin and len(gstin) >= 2:
        code = gstin[:2]
        if code in STATES:
            return code
    return None


def get_state_info(state_code: str) -> Optional[dict]:
    """Get full state info by code"""
    info = STATES.get(state_code)
    if info:
        return {"code": state_code, **info}
    return None


def compute_tax(
    supplier_state: str,
    recipient_state: str,
    gst_rate: float,
    taxable_value: float,
) -> dict:
    """
    Compute GST tax components based on:
    - Supplier state (company's state or vendor's state)
    - Recipient state (buyer's/customer's state)
    - GST rate (e.g. 18 for 18%)
    - Taxable value (base amount before tax)

    Returns dict with tax_type, components, total_tax, grand_total
    
    Rules (IGST Act 2017):
    - Section 7: Inter-state supply → IGST
    - Section 8: Intra-state supply → CGST + SGST (or CGST + UTGST for certain UTs)
    """
    supplier_code = resolve_state_code(supplier_state)
    recipient_code = resolve_state_code(recipient_state)

    if not supplier_code:
        return {"error": f"Cannot resolve supplier state: {supplier_state}"}
    if not recipient_code:
        return {"error": f"Cannot resolve recipient state: {recipient_state}"}

    rate_fraction = gst_rate / 100
    total_tax = round(taxable_value * rate_fraction, 2)

    supplier_info = STATES[supplier_code]
    recipient_info = STATES[recipient_code]

    result = {
        "supplier_state": {"code": supplier_code, "name": supplier_info["name"]},
        "recipient_state": {"code": recipient_code, "name": recipient_info["name"]},
        "gst_rate": gst_rate,
        "taxable_value": taxable_value,
    }

    if supplier_code == recipient_code:
        # INTRA-STATE: CGST + SGST or CGST + UTGST
        half_tax = round(total_tax / 2, 2)
        # Adjust rounding: ensure halves sum to total
        other_half = round(total_tax - half_tax, 2)

        if recipient_info.get("utgst"):
            # UTs without legislature: CGST + UTGST
            result["supply_type"] = "intra_state"
            result["tax_type"] = "CGST + UTGST"
            result["components"] = {
                "cgst_rate": round(gst_rate / 2, 2),
                "cgst_amount": half_tax,
                "utgst_rate": round(gst_rate / 2, 2),
                "utgst_amount": other_half,
                "sgst_rate": 0,
                "sgst_amount": 0,
                "igst_rate": 0,
                "igst_amount": 0,
            }
        else:
            # States and UTs with legislature (Delhi, Puducherry, J&K): CGST + SGST
            result["supply_type"] = "intra_state"
            result["tax_type"] = "CGST + SGST"
            result["components"] = {
                "cgst_rate": round(gst_rate / 2, 2),
                "cgst_amount": half_tax,
                "sgst_rate": round(gst_rate / 2, 2),
                "sgst_amount": other_half,
                "utgst_rate": 0,
                "utgst_amount": 0,
                "igst_rate": 0,
                "igst_amount": 0,
            }
    else:
        # INTER-STATE: IGST
        result["supply_type"] = "inter_state"
        result["tax_type"] = "IGST"
        result["components"] = {
            "igst_rate": gst_rate,
            "igst_amount": total_tax,
            "cgst_rate": 0,
            "cgst_amount": 0,
            "sgst_rate": 0,
            "sgst_amount": 0,
            "utgst_rate": 0,
            "utgst_amount": 0,
        }

    result["total_tax"] = total_tax
    result["grand_total"] = round(taxable_value + total_tax, 2)
    return result


def compute_line_item_tax(
    supplier_state: str,
    recipient_state: str,
    items: list,
) -> dict:
    """
    Compute tax for multiple line items, each with its own HSN, rate, and value.
    items: [{hsn_sac, gst_rate, taxable_value, qty, ...}, ...]
    Returns aggregated tax breakdown.
    """
    line_results = []
    totals = {
        "taxable_value": 0,
        "cgst": 0, "sgst": 0, "igst": 0, "utgst": 0,
        "total_tax": 0, "grand_total": 0,
    }

    for item in items:
        gst_rate = item.get("gst_rate", 18)
        taxable_value = item.get("taxable_value", 0)

        tax = compute_tax(supplier_state, recipient_state, gst_rate, taxable_value)
        if "error" in tax:
            return tax

        comp = tax["components"]
        line_results.append({
            "hsn_sac": item.get("hsn_sac", ""),
            "item": item.get("item", item.get("item_code", "")),
            "gst_rate": gst_rate,
            "taxable_value": taxable_value,
            "tax_type": tax["tax_type"],
            "cgst": comp["cgst_amount"],
            "sgst": comp["sgst_amount"],
            "igst": comp["igst_amount"],
            "utgst": comp["utgst_amount"],
            "total_tax": tax["total_tax"],
            "line_total": tax["grand_total"],
        })

        totals["taxable_value"] += taxable_value
        totals["cgst"] += comp["cgst_amount"]
        totals["sgst"] += comp["sgst_amount"]
        totals["igst"] += comp["igst_amount"]
        totals["utgst"] += comp["utgst_amount"]
        totals["total_tax"] += tax["total_tax"]
        totals["grand_total"] += tax["grand_total"]

    # Round totals
    for k in totals:
        totals[k] = round(totals[k], 2)

    return {
        "supply_type": line_results[0]["tax_type"] if line_results else "",
        "supplier_state": supplier_state,
        "recipient_state": recipient_state,
        "line_items": line_results,
        "totals": totals,
    }


def validate_hsn_sac(code: str) -> dict:
    """
    Validate HSN/SAC code format.
    HSN: 2, 4, 6, or 8 digit numeric code for goods
    SAC: 6 digit numeric code starting with 99 for services
    """
    if not code:
        return {"valid": False, "error": "HSN/SAC code is required"}

    clean = code.strip()
    if not clean.isdigit():
        return {"valid": False, "error": "HSN/SAC must be numeric"}

    if clean.startswith("99"):
        # SAC code for services
        if len(clean) < 4 or len(clean) > 6:
            return {"valid": False, "error": "SAC code must be 4-6 digits starting with 99"}
        return {"valid": True, "type": "SAC", "code": clean, "category": "Services"}
    else:
        # HSN code for goods
        if len(clean) < 2 or len(clean) > 8:
            return {"valid": False, "error": "HSN code must be 2-8 digits"}
        return {"valid": True, "type": "HSN", "code": clean, "category": "Goods"}


def get_all_states() -> list:
    """Return all states/UTs sorted by code"""
    result = []
    for code in sorted(STATES.keys(), key=lambda x: int(x)):
        info = STATES[code]
        result.append({
            "code": code,
            "name": info["name"],
            "alpha": info["alpha"],
            "is_ut": info["is_ut"],
            "utgst": info["utgst"],
            "tax_regime": "CGST + UTGST" if info["utgst"] else "CGST + SGST",
        })
    return result
