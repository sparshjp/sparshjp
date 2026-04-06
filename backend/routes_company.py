# Company Settings & Reporting AI Routes
from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime, timezone
import json, uuid, os, logging
import audit_trail

router = APIRouter()
db = None
EMERGENT_KEY = None

def set_db(database):
    global db
    db = database

def set_key(key):
    global EMERGENT_KEY
    EMERGENT_KEY = key


# ═══════════════════════════════════════════════
# COMPANY SETTINGS
# ═══════════════════════════════════════════════

LOGO_DIR = "/app/backend/uploads"
os.makedirs(LOGO_DIR, exist_ok=True)

@router.get("/settings")
async def get_company_settings():
    doc = await db.company_settings.find_one({}, {"_id": 0})
    if not doc:
        return {"exists": False}
    doc["exists"] = True
    return doc

@router.put("/settings")
async def update_company_settings(data: dict):
    old_doc = await db.company_settings.find_one({}, {"_id": 0})
    data.pop("_id", None)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.company_settings.update_one({}, {"$set": data}, upsert=True)
    changes = audit_trail.compute_changes(old_doc or {}, data) if old_doc else []
    action = audit_trail.ACTION_UPDATE if old_doc else audit_trail.ACTION_CREATE
    await audit_trail.log_audit(action, audit_trail.DOC_COMPANY_SETTINGS, "company_settings", "Company Settings", changes=changes, snapshot=data if not old_doc else None, notes="Company settings updated")
    return {"status": "saved"}

@router.post("/settings/logo")
async def upload_company_logo(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"company_logo_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(LOGO_DIR, filename)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 5MB")
    with open(filepath, "wb") as f:
        f.write(content)
    logo_url = f"/api/company/uploads/{filename}"
    await db.company_settings.update_one({}, {"$set": {"logo_url": logo_url, "updated_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
    return {"logo_url": logo_url}

@router.get("/uploads/{filename}")
async def serve_upload(filename: str):
    from fastapi.responses import FileResponse
    filepath = os.path.join(LOGO_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)


# ═══════════════════════════════════════════════
# CONVERSATIONAL REPORTING AI
# ═══════════════════════════════════════════════

@router.post("/ai-query")
async def reporting_ai_query(body: dict):
    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    # Gather summary stats for context
    po_count = await db.purchase_orders.count_documents({})
    so_count = await db.selling_sales_orders.count_documents({})
    inv_count = await db.selling_invoices.count_documents({})
    pi_count = await db.purchase_invoices.count_documents({})
    je_count = await db.journal_entries.count_documents({})
    vendor_count = await db.entities.count_documents({"entity_type": "vendor"})
    customer_count = await db.entities.count_documents({"entity_type": "customer"})
    item_count = await db.items.count_documents({})

    # Get vendor names, customer names
    vendors = [v["name"] async for v in db.entities.find({"entity_type": "vendor"}, {"_id": 0, "name": 1})]
    customers = [c["name"] async for c in db.entities.find({"entity_type": "customer"}, {"_id": 0, "name": 1})]
    coa_cats = await db.chart_of_accounts.find({}, {"_id": 0, "ledger_name": 1, "category": 1, "current_balance": 1}).to_list(200)

    # Get sample data structures
    sample_po = await db.purchase_orders.find_one({}, {"_id": 0})
    sample_so = await db.selling_sales_orders.find_one({}, {"_id": 0})
    sample_si = await db.selling_invoices.find_one({}, {"_id": 0})
    sample_pi = await db.purchase_invoices.find_one({}, {"_id": 0})
    sample_je = await db.journal_entries.find_one({}, {"_id": 0})

    coa_summary = json.dumps(sorted([{"name": c["ledger_name"], "cat": c["category"], "bal": c.get("current_balance",0)} for c in coa_cats], key=lambda x: abs(x["bal"]), reverse=True)[:20])

    system_msg = f"""You are the Reporting AI for Kairos AI ERP (PolyMerx Specialty Chemicals Pvt. Ltd.).

DATABASE OVERVIEW:
- purchase_orders: {po_count} docs. Fields: {list(sample_po.keys()) if sample_po else 'empty'}
- selling_sales_orders: {so_count} docs. Fields: {list(sample_so.keys()) if sample_so else 'empty'}
- selling_invoices: {inv_count} docs. Fields: {list(sample_si.keys()) if sample_si else 'empty'}
- purchase_invoices: {pi_count} docs. Fields: {list(sample_pi.keys()) if sample_pi else 'empty'}
- journal_entries: {je_count} docs. Fields: {list(sample_je.keys()) if sample_je else 'empty'}
- entities: {vendor_count} vendors, {customer_count} customers
- items: {item_count} items
- chart_of_accounts: {len(coa_cats)} ledgers

VENDORS: {json.dumps(vendors)}
CUSTOMERS: {json.dumps(customers)}
CoA SUMMARY (top 20 by balance): {coa_summary}

SAMPLE purchase_order: {json.dumps(sample_po, default=str)[:800] if sample_po else 'none'}
SAMPLE selling_sales_order: {json.dumps(sample_so, default=str)[:800] if sample_so else 'none'}
SAMPLE selling_invoice: {json.dumps(sample_si, default=str)[:800] if sample_si else 'none'}

Your job: answer the user's reporting question by writing a MongoDB aggregation pipeline.

Return ONLY this JSON:
{{
  "title": "Report title",
  "description": "Brief explanation of what the report shows",
  "collection": "collection_name to query",
  "pipeline": [ <MongoDB aggregation pipeline stages> ],
  "columns": [ {{"key": "field_name", "label": "Display Label", "format": "text|number|currency|date|percent"}} ],
  "chart": {{
    "type": "bar|line|pie|none",
    "x_key": "field for X axis",
    "y_key": "field for Y axis",
    "label_key": "field for labels (pie chart)"
  }},
  "summary_text": "One-line summary of the insight"
}}

RULES:
- Pipeline must be valid MongoDB aggregation. Use $match, $group, $sort, $project, $limit, $unwind etc.
- For currency format, numbers will be formatted as INR.
- For "top N" queries, always add $sort and $limit.
- For date filtering, dates are stored as ISO strings like "2026-04-01".
- grand_total fields are numbers. items arrays contain objects with item_code, item_name, qty, rate, amount.
- For vendor purchase value: group purchase_orders by vendor, sum grand_total.
- For customer revenue: group selling_invoices by customer, sum grand_total.
- Chart type "none" if data is a single summary row.
- Return ONLY valid JSON. No markdown fences."""

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"report-{uuid.uuid4()}",
            system_message=system_msg
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        raw = await chat.send_message(UserMessage(text=question))

        # Parse the AI response
        from ai_orchestrator import clean_json_response
        parsed = clean_json_response(raw)

        # Execute the pipeline
        collection_name = parsed.get("collection", "")
        pipeline = parsed.get("pipeline", [])

        if not collection_name or not pipeline:
            return {**parsed, "data": [], "error": "AI could not generate a valid query"}

        coll = db[collection_name]
        results = await coll.aggregate(pipeline).to_list(500)

        # Clean ObjectIds from results
        clean_results = []
        for r in results:
            clean = {}
            for k, v in r.items():
                if k == "_id" and not isinstance(v, (str, int, float)):
                    continue
                clean[k] = v
            clean_results.append(clean)

        return {
            "title": parsed.get("title", "Report"),
            "description": parsed.get("description", ""),
            "columns": parsed.get("columns", []),
            "chart": parsed.get("chart", {"type": "none"}),
            "data": clean_results,
            "summary_text": parsed.get("summary_text", ""),
            "query_info": {"collection": collection_name, "pipeline_stages": len(pipeline)}
        }

    except Exception as e:
        logging.error(f"Reporting AI error: {e}")
        raise HTTPException(status_code=500, detail=f"Reporting AI failed: {str(e)}")
