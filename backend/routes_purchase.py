# Kairos Advisory - Purchase Module with Linked Document Flow
# PO → GRN (from PO) → Purchase Invoice (from GRN) → Vendor Payment (from Invoice)
# Each stage auto-flows from the previous. No orphan documents.

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional
import uuid
import math

router = APIRouter(prefix="/purchase", tags=["purchase"])
db = None

def set_db(database):
    global db
    db = database

async def auto_post_journal_entries(entries, narration, cost_center="General", ref_doc_type="", ref_doc_id=""):
    entry = {
        "id": str(uuid.uuid4()),
        "entry_type": "Auto Generated",
        "posting_date": datetime.now(timezone.utc).date().isoformat(),
        "cost_center": cost_center,
        "journal_entries": entries,
        "narration": narration,
        "ref_doc_type": ref_doc_type,
        "ref_doc_id": ref_doc_id,
        "voucher_type": "Journal Entry",
        "status": "Posted",
        "user_id": "system",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "posted_at": datetime.now(timezone.utc).isoformat()
    }
    await db.manual_journal_entries.insert_one(entry)
    for je in entries:
        journal_doc = {
            "id": str(uuid.uuid4()),
            "transaction_id": entry["id"],
            "account": je["account"],
            "debit": je.get("debit", 0),
            "credit": je.get("credit", 0),
            "description": je.get("description", ""),
            "posting_date": entry["posting_date"],
            "cost_center": cost_center,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.journal_entries.insert_one(journal_doc)
        net = je.get("debit", 0) - je.get("credit", 0)
        await db.chart_of_accounts.update_one(
            {"ledger_name": je["account"]},
            {"$inc": {"current_balance": net}},
            upsert=False
        )
    return entry["id"]


# ═══════════════════════════════════════════════════════
# PURCHASE ORDERS
# ═══════════════════════════════════════════════════════
@router.post("/orders")
async def create_purchase_order(data: dict):
    # Validate vendor exists in master data
    vendor_name = data.get("vendor", "")
    vendor_doc = await db.entities.find_one({"name": vendor_name, "entity_type": "vendor"}, {"_id": 0})
    if not vendor_doc:
        raise HTTPException(status_code=400, detail=f"Vendor '{vendor_name}' not found in master data. Create the vendor first in Master Data.")
    # Validate items exist in master data
    items = data.get("items", [])
    for it in items:
        item_code = it.get("item_code", "")
        item_doc = await db.items.find_one({"item_code": item_code}, {"_id": 0})
        if not item_doc:
            raise HTTPException(status_code=400, detail=f"Item '{item_code}' not found in master data. Create the item first in Master Data.")
    total = sum(i.get("amount", i.get("qty", 0) * i.get("rate", 0)) for i in items)
    gst_rate = data.get("gst_rate", 18)
    gst_amount = round(total * gst_rate / 100, 2)
    po = {
        "id": str(uuid.uuid4()),
        "po_number": data.get("po_number", f"PO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"),
        "vendor": data.get("vendor"),
        "vendor_gstin": data.get("vendor_gstin", ""),
        "transaction_date": data.get("transaction_date", datetime.now(timezone.utc).date().isoformat()),
        "delivery_date": data.get("delivery_date"),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": round(total + gst_amount, 2),
        "payment_terms": data.get("payment_terms", "Net 30"),
        "cost_center": data.get("cost_center", "General"),
        "status": "Submitted",
        "grn_status": "Pending",
        "invoice_status": "Pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.purchase_orders.insert_one(po)
    del po["_id"]
    return po

@router.get("/orders")
async def list_purchase_orders(status: Optional[str] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    orders = await db.purchase_orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return orders

@router.put("/orders/{po_id}/submit")
async def submit_purchase_order(po_id: str):
    po = await db.purchase_orders.find_one({"id": po_id}, {"_id": 0})
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    await db.purchase_orders.update_one({"id": po_id}, {"$set": {"status": "Submitted"}})
    return {"message": "PO submitted", "id": po_id}


# ═══════════════════════════════════════════════════════
# GRN - Linked to PO
# ═══════════════════════════════════════════════════════
@router.get("/grn/pending")
async def list_pending_grn():
    """POs that are submitted but not yet received (pending deliveries)"""
    pos = await db.purchase_orders.find(
        {"grn_status": "Pending", "status": {"$in": ["Submitted", "Draft"]}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return pos

@router.post("/grn/from-po/{po_id}")
async def create_grn_from_po(po_id: str):
    """Confirm receipt of goods from a PO - creates GRN with PO data"""
    po = await db.purchase_orders.find_one({"id": po_id}, {"_id": 0})
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    if po.get("grn_status") == "Received":
        raise HTTPException(status_code=400, detail="GRN already created for this PO")

    grn = {
        "id": str(uuid.uuid4()),
        "grn_number": f"GRN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "po_id": po["id"],
        "po_number": po["po_number"],
        "vendor": po["vendor"],
        "posting_date": datetime.now(timezone.utc).date().isoformat(),
        "items": po["items"],
        "subtotal": po["subtotal"],
        "gst_rate": po["gst_rate"],
        "gst_amount": po["gst_amount"],
        "grand_total": po["grand_total"],
        "warehouse": "Main Warehouse",
        "qc_status": "Accepted",
        "cost_center": po.get("cost_center", "General"),
        "invoice_status": "Pending",
        "status": "Received",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.goods_receipt_notes.insert_one(grn)
    del grn["_id"]

    # Auto JE: DR Raw Material Inventory, DR GST Input, CR Accounts Payable
    journal_entries = [
        {"account": "Raw Material Inventory", "debit": po["subtotal"], "credit": 0,
         "description": f"GRN {grn['grn_number']} from {po['vendor']}"},
        {"account": "GST Input", "debit": po["gst_amount"], "credit": 0,
         "description": f"GST on GRN {grn['grn_number']}"},
        {"account": "Accounts Payable", "debit": 0, "credit": po["grand_total"],
         "description": f"Payable to {po['vendor']}"}
    ]
    je_id = await auto_post_journal_entries(
        journal_entries,
        f"GRN: {grn['grn_number']} from {po['vendor']} (PO: {po['po_number']})",
        grn["cost_center"], "GRN", grn["id"]
    )
    grn["journal_entry_id"] = je_id

    # Update PO status
    await db.purchase_orders.update_one(
        {"id": po_id},
        {"$set": {"grn_status": "Received", "status": "To Invoice"}}
    )

    # Update stock levels
    for item in po["items"]:
        await db.items.update_one(
            {"item_code": item.get("item_code", item.get("item", ""))},
            {"$inc": {"current_stock": item.get("qty", 0)}},
            upsert=False
        )

    return grn

@router.post("/grn")
async def create_grn_legacy(data: dict):
    """Legacy GRN creation for backward compat / AI entry"""
    items = data.get("items", [])
    total = sum(i.get("amount", i.get("qty", 0) * i.get("rate", 0)) for i in items)
    gst_rate = data.get("gst_rate", 18)
    gst_amount = round(total * gst_rate / 100, 2)
    grn = {
        "id": str(uuid.uuid4()),
        "grn_number": f"GRN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "po_id": data.get("purchase_order_ref", ""),
        "po_number": data.get("po_number", ""),
        "vendor": data.get("vendor"),
        "posting_date": data.get("posting_date", datetime.now(timezone.utc).date().isoformat()),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": round(total + gst_amount, 2),
        "warehouse": data.get("warehouse", "Main Warehouse"),
        "qc_status": data.get("qc_status", "Accepted"),
        "cost_center": data.get("cost_center", "General"),
        "invoice_status": "Pending",
        "status": "Received",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.goods_receipt_notes.insert_one(grn)
    del grn["_id"]
    journal_entries = [
        {"account": "Raw Material Inventory", "debit": total, "credit": 0,
         "description": f"GRN {grn['grn_number']} - {data.get('vendor', '')}"},
        {"account": "GST Input", "debit": gst_amount, "credit": 0,
         "description": f"GST on GRN {grn['grn_number']}"},
        {"account": "Accounts Payable", "debit": 0, "credit": round(total + gst_amount, 2),
         "description": f"Payable to {data.get('vendor', '')}"}
    ]
    await auto_post_journal_entries(
        journal_entries,
        f"GRN: {grn['grn_number']} from {data.get('vendor', '')}",
        grn["cost_center"], "GRN", grn["id"]
    )
    if data.get("purchase_order_ref"):
        await db.purchase_orders.update_one(
            {"id": data["purchase_order_ref"]},
            {"$set": {"grn_status": "Received", "status": "To Invoice"}}
        )
    for item in items:
        await db.items.update_one(
            {"item_code": item.get("item_code", item.get("item", ""))},
            {"$inc": {"current_stock": item.get("qty", 0)}},
            upsert=False
        )
    return grn

@router.get("/grn")
async def list_grn(limit: int = 100):
    grns = await db.goods_receipt_notes.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return grns


# ═══════════════════════════════════════════════════════
# PURCHASE INVOICE - Linked to GRN
# ═══════════════════════════════════════════════════════
@router.get("/invoices/pending")
async def list_pending_invoices():
    """GRNs that have been received but not yet invoiced"""
    grns = await db.goods_receipt_notes.find(
        {"invoice_status": "Pending", "status": "Received"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return grns

@router.post("/invoices/from-grn/{grn_id}")
async def create_invoice_from_grn(grn_id: str, data: dict = None):
    """Create purchase invoice from GRN - uses GRN data, user can attach vendor invoice no"""
    if data is None:
        data = {}
    grn = await db.goods_receipt_notes.find_one({"id": grn_id}, {"_id": 0})
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")
    if grn.get("invoice_status") == "Invoiced":
        raise HTTPException(status_code=400, detail="Invoice already created for this GRN")

    inv = {
        "id": str(uuid.uuid4()),
        "invoice_number": f"PI-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "grn_id": grn["id"],
        "grn_number": grn["grn_number"],
        "po_id": grn.get("po_id", ""),
        "po_number": grn.get("po_number", ""),
        "vendor": grn["vendor"],
        "vendor_invoice_no": data.get("vendor_invoice_no", ""),
        "posting_date": datetime.now(timezone.utc).date().isoformat(),
        "due_date": data.get("due_date"),
        "items": grn["items"],
        "subtotal": grn["subtotal"],
        "gst_rate": grn["gst_rate"],
        "gst_amount": grn["gst_amount"],
        "grand_total": grn["grand_total"],
        "cost_center": grn.get("cost_center", "General"),
        "status": "Unpaid",
        "amount_paid": 0,
        "payment_status": "Unpaid",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.purchase_invoices.insert_one(inv)
    del inv["_id"]

    # GRN already posted JE for inventory. Invoice just records the liability formally.
    # No duplicate JE needed since GRN already DR Inventory, CR AP.
    # But if invoice amount differs from GRN (price variance), we'd post adjustment.
    # For now, mark GRN as invoiced.

    # Update GRN invoice status
    await db.goods_receipt_notes.update_one(
        {"id": grn_id},
        {"$set": {"invoice_status": "Invoiced"}}
    )

    # Update PO status
    if grn.get("po_id"):
        await db.purchase_orders.update_one(
            {"id": grn["po_id"]},
            {"$set": {"invoice_status": "Invoiced", "status": "Completed"}}
        )

    return inv

@router.post("/invoices")
async def create_purchase_invoice_legacy(data: dict):
    """Legacy direct invoice creation for backward compat / AI entry"""
    items = data.get("items", [])
    total = sum(i.get("amount", i.get("qty", 0) * i.get("rate", 0)) for i in items)
    gst_rate = data.get("gst_rate", 18)
    gst_amount = round(total * gst_rate / 100, 2)
    inv = {
        "id": str(uuid.uuid4()),
        "invoice_number": data.get("invoice_number",
                                   f"PI-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"),
        "vendor": data.get("vendor"),
        "vendor_gstin": data.get("vendor_gstin", ""),
        "vendor_invoice_no": data.get("vendor_invoice_no", ""),
        "posting_date": data.get("posting_date", datetime.now(timezone.utc).date().isoformat()),
        "due_date": data.get("due_date"),
        "grn_id": data.get("grn_ref", ""),
        "grn_number": data.get("grn_number", ""),
        "po_id": data.get("purchase_order_ref", ""),
        "po_number": data.get("po_number", ""),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": round(total + gst_amount, 2),
        "cost_center": data.get("cost_center", "General"),
        "status": "Unpaid",
        "amount_paid": 0,
        "payment_status": "Unpaid",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.purchase_invoices.insert_one(inv)
    del inv["_id"]
    if not data.get("grn_ref"):
        journal_entries = [
            {"account": data.get("expense_account", "Raw Material Inventory"), "debit": total, "credit": 0,
             "description": f"Purchase Invoice {inv['invoice_number']}"},
            {"account": "GST Input", "debit": gst_amount, "credit": 0,
             "description": f"GST on PI {inv['invoice_number']}"},
            {"account": "Accounts Payable", "debit": 0, "credit": round(total + gst_amount, 2),
             "description": f"Payable to {data.get('vendor', '')}"}
        ]
        await auto_post_journal_entries(
            journal_entries,
            f"Purchase Invoice: {inv['invoice_number']} from {data.get('vendor', '')}",
            inv["cost_center"], "Purchase Invoice", inv["id"]
        )
    return inv

@router.get("/invoices")
async def list_purchase_invoices(status: Optional[str] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    invoices = await db.purchase_invoices.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return invoices


# ═══════════════════════════════════════════════════════
# VENDOR PAYMENT - Linked to Invoice (with aging)
# ═══════════════════════════════════════════════════════
@router.get("/payments/outstanding")
async def list_outstanding_invoices():
    """Unpaid/partially paid invoices sorted by days outstanding"""
    invoices = await db.purchase_invoices.find(
        {"status": {"$in": ["Unpaid", "Partially Paid"]}},
        {"_id": 0}
    ).sort("created_at", 1).to_list(500)

    today = datetime.now(timezone.utc).date()
    for inv in invoices:
        inv_date = inv.get("posting_date", inv.get("created_at", "")[:10])
        try:
            d = datetime.strptime(inv_date, "%Y-%m-%d").date()
            inv["days_outstanding"] = (today - d).days
        except (ValueError, TypeError):
            inv["days_outstanding"] = 0
        inv["balance_due"] = round(inv.get("grand_total", 0) - inv.get("amount_paid", 0), 2)

    invoices.sort(key=lambda x: x.get("days_outstanding", 0), reverse=True)
    return invoices

@router.post("/payments/for-invoice/{invoice_id}")
async def create_payment_for_invoice(invoice_id: str, data: dict = None):
    """Pay a specific invoice"""
    if data is None:
        data = {}
    inv = await db.purchase_invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    balance = round(inv.get("grand_total", 0) - inv.get("amount_paid", 0), 2)
    amount = data.get("amount", balance)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    payment = {
        "id": str(uuid.uuid4()),
        "payment_number": f"VP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "vendor": inv["vendor"],
        "invoice_id": inv["id"],
        "invoice_number": inv["invoice_number"],
        "po_number": inv.get("po_number", ""),
        "grn_number": inv.get("grn_number", ""),
        "amount": amount,
        "payment_date": data.get("payment_date", datetime.now(timezone.utc).date().isoformat()),
        "payment_mode": data.get("payment_mode", "Bank Transfer"),
        "bank_account": data.get("bank_account", "Cash & Bank (HDFC Current)"),
        "reference": data.get("reference", ""),
        "cost_center": inv.get("cost_center", "General"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.vendor_payments.insert_one(payment)
    del payment["_id"]

    # Auto JE: DR Accounts Payable, CR Bank
    journal_entries = [
        {"account": "Accounts Payable", "debit": amount, "credit": 0,
         "description": f"Payment to {inv['vendor']} (Inv: {inv['invoice_number']})"},
        {"account": payment["bank_account"], "debit": 0, "credit": amount,
         "description": f"VP {payment['payment_number']}"}
    ]
    je_id = await auto_post_journal_entries(
        journal_entries,
        f"Vendor Payment: {payment['payment_number']} for {inv['invoice_number']}",
        payment["cost_center"], "Vendor Payment", payment["id"]
    )
    payment["journal_entry_id"] = je_id

    # Update invoice paid amount and status
    new_paid = inv.get("amount_paid", 0) + amount
    status = "Paid" if new_paid >= inv.get("grand_total", 0) else "Partially Paid"
    await db.purchase_invoices.update_one(
        {"id": invoice_id},
        {"$set": {"amount_paid": new_paid, "status": status, "payment_status": status}}
    )

    return payment

@router.post("/payments")
async def create_vendor_payment_legacy(data: dict):
    """Legacy payment creation"""
    amount = data.get("amount", 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    payment = {
        "id": str(uuid.uuid4()),
        "payment_number": f"VP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "vendor": data.get("vendor"),
        "amount": amount,
        "payment_date": data.get("payment_date", datetime.now(timezone.utc).date().isoformat()),
        "payment_mode": data.get("payment_mode", "Bank Transfer"),
        "bank_account": data.get("bank_account", "Cash & Bank (HDFC Current)"),
        "reference": data.get("reference", ""),
        "invoice_refs": data.get("invoice_refs", []),
        "cost_center": data.get("cost_center", "General"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.vendor_payments.insert_one(payment)
    del payment["_id"]
    journal_entries = [
        {"account": "Accounts Payable", "debit": amount, "credit": 0,
         "description": f"Payment to {data.get('vendor', '')}"},
        {"account": payment["bank_account"], "debit": 0, "credit": amount,
         "description": f"VP {payment['payment_number']}"}
    ]
    await auto_post_journal_entries(
        journal_entries,
        f"Vendor Payment: {payment['payment_number']} to {data.get('vendor', '')}",
        payment["cost_center"], "Vendor Payment", payment["id"]
    )
    for inv_id in data.get("invoice_refs", []):
        inv = await db.purchase_invoices.find_one({"id": inv_id}, {"_id": 0})
        if inv:
            new_paid = inv.get("amount_paid", 0) + amount
            status = "Paid" if new_paid >= inv.get("grand_total", 0) else "Partially Paid"
            await db.purchase_invoices.update_one(
                {"id": inv_id},
                {"$set": {"amount_paid": new_paid, "status": status}}
            )
    return payment

@router.get("/payments")
async def list_vendor_payments(limit: int = 100):
    payments = await db.vendor_payments.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return payments
