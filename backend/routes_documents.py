"""Document Management — File attachments for transactions, contracts, projects."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from datetime import datetime, timezone
import uuid
import os
import base64

router = APIRouter(prefix="/documents")
db = None
UPLOAD_DIR = "/app/backend/uploads/documents"

def set_db(database):
    global db
    db = database
    os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
async def list_documents(entity_type: str = None, entity_id: str = None):
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    if entity_id:
        query["entity_id"] = entity_id
    return await db.documents.find(query, {"_id": 0}).sort("uploaded_at", -1).to_list(200)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), entity_type: str = Form("general"), entity_id: str = Form(""), entity_name: str = Form(""), category: str = Form("general")):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    file_id = str(uuid.uuid4())[:12]
    ext = os.path.splitext(file.filename or "")[1] or ".bin"
    filename = f"{file_id}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    doc = {
        "id": file_id,
        "filename": file.filename,
        "stored_filename": filename,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "category": category,
        "content_type": file.content_type or "application/octet-stream",
        "size_bytes": len(content),
        "size_display": f"{len(content) / 1024:.1f} KB" if len(content) < 1048576 else f"{len(content) / 1048576:.1f} MB",
        "download_url": f"/api/documents/download/{file_id}",
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.documents.insert_one(doc)
    doc.pop("_id", None)
    # Event: Document uploaded → Compliance access log
    import module_events
    await module_events.on_document_uploaded(doc)
    return doc

@router.get("/download/{doc_id}")
async def download_document(doc_id: str):
    from fastapi.responses import FileResponse
    doc = await db.documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    filepath = os.path.join(UPLOAD_DIR, doc["stored_filename"])
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(filepath, filename=doc["filename"], media_type=doc.get("content_type", "application/octet-stream"))

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    doc = await db.documents.find_one({"id": doc_id}, {"_id": 0})
    if doc:
        filepath = os.path.join(UPLOAD_DIR, doc.get("stored_filename", ""))
        if os.path.isfile(filepath):
            os.remove(filepath)
    await db.documents.delete_one({"id": doc_id})
    return {"status": "ok"}

@router.get("/categories")
async def get_categories():
    return ["contract", "purchase_order", "invoice", "receipt", "sow", "msa", "nda", "proposal", "timesheet", "expense_receipt", "general"]

@router.get("/stats")
async def document_stats():
    pipeline = [{"$group": {"_id": "$entity_type", "count": {"$sum": 1}, "total_size": {"$sum": "$size_bytes"}}}]
    stats = await db.documents.aggregate(pipeline).to_list(20)
    return {s["_id"]: {"count": s["count"], "total_size_mb": round(s["total_size"] / 1048576, 2)} for s in stats if s["_id"]}
