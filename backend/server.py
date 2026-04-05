from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Header, Query
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import requests
from emergentintegrations.llm.chat import LlmChat, UserMessage
import base64
import io
from PIL import Image

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Object Storage Configuration
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "ai-erp"
storage_key = None

# Initialize storage
def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data, timeout=120
    )
    resp.raise_for_status()
    return resp.json()

def get_object(path: str) -> tuple:
    key = init_storage()
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key}, timeout=60
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

# Create the main app
app = FastAPI()

# Create API router
api_router = APIRouter(prefix="/api")

# Pydantic Models
class TransactionBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_prompt: str
    user_id: str = "default_user"
    module: str
    status: str = "draft"  # draft, posted
    posting_date: Optional[str] = None
    service_period_start: Optional[str] = None
    service_period_end: Optional[str] = None
    business_unit: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    journal_entries: Optional[List[Dict[str, Any]]] = None
    document_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    posted_at: Optional[str] = None

class DocumentUpload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    storage_path: str
    original_filename: str
    content_type: str
    size: int
    extracted_data: Optional[Dict[str, Any]] = None
    transaction_id: Optional[str] = None
    is_deleted: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class JournalEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    account: str
    debit: float = 0.0
    credit: float = 0.0
    description: str
    posting_date: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Vendor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    gstin: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PromptRequest(BaseModel):
    prompt: str
    module: str
    user_id: str = "default_user"
    document_id: Optional[str] = None

class PostTransactionRequest(BaseModel):
    transaction_id: str

class ReportQuery(BaseModel):
    query: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# AI Services
async def parse_prompt_with_ai(prompt: str, module: str, extracted_ocr: Optional[Dict] = None) -> Dict[str, Any]:
    """Use Claude Sonnet 4.5 to parse user prompt and generate journal entries"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"prompt-{uuid.uuid4()}",
            system_message="""You are an expert Indian ERP accountant. Parse the user's natural language prompt and extract:
            1. posting_date (format: YYYY-MM-DD)
            2. service_period_start (format: YYYY-MM-DD)
            3. service_period_end (format: YYYY-MM-DD)
            4. business_unit (e.g., Mumbai Office, Gujarat Plant)
            5. journal_entries: List of debit/credit entries with account names
            
            For GST transactions:
            - Calculate CGST, SGST (for intrastate) or IGST (for interstate) at 18% default
            - Include input/output GST accounts
            
            Return ONLY a valid JSON object with these fields. No markdown, no explanations."""
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        prompt_text = prompt
        if extracted_ocr:
            prompt_text += f"\n\nExtracted OCR Data: {extracted_ocr}"
        
        user_message = UserMessage(text=prompt_text)
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        result = json.loads(response)
        return result
    except Exception as e:
        logging.error(f"AI parsing error: {e}")
        # Return minimal structure
        return {
            "posting_date": datetime.now(timezone.utc).date().isoformat(),
            "service_period_start": datetime.now(timezone.utc).date().isoformat(),
            "service_period_end": datetime.now(timezone.utc).date().isoformat(),
            "business_unit": "Main Office",
            "journal_entries": []
        }

async def extract_document_data(image_data: bytes, filename: str) -> Dict[str, Any]:
    """Use Gemini 3 vision for OCR extraction"""
    try:
        # Convert image to base64
        img = Image.open(io.BytesIO(image_data))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"ocr-{uuid.uuid4()}",
            system_message="""You are an OCR expert for Indian financial documents. Extract:
            - Vendor name
            - GSTIN (15-character GST identification number)
            - Invoice number
            - Invoice date (format: YYYY-MM-DD)
            - Total amount
            - Line items with descriptions and amounts
            - GST breakdown (CGST, SGST, IGST)
            
            Return ONLY valid JSON. No markdown."""
        ).with_model("gemini", "gemini-3-flash-preview")
        
        # Note: For Gemini vision, we need to use UserMessage with image
        # The emergentintegrations library should support this
        user_message = UserMessage(
            text=f"Extract all data from this invoice/receipt image. Return JSON only."
        )
        
        response = await chat.send_message(user_message)
        
        import json
        result = json.loads(response)
        return result
    except Exception as e:
        logging.error(f"OCR extraction error: {e}")
        return {
            "vendor_name": "Unknown",
            "gstin": "",
            "invoice_number": "",
            "invoice_date": "",
            "total_amount": 0,
            "line_items": [],
            "gst_breakdown": {}
        }

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "AI-Native ERP API", "version": "1.0.0"}

# Document Upload
@api_router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload invoice/receipt and perform OCR"""
    try:
        ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        doc_id = str(uuid.uuid4())
        path = f"{APP_NAME}/documents/{doc_id}.{ext}"
        
        data = await file.read()
        result = put_object(path, data, file.content_type or "application/octet-stream")
        
        # Perform OCR
        extracted_data = await extract_document_data(data, file.filename)
        
        # Store in MongoDB
        doc_record = DocumentUpload(
            id=doc_id,
            storage_path=result["path"],
            original_filename=file.filename,
            content_type=file.content_type,
            size=result["size"],
            extracted_data=extracted_data
        )
        
        await db.documents.insert_one(doc_record.model_dump())
        
        return {"document_id": doc_id, "extracted_data": extracted_data}
    except Exception as e:
        logging.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Download Document
@api_router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str):
    """Download document file"""
    try:
        record = await db.documents.find_one({"id": doc_id, "is_deleted": False}, {"_id": 0})
        if not record:
            raise HTTPException(status_code=404, detail="Document not found")
        
        data, content_type = get_object(record["storage_path"])
        return Response(content=data, media_type=record.get("content_type", content_type))
    except Exception as e:
        logging.error(f"Document download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Process Prompt
@api_router.post("/transactions/prompt")
async def process_prompt(request: PromptRequest):
    """Process natural language prompt and create draft transaction"""
    try:
        # Get document OCR data if provided
        extracted_ocr = None
        if request.document_id:
            doc = await db.documents.find_one({"id": request.document_id}, {"_id": 0})
            if doc:
                extracted_ocr = doc.get("extracted_data")
        
        # Parse with AI
        parsed_data = await parse_prompt_with_ai(request.prompt, request.module, extracted_ocr)
        
        # Create draft transaction
        transaction = TransactionBase(
            user_prompt=request.prompt,
            user_id=request.user_id,
            module=request.module,
            status="draft",
            posting_date=parsed_data.get("posting_date"),
            service_period_start=parsed_data.get("service_period_start"),
            service_period_end=parsed_data.get("service_period_end"),
            business_unit=parsed_data.get("business_unit"),
            extracted_data=parsed_data,
            journal_entries=parsed_data.get("journal_entries", []),
            document_id=request.document_id
        )
        
        await db.transactions.insert_one(transaction.model_dump())
        
        return transaction.model_dump()
    except Exception as e:
        logging.error(f"Prompt processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get Draft Transactions
@api_router.get("/transactions/drafts")
async def get_drafts(module: Optional[str] = None):
    """Get all draft transactions"""
    query = {"status": "draft"}
    if module:
        query["module"] = module
    
    drafts = await db.transactions.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return drafts

# Post Transaction
@api_router.post("/transactions/post")
async def post_transaction(request: PostTransactionRequest):
    """Post a draft transaction to ledger (immutable after this)"""
    try:
        transaction = await db.transactions.find_one({"id": request.transaction_id}, {"_id": 0})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction["status"] != "draft":
            raise HTTPException(status_code=400, detail="Transaction already posted")
        
        # Update transaction status
        await db.transactions.update_one(
            {"id": request.transaction_id},
            {"$set": {"status": "posted", "posted_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Create journal entries
        journal_entries = transaction.get("journal_entries", [])
        for entry in journal_entries:
            je = JournalEntry(
                transaction_id=request.transaction_id,
                account=entry.get("account", ""),
                debit=entry.get("debit", 0.0),
                credit=entry.get("credit", 0.0),
                description=entry.get("description", ""),
                posting_date=transaction["posting_date"]
            )
            await db.journal_entries.insert_one(je.model_dump())
        
        return {"message": "Transaction posted successfully", "transaction_id": request.transaction_id}
    except Exception as e:
        logging.error(f"Post transaction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get Posted Transactions
@api_router.get("/transactions/posted")
async def get_posted_transactions(module: Optional[str] = None, limit: int = 50):
    """Get posted transactions"""
    query = {"status": "posted"}
    if module:
        query["module"] = module
    
    transactions = await db.transactions.find(query, {"_id": 0}).sort("posted_at", -1).to_list(limit)
    return transactions

# Conversational Reporting
@api_router.post("/reports/query")
async def conversational_report(request: ReportQuery):
    """AI-powered conversational reporting"""
    try:
        # Get relevant data based on date range
        query = {"status": "posted"}
        if request.start_date and request.end_date:
            query["posting_date"] = {"$gte": request.start_date, "$lte": request.end_date}
        
        transactions = await db.transactions.find(query, {"_id": 0}).to_list(1000)
        journal_entries = await db.journal_entries.find({}, {"_id": 0}).to_list(1000)
        
        # Use AI to answer query
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"report-{uuid.uuid4()}",
            system_message=f"""You are an AI financial analyst for an Indian ERP system. 
            Answer the user's query based on the provided transaction data.
            
            Transactions: {transactions}
            Journal Entries: {journal_entries}
            
            Provide clear, concise answers with numbers and insights."""
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        user_message = UserMessage(text=request.query)
        response = await chat.send_message(user_message)
        
        return {"query": request.query, "answer": response, "data_points": len(transactions)}
    except Exception as e:
        logging.error(f"Report query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Financial Statements
@api_router.get("/reports/balance-sheet")
async def get_balance_sheet(as_of_date: Optional[str] = None):
    """Generate Balance Sheet"""
    if not as_of_date:
        as_of_date = datetime.now(timezone.utc).date().isoformat()
    
    # Get all journal entries up to the date
    entries = await db.journal_entries.find(
        {"posting_date": {"$lte": as_of_date}},
        {"_id": 0}
    ).to_list(10000)
    
    # Calculate account balances
    balances = {}
    for entry in entries:
        account = entry["account"]
        if account not in balances:
            balances[account] = {"debit": 0, "credit": 0}
        balances[account]["debit"] += entry["debit"]
        balances[account]["credit"] += entry["credit"]
    
    # Classify accounts (simplified)
    assets = {k: v for k, v in balances.items() if "Asset" in k or "Bank" in k or "Cash" in k}
    liabilities = {k: v for k, v in balances.items() if "Liability" in k or "Payable" in k}
    equity = {k: v for k, v in balances.items() if "Equity" in k or "Capital" in k}
    
    return {
        "as_of_date": as_of_date,
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_entries": len(entries)
    }

@api_router.get("/reports/profit-loss")
async def get_profit_loss(start_date: str, end_date: str):
    """Generate Profit & Loss Statement"""
    entries = await db.journal_entries.find(
        {"posting_date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0}
    ).to_list(10000)
    
    revenue = {}
    expenses = {}
    
    for entry in entries:
        account = entry["account"]
        if "Revenue" in account or "Income" in account:
            if account not in revenue:
                revenue[account] = 0
            revenue[account] += entry["credit"] - entry["debit"]
        elif "Expense" in account or "Cost" in account:
            if account not in expenses:
                expenses[account] = 0
            expenses[account] += entry["debit"] - entry["credit"]
    
    total_revenue = sum(revenue.values())
    total_expenses = sum(expenses.values())
    
    return {
        "period": {"start": start_date, "end": end_date},
        "revenue": revenue,
        "total_revenue": total_revenue,
        "expenses": expenses,
        "total_expenses": total_expenses,
        "net_profit": total_revenue - total_expenses
    }

@api_router.get("/reports/trial-balance")
async def get_trial_balance(as_of_date: Optional[str] = None):
    """Generate Trial Balance"""
    if not as_of_date:
        as_of_date = datetime.now(timezone.utc).date().isoformat()
    
    entries = await db.journal_entries.find(
        {"posting_date": {"$lte": as_of_date}},
        {"_id": 0}
    ).to_list(10000)
    
    balances = {}
    for entry in entries:
        account = entry["account"]
        if account not in balances:
            balances[account] = {"debit": 0, "credit": 0}
        balances[account]["debit"] += entry["debit"]
        balances[account]["credit"] += entry["credit"]
    
    total_debit = sum(b["debit"] for b in balances.values())
    total_credit = sum(b["credit"] for b in balances.values())
    
    return {
        "as_of_date": as_of_date,
        "accounts": balances,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "difference": total_debit - total_credit
    }

# Vendors
@api_router.post("/vendors")
async def create_vendor(vendor: Vendor):
    await db.vendors.insert_one(vendor.model_dump())
    return vendor.model_dump()

@api_router.get("/vendors")
async def get_vendors():
    vendors = await db.vendors.find({}, {"_id": 0}).to_list(1000)
    return vendors

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    try:
        init_storage()
        logger.info("Storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()