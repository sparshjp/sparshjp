"""Revenue Recognition routes (Ind AS 115)"""
from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/revenue", tags=["Revenue Recognition"])

def get_db():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return client[os.environ['DB_NAME']]

@router.get("/schedule")
async def revenue_schedule():
    db = get_db()
    schedule = await db.revenue_schedule.find({}, {"_id": 0}).to_list(20)
    
    total_contract_assets = sum(s.get("contract_asset", 0) or 0 for s in schedule)
    total_contract_liabilities = sum(s.get("contract_liability", 0) or 0 for s in schedule)
    total_rev_mar = sum(s.get("rev_mar", 0) or 0 for s in schedule)
    total_billed = sum(s.get("billed_to_mar", 0) or 0 for s in schedule)
    
    return {
        "schedule": schedule,
        "summary": {
            "total_revenue_march": total_rev_mar,
            "total_billed_march": total_billed,
            "total_contract_assets": total_contract_assets,
            "total_contract_liabilities": total_contract_liabilities,
            "unbilled_ar": total_contract_assets,
            "deferred_revenue": total_contract_liabilities,
        }
    }

@router.get("/transactions")
async def revenue_transactions():
    db = get_db()
    txns = await db.erp_transactions.find(
        {"module": {"$in": ["Projects", "Selling", "Accounting"]},
         "$or": [
            {"type": {"$regex": "revenue|milestone|billing|invoice|accrual", "$options": "i"}},
            {"accounting": {"$regex": "revenue|Dr AR|Cr Revenue|unbilled|deferred|contract", "$options": "i"}},
         ]},
        {"_id": 0}
    ).sort("date", 1).to_list(500)
    return txns

@router.get("/ind-as-115")
async def ind_as_115_disclosure():
    db = get_db()
    schedule = await db.revenue_schedule.find({}, {"_id": 0}).to_list(20)
    projects = await db.projects.find({"id": {"$ne": "PRJ-INT"}}, {"_id": 0}).to_list(20)
    
    # Disaggregation by contract type
    by_type = {}
    for s in schedule:
        proj = next((p for p in projects if p["id"] == s["project_id"]), {})
        ptype = proj.get("type", "Unknown")
        if ptype not in by_type:
            by_type[ptype] = {"type": ptype, "revenue": 0, "count": 0, "projects": []}
        by_type[ptype]["revenue"] += s.get("rev_mar", 0) or 0
        by_type[ptype]["count"] += 1
        by_type[ptype]["projects"].append(s["project_id"])
    
    # Disaggregation by geography
    domestic_rev = 0
    export_rev = 0
    for s in schedule:
        proj = next((p for p in projects if p["id"] == s["project_id"]), {})
        currency = proj.get("currency", "INR")
        rev = s.get("rev_mar", 0) or 0
        if currency in ["USD", "GBP"]:
            export_rev += rev
        else:
            domestic_rev += rev
    
    # Contract balances
    contract_assets = []
    contract_liabilities = []
    for s in schedule:
        if (s.get("contract_asset", 0) or 0) > 0:
            contract_assets.append({
                "project": s["project_id"],
                "name": s["project_name"],
                "amount": s["contract_asset"],
                "reason": "Revenue earned > billed (Unbilled AR)"
            })
        if (s.get("contract_liability", 0) or 0) > 0:
            contract_liabilities.append({
                "project": s["project_id"],
                "name": s["project_name"],
                "amount": s["contract_liability"],
                "reason": "Billed > revenue earned (Deferred Revenue)"
            })
    
    # RPO (Remaining Performance Obligations)
    rpo = []
    for p in projects:
        if p.get("pct_complete") and p.get("value_inr") and p["pct_complete"] < 100:
            remaining = p["value_inr"] * (1 - p["pct_complete"] / 100)
            rpo.append({"project": p["id"], "name": p["name"], "remaining_value": remaining, "currency": "INR"})
        elif p.get("type") == "Monthly Retainer" and p.get("value_inr"):
            rpo.append({"project": p["id"], "name": p["name"], "remaining_value": p["value_inr"] * 12, "currency": "INR", "note": "12-month estimate"})
    
    total_rev = sum(s.get("rev_mar", 0) or 0 for s in schedule)
    
    return {
        "period": "March 2026",
        "total_revenue": total_rev,
        "disaggregation": {
            "by_type": list(by_type.values()),
            "by_geography": {
                "domestic": domestic_rev,
                "export": export_rev,
                "export_pct": round(export_rev / total_rev * 100, 1) if total_rev > 0 else 0,
            }
        },
        "contract_balances": {
            "assets": contract_assets,
            "liabilities": contract_liabilities,
            "total_assets": sum(a["amount"] for a in contract_assets),
            "total_liabilities": sum(l["amount"] for l in contract_liabilities),
        },
        "remaining_performance_obligations": rpo,
        "total_rpo": sum(r["remaining_value"] for r in rpo),
        "significant_judgments": [
            "POC method (cost-to-cost) applied for fixed-price contracts",
            "T&M revenue recognized as hours are incurred (right to invoice)",
            "Milestone revenue recognized on client acceptance",
            "Export revenue under LUT - zero-rated, no GST output",
            "Retainer revenue recognized straight-line over service period",
        ]
    }

@router.get("/all-transactions")
async def all_transactions(module: str = None, priority: str = None, search: str = None):
    db = get_db()
    query = {}
    if module and module != "All":
        query["module"] = module
    if priority and priority != "All":
        query["priority"] = priority
    if search:
        query["$or"] = [
            {"prompt": {"$regex": search, "$options": "i"}},
            {"type": {"$regex": search, "$options": "i"}},
            {"id": {"$regex": search, "$options": "i"}},
        ]
    txns = await db.erp_transactions.find(query, {"_id": 0}).sort("date", 1).to_list(500)
    
    # Module counts
    all_txns = await db.erp_transactions.find({}, {"_id": 0, "module": 1}).to_list(500)
    mod_counts = {}
    for t in all_txns:
        m = t.get("module", "Unknown")
        mod_counts[m] = mod_counts.get(m, 0) + 1
    
    return {
        "transactions": txns,
        "total": len(txns),
        "module_counts": mod_counts,
    }
