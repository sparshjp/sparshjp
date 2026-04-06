# Kairos Accounting - Purchase Module with Auto-Accounting
# Handles: Purchase Orders → GRN → Purchase Invoice (auto JE) → Vendor Payment (auto JE)

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional
import uuid

router = APIRouter(prefix="/purchase", tags=["purchase"])
db = None

def set_db(database):
    global db
    db = database

async def auto_post_journal_entries(entries, narration, cost_center="General", ref_doc_type="", ref_doc_id=""):
    """Create and post journal entries automatically, update CoA balances"""
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
    items = data.get("items", [])
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
        "status": "Draft",
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
# GOODS RECEIPT NOTE (GRN)
# ═══════════════════════════════════════════════════════
@router.post("/grn")
async def create_grn(data: dict):
    """Create GRN and auto-generate inventory journal entries"""
    items = data.get("items", [])
    total = sum(i.get("amount", i.get("qty", 0) * i.get("rate", 0)) for i in items)
    gst_rate = data.get("gst_rate", 18)
    gst_amount = round(total * gst_rate / 100, 2)

    grn = {
        "id": str(uuid.uuid4()),
        "grn_number": f"GRN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "purchase_order_ref": data.get("purchase_order_ref"),
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
        "status": "Received",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.goods_receipt_notes.insert_one(grn)
    del grn["_id"]

    # Auto-generate JE: DR Inventory, DR GST Input, CR Accounts Payable
    journal_entries = [
        {"account": "Raw Material Inventory", "debit": total, "credit": 0,
         "description": f"GRN {grn['grn_number']} - {data.get('vendor', '')}"},
        {"account": "GST Input", "debit": gst_amount, "credit": 0,
         "description": f"GST on GRN {grn['grn_number']}"},
        {"account": "Accounts Payable", "debit": 0, "credit": round(total + gst_amount, 2),
         "description": f"Payable to {data.get('vendor', '')}"}
    ]
    je_id = await auto_post_journal_entries(
        journal_entries,
        f"GRN: {grn['grn_number']} from {data.get('vendor', '')}",
        grn["cost_center"],
        "GRN", grn["id"]
    )
    grn["journal_entry_id"] = je_id

    # Update PO status
    if data.get("purchase_order_ref"):
        await db.purchase_orders.update_one(
            {"id": data["purchase_order_ref"]},
            {"$set": {"grn_status": "Received", "status": "To Invoice"}}
        )

    # Update stock levels
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
# PURCHASE INVOICE (auto-accounting)
# ═══════════════════════════════════════════════════════
@router.post("/invoices")
async def create_purchase_invoice(data: dict):
    """Create Purchase Invoice - if GRN already done, just reconcile. Otherwise, create full entries."""
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
        "purchase_order_ref": data.get("purchase_order_ref"),
        "grn_ref": data.get("grn_ref"),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": round(total + gst_amount, 2),
        "cost_center": data.get("cost_center", "General"),
        "status": "Unpaid",
        "amount_paid": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.purchase_invoices.insert_one(inv)
    del inv["_id"]

    # If no GRN ref (direct invoice), auto-generate full JE
    if not data.get("grn_ref"):
        journal_entries = [
            {"account": data.get("expense_account", "Raw Material Inventory"), "debit": total, "credit": 0,
             "description": f"Purchase Invoice {inv['invoice_number']}"},
            {"account": "GST Input", "debit": gst_amount, "credit": 0,
             "description": f"GST on PI {inv['invoice_number']}"},
            {"account": "Accounts Payable", "debit": 0, "credit": round(total + gst_amount, 2),
             "description": f"Payable to {data.get('vendor', '')}"}
        ]
        je_id = await auto_post_journal_entries(
            journal_entries,
            f"Purchase Invoice: {inv['invoice_number']} from {data.get('vendor', '')}",
            inv["cost_center"],
            "Purchase Invoice", inv["id"]
        )
        inv["journal_entry_id"] = je_id

    # Update PO status
    if data.get("purchase_order_ref"):
        await db.purchase_orders.update_one(
            {"id": data["purchase_order_ref"]},
            {"$set": {"invoice_status": "Invoiced", "status": "Completed"}}
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
# VENDOR PAYMENT (auto-accounting)
# ═══════════════════════════════════════════════════════
@router.post("/payments")
async def create_vendor_payment(data: dict):
    """Record vendor payment - auto DR AP, CR Bank"""
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

    # Auto JE: DR Accounts Payable, CR Bank
    journal_entries = [
        {"account": "Accounts Payable", "debit": amount, "credit": 0,
         "description": f"Payment to {data.get('vendor', '')}"},
        {"account": payment["bank_account"], "debit": 0, "credit": amount,
         "description": f"VP {payment['payment_number']}"}
    ]
    je_id = await auto_post_journal_entries(
        journal_entries,
        f"Vendor Payment: {payment['payment_number']} to {data.get('vendor', '')}",
        payment["cost_center"],
        "Vendor Payment", payment["id"]
    )
    payment["journal_entry_id"] = je_id

    # Update invoice status
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
