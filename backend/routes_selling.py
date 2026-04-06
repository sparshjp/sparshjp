# Kairos Advisory - Selling Module with Linked Document Flow
# SO → DN (from SO) → Sales Invoice (from DN) → Customer Payment (from Invoice)
# Each stage auto-flows from the previous. No orphan documents.

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional
import uuid

router = APIRouter(prefix="/selling", tags=["selling"])
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
# QUOTATIONS
# ═══════════════════════════════════════════════════════
@router.post("/quotations")
async def create_quotation(data: dict):
    items = data.get("items", [])
    total = sum(i.get("amount", i.get("qty", 0) * i.get("rate", 0)) for i in items)
    gst_rate = data.get("gst_rate", 18)
    gst_amount = round(total * gst_rate / 100, 2)
    quot = {
        "id": str(uuid.uuid4()),
        "quotation_number": f"QTN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "customer": data.get("customer"),
        "customer_gstin": data.get("customer_gstin", ""),
        "transaction_date": data.get("transaction_date", datetime.now(timezone.utc).date().isoformat()),
        "valid_till": data.get("valid_till"),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": round(total + gst_amount, 2),
        "status": "Draft",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.selling_quotations.insert_one(quot)
    del quot["_id"]
    return quot

@router.get("/quotations")
async def list_quotations(status: Optional[str] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    return await db.selling_quotations.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)


# ═══════════════════════════════════════════════════════
# SALES ORDERS
# ═══════════════════════════════════════════════════════
@router.post("/sales-orders")
async def create_sales_order(data: dict):
    # Validate customer exists in master data
    customer_name = data.get("customer", "")
    customer_doc = await db.entities.find_one({"name": customer_name, "entity_type": "customer"}, {"_id": 0})
    if not customer_doc:
        raise HTTPException(status_code=400, detail=f"Customer '{customer_name}' not found in master data. Create the customer first in Master Data.")
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
    total_qty = sum(i.get("qty", 0) for i in items)

    so = {
        "id": str(uuid.uuid4()),
        "so_number": data.get("so_number", f"SO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"),
        "customer": data.get("customer"),
        "customer_gstin": data.get("customer_gstin", ""),
        "customer_po": data.get("po_no", ""),
        "transaction_date": data.get("transaction_date", datetime.now(timezone.utc).date().isoformat()),
        "delivery_date": data.get("delivery_date"),
        "quotation_ref": data.get("quotation_ref"),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": round(total + gst_amount, 2),
        "total_qty": total_qty,
        "delivered_qty": 0,
        "invoiced_amount": 0,
        "payment_terms": data.get("payment_terms", ""),
        "cost_center": data.get("cost_center", "Sales & Marketing"),
        "status": "Submitted",
        "delivery_status": "Not Delivered",
        "billing_status": "Not Billed",
        "invoice_status": "Pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    # Credit limit check
    customer_data = await db.customers.find_one({"customer_name": data.get("customer")}, {"_id": 0})
    if customer_data:
        credit_limit = customer_data.get("credit_limit", 0)
        if credit_limit > 0:
            outstanding_ar = await db.selling_invoices.find(
                {"customer": data.get("customer"), "status": {"$in": ["Unpaid", "Partially Paid"]}},
                {"_id": 0}
            ).to_list(10000)
            total_outstanding = sum(inv.get("grand_total", 0) - inv.get("amount_paid", 0) for inv in outstanding_ar)
            if total_outstanding + so["grand_total"] > credit_limit:
                so["credit_warning"] = f"Credit limit: {credit_limit}, Outstanding: {total_outstanding}, This SO: {so['grand_total']}"

    await db.selling_sales_orders.insert_one(so)
    del so["_id"]
    return so

@router.get("/sales-orders")
async def list_sales_orders(status: Optional[str] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    return await db.selling_sales_orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)

@router.put("/sales-orders/{so_id}/submit")
async def submit_sales_order(so_id: str):
    so = await db.selling_sales_orders.find_one({"id": so_id}, {"_id": 0})
    if not so:
        raise HTTPException(status_code=404, detail="SO not found")
    await db.selling_sales_orders.update_one({"id": so_id}, {"$set": {"status": "Submitted"}})
    return {"message": "SO submitted", "id": so_id}


# ═══════════════════════════════════════════════════════
# DELIVERY NOTE - Linked to SO
# ═══════════════════════════════════════════════════════
@router.get("/delivery-notes/pending")
async def list_pending_delivery():
    """SOs that need to be dispatched (pending delivery)"""
    sos = await db.selling_sales_orders.find(
        {"delivery_status": "Not Delivered", "status": {"$in": ["Submitted", "Draft"]}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return sos

@router.post("/delivery-notes/from-so/{so_id}")
async def create_dn_from_so(so_id: str):
    """Confirm delivery from a SO - creates DN with SO data"""
    so = await db.selling_sales_orders.find_one({"id": so_id}, {"_id": 0})
    if not so:
        raise HTTPException(status_code=404, detail="SO not found")
    if so.get("delivery_status") == "Fully Delivered":
        raise HTTPException(status_code=400, detail="Already fully delivered")

    dn = {
        "id": str(uuid.uuid4()),
        "dn_number": f"DN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "so_id": so["id"],
        "so_number": so["so_number"],
        "customer": so["customer"],
        "posting_date": datetime.now(timezone.utc).date().isoformat(),
        "items": so["items"],
        "total_qty": so["total_qty"],
        "subtotal": so["subtotal"],
        "gst_rate": so["gst_rate"],
        "gst_amount": so["gst_amount"],
        "grand_total": so["grand_total"],
        "warehouse": "Main Warehouse",
        "cost_center": so.get("cost_center", "Sales & Marketing"),
        "invoice_status": "Pending",
        "status": "Delivered",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.selling_delivery_notes.insert_one(dn)
    del dn["_id"]

    # Update stock levels (reduce FG) with negative stock warning
    for item in so["items"]:
        item_code = item.get("item_code", item.get("item", ""))
        item_doc = await db.items.find_one({"item_code": item_code}, {"_id": 0})
        current_stock = item_doc.get("current_stock", 0) if item_doc else 0
        if current_stock < item.get("qty", 0):
            dn["warning"] = f"Negative stock: {item_code} has {current_stock} units, dispatching {item.get('qty', 0)}"
        await db.items.update_one(
            {"item_code": item_code},
            {"$inc": {"current_stock": -item.get("qty", 0)}},
            upsert=False
        )

    # Update SO delivery status
    new_delivered = so.get("delivered_qty", 0) + so["total_qty"]
    d_status = "Fully Delivered" if new_delivered >= so.get("total_qty", 0) else "Partially Delivered"
    await db.selling_sales_orders.update_one(
        {"id": so_id},
        {"$set": {"delivered_qty": new_delivered, "delivery_status": d_status, "status": "To Invoice"}}
    )

    return dn

@router.post("/delivery-notes")
async def create_dn_legacy(data: dict):
    """Legacy DN creation for backward compat / AI entry"""
    items = data.get("items", [])
    total_qty = sum(i.get("qty", 0) for i in items)
    dn = {
        "id": str(uuid.uuid4()),
        "dn_number": f"DN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "customer": data.get("customer"),
        "so_id": data.get("sales_order_ref", ""),
        "so_number": data.get("so_number", ""),
        "posting_date": data.get("posting_date", datetime.now(timezone.utc).date().isoformat()),
        "items": items,
        "total_qty": total_qty,
        "warehouse": data.get("warehouse", "Main Warehouse"),
        "cost_center": data.get("cost_center", "Sales & Marketing"),
        "invoice_status": "Pending",
        "status": "Delivered",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.selling_delivery_notes.insert_one(dn)
    del dn["_id"]
    for item in items:
        item_code = item.get("item_code", item.get("item", ""))
        await db.items.update_one(
            {"item_code": item_code},
            {"$inc": {"current_stock": -item.get("qty", 0)}},
            upsert=False
        )
    if data.get("sales_order_ref"):
        so = await db.selling_sales_orders.find_one({"id": data["sales_order_ref"]}, {"_id": 0})
        if so:
            new_delivered = so.get("delivered_qty", 0) + total_qty
            d_status = "Fully Delivered" if new_delivered >= so.get("total_qty", 0) else "Partially Delivered"
            await db.selling_sales_orders.update_one(
                {"id": data["sales_order_ref"]},
                {"$set": {"delivered_qty": new_delivered, "delivery_status": d_status}}
            )
    return dn

@router.get("/delivery-notes")
async def list_delivery_notes(limit: int = 100):
    return await db.selling_delivery_notes.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)


# ═══════════════════════════════════════════════════════
# SALES INVOICE - Linked to DN
# ═══════════════════════════════════════════════════════
@router.get("/invoices/pending")
async def list_pending_sales_invoices():
    """DNs that have been delivered but not yet invoiced"""
    dns = await db.selling_delivery_notes.find(
        {"invoice_status": "Pending", "status": "Delivered"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return dns

@router.post("/invoices/from-dn/{dn_id}")
async def create_invoice_from_dn(dn_id: str, data: dict = None):
    """Create sales invoice from DN - auto-generates accounting entries"""
    if data is None:
        data = {}
    dn = await db.selling_delivery_notes.find_one({"id": dn_id}, {"_id": 0})
    if not dn:
        raise HTTPException(status_code=404, detail="DN not found")
    if dn.get("invoice_status") == "Invoiced":
        raise HTTPException(status_code=400, detail="Invoice already created for this DN")

    items = dn["items"]
    total = dn.get("subtotal", sum(i.get("amount", i.get("qty", 0) * i.get("rate", 0)) for i in items))
    gst_rate = dn.get("gst_rate", 18)
    gst_amount = dn.get("gst_amount", round(total * gst_rate / 100, 2))
    grand_total = dn.get("grand_total", round(total + gst_amount, 2))

    # Calculate COGS
    cogs_total = 0
    for item in items:
        item_code = item.get("item_code", item.get("item", ""))
        item_doc = await db.items.find_one({"item_code": item_code}, {"_id": 0})
        cost = item_doc.get("valuation_rate", 0) if item_doc else 0
        item["cost_price"] = cost
        item["cogs"] = round(cost * item.get("qty", 0), 2)
        cogs_total += item["cogs"]

    inv = {
        "id": str(uuid.uuid4()),
        "invoice_number": f"SI-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "dn_id": dn["id"],
        "dn_number": dn["dn_number"],
        "so_id": dn.get("so_id", ""),
        "so_number": dn.get("so_number", ""),
        "customer": dn["customer"],
        "posting_date": datetime.now(timezone.utc).date().isoformat(),
        "due_date": data.get("due_date"),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": grand_total,
        "cogs_total": cogs_total,
        "cost_center": dn.get("cost_center", "Sales & Marketing"),
        "status": "Unpaid",
        "amount_paid": 0,
        "payment_status": "Unpaid",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.selling_invoices.insert_one(inv)
    del inv["_id"]

    # Auto JE: Revenue + COGS + GST
    journal_entries = [
        {"account": "Accounts Receivable", "debit": grand_total, "credit": 0,
         "description": f"AR: {inv['invoice_number']} - {dn['customer']}"},
        {"account": "Sales Revenue", "debit": 0, "credit": total,
         "description": f"Revenue: {inv['invoice_number']}"},
        {"account": "GST Output", "debit": 0, "credit": gst_amount,
         "description": f"GST on {inv['invoice_number']}"},
    ]
    if cogs_total > 0:
        journal_entries.extend([
            {"account": "Cost of Goods Sold", "debit": cogs_total, "credit": 0,
             "description": f"COGS: {inv['invoice_number']}"},
            {"account": "Finished Goods Inventory", "debit": 0, "credit": cogs_total,
             "description": f"FG dispatched: {inv['invoice_number']}"},
        ])

    je_id = await auto_post_journal_entries(
        journal_entries,
        f"Sales Invoice: {inv['invoice_number']} to {dn['customer']}",
        inv["cost_center"], "Sales Invoice", inv["id"]
    )
    inv["journal_entry_id"] = je_id

    # Update DN invoice status
    await db.selling_delivery_notes.update_one(
        {"id": dn_id},
        {"$set": {"invoice_status": "Invoiced"}}
    )

    # Update SO billing status
    if dn.get("so_id"):
        so = await db.selling_sales_orders.find_one({"id": dn["so_id"]}, {"_id": 0})
        if so:
            new_invoiced = so.get("invoiced_amount", 0) + grand_total
            b_status = "Fully Billed" if new_invoiced >= so.get("grand_total", 0) else "Partially Billed"
            await db.selling_sales_orders.update_one(
                {"id": dn["so_id"]},
                {"$set": {"invoiced_amount": new_invoiced, "billing_status": b_status, "invoice_status": "Invoiced", "status": "Completed"}}
            )

    return inv

@router.post("/invoices")
async def create_sales_invoice_legacy(data: dict):
    """Legacy direct invoice creation for backward compat / AI entry"""
    items = data.get("items", [])
    total = sum(i.get("amount", i.get("qty", 0) * i.get("rate", 0)) for i in items)
    gst_rate = data.get("gst_rate", 18)
    gst_amount = round(total * gst_rate / 100, 2)
    grand_total = round(total + gst_amount, 2)
    cogs_total = 0
    for item in items:
        item_code = item.get("item_code", item.get("item", ""))
        item_doc = await db.items.find_one({"item_code": item_code}, {"_id": 0})
        cost = item_doc.get("valuation_rate", 0) if item_doc else 0
        item["cost_price"] = cost
        item["cogs"] = round(cost * item.get("qty", 0), 2)
        cogs_total += item["cogs"]

    inv = {
        "id": str(uuid.uuid4()),
        "invoice_number": data.get("invoice_number",
                                   f"SI-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"),
        "customer": data.get("customer"),
        "customer_gstin": data.get("customer_gstin", ""),
        "posting_date": data.get("posting_date", datetime.now(timezone.utc).date().isoformat()),
        "due_date": data.get("due_date"),
        "so_id": data.get("sales_order_ref", ""),
        "dn_id": data.get("delivery_note_ref", ""),
        "items": items,
        "subtotal": total,
        "gst_rate": gst_rate,
        "gst_amount": gst_amount,
        "grand_total": grand_total,
        "cogs_total": cogs_total,
        "cost_center": data.get("cost_center", "Sales & Marketing"),
        "status": "Unpaid",
        "amount_paid": 0,
        "payment_status": "Unpaid",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.selling_invoices.insert_one(inv)
    del inv["_id"]
    journal_entries = [
        {"account": "Accounts Receivable", "debit": grand_total, "credit": 0,
         "description": f"AR: {inv['invoice_number']} - {data.get('customer', '')}"},
        {"account": "Sales Revenue", "debit": 0, "credit": total,
         "description": f"Revenue: {inv['invoice_number']}"},
        {"account": "GST Output", "debit": 0, "credit": gst_amount,
         "description": f"GST on {inv['invoice_number']}"},
    ]
    if cogs_total > 0:
        journal_entries.extend([
            {"account": "Cost of Goods Sold", "debit": cogs_total, "credit": 0,
             "description": f"COGS: {inv['invoice_number']}"},
            {"account": "Finished Goods Inventory", "debit": 0, "credit": cogs_total,
             "description": f"FG dispatched: {inv['invoice_number']}"},
        ])
    await auto_post_journal_entries(
        journal_entries,
        f"Sales Invoice: {inv['invoice_number']} to {data.get('customer', '')}",
        inv["cost_center"], "Sales Invoice", inv["id"]
    )
    if data.get("sales_order_ref"):
        so = await db.selling_sales_orders.find_one({"id": data["sales_order_ref"]}, {"_id": 0})
        if so:
            new_invoiced = so.get("invoiced_amount", 0) + grand_total
            b_status = "Fully Billed" if new_invoiced >= so.get("grand_total", 0) else "Partially Billed"
            await db.selling_sales_orders.update_one(
                {"id": data["sales_order_ref"]},
                {"$set": {"invoiced_amount": new_invoiced, "billing_status": b_status}}
            )
    return inv

@router.get("/invoices")
async def list_sales_invoices(status: Optional[str] = None, limit: int = 100):
    query = {}
    if status:
        query["status"] = status
    return await db.selling_invoices.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)


# ═══════════════════════════════════════════════════════
# CUSTOMER PAYMENT - Linked to Invoice (with aging)
# ═══════════════════════════════════════════════════════
@router.get("/payments/outstanding")
async def list_outstanding_sales_invoices():
    """Unpaid/partially paid invoices sorted by days outstanding"""
    invoices = await db.selling_invoices.find(
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
    """Receive payment against a specific invoice"""
    if data is None:
        data = {}
    inv = await db.selling_invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    balance = round(inv.get("grand_total", 0) - inv.get("amount_paid", 0), 2)
    amount = data.get("amount", balance)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    payment = {
        "id": str(uuid.uuid4()),
        "payment_number": f"CR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "customer": inv["customer"],
        "invoice_id": inv["id"],
        "invoice_number": inv["invoice_number"],
        "so_number": inv.get("so_number", ""),
        "dn_number": inv.get("dn_number", ""),
        "amount": amount,
        "payment_date": data.get("payment_date", datetime.now(timezone.utc).date().isoformat()),
        "payment_mode": data.get("payment_mode", "Bank Transfer"),
        "bank_account": data.get("bank_account", "Cash & Bank (HDFC Current)"),
        "reference": data.get("reference", ""),
        "is_advance": False,
        "cost_center": inv.get("cost_center", "Sales & Marketing"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.customer_payments.insert_one(payment)
    del payment["_id"]

    # Auto JE: DR Bank, CR AR
    journal_entries = [
        {"account": payment["bank_account"], "debit": amount, "credit": 0,
         "description": f"Receipt from {inv['customer']} (Inv: {inv['invoice_number']})"},
        {"account": "Accounts Receivable", "debit": 0, "credit": amount,
         "description": f"CR {payment['payment_number']}"}
    ]
    je_id = await auto_post_journal_entries(
        journal_entries,
        f"Customer Payment: {payment['payment_number']} for {inv['invoice_number']}",
        payment["cost_center"], "Customer Payment", payment["id"]
    )
    payment["journal_entry_id"] = je_id

    # Update invoice status
    new_paid = inv.get("amount_paid", 0) + amount
    status = "Paid" if new_paid >= inv.get("grand_total", 0) else "Partially Paid"
    await db.selling_invoices.update_one(
        {"id": invoice_id},
        {"$set": {"amount_paid": new_paid, "status": status, "payment_status": status}}
    )

    return payment

@router.post("/payments")
async def create_customer_payment_legacy(data: dict):
    """Legacy payment creation"""
    amount = data.get("amount", 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    payment = {
        "id": str(uuid.uuid4()),
        "payment_number": f"CR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
        "customer": data.get("customer"),
        "amount": amount,
        "payment_date": data.get("payment_date", datetime.now(timezone.utc).date().isoformat()),
        "payment_mode": data.get("payment_mode", "Bank Transfer"),
        "bank_account": data.get("bank_account", "Cash & Bank (HDFC Current)"),
        "reference": data.get("reference", ""),
        "invoice_refs": data.get("invoice_refs", []),
        "is_advance": data.get("is_advance", False),
        "cost_center": data.get("cost_center", "Sales & Marketing"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.customer_payments.insert_one(payment)
    del payment["_id"]
    cr_account = "Advance from Customer" if payment["is_advance"] else "Accounts Receivable"
    journal_entries = [
        {"account": payment["bank_account"], "debit": amount, "credit": 0,
         "description": f"Receipt from {data.get('customer', '')}"},
        {"account": cr_account, "debit": 0, "credit": amount,
         "description": f"CR {payment['payment_number']}"}
    ]
    if payment["is_advance"] and data.get("gst_on_advance"):
        gst_amt = round(amount * 18 / 118, 2)
        journal_entries[1]["credit"] = amount - gst_amt
        journal_entries.append(
            {"account": "GST Output", "debit": 0, "credit": gst_amt,
             "description": f"GST on advance {payment['payment_number']}"}
        )
    await auto_post_journal_entries(
        journal_entries,
        f"Customer Payment: {payment['payment_number']} from {data.get('customer', '')}",
        payment["cost_center"], "Customer Payment", payment["id"]
    )
    for inv_id in data.get("invoice_refs", []):
        inv = await db.selling_invoices.find_one({"id": inv_id}, {"_id": 0})
        if inv:
            new_paid = inv.get("amount_paid", 0) + amount
            status = "Paid" if new_paid >= inv.get("grand_total", 0) else "Partially Paid"
            await db.selling_invoices.update_one(
                {"id": inv_id},
                {"$set": {"amount_paid": new_paid, "status": status}}
            )
    return payment

@router.get("/payments")
async def list_customer_payments(limit: int = 100):
    return await db.customer_payments.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
