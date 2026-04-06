# AP/AR Aging Report - 0-30, 30-60, 60-90, 90+ day buckets
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/aging", tags=["aging"])
db = None

def set_db(database):
    global db
    db = database


def _days_outstanding(date_str):
    """Calculate days between invoice date and today"""
    try:
        inv_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - inv_date).days
    except:
        return 0


def _bucket(days):
    if days <= 30: return "0-30"
    if days <= 60: return "30-60"
    if days <= 90: return "60-90"
    return "90+"


@router.get("/payables")
async def accounts_payable_aging():
    """AP Aging: Outstanding purchase invoices by vendor"""
    invoices = await db.purchase_invoices.find(
        {"status": {"$in": ["Unpaid", "Partially Paid", "Overdue"]}},
        {"_id": 0}
    ).to_list(10000)

    # Also include invoices where amount_paid < grand_total
    all_invoices = await db.purchase_invoices.find({}, {"_id": 0}).to_list(10000)
    for inv in all_invoices:
        outstanding = inv.get("grand_total", 0) - inv.get("amount_paid", 0)
        if outstanding > 0 and inv not in invoices:
            invoices.append(inv)

    buckets = {"0-30": 0, "30-60": 0, "60-90": 0, "90+": 0}
    vendor_aging = {}
    details = []

    for inv in invoices:
        outstanding = inv.get("grand_total", 0) - inv.get("amount_paid", 0)
        if outstanding <= 0:
            continue
        days = _days_outstanding(inv.get("posting_date", inv.get("transaction_date", inv.get("created_at", ""))))
        bucket = _bucket(days)
        buckets[bucket] += outstanding

        vendor = inv.get("vendor", "Unknown")
        if vendor not in vendor_aging:
            vendor_aging[vendor] = {"vendor": vendor, "0-30": 0, "30-60": 0, "60-90": 0, "90+": 0, "total": 0}
        vendor_aging[vendor][bucket] += outstanding
        vendor_aging[vendor]["total"] += outstanding

        details.append({
            "vendor": vendor,
            "invoice_number": inv.get("invoice_number", ""),
            "invoice_date": inv.get("posting_date", inv.get("transaction_date", "")),
            "grand_total": inv.get("grand_total", 0),
            "amount_paid": inv.get("amount_paid", 0),
            "outstanding": round(outstanding, 2),
            "days": days,
            "bucket": bucket,
        })

    # Round
    for k in buckets: buckets[k] = round(buckets[k], 2)
    total = round(sum(buckets.values()), 2)

    return {
        "report_type": "Accounts Payable Aging",
        "as_of": datetime.now(timezone.utc).date().isoformat(),
        "buckets": buckets,
        "total_outstanding": total,
        "by_vendor": sorted(vendor_aging.values(), key=lambda x: x["total"], reverse=True),
        "details": sorted(details, key=lambda x: x["days"], reverse=True),
    }


@router.get("/receivables")
async def accounts_receivable_aging():
    """AR Aging: Outstanding sales invoices by customer"""
    all_invoices = await db.selling_invoices.find({}, {"_id": 0}).to_list(10000)

    buckets = {"0-30": 0, "30-60": 0, "60-90": 0, "90+": 0}
    customer_aging = {}
    details = []

    for inv in all_invoices:
        outstanding = inv.get("grand_total", 0) - inv.get("amount_paid", 0)
        if outstanding <= 0:
            continue
        days = _days_outstanding(inv.get("posting_date", inv.get("transaction_date", inv.get("created_at", ""))))
        bucket = _bucket(days)
        buckets[bucket] += outstanding

        customer = inv.get("customer", "Unknown")
        if customer not in customer_aging:
            customer_aging[customer] = {"customer": customer, "0-30": 0, "30-60": 0, "60-90": 0, "90+": 0, "total": 0}
        customer_aging[customer][bucket] += outstanding
        customer_aging[customer]["total"] += outstanding

        details.append({
            "customer": customer,
            "invoice_number": inv.get("invoice_number", ""),
            "invoice_date": inv.get("posting_date", inv.get("transaction_date", "")),
            "grand_total": inv.get("grand_total", 0),
            "amount_paid": inv.get("amount_paid", 0),
            "outstanding": round(outstanding, 2),
            "days": days,
            "bucket": bucket,
        })

    for k in buckets: buckets[k] = round(buckets[k], 2)
    total = round(sum(buckets.values()), 2)

    return {
        "report_type": "Accounts Receivable Aging",
        "as_of": datetime.now(timezone.utc).date().isoformat(),
        "buckets": buckets,
        "total_outstanding": total,
        "by_customer": sorted(customer_aging.values(), key=lambda x: x["total"], reverse=True),
        "details": sorted(details, key=lambda x: x["days"], reverse=True),
    }
