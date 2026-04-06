# GST Statutory Returns - State-aware GSTR-1, GSTR-3B, E-Invoice
# Uses gst_rules engine for proper IGST/CGST+SGST/UTGST determination

from fastapi import APIRouter, HTTPException, Response
from datetime import datetime, timezone
from typing import Optional
import uuid, csv, json, hashlib
from io import StringIO
import gst_rules

router = APIRouter(prefix="/statutory", tags=["statutory"])
db = None

def set_db(database):
    global db
    db = database


async def _get_company_info():
    """Get company settings for GSTIN, state, legal name"""
    settings = await db.company_settings.find_one({}, {"_id": 0})
    return {
        "gstin": (settings or {}).get("gstin", ""),
        "legal_name": (settings or {}).get("legal_name", "PolyMerx Specialty Chemicals Pvt. Ltd."),
        "state": (settings or {}).get("state", "Maharashtra"),
        "state_code": (settings or {}).get("gst_state_code", "27"),
    }


# ═══════════════════════════════════════════════════════
# GSTR-1: Outward Supplies (State-Aware)
# ═══════════════════════════════════════════════════════
@router.get("/gstr1")
async def get_gstr1(month: Optional[str] = None, year: Optional[str] = None):
    """Generate GSTR-1 from Sales Invoices with proper state-based tax split"""
    company = await _get_company_info()
    invoices = await db.selling_invoices.find({}, {"_id": 0}).sort("posting_date", -1).to_list(10000)

    b2b_invoices = []
    b2c_large = []
    b2c_small = []
    hsn_summary = {}
    doc_summary = {"invoices_issued": 0, "credit_notes": 0, "debit_notes": 0}

    totals = {"taxable": 0, "igst": 0, "cgst": 0, "sgst": 0, "utgst": 0, "cess": 0}

    for inv in invoices:
        subtotal = inv.get("subtotal", 0)
        tb = inv.get("tax_breakdown", {})
        customer_gstin = inv.get("customer_gstin", "")
        customer_state = inv.get("customer_state", "")
        supply_type = tb.get("supply_type", inv.get("supply_type", ""))

        # If no tax_breakdown, compute from gst_rules
        if not tb or not supply_type:
            gst_amt = inv.get("gst_amount", 0)
            if customer_state and customer_state != company["state"]:
                supply_type = "IGST"
                tb = {"igst": gst_amt, "cgst": 0, "sgst": 0, "utgst": 0}
            else:
                supply_type = "CGST + SGST"
                tb = {"igst": 0, "cgst": round(gst_amt / 2, 2), "sgst": round(gst_amt - round(gst_amt / 2, 2), 2), "utgst": 0}

        igst = tb.get("igst", 0)
        cgst = tb.get("cgst", 0)
        sgst = tb.get("sgst", 0)
        utgst = tb.get("utgst", 0)
        total_tax = igst + cgst + sgst + utgst

        # Resolve place of supply
        recipient_code = gst_rules.resolve_state_code(customer_state) if customer_state else company["state_code"]
        recipient_info = gst_rules.STATES.get(recipient_code or company["state_code"], {})
        place_of_supply = f"{recipient_code or company['state_code']}-{recipient_info.get('name', '')}"

        inv_entry = {
            "gstin_of_recipient": customer_gstin,
            "receiver_name": inv.get("customer", ""),
            "invoice_number": inv.get("invoice_number", ""),
            "invoice_date": inv.get("posting_date", ""),
            "invoice_value": inv.get("grand_total", 0),
            "place_of_supply": place_of_supply,
            "supply_type": supply_type,
            "reverse_charge": "N",
            "invoice_type": "Regular",
            "rate": inv.get("gst_rate", 18),
            "taxable_value": subtotal,
            "igst": igst,
            "cgst": cgst,
            "sgst": sgst,
            "utgst": utgst,
            "cess": 0,
        }

        # Classify: B2B (has GSTIN), B2C Large (inter-state > 2.5L), B2C Small
        if customer_gstin and len(customer_gstin) == 15:
            b2b_invoices.append(inv_entry)
        elif "IGST" in supply_type and subtotal > 250000:
            b2c_large.append(inv_entry)
        else:
            b2c_small.append(inv_entry)

        doc_summary["invoices_issued"] += 1

        totals["taxable"] += subtotal
        totals["igst"] += igst
        totals["cgst"] += cgst
        totals["sgst"] += sgst
        totals["utgst"] += utgst

        # HSN summary
        for item in inv.get("items", []):
            hsn = item.get("hsn_sac", item.get("hsn", ""))
            if hsn:
                if hsn not in hsn_summary:
                    hsn_summary[hsn] = {"hsn_sac": hsn, "description": item.get("item_name", ""), "uqc": item.get("uom", "KG"), "total_qty": 0, "taxable_value": 0, "igst": 0, "cgst": 0, "sgst": 0}
                hsn_summary[hsn]["total_qty"] += item.get("qty", 0)
                item_val = item.get("amount", item.get("qty", 0) * item.get("rate", 0))
                hsn_summary[hsn]["taxable_value"] += item_val

    return {
        "report_type": "GSTR-1",
        "return_period": month or datetime.now().strftime("%m-%Y"),
        "gstin": company["gstin"],
        "legal_name": company["legal_name"],
        "state": company["state"],
        "sections": {
            "b2b": {"label": "4A, 4B, 6B, 6C - B2B Invoices", "invoices": b2b_invoices, "count": len(b2b_invoices)},
            "b2c_large": {"label": "5A, 5B - B2C (Large) Invoices", "invoices": b2c_large, "count": len(b2c_large)},
            "b2c_small": {"label": "7 - B2C (Small) Invoices", "invoices": b2c_small, "count": len(b2c_small)},
            "hsn": {"label": "12 - HSN-wise Summary", "items": list(hsn_summary.values()), "count": len(hsn_summary)},
            "docs": {"label": "13 - Document Summary", **doc_summary},
        },
        "summary": {
            "total_invoices": len(invoices),
            "b2b_count": len(b2b_invoices),
            "b2c_large_count": len(b2c_large),
            "b2c_small_count": len(b2c_small),
            "total_taxable_value": round(totals["taxable"], 2),
            "total_igst": round(totals["igst"], 2),
            "total_cgst": round(totals["cgst"], 2),
            "total_sgst": round(totals["sgst"], 2),
            "total_utgst": round(totals["utgst"], 2),
            "total_cess": round(totals["cess"], 2),
            "total_tax": round(totals["igst"] + totals["cgst"] + totals["sgst"] + totals["utgst"], 2),
        }
    }


# ═══════════════════════════════════════════════════════
# GSTR-3B: Monthly Summary Return (State-Aware)
# ═══════════════════════════════════════════════════════
@router.get("/gstr3b")
async def get_gstr3b(month: Optional[str] = None, year: Optional[str] = None):
    """Generate GSTR-3B from actual invoice data with proper state-based ITC"""
    company = await _get_company_info()

    # Section 3.1 - Outward supplies from sales invoices
    sales_invoices = await db.selling_invoices.find({}, {"_id": 0}).to_list(10000)
    outward = {"taxable": 0, "igst": 0, "cgst": 0, "sgst": 0, "utgst": 0, "cess": 0}
    inter_state_unreg = {"taxable": 0, "igst": 0}

    for inv in sales_invoices:
        subtotal = inv.get("subtotal", 0)
        tb = inv.get("tax_breakdown", {})
        outward["taxable"] += subtotal
        outward["igst"] += tb.get("igst", 0)
        outward["cgst"] += tb.get("cgst", 0)
        outward["sgst"] += tb.get("sgst", 0)
        outward["utgst"] += tb.get("utgst", 0)
        # Inter-state to unregistered
        if "IGST" in tb.get("supply_type", "") and not inv.get("customer_gstin"):
            inter_state_unreg["taxable"] += subtotal
            inter_state_unreg["igst"] += tb.get("igst", 0)

    # Section 4 - ITC from purchase invoices
    purchase_invoices = await db.purchase_invoices.find({}, {"_id": 0}).to_list(10000)
    itc = {"igst": 0, "cgst": 0, "sgst": 0, "utgst": 0, "cess": 0}

    for inv in purchase_invoices:
        tb = inv.get("tax_breakdown", {})
        if tb:
            itc["igst"] += tb.get("igst", 0)
            itc["cgst"] += tb.get("cgst", 0)
            itc["sgst"] += tb.get("sgst", 0)
            itc["utgst"] += tb.get("utgst", 0)
        else:
            gst_amt = inv.get("gst_amount", 0)
            itc["cgst"] += round(gst_amt / 2, 2)
            itc["sgst"] += round(gst_amt - round(gst_amt / 2, 2), 2)

    # Also check CoA balances for legacy data
    accounts = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(1000)
    balances = {a["ledger_name"]: a.get("current_balance", 0) for a in accounts}

    # Add legacy GST balances if no invoice-level data
    if outward["igst"] == 0 and outward["cgst"] == 0:
        gst_output = abs(balances.get("GST Output", 0))
        outward["cgst"] = round(gst_output / 2, 2)
        outward["sgst"] = round(gst_output - round(gst_output / 2, 2), 2)
        if gst_output > 0:
            outward["taxable"] = round(gst_output / 0.18, 2)

    if itc["igst"] == 0 and itc["cgst"] == 0:
        gst_input = balances.get("GST Input", 0)
        itc["cgst"] = round(gst_input / 2, 2)
        itc["sgst"] = round(gst_input - round(gst_input / 2, 2), 2)

    # Section 5 - Exempt / nil / non-GST
    exempt_inward = {"inter_state": 0, "intra_state": 0}

    # Section 6.1 - Net tax payable
    net_igst = round(outward["igst"] - itc["igst"], 2)
    net_cgst = round(outward["cgst"] - itc["cgst"], 2)
    net_sgst = round(outward["sgst"] - itc["sgst"], 2)
    net_utgst = round(outward["utgst"] - itc["utgst"], 2)
    net_total = round(net_igst + net_cgst + net_sgst + net_utgst, 2)

    # Round all
    for d in [outward, itc]:
        for k in d:
            d[k] = round(d[k], 2)

    return {
        "report_type": "GSTR-3B",
        "return_period": month or datetime.now().strftime("%m-%Y"),
        "gstin": company["gstin"],
        "legal_name": company["legal_name"],
        "state": company["state"],
        "sections": {
            "3_1": {
                "label": "3.1 - Details of Outward Supplies and inward supplies liable to reverse charge",
                "outward_taxable_supplies": {
                    "total_taxable_value": outward["taxable"],
                    "igst": outward["igst"], "cgst": outward["cgst"],
                    "sgst": outward["sgst"], "utgst": outward["utgst"], "cess": 0,
                },
                "zero_rated": {"igst": 0, "cess": 0},
                "nil_rated_exempt": 0,
                "reverse_charge_inward": {"igst": 0, "cgst": 0, "sgst": 0, "cess": 0},
            },
            "3_2": {
                "label": "3.2 - Inter-State supplies to unregistered persons, composition taxpayers and UIN holders",
                "to_unregistered": inter_state_unreg,
            },
            "4": {
                "label": "4 - Eligible ITC",
                "itc_available": {
                    "igst": itc["igst"], "cgst": itc["cgst"],
                    "sgst": itc["sgst"], "utgst": itc["utgst"], "cess": 0,
                },
                "itc_reversed": {"igst": 0, "cgst": 0, "sgst": 0, "cess": 0},
                "net_itc": {
                    "igst": itc["igst"], "cgst": itc["cgst"],
                    "sgst": itc["sgst"], "utgst": itc["utgst"],
                },
            },
            "5": {
                "label": "5 - Values of exempt, nil-rated and non-GST inward supplies",
                "exempt": exempt_inward,
            },
            "6_1": {
                "label": "6.1 - Payment of Tax",
                "tax_payable": {
                    "igst": max(outward["igst"], 0), "cgst": max(outward["cgst"], 0),
                    "sgst": max(outward["sgst"], 0), "utgst": max(outward["utgst"], 0), "cess": 0,
                    "total": round(outward["igst"] + outward["cgst"] + outward["sgst"] + outward["utgst"], 2),
                },
                "itc_utilized": {
                    "igst": min(itc["igst"], outward["igst"]),
                    "cgst": min(itc["cgst"], outward["cgst"]),
                    "sgst": min(itc["sgst"], outward["sgst"]),
                    "utgst": min(itc["utgst"], outward["utgst"]),
                },
                "cash_payable": {
                    "igst": max(net_igst, 0), "cgst": max(net_cgst, 0),
                    "sgst": max(net_sgst, 0), "utgst": max(net_utgst, 0),
                    "total": max(net_total, 0),
                }
            }
        },
        "summary": {
            "total_output_tax": round(outward["igst"] + outward["cgst"] + outward["sgst"] + outward["utgst"], 2),
            "total_input_credit": round(itc["igst"] + itc["cgst"] + itc["sgst"] + itc["utgst"], 2),
            "net_payable": max(net_total, 0),
            "net_refundable": abs(min(net_total, 0)),
        }
    }


# ═══════════════════════════════════════════════════════
# E-INVOICE: IRN Generation (JSON for GST Portal)
# ═══════════════════════════════════════════════════════
@router.get("/e-invoices")
async def get_e_invoices():
    """List invoices eligible for e-invoicing (B2B > threshold)"""
    company = await _get_company_info()
    invoices = await db.selling_invoices.find({}, {"_id": 0}).sort("posting_date", -1).to_list(10000)

    e_invoices = []
    for inv in invoices:
        gstin = inv.get("customer_gstin", "")
        if not gstin or len(gstin) != 15:
            continue

        tb = inv.get("tax_breakdown", {})
        irn_hash = hashlib.sha256(f"{company['gstin']}|{inv.get('invoice_number','')}|{inv.get('posting_date','')}".encode()).hexdigest()[:32]

        e_inv = {
            "invoice_number": inv.get("invoice_number", ""),
            "invoice_date": inv.get("posting_date", ""),
            "customer": inv.get("customer", ""),
            "customer_gstin": gstin,
            "supply_type": tb.get("supply_type", inv.get("supply_type", "")),
            "subtotal": inv.get("subtotal", 0),
            "igst": tb.get("igst", 0),
            "cgst": tb.get("cgst", 0),
            "sgst": tb.get("sgst", 0),
            "grand_total": inv.get("grand_total", 0),
            "irn": irn_hash.upper(),
            "status": "Generated",
            "items": inv.get("items", []),
        }
        e_invoices.append(e_inv)

    return {
        "company": company,
        "e_invoices": e_invoices,
        "total": len(e_invoices),
    }


@router.get("/e-invoice/{invoice_number}/json")
async def get_e_invoice_json(invoice_number: str):
    """Generate IRN-ready JSON for a specific invoice"""
    company = await _get_company_info()
    inv = await db.selling_invoices.find_one({"invoice_number": invoice_number}, {"_id": 0})
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    tb = inv.get("tax_breakdown", {})
    supply_type = tb.get("supply_type", "")

    # Build e-invoice JSON (NIC format)
    e_json = {
        "Version": "1.1",
        "TranDtls": {
            "TaxSch": "GST",
            "SupTyp": "B2B",
            "RegRev": "N",
            "IgstOnIntra": "N",
        },
        "DocDtls": {
            "Typ": "INV",
            "No": inv.get("invoice_number", ""),
            "Dt": inv.get("posting_date", ""),
        },
        "SellerDtls": {
            "Gstin": company["gstin"],
            "LglNm": company["legal_name"],
            "Addr1": "",
            "Loc": company["state"],
            "Pin": 0,
            "Stcd": company["state_code"],
        },
        "BuyerDtls": {
            "Gstin": inv.get("customer_gstin", ""),
            "LglNm": inv.get("customer", ""),
            "Pos": gst_rules.resolve_state_code(inv.get("customer_state", "")) or company["state_code"],
            "Addr1": "",
            "Loc": inv.get("customer_state", ""),
            "Pin": 0,
            "Stcd": gst_rules.resolve_state_code(inv.get("customer_state", "")) or company["state_code"],
        },
        "ItemList": [],
        "ValDtls": {
            "AssVal": inv.get("subtotal", 0),
            "IgstVal": tb.get("igst", 0),
            "CgstVal": tb.get("cgst", 0),
            "SgstVal": tb.get("sgst", 0),
            "TotInvVal": inv.get("grand_total", 0),
        },
    }

    for idx, item in enumerate(inv.get("items", []), 1):
        item_val = item.get("amount", item.get("qty", 0) * item.get("rate", 0))
        e_json["ItemList"].append({
            "SlNo": str(idx),
            "PrdDesc": item.get("item_name", ""),
            "IsServc": "N",
            "HsnCd": item.get("hsn_sac", item.get("hsn", "")),
            "Qty": item.get("qty", 0),
            "Unit": item.get("uom", "KGS"),
            "UnitPrice": item.get("rate", 0),
            "TotAmt": item_val,
            "AssAmt": item_val,
            "GstRt": item.get("gst_rate", 18),
            "IgstAmt": round(item_val * item.get("gst_rate", 18) / 100, 2) if "IGST" in supply_type else 0,
            "CgstAmt": round(item_val * item.get("gst_rate", 18) / 200, 2) if "IGST" not in supply_type else 0,
            "SgstAmt": round(item_val * item.get("gst_rate", 18) / 200, 2) if "IGST" not in supply_type else 0,
            "TotItemVal": round(item_val * (1 + item.get("gst_rate", 18) / 100), 2),
        })

    return e_json


# ═══════════════════════════════════════════════════════
# TDS RETURN: Form 26Q
# ═══════════════════════════════════════════════════════
@router.get("/tds-return")
async def get_tds_return(quarter: Optional[str] = None):
    """Generate TDS return summary from transactions with TDS"""
    company = await _get_company_info()

    tds_entries = await db.journal_entries.find(
        {"$or": [
            {"description": {"$regex": "TDS", "$options": "i"}},
            {"account": {"$regex": "TDS", "$options": "i"}},
        ]},
        {"_id": 0}
    ).to_list(10000)

    manual_entries = await db.manual_journal_entries.find(
        {"narration": {"$regex": "TDS", "$options": "i"}},
        {"_id": 0}
    ).to_list(10000)

    deductees = []
    total_tds = 0

    for entry in manual_entries:
        for je in entry.get("journal_entries", []):
            if "TDS" in je.get("description", "").upper() or "TDS" in je.get("account", "").upper():
                tds_amt = je.get("credit", 0)
                if tds_amt > 0:
                    deductees.append({
                        "deductee_name": entry.get("narration", "")[:50],
                        "pan": "",
                        "section": "194C",
                        "date_of_payment": entry.get("posting_date", ""),
                        "amount_paid": round(tds_amt / 0.10, 2),
                        "tds_amount": tds_amt,
                        "tds_rate": 10,
                        "challan_no": "",
                        "entry_id": entry.get("id", ""),
                    })
                    total_tds += tds_amt

    return {
        "report_type": "TDS Return (Form 26Q)",
        "quarter": quarter or "Q4",
        "financial_year": "2025-26",
        "tan": (await db.company_settings.find_one({}, {"_id": 0}) or {}).get("tan", ""),
        "deductor_name": company["legal_name"],
        "deductees": deductees,
        "summary": {
            "total_deductees": len(deductees),
            "total_amount_paid": round(sum(d["amount_paid"] for d in deductees), 2),
            "total_tds_deducted": round(total_tds, 2),
            "total_tds_deposited": 0,
            "tds_pending_deposit": round(total_tds, 2),
        }
    }


# ═══════════════════════════════════════════════════════
# EXPORT ENDPOINTS
# ═══════════════════════════════════════════════════════
@router.get("/gstr1/export")
async def export_gstr1():
    data = await get_gstr1()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["GSTIN", "Receiver Name", "Invoice No", "Invoice Date", "Invoice Value",
                     "Place of Supply", "Supply Type", "Rate", "Taxable Value", "IGST", "CGST", "SGST", "UTGST", "Cess"])
    for section_key in ["b2b", "b2c_large", "b2c_small"]:
        for inv in data["sections"].get(section_key, {}).get("invoices", []):
            writer.writerow([
                inv.get("gstin_of_recipient",""), inv["receiver_name"], inv["invoice_number"],
                inv["invoice_date"], inv["invoice_value"], inv["place_of_supply"], inv.get("supply_type",""),
                inv["rate"], inv["taxable_value"], inv["igst"], inv["cgst"], inv["sgst"], inv.get("utgst",0), inv["cess"]
            ])
    return Response(content=output.getvalue(), media_type="text/csv",
                   headers={"Content-Disposition": "attachment; filename=GSTR1.csv"})

@router.get("/gstr3b/export")
async def export_gstr3b():
    data = await get_gstr3b()
    return Response(content=json.dumps(data, indent=2), media_type="application/json",
                   headers={"Content-Disposition": "attachment; filename=GSTR3B.json"})

@router.get("/tds-return/export")
async def export_tds_return():
    data = await get_tds_return()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Deductee Name", "PAN", "Section", "Date", "Amount Paid", "TDS Amount", "TDS Rate %", "Challan No"])
    for d in data["deductees"]:
        writer.writerow([d["deductee_name"], d["pan"], d["section"], d["date_of_payment"],
                        d["amount_paid"], d["tds_amount"], d["tds_rate"], d["challan_no"]])
    return Response(content=output.getvalue(), media_type="text/csv",
                   headers={"Content-Disposition": "attachment; filename=TDS_Return_26Q.csv"})
