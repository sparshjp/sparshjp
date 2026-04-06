# Kairos Accounting - GST & TDS Statutory Reports Module
# Generates GSTR-1, GSTR-3B, TDS Returns for filing

from fastapi import APIRouter, HTTPException, Response
from datetime import datetime, timezone
from typing import Optional
import uuid
import csv
import json
from io import StringIO

router = APIRouter(prefix="/statutory", tags=["statutory"])
db = None

def set_db(database):
    global db
    db = database


# ═══════════════════════════════════════════════════════
# GSTR-1: Outward Supplies
# ═══════════════════════════════════════════════════════
@router.get("/gstr1")
async def get_gstr1(month: Optional[str] = None, year: Optional[str] = None):
    """Generate GSTR-1 from Sales Invoices"""
    invoices = await db.selling_invoices.find({}, {"_id": 0}).sort("posting_date", -1).to_list(10000)

    b2b_invoices = []
    total_taxable = 0
    total_igst = 0
    total_cgst = 0
    total_sgst = 0
    total_cess = 0

    for inv in invoices:
        gst_amt = inv.get("gst_amount", 0)
        subtotal = inv.get("subtotal", 0)
        # Assume intrastate (CGST+SGST split)
        cgst = round(gst_amt / 2, 2)
        sgst = round(gst_amt / 2, 2)

        b2b_invoices.append({
            "gstin_of_recipient": inv.get("customer_gstin", ""),
            "receiver_name": inv.get("customer", ""),
            "invoice_number": inv.get("invoice_number", ""),
            "invoice_date": inv.get("posting_date", ""),
            "invoice_value": inv.get("grand_total", 0),
            "place_of_supply": "24-Gujarat",
            "reverse_charge": "N",
            "invoice_type": "Regular",
            "rate": inv.get("gst_rate", 18),
            "taxable_value": subtotal,
            "igst": 0,
            "cgst": cgst,
            "sgst": sgst,
            "cess": 0,
        })
        total_taxable += subtotal
        total_cgst += cgst
        total_sgst += sgst

    # Also check legacy transactions
    legacy_invoices = await db.transactions.find(
        {"module": {"$in": ["sale", "o2c", "sales"]}},
        {"_id": 0}
    ).to_list(10000)

    for txn in legacy_invoices:
        for je in txn.get("journal_entries", []):
            if "GST" in je.get("account", "") and je.get("credit", 0) > 0:
                total_cgst += round(je["credit"] / 2, 2)
                total_sgst += round(je["credit"] / 2, 2)

    return {
        "report_type": "GSTR-1",
        "return_period": month or datetime.now().strftime("%m-%Y"),
        "gstin": "24AABCN1234A1Z5",
        "legal_name": "NanoChip Industries Pvt. Ltd.",
        "sections": {
            "b2b": {
                "label": "4A, 4B, 6B, 6C - B2B Invoices",
                "invoices": b2b_invoices,
                "count": len(b2b_invoices)
            }
        },
        "summary": {
            "total_invoices": len(b2b_invoices),
            "total_taxable_value": round(total_taxable, 2),
            "total_igst": round(total_igst, 2),
            "total_cgst": round(total_cgst, 2),
            "total_sgst": round(total_sgst, 2),
            "total_cess": round(total_cess, 2),
            "total_tax": round(total_igst + total_cgst + total_sgst + total_cess, 2),
        }
    }


# ═══════════════════════════════════════════════════════
# GSTR-3B: Monthly Summary Return
# ═══════════════════════════════════════════════════════
@router.get("/gstr3b")
async def get_gstr3b(month: Optional[str] = None, year: Optional[str] = None):
    """Generate GSTR-3B summary"""
    balances = {}
    accounts = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(1000)
    for a in accounts:
        balances[a["ledger_name"]] = a.get("current_balance", 0)

    gst_output = abs(balances.get("GST Output", 0))
    gst_payable_old = abs(balances.get("GST Payable", 0))
    gst_input = balances.get("GST Input", 0)

    # 3.1 - Outward supplies
    output_cgst = round(gst_output / 2, 2)
    output_sgst = round(gst_output / 2, 2)

    # 4 - Input Tax Credit
    input_cgst = round(gst_input / 2, 2)
    input_sgst = round(gst_input / 2, 2)

    # 6.1 - Net tax payable
    net_cgst = round(output_cgst - input_cgst, 2)
    net_sgst = round(output_sgst - input_sgst, 2)
    net_total = round(net_cgst + net_sgst, 2)

    return {
        "report_type": "GSTR-3B",
        "return_period": month or datetime.now().strftime("%m-%Y"),
        "gstin": "24AABCN1234A1Z5",
        "legal_name": "NanoChip Industries Pvt. Ltd.",
        "sections": {
            "3_1": {
                "label": "3.1 - Details of Outward Supplies",
                "outward_taxable_supplies": {
                    "total_taxable_value": round(gst_output / 0.18 if gst_output > 0 else 0, 2),
                    "igst": 0,
                    "cgst": output_cgst,
                    "sgst": output_sgst,
                    "cess": 0,
                }
            },
            "4": {
                "label": "4 - Eligible ITC",
                "itc_available": {
                    "igst": 0,
                    "cgst": input_cgst,
                    "sgst": input_sgst,
                    "cess": 0,
                }
            },
            "6_1": {
                "label": "6.1 - Payment of Tax",
                "tax_payable": {
                    "igst": 0,
                    "cgst": max(net_cgst, 0),
                    "sgst": max(net_sgst, 0),
                    "cess": 0,
                    "total": max(net_total, 0),
                },
                "itc_utilized": {
                    "igst": 0,
                    "cgst": min(input_cgst, output_cgst),
                    "sgst": min(input_sgst, output_sgst),
                },
                "cash_payable": {
                    "igst": 0,
                    "cgst": max(net_cgst, 0),
                    "sgst": max(net_sgst, 0),
                    "total": max(net_total, 0),
                }
            }
        },
        "summary": {
            "total_output_tax": round(gst_output, 2),
            "total_input_credit": round(gst_input, 2),
            "net_payable": max(net_total, 0),
            "net_refundable": abs(min(net_total, 0)),
        }
    }


# ═══════════════════════════════════════════════════════
# TDS RETURN: Form 26Q style
# ═══════════════════════════════════════════════════════
@router.get("/tds-return")
async def get_tds_return(quarter: Optional[str] = None):
    """Generate TDS return summary from transactions with TDS"""
    # Find journal entries with TDS
    tds_entries = await db.journal_entries.find(
        {"$or": [
            {"description": {"$regex": "TDS", "$options": "i"}},
            {"account": {"$regex": "TDS", "$options": "i"}},
        ]},
        {"_id": 0}
    ).to_list(10000)

    # Also check all manual journal entries for TDS narrations
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
                        "amount_paid": tds_amt / 0.10,
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
        "tan": "AHMA12345B",
        "deductor_name": "NanoChip Industries Pvt. Ltd.",
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
                     "Place of Supply", "Rate", "Taxable Value", "IGST", "CGST", "SGST", "Cess"])
    for inv in data["sections"]["b2b"]["invoices"]:
        writer.writerow([
            inv["gstin_of_recipient"], inv["receiver_name"], inv["invoice_number"],
            inv["invoice_date"], inv["invoice_value"], inv["place_of_supply"],
            inv["rate"], inv["taxable_value"], inv["igst"], inv["cgst"], inv["sgst"], inv["cess"]
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
