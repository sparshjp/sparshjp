# Audit Trail Service - Companies Act 2013, Rule 3(1) Compliance
# Append-only audit log. No edit/delete operations permitted.
# Preserves: timestamp, user, action, document type/id, before/after changes

from datetime import datetime, timezone
import uuid

db = None

def set_db(database):
    global db
    db = database

# Action types
ACTION_CREATE = "CREATE"
ACTION_UPDATE = "UPDATE"
ACTION_DELETE = "DELETE"
ACTION_SUBMIT = "SUBMIT"
ACTION_CANCEL = "CANCEL"
ACTION_POST = "POST"

# Document types
DOC_PURCHASE_ORDER = "Purchase Order"
DOC_GRN = "Goods Receipt Note"
DOC_PURCHASE_INVOICE = "Purchase Invoice"
DOC_VENDOR_PAYMENT = "Vendor Payment"
DOC_SALES_ORDER = "Sales Order"
DOC_DELIVERY_NOTE = "Delivery Note"
DOC_SALES_INVOICE = "Sales Invoice"
DOC_CUSTOMER_RECEIPT = "Customer Receipt"
DOC_WORK_ORDER = "Work Order"
DOC_JOURNAL_ENTRY = "Journal Entry"
DOC_MANUAL_JE = "Manual Journal Entry"
DOC_COA = "Chart of Accounts"
DOC_ENTITY = "Entity (Vendor/Customer)"
DOC_ITEM = "Item"
DOC_COST_CENTER = "Cost Center"
DOC_COMPANY_SETTINGS = "Company Settings"
DOC_QUOTATION = "Quotation"


def _serialize_value(val):
    """Convert values to JSON-safe strings for audit comparison"""
    if val is None:
        return None
    if isinstance(val, (str, int, float, bool)):
        return val
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, list):
        return str(val)[:500]
    if isinstance(val, dict):
        return str(val)[:500]
    return str(val)[:500]


def compute_changes(old_doc, new_doc):
    """Compute field-level diff between old and new document"""
    if not old_doc:
        return []
    changes = []
    all_keys = set(list(old_doc.keys()) + list(new_doc.keys()))
    skip_keys = {"_id", "updated_at", "created_at"}
    for key in sorted(all_keys):
        if key in skip_keys:
            continue
        old_val = _serialize_value(old_doc.get(key))
        new_val = _serialize_value(new_doc.get(key))
        if old_val != new_val:
            changes.append({
                "field": key,
                "old_value": old_val,
                "new_value": new_val,
            })
    return changes


async def log_audit(action, document_type, document_id, document_number=None,
                    changes=None, snapshot=None, user="system", notes=None):
    """
    Append an immutable audit trail entry.
    
    Args:
        action: CREATE | UPDATE | DELETE | SUBMIT | CANCEL | POST
        document_type: e.g. "Purchase Order", "Journal Entry"
        document_id: unique ID of the document
        document_number: human-readable number (e.g. PO-2026-001)
        changes: list of {field, old_value, new_value} dicts (for UPDATE)
        snapshot: full document snapshot (for CREATE/DELETE)
        user: user ID who performed the action
        notes: optional description of what happened
    """
    if db is None:
        return

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "action": action,
        "document_type": document_type,
        "document_id": str(document_id) if document_id else "",
        "document_number": document_number or "",
        "changes": changes or [],
        "notes": notes or "",
    }

    # For CREATE/DELETE, store a snapshot of the full document
    if snapshot:
        clean = {}
        for k, v in snapshot.items():
            if k == "_id":
                continue
            clean[k] = _serialize_value(v)
        entry["snapshot"] = clean

    await db.audit_trail.insert_one(entry)
