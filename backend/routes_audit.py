# Audit Trail API Routes - READ-ONLY (no edit/delete endpoints)
# Compliant with Companies Act 2013, Section 128(5) - 8 year preservation

from fastapi import APIRouter, Response
from datetime import datetime, timezone
from typing import Optional
from io import StringIO
import csv

router = APIRouter(prefix="/audit-trail", tags=["audit-trail"])
db = None

def set_db(database):
    global db
    db = database


@router.get("")
async def get_audit_trail(
    document_type: Optional[str] = None,
    action: Optional[str] = None,
    document_number: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 200,
    skip: int = 0,
):
    """Get audit trail entries with filters. Read-only endpoint."""
    query = {}

    if document_type:
        query["document_type"] = document_type
    if action:
        query["action"] = action
    if document_number:
        query["document_number"] = {"$regex": document_number, "$options": "i"}
    if user:
        query["user"] = {"$regex": user, "$options": "i"}
    if date_from:
        query.setdefault("timestamp", {})["$gte"] = date_from
    if date_to:
        query.setdefault("timestamp", {})["$lte"] = date_to + "T23:59:59"
    if search:
        query["$or"] = [
            {"document_number": {"$regex": search, "$options": "i"}},
            {"document_type": {"$regex": search, "$options": "i"}},
            {"notes": {"$regex": search, "$options": "i"}},
            {"user": {"$regex": search, "$options": "i"}},
        ]

    total = await db.audit_trail.count_documents(query)
    entries = await db.audit_trail.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "entries": entries,
        "total": total,
        "limit": limit,
        "skip": skip,
    }


@router.get("/stats")
async def get_audit_stats():
    """Get audit trail summary stats"""
    total = await db.audit_trail.count_documents({})

    # Count by action
    action_pipeline = [
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    action_counts = {r["_id"]: r["count"] async for r in db.audit_trail.aggregate(action_pipeline)}

    # Count by document type
    doc_pipeline = [
        {"$group": {"_id": "$document_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    doc_counts = {r["_id"]: r["count"] async for r in db.audit_trail.aggregate(doc_pipeline)}

    # Latest entry
    latest = await db.audit_trail.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])

    return {
        "total_entries": total,
        "by_action": action_counts,
        "by_document_type": doc_counts,
        "latest_entry": latest,
    }


@router.get("/document-types")
async def get_document_types():
    """Get distinct document types for filter dropdown"""
    types = await db.audit_trail.distinct("document_type")
    return sorted(types)


@router.get("/export")
async def export_audit_trail(
    document_type: Optional[str] = None,
    action: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    """Export audit trail as CSV for auditor handoff"""
    query = {}
    if document_type:
        query["document_type"] = document_type
    if action:
        query["action"] = action
    if date_from:
        query.setdefault("timestamp", {})["$gte"] = date_from
    if date_to:
        query.setdefault("timestamp", {})["$lte"] = date_to + "T23:59:59"

    entries = await db.audit_trail.find(query, {"_id": 0}).sort("timestamp", -1).to_list(50000)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Timestamp", "User", "Action", "Document Type",
        "Document Number", "Document ID", "Changes", "Notes"
    ])
    for e in entries:
        changes_str = "; ".join(
            f"{c['field']}: {c.get('old_value', '')} -> {c.get('new_value', '')}"
            for c in e.get("changes", [])
        ) if e.get("changes") else ""
        writer.writerow([
            e.get("timestamp", ""),
            e.get("user", ""),
            e.get("action", ""),
            e.get("document_type", ""),
            e.get("document_number", ""),
            e.get("document_id", ""),
            changes_str,
            e.get("notes", ""),
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_trail.csv"},
    )
