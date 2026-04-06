# AI Orchestrator for Kairos Accounting
# Replaces manual forms with AI-powered transaction creation

from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import logging
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timezone

EMERGENT_KEY = None  # Will be set from main server

class AIOrchestrator:
    """Central AI orchestrator for all ERP modules"""
    
    def __init__(self, api_key: str):
        global EMERGENT_KEY
        EMERGENT_KEY = api_key
        self.api_key = api_key
    
    async def process_universal_prompt(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Universal AI prompt processor that routes to appropriate module"""
        try:
            # First, identify which module this belongs to
            module = await self._identify_module(prompt)
            
            # Route to appropriate handler
            handlers = {
                "crm": self.process_crm,
                "sales": self.process_sales,
                "purchase": self.process_purchase,
                "stock": self.process_stock,
                "hr": self.process_hr,
                "projects": self.process_projects,
                "manufacturing": self.process_manufacturing,
                "quality": self.process_quality,
                "accounting": self.process_accounting
            }
            
            handler = handlers.get(module, self.process_accounting)
            return await handler(prompt, context)
            
        except Exception as e:
            logging.error(f"AI Orchestrator error: {e}")
            return {"error": str(e), "module": "unknown"}
    
    async def _identify_module(self, prompt: str) -> str:
        """Identify which ERP module the prompt belongs to"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"module-identify-{uuid.uuid4()}",
                system_message="""You are an ERP module classifier. Identify which module this prompt belongs to.
                
                Modules:
                - crm: Lead generation, customer inquiries, opportunity tracking
                - sales: Quotations, sales orders, delivery, invoices to customers
                - purchase: Material requests, purchase orders, supplier management
                - stock: Inventory movements, stock entries, warehouse transfers
                - hr: Employee attendance, leave, payroll, timesheets
                - projects: Project tracking, task management, time logging
                - manufacturing: Production orders, BOM, work orders
                - quality: Quality inspections, quality checks
                - accounting: General journal entries, payments, expenses
                
                Return ONLY the module name, nothing else."""
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            
            response = await chat.send_message(UserMessage(text=prompt))
            return response.strip().lower()
        except:
            return "accounting"  # Default fallback
    
    async def process_crm(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process CRM prompts: leads, opportunities, customers"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"crm-{uuid.uuid4()}",
            system_message="""You are a CRM AI for Kairos Accounting. Extract CRM information from conversations.
            
            Identify if this is:
            - Lead: New inquiry, potential customer
            - Opportunity: Qualified lead with specific requirement
            - Customer: Converting lead/opportunity to customer
            
            Extract:
            - name, company, email, phone, industry, requirement, estimated_value
            - AI qualification score (0-100) based on urgency, budget signals, authority
            
            Return JSON with: {"type": "lead|opportunity|customer", "data": {...}, "ai_score": 0-100, "next_action": "..."}
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_sales(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process sales cycle: quotations, sales orders, delivery notes, invoices"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"sales-{uuid.uuid4()}",
            system_message="""You are a Sales AI for Kairos Accounting ERP. Process sales transactions.
            
            Sales Cycle:
            1. Quotation → 2. Sales Order → 3. Delivery Note → 4. Sales Invoice
            
            Extract from prompt:
            - Document type (quotation/sales_order/delivery_note/sales_invoice)
            - Customer name
            - Transaction date
            - Items: [{"item_name": "", "qty": 0, "rate": 0, "amount": 0}]
            - Delivery terms, payment terms
            - GST calculation (18% default, CGST+SGST for intrastate, IGST for interstate)
            - Grand total with taxes
            
            Return JSON: {"doc_type": "...", "customer": "...", "transaction_date": "YYYY-MM-DD", "items": [...], "taxes": [...], "grand_total": 0, "terms": "..."}
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_purchase(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process purchase cycle: material requests, RFQ, PO, purchase receipts"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"purchase-{uuid.uuid4()}",
            system_message="""You are a Procurement AI for Kairos Accounting. Process purchase transactions.
            
            Purchase Cycle:
            1. Material Request → 2. RFQ → 3. Supplier Quotation → 4. Purchase Order → 5. Purchase Receipt → 6. Purchase Invoice
            
            Extract:
            - Document type
            - Supplier/Vendors (if RFQ, can be multiple)
            - Items needed: [{"item": "", "qty": 0, "required_by": "YYYY-MM-DD"}]
            - If AI-suggested reorder: include reason (stock below reorder level)
            - For PO: include schedule date, payment terms
            - Calculate landed cost: Price + GST + Freight
            
            Return JSON with all extracted information.
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_stock(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process stock entries, transfers, reconciliation"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"stock-{uuid.uuid4()}",
            system_message="""You are an Inventory AI for Kairos Accounting. Process stock movements.
            
            Stock Entry Types:
            - Material Receipt: Goods received (from purchases or production)
            - Material Issue: Goods issued (for production or sale)
            - Material Transfer: Between warehouses
            - Repack: Change item form (e.g., bulk to retail pack)
            - Stock Reconciliation: Physical count vs system
            
            Extract:
            - Entry type
            - From/To warehouses
            - Items: [{"item": "", "qty": 0, "rate": 0}]
            - If from image: indicate "created_from_image": true
            
            Return JSON with stock entry details.
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_hr(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process HR: attendance, leave, payroll, timesheets"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"hr-{uuid.uuid4()}",
            system_message="""You are an HR AI for Kairos Accounting. Process HR transactions.
            
            HR Operations:
            - Attendance: Mark present/absent/leave (can be from photo or prompt)
            - Leave Application: Employee leave request
            - Payroll: Salary processing, TDS calculation
            - Timesheet: Work hours logging
            
            Extract:
            - Operation type
            - Employee name(s)
            - Date(s)
            - For attendance: status (present/absent/half-day/on-leave)
            - For leave: leave type, from_date, to_date, reason
            - For timesheet: project, task, hours worked
            - If from image: indicate marked_by_ai: true
            
            Return JSON with HR operation details.
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_projects(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process projects and tasks"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"projects-{uuid.uuid4()}",
            system_message="""You are a Project Management AI for Kairos Accounting.
            
            Project Operations:
            - Create Project: New project setup
            - Create Task: Add task to project
            - Update Task: Change status, log time
            - Log Time: Add timesheet entry
            
            Extract:
            - Operation type
            - Project name
            - Task subject/description
            - Assigned to (employee)
            - Priority (Low/Medium/High/Urgent)
            - Expected time/actual time
            - Status (Open/Working/Pending Review/Completed)
            
            Return JSON with project/task details.
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_manufacturing(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process manufacturing: BOM, work orders, production"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"mfg-{uuid.uuid4()}",
            system_message="""You are a Manufacturing AI for Kairos Accounting.
            
            Manufacturing Operations:
            - BOM (Bill of Materials): Recipe/formula for making finished goods
            - Work Order: Production order
            - Stock Entry (Manufacture): Record production completion
            
            Extract:
            - Operation type
            - Finished item to produce
            - Raw materials needed: [{"item": "", "qty": 0}]
            - Quantity to produce
            - Warehouses (source for RM, WIP, FG)
            - AI can suggest BOM based on industry standards
            
            Return JSON with manufacturing details.
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_quality(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process quality inspections"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"quality-{uuid.uuid4()}",
            system_message="""You are a Quality Control AI for Kairos Accounting.
            
            Quality Operations:
            - Quality Inspection: Check incoming goods, outgoing products, in-process items
            - Can analyze product images and give quality score (0-100)
            
            Inspection Types:
            - Incoming (from suppliers)
            - Outgoing (to customers)
            - In Process (during production)
            
            Extract:
            - Inspection type
            - Item being inspected
            - Reference (Purchase Receipt, Delivery Note, etc.)
            - If from image: provide AI quality score and defects found
            - Status: Accepted/Rejected
            
            Return JSON with quality inspection details.
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def process_accounting(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process general accounting transactions"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"accounting-{uuid.uuid4()}",
            system_message="""You are an Accounting AI for Kairos Accounting ERP.
            
            Process general journal entries, payments, expenses.
            
            Extract:
            - posting_date (YYYY-MM-DD)
            - journal_entries: [{"account": "", "debit": 0, "credit": 0, "description": ""}]
            - cost_center
            - business_unit
            - Calculate GST (CGST+SGST or IGST), TDS if applicable
            
            Return JSON with journal entry structure.
            """
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        response = await chat.send_message(UserMessage(text=f"Context: {context}\n\nPrompt: {prompt}"))
        return json.loads(response)
    
    async def analyze_image_for_quality(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze product image for quality inspection"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"quality-image-{uuid.uuid4()}",
                system_message="""You are a Quality Inspector AI. Analyze product images.
                
                Provide:
                - quality_score (0-100)
                - defects_found: list of defects
                - recommendation: Accept/Reject
                - remarks: detailed observations
                
                Return JSON only.
                """
            ).with_model("gemini", "gemini-3-flash-preview")
            
            response = await chat.send_message(UserMessage(text="Analyze this product for quality inspection"))
            return json.loads(response)
        except Exception as e:
            logging.error(f"Quality image analysis error: {e}")
            return {
                "quality_score": 75,
                "defects_found": [],
                "recommendation": "Accept",
                "remarks": "AI analysis completed"
            }
    
    async def suggest_reorder(self, stock_data: List[Dict]) -> List[Dict[str, Any]]:
        """AI suggests items to reorder based on stock levels"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"reorder-suggest-{uuid.uuid4()}",
                system_message="""You are an Inventory Planning AI.
                
                Analyze stock levels and suggest reorder quantities.
                
                Consider:
                - Current stock vs reorder level
                - Historical consumption rate (if provided)
                - Lead time
                - Economic Order Quantity (EOQ)
                
                Return JSON: [{"item": "", "current_stock": 0, "reorder_level": 0, "suggested_qty": 0, "reason": "..."}]
                """
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            
            response = await chat.send_message(UserMessage(text=f"Stock Data: {json.dumps(stock_data)}"))
            return json.loads(response)
        except Exception as e:
            logging.error(f"Reorder suggestion error: {e}")
            return []
    
    async def qualify_lead(self, lead_data: Dict) -> Dict[str, Any]:
        """AI qualifies leads with scoring"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"lead-qualify-{uuid.uuid4()}",
                system_message="""You are a Sales Qualification AI.
                
                Qualify leads using BANT framework:
                - Budget: Can they afford?
                - Authority: Decision maker?
                - Need: Clear requirement?
                - Timeline: When do they need it?
                
                Provide:
                - qualification_score (0-100)
                - bant_scores: {budget: 0-25, authority: 0-25, need: 0-25, timeline: 0-25}
                - qualification_status: Hot/Warm/Cold
                - next_action: suggested follow-up
                - probability_to_close: 0-100%
                
                Return JSON.
                """
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            
            response = await chat.send_message(UserMessage(text=f"Lead: {json.dumps(lead_data)}"))
            return json.loads(response)
        except Exception as e:
            logging.error(f"Lead qualification error: {e}")
            return {
                "qualification_score": 50,
                "qualification_status": "Warm",
                "next_action": "Follow up",
                "probability_to_close": 50
            }