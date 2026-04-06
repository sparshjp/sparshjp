# Kairos Accounting - API Routes for CRM Module
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/crm", tags=["CRM"])

# Will be set by main server
db = None
ai_orchestrator = None

def set_db(database):
    global db
    db = database

def set_ai_orchestrator(orchestrator):
    global ai_orchestrator
    ai_orchestrator = orchestrator

# ==================== LEADS ====================
@router.post("/leads")
async def create_lead(data: dict):
    """Create lead from AI prompt or manual entry"""
    lead = {
        "id": str(uuid.uuid4()),
        "lead_name": data.get("lead_name"),
        "company_name": data.get("company_name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "source": data.get("source", "AI Conversation"),
        "status": data.get("status", "Open"),
        "industry": data.get("industry"),
        "requirement": data.get("requirement"),
        "ai_score": data.get("ai_score"),
        "conversation_log": data.get("conversation_log"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.leads.insert_one(lead)
    return {**lead, "_id": None}

@router.get("/leads")
async def get_leads(status: Optional[str] = None, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    leads = await db.leads.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return leads

@router.get("/leads/{lead_id}")
async def get_lead(lead_id: str):
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/leads/{lead_id}")
async def update_lead(lead_id: str, data: dict):
    result = await db.leads.update_one({"id": lead_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead updated"}

@router.post("/leads/{lead_id}/qualify")
async def qualify_lead(lead_id: str):
    """AI qualifies lead with BANT scoring"""
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if ai_orchestrator:
        qualification = await ai_orchestrator.qualify_lead(lead)
        await db.leads.update_one({"id": lead_id}, {"$set": {"ai_score": qualification.get("qualification_score")}})
        return qualification
    return {"ai_score": 50, "message": "AI orchestrator not available"}

@router.post("/leads/{lead_id}/convert")
async def convert_lead_to_customer(lead_id: str):
    """Convert qualified lead to customer"""
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    customer = {
        "id": str(uuid.uuid4()),
        "customer_name": lead.get("company_name") or lead.get("lead_name"),
        "customer_type": "Company",
        "customer_group": "Commercial",
        "territory": "India",
        "created_from_lead": lead_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.customers.insert_one(customer)
    await db.leads.update_one({"id": lead_id}, {"$set": {"status": "Converted"}})
    return customer

# ==================== OPPORTUNITIES ====================
@router.post("/opportunities")
async def create_opportunity(data: dict):
    opp = {
        "id": str(uuid.uuid4()),
        "opportunity_from": data.get("opportunity_from", "Lead"),
        "party_name": data.get("party_name"),
        "expected_closing": data.get("expected_closing"),
        "probability": data.get("probability", 50.0),
        "opportunity_amount": data.get("opportunity_amount", 0.0),
        "status": data.get("status", "Open"),
        "items": data.get("items", []),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.opportunities.insert_one(opp)
    return {**opp, "_id": None}

@router.get("/opportunities")
async def get_opportunities(status: Optional[str] = None, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    opps = await db.opportunities.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return opps

# ==================== CUSTOMERS ====================
@router.post("/customers")
async def create_customer(data: dict):
    customer = {
        "id": str(uuid.uuid4()),
        "customer_name": data.get("customer_name"),
        "customer_type": data.get("customer_type", "Company"),
        "customer_group": data.get("customer_group", "Commercial"),
        "territory": data.get("territory", "India"),
        "gstin": data.get("gstin"),
        "pan": data.get("pan"),
        "billing_address": data.get("billing_address"),
        "shipping_address": data.get("shipping_address"),
        "credit_limit": data.get("credit_limit", 0.0),
        "payment_terms": data.get("payment_terms"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.customers.insert_one(customer)
    return {**customer, "_id": None}

@router.get("/customers")
async def get_customers(limit: int = 100):
    customers = await db.customers.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return customers

@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer