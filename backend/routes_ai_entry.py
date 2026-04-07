"""AI-powered data entry parser. Takes a natural language prompt + module schema
and returns structured JSON fields for any ERP module."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid
import json
import logging
import asyncio

router = APIRouter(prefix="/ai", tags=["AI Entry"])
db = None
EMERGENT_KEY = None
ANTHROPIC_API_KEY = ""
OPENAI_API_KEY = ""

def set_config(key, database, anthropic_key="", openai_key=""):
    global EMERGENT_KEY, db, ANTHROPIC_API_KEY, OPENAI_API_KEY
    EMERGENT_KEY = key
    db = database
    ANTHROPIC_API_KEY = anthropic_key
    OPENAI_API_KEY = openai_key

MODULE_SCHEMAS = {
    "project": {
        "fields": {
            "name": {"type": "string", "required": True, "label": "Project Name"},
            "client": {"type": "string", "required": True, "label": "Client"},
            "type": {"type": "enum", "options": ["Fixed-Price", "T&M", "T&M Export", "Fixed-Price Export", "Fixed-Price Milestone", "Monthly Retainer", "Non-billable"], "default": "T&M", "label": "Project Type"},
            "pm": {"type": "string", "required": False, "label": "Project Manager"},
            "currency": {"type": "enum", "options": ["INR", "USD", "GBP", "EUR"], "default": "INR", "label": "Currency"},
            "value_inr": {"type": "number", "required": False, "label": "Value (INR)"},
            "value_usd": {"type": "number", "required": False, "label": "Value (Foreign Currency)"},
            "billing": {"type": "enum", "options": ["Monthly", "Milestone", "Quarterly"], "default": "Monthly", "label": "Billing Cycle"},
            "duration": {"type": "string", "required": False, "label": "Duration"},
            "team_names": {"type": "array", "required": False, "label": "Team Members"},
            "milestones": {"type": "array_of_objects", "required": False, "label": "Milestones", "fields": {"name": "string", "value": "number", "date": "date"}},
        },
        "example": "Create T&M project for Acme Corp, $120K, 6 months, PM is Priya, team: Raj, Ankit, Meena"
    },
    "timesheet": {
        "fields": {
            "employee_id": {"type": "string", "required": True, "label": "Employee ID"},
            "employee_name": {"type": "string", "required": True, "label": "Employee Name"},
            "week": {"type": "string", "required": True, "label": "Week (e.g. W1-Apr)"},
            "week_start": {"type": "date", "required": False, "label": "Week Start"},
            "week_end": {"type": "date", "required": False, "label": "Week End"},
            "entries": {"type": "array_of_objects", "required": True, "label": "Time Entries", "fields": {"project_id": "string", "hours": "number", "billable": "boolean", "note": "string", "rate": "number", "currency": "string"}},
            "leave_hours": {"type": "number", "required": False, "label": "Leave Hours"},
            "leave_type": {"type": "enum", "options": ["Casual", "Sick", "Comp-off", "Holiday", ""], "default": "", "label": "Leave Type"},
        },
        "example": "Log 40h for Raj (EMP-005) on PRJ-001 this week (W1-Apr), all billable at 2500/hr"
    },
    "contract": {
        "fields": {
            "title": {"type": "string", "required": True, "label": "Contract Title"},
            "client_name": {"type": "string", "required": True, "label": "Client Name"},
            "type": {"type": "enum", "options": ["msa", "sow", "nda", "amendment"], "default": "sow", "label": "Contract Type"},
            "billing_type": {"type": "enum", "options": ["fixed", "tm", "retainer"], "default": "fixed", "label": "Billing Type"},
            "start_date": {"type": "date", "required": True, "label": "Start Date"},
            "end_date": {"type": "date", "required": True, "label": "End Date"},
            "value": {"type": "number", "required": True, "label": "Contract Value"},
            "currency": {"type": "enum", "options": ["INR", "USD", "GBP", "EUR"], "default": "INR", "label": "Currency"},
            "auto_renew": {"type": "boolean", "default": False, "label": "Auto-Renew"},
            "milestones": {"type": "array_of_objects", "required": False, "label": "Milestones", "fields": {"name": "string", "amount": "number", "due_date": "date"}},
        },
        "example": "SOW for CloudMigrate with TechCorp, $200K fixed-price, Apr-Dec 2026, 3 milestones"
    },
    "approval_workflow": {
        "fields": {
            "name": {"type": "string", "required": True, "label": "Workflow Name"},
            "type": {"type": "enum", "options": ["purchase_order", "sales_invoice", "expense", "journal_entry", "leave_request", "timesheet", "budget_override"], "required": True, "label": "Document Type"},
            "threshold_amount": {"type": "number", "required": False, "default": 0, "label": "Threshold Amount"},
            "steps": {"type": "array_of_objects", "required": True, "label": "Approval Steps", "fields": {"role": "string", "label": "string"}},
        },
        "example": "PO approval: above 50K needs finance_manager, above 5L needs admin"
    },
    "approval_request": {
        "fields": {
            "type": {"type": "enum", "options": ["purchase_order", "sales_invoice", "expense", "journal_entry", "leave_request", "timesheet", "budget_override"], "required": True, "label": "Request Type"},
            "reference_name": {"type": "string", "required": True, "label": "Reference"},
            "amount": {"type": "number", "required": True, "label": "Amount"},
            "requester_name": {"type": "string", "required": True, "label": "Requester"},
            "comments": {"type": "string", "required": False, "label": "Comments"},
        },
        "example": "Submit expense claim for Raj - 45000 INR for client travel to Mumbai"
    },
    "budget": {
        "fields": {
            "name": {"type": "string", "required": True, "label": "Budget Name"},
            "type": {"type": "enum", "options": ["department", "project"], "default": "department", "label": "Budget Type"},
            "department": {"type": "string", "required": False, "label": "Department"},
            "fiscal_year": {"type": "string", "default": "2025-26", "label": "Fiscal Year"},
            "line_items": {"type": "array_of_objects", "required": True, "label": "Line Items", "fields": {"category": "string", "amount": "number"}},
        },
        "example": "Engineering dept budget FY2025-26: Salaries 80L, Cloud infra 15L, Training 5L"
    },
    "resource_allocation": {
        "fields": {
            "employee_name": {"type": "string", "required": True, "label": "Employee"},
            "project_name": {"type": "string", "required": True, "label": "Project"},
            "role": {"type": "string", "required": False, "label": "Role"},
            "allocation_pct": {"type": "number", "default": 100, "label": "Allocation %"},
            "start_date": {"type": "date", "required": False, "label": "Start Date"},
            "end_date": {"type": "date", "required": False, "label": "End Date"},
            "billable": {"type": "boolean", "default": True, "label": "Billable"},
            "bill_rate": {"type": "number", "required": False, "label": "Bill Rate/hr"},
        },
        "example": "Allocate Priya 100% to CloudMigrate as Tech Lead, billable at 3000/hr, Apr-Sep 2026"
    },
    "forex_transaction": {
        "fields": {
            "type": {"type": "enum", "options": ["invoice", "payment", "receipt"], "default": "invoice", "label": "Transaction Type"},
            "reference_name": {"type": "string", "required": True, "label": "Reference"},
            "currency": {"type": "enum", "options": ["USD", "GBP", "EUR", "AUD", "CAD", "SGD", "JPY", "AED"], "default": "USD", "label": "Currency"},
            "foreign_amount": {"type": "number", "required": True, "label": "Foreign Amount"},
            "booking_rate": {"type": "number", "required": True, "label": "Booking Rate (INR)"},
        },
        "example": "Invoice to TechCorp USD 25000 at rate 84.50"
    },
    "portal_client": {
        "fields": {
            "client_name": {"type": "string", "required": True, "label": "Client Name"},
            "contact_name": {"type": "string", "required": False, "label": "Contact Person"},
            "email": {"type": "string", "required": False, "label": "Email"},
        },
        "example": "Add TechCorp to portal, contact: John Smith, john@techcorp.com"
    },
}


PARSE_SYSTEM = """You are an ERP data entry assistant. Parse the user's natural language input into structured JSON.

RULES:
1. Return ONLY valid JSON — no markdown, no explanation, no code fences
2. Extract every field you can from the user's text
3. For missing REQUIRED fields, set value to null
4. For missing optional fields, use defaults from the schema or omit
5. For amounts like "50K" = 50000, "5L" = 500000, "2Cr" = 20000000
6. For dates, use YYYY-MM-DD format. If relative ("next month"), estimate from today
7. If user mentions a currency symbol ($, USD, GBP), set currency accordingly
8. For arrays of team members, split by comma or "and"
9. Be smart about context: "T&M" = Time & Material, "fixed" = Fixed-Price, "SOW" = sow, etc.
"""

async def _quick_llm_call(prompt: str) -> str:
    """Fast LLM call for parsing — tries direct keys first, then Emergent."""
    # Check for user-stored keys in DB
    anthro_key = ANTHROPIC_API_KEY
    oai_key = OPENAI_API_KEY
    if db is not None:
        try:
            stored = await db.api_keys.find({}, {"_id": 0}).to_list(10)
            for k in stored:
                if k.get("provider") == "anthropic" and k.get("key"):
                    anthro_key = k["key"]
                elif k.get("provider") == "openai" and k.get("key"):
                    oai_key = k["key"]
        except Exception:
            pass

    # Try direct Anthropic key first (fastest, no Emergent credits)
    if anthro_key:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=anthro_key)
            resp = await client.messages.create(
                model="claude-sonnet-4-5-20250929", max_tokens=2000, temperature=0.1,
                system=PARSE_SYSTEM, messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text
        except Exception as e:
            logging.warning(f"Direct Anthropic failed: {e}")

    # Try direct OpenAI key
    if oai_key:
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=oai_key)
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", max_tokens=2000, temperature=0.1,
                messages=[{"role": "system", "content": PARSE_SYSTEM}, {"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content
        except Exception as e:
            logging.warning(f"Direct OpenAI failed: {e}")

    # Fallback to Emergent LLM
    if EMERGENT_KEY:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(
                api_key=EMERGENT_KEY, session_id=f"parse-{uuid.uuid4()}", system_message=PARSE_SYSTEM,
            ).with_model("gemini", "gemini-3-flash-preview")
            resp = await chat.send_message(UserMessage(text=prompt))
            return resp
        except Exception as e:
            logging.warning(f"Emergent Gemini failed: {e}")
            try:
                chat = LlmChat(
                    api_key=EMERGENT_KEY, session_id=f"parse-{uuid.uuid4()}", system_message=PARSE_SYSTEM,
                ).with_model("openai", "gpt-4o-mini")
                resp = await chat.send_message(UserMessage(text=prompt))
                return resp
            except Exception as e2:
                logging.warning(f"Emergent GPT-4o-mini failed: {e2}")

    raise HTTPException(status_code=503, detail="No AI provider available. Configure an API key in Kairos settings.")


@router.post("/parse-entry")
async def parse_entry(body: dict):
    module = body.get("module", "")
    prompt = body.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    if module not in MODULE_SCHEMAS:
        raise HTTPException(status_code=400, detail=f"Unknown module: {module}. Available: {list(MODULE_SCHEMAS.keys())}")

    schema = MODULE_SCHEMAS[module]

    # Fast path for manual entry — just return schema + defaults, no LLM call
    if prompt == "__manual__":
        defaults = {}
        for fname, fdef in schema["fields"].items():
            if "default" in fdef:
                defaults[fname] = fdef["default"]
            elif fdef.get("type") == "number":
                defaults[fname] = 0
            elif fdef.get("type") == "boolean":
                defaults[fname] = False
            elif fdef.get("type") in ("array", "array_of_objects"):
                defaults[fname] = []
            else:
                defaults[fname] = ""
        missing = [{"field": k, "label": v.get("label", k), "type": v.get("type"), "options": v.get("options")} for k, v in schema["fields"].items() if v.get("required")]
        schema_out = {}
        for k, v in schema["fields"].items():
            entry = {"label": v.get("label", k), "type": v.get("type"), "options": v.get("options"), "required": v.get("required", False), "default": v.get("default")}
            if v.get("fields"):
                entry["fields"] = v["fields"]
            schema_out[k] = entry
        return {
            "parsed": defaults,
            "missing_fields": missing,
            "schema": schema_out,
            "module": module,
        }

    field_desc = []
    for fname, fdef in schema["fields"].items():
        req = "REQUIRED" if fdef.get("required") else "optional"
        ftype = fdef.get("type", "string")
        opts = f" (one of: {', '.join(fdef['options'])})" if fdef.get("options") else ""
        default = f" [default: {fdef['default']}]" if "default" in fdef else ""
        field_desc.append(f'  "{fname}": {ftype} — {fdef.get("label", fname)} [{req}]{opts}{default}')

    llm_prompt = f"""Module: {module}
User input: "{prompt}"
Today's date: {datetime.now().strftime('%Y-%m-%d')}

Schema:
{chr(10).join(field_desc)}

Parse the user input and return a JSON object with all fields from the schema.
Set null for required fields you cannot determine from the text.
Return ONLY the JSON object."""

    raw = await _quick_llm_call(llm_prompt)

    # Extract JSON from response (handle markdown code fences)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    if cleaned.startswith("{"):
        pass
    else:
        # Try to find JSON in the response
        import re
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            cleaned = match.group()
        else:
            raise HTTPException(status_code=500, detail="AI did not return valid JSON")

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")

    # Identify missing required fields
    missing = []
    for fname, fdef in schema["fields"].items():
        if fdef.get("required") and (parsed.get(fname) is None or parsed.get(fname) == ""):
            missing.append({"field": fname, "label": fdef.get("label", fname), "type": fdef.get("type", "string"), "options": fdef.get("options")})

    schema_out = {}
    for k, v in schema["fields"].items():
        entry = {"label": v.get("label", k), "type": v.get("type"), "options": v.get("options"), "required": v.get("required", False), "default": v.get("default")}
        if v.get("fields"):
            entry["fields"] = v["fields"]
        schema_out[k] = entry
    return {
        "parsed": parsed,
        "missing_fields": missing,
        "schema": schema_out,
        "module": module,
    }


@router.get("/schemas")
async def list_schemas():
    return {k: {"example": v["example"], "fields": list(v["fields"].keys())} for k, v in MODULE_SCHEMAS.items()}
