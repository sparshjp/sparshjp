"""
PolyMerx Specialty Chemicals - Full ERP Test Data Seed
Runs 200 transactions for March 2026
"""
import asyncio, os, uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

def uid(): return str(uuid.uuid4())
def now_iso(): return datetime.now(timezone.utc).isoformat()

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("=" * 60)
    print("POLYMERX SPECIALTY CHEMICALS - FULL ERP SEED")
    print("=" * 60)

    # ═══════════════════════════════════════════════════════════
    # 1. CHART OF ACCOUNTS
    # ═══════════════════════════════════════════════════════════
    print("\n[1/8] Seeding Chart of Accounts...")
    coa = [
        # Assets
        {"ledger_name": "Cash & Bank (HDFC Current)", "category": "Asset", "sub_category": "Current Asset", "current_balance": 25000000},
        {"ledger_name": "Cash & Bank (ICICI Current)", "category": "Asset", "sub_category": "Current Asset", "current_balance": 8000000},
        {"ledger_name": "Cash & Bank (Axis Bank)", "category": "Asset", "sub_category": "Current Asset", "current_balance": 5000000},
        {"ledger_name": "Fixed Deposits", "category": "Asset", "sub_category": "Current Asset", "current_balance": 4500000},
        {"ledger_name": "Accounts Receivable", "category": "Asset", "sub_category": "Current Asset", "current_balance": 4200000},
        {"ledger_name": "Raw Material Inventory", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "Work-in-Progress (WIP)", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "Finished Goods Inventory", "category": "Asset", "sub_category": "Current Asset", "current_balance": 5000000},
        {"ledger_name": "GST Input", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "Advance to Vendors", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "Advance Tax", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "Prepaid Expenses", "category": "Asset", "sub_category": "Current Asset", "current_balance": 240000},
        {"ledger_name": "Accrued Interest Receivable", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "RoDTEP Receivable", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "LC Margin Account", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "Receivable from Related Party (LLP)", "category": "Asset", "sub_category": "Current Asset", "current_balance": 0},
        {"ledger_name": "Capital Work-in-Progress", "category": "Asset", "sub_category": "Non-Current Asset", "current_balance": 0},
        {"ledger_name": "Plant & Machinery", "category": "Asset", "sub_category": "Non-Current Asset", "current_balance": 28500000},
        {"ledger_name": "Accumulated Depreciation", "category": "Asset", "sub_category": "Non-Current Asset", "current_balance": -4200000},
        {"ledger_name": "Right-of-Use Asset", "category": "Asset", "sub_category": "Non-Current Asset", "current_balance": 2880000},
        {"ledger_name": "Deferred Tax Asset", "category": "Asset", "sub_category": "Non-Current Asset", "current_balance": 0},
        # Liabilities
        {"ledger_name": "Accounts Payable", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "Advance from Customers", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "GST Output", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "GST (Advance)", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "GST Input Reversal", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "TDS Payable", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "PF Payable", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "ESI Payable", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "Provision for Tax", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "Accrued Purchases", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "Warranty Provision", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "Provision for Doubtful Debts", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "Salary Payable", "category": "Liability", "sub_category": "Current Liability", "current_balance": 0},
        {"ledger_name": "Term Loan - HDFC", "category": "Liability", "sub_category": "Non-Current Liability", "current_balance": -12500000},
        {"ledger_name": "Lease Liability", "category": "Liability", "sub_category": "Non-Current Liability", "current_balance": -2400000},
        # Equity
        {"ledger_name": "Share Capital", "category": "Equity", "sub_category": "Equity", "current_balance": -15000000},
        {"ledger_name": "Retained Earnings (P&L)", "category": "Equity", "sub_category": "Equity", "current_balance": -46020000},
        {"ledger_name": "Reserves & Surplus", "category": "Equity", "sub_category": "Equity", "current_balance": -3200000},
        # Revenue
        {"ledger_name": "Sales Revenue", "category": "Revenue", "sub_category": "Revenue", "current_balance": 0},
        {"ledger_name": "Export Revenue", "category": "Revenue", "sub_category": "Revenue", "current_balance": 0},
        {"ledger_name": "Interest Income", "category": "Revenue", "sub_category": "Other Income", "current_balance": 0},
        {"ledger_name": "Other Income", "category": "Revenue", "sub_category": "Other Income", "current_balance": 0},
        {"ledger_name": "Forex Gain", "category": "Revenue", "sub_category": "Other Income", "current_balance": 0},
        {"ledger_name": "Purchase Returns", "category": "Revenue", "sub_category": "Other Income", "current_balance": 0},
        # Expenses
        {"ledger_name": "Cost of Goods Sold", "category": "Expense", "sub_category": "Direct Expense", "current_balance": 0},
        {"ledger_name": "Raw Material Consumed", "category": "Expense", "sub_category": "Direct Expense", "current_balance": 0},
        {"ledger_name": "Manufacturing Overhead", "category": "Expense", "sub_category": "Direct Expense", "current_balance": 0},
        {"ledger_name": "Salary Expense", "category": "Expense", "sub_category": "Employee Costs", "current_balance": 0},
        {"ledger_name": "PF Expense (Employer)", "category": "Expense", "sub_category": "Employee Costs", "current_balance": 0},
        {"ledger_name": "ESI Expense (Employer)", "category": "Expense", "sub_category": "Employee Costs", "current_balance": 0},
        {"ledger_name": "Bonus Expense", "category": "Expense", "sub_category": "Employee Costs", "current_balance": 0},
        {"ledger_name": "Gratuity Expense", "category": "Expense", "sub_category": "Employee Costs", "current_balance": 0},
        {"ledger_name": "Depreciation Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Selling Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Testing Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Warehousing Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Inward Freight", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Outward Freight", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Bank Charges", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Waste Disposal Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Machine Maintenance", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Idle Time Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Evaporation Loss", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Rework Cost", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Inventory Loss / Damage", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Software Subscription Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Interest Expense", "category": "Expense", "sub_category": "Finance Cost", "current_balance": 0},
        {"ledger_name": "Interest Expense (Sec 234C)", "category": "Expense", "sub_category": "Finance Cost", "current_balance": 0},
        {"ledger_name": "Lease Interest Expense", "category": "Expense", "sub_category": "Finance Cost", "current_balance": 0},
        {"ledger_name": "Forex Loss", "category": "Expense", "sub_category": "Finance Cost", "current_balance": 0},
        {"ledger_name": "Bad Debt Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Income Tax Expense", "category": "Expense", "sub_category": "Tax Expense", "current_balance": 0},
        {"ledger_name": "Deferred Tax Expense", "category": "Expense", "sub_category": "Tax Expense", "current_balance": 0},
        {"ledger_name": "Warranty Expense", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "ROU Asset Amortization", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
        {"ledger_name": "Late Fee / Penalty", "category": "Expense", "sub_category": "Operating Expense", "current_balance": 0},
    ]
    for a in coa:
        a["id"] = uid()
        a["created_at"] = now_iso()
    await db.chart_of_accounts.insert_many(coa)
    print(f"  Created {len(coa)} ledger accounts")

    # ═══════════════════════════════════════════════════════════
    # 2. COST CENTERS
    # ═══════════════════════════════════════════════════════════
    print("\n[2/8] Seeding Cost Centers...")
    centers = ["Production-U1", "Production-U2", "QC & R&D", "Sales & Marketing", "Logistics", "Finance & Admin", "Corporate"]
    for c in centers:
        await db.cost_centers.insert_one({"id": uid(), "name": c, "description": f"PolyMerx {c}", "created_at": now_iso()})
    print(f"  Created {len(centers)} cost centers")

    # ═══════════════════════════════════════════════════════════
    # 3. VENDORS (ENTITIES)
    # ═══════════════════════════════════════════════════════════
    print("\n[3/8] Seeding Vendors...")
    vendors = [
        {"id": "V001", "name": "INEOS India", "entity_type": "vendor", "gstin": "24AABCI1234A1Z5", "pan": "AABCI1234A", "contact": "9898001234", "email": "purchase@ineosindia.co.in", "address": "GIDC Dahej, Bharuch, Gujarat", "status": "Active", "payment_terms": "Net 30", "currency": "INR"},
        {"id": "V002", "name": "Jubilant Chem Solutions", "entity_type": "vendor", "gstin": "24AABCJ5678B1Z2", "pan": "AABCJ5678B", "contact": "9898005678", "email": "orders@jubilantchem.com", "address": "GIDC Sarigam, Valsad, Gujarat", "status": "Active", "payment_terms": "Net 30", "currency": "INR"},
        {"id": "V003", "name": "Huntsman Corp Singapore", "entity_type": "vendor", "gstin": "IMPORT", "pan": "", "contact": "+65-6508-0001", "email": "asia-orders@huntsman.com", "address": "10 Collyer Quay, Singapore", "status": "Active", "payment_terms": "LC 90 days", "currency": "USD"},
        {"id": "V004", "name": "LANXESS India", "entity_type": "vendor", "gstin": "27AABCL9012C1Z9", "pan": "AABCL9012C", "contact": "9820112233", "email": "sales@lanxess.co.in", "address": "Thane, Maharashtra", "status": "Active", "payment_terms": "Net 30", "currency": "INR"},
        {"id": "V005", "name": "Reliance Petrochemicals", "entity_type": "vendor", "gstin": "24AABCR3456D1Z6", "pan": "AABCR3456D", "contact": "9898009876", "email": "chemicals@ril.com", "address": "Jamnagar, Gujarat", "status": "Active", "payment_terms": "Net 15", "currency": "INR"},
        {"id": "V006", "name": "Gujarat Containers Ltd.", "entity_type": "vendor", "gstin": "24AABCG7890E1Z3", "pan": "AABCG7890E", "contact": "9898887766", "email": "sales@gujaratcontainers.in", "address": "Ahmedabad, Gujarat", "status": "Active", "payment_terms": "Net 15", "currency": "INR"},
        {"id": "V007", "name": "SafeStore Chemicals", "entity_type": "vendor", "gstin": "24AABCS4567F1Z0", "pan": "AABCS4567F", "contact": "9898776655", "email": "billing@safestorechem.in", "address": "Hazira, Gujarat", "status": "Active", "payment_terms": "Monthly", "currency": "INR"},
        {"id": "V008", "name": "TransTech Freight", "entity_type": "vendor", "gstin": "24AABCT8901G1Z7", "pan": "AABCT8901G", "contact": "9898665544", "email": "ops@transtechfreight.com", "address": "Vadodara, Gujarat", "status": "Active", "payment_terms": "Net 15", "currency": "INR"},
        {"id": "V009", "name": "Analytical Labs", "entity_type": "vendor", "gstin": "24AABCA9012H1Z4", "pan": "AABCA9012H", "contact": "9898554433", "email": "testing@analyticallabs.in", "address": "Ahmedabad, Gujarat", "status": "Active", "payment_terms": "Net 20", "currency": "INR"},
        {"id": "V010", "name": "Thermax Engineering", "entity_type": "vendor", "gstin": "27AAACT3456I1Z1", "pan": "AAACT3456I", "contact": "9822334455", "email": "projects@thermax.com", "address": "Pune, Maharashtra", "status": "Active", "payment_terms": "Net 60", "currency": "INR"},
        {"id": "V011", "name": "Henkel AG (Import)", "entity_type": "vendor", "gstin": "IMPORT", "pan": "", "contact": "+49-211-797-0", "email": "procurement@henkel.com", "address": "Dusseldorf, Germany", "status": "Active", "payment_terms": "TT Advance", "currency": "EUR"},
        {"id": "V012", "name": "Ashland Global Holdings", "entity_type": "vendor", "gstin": "IMPORT", "pan": "", "contact": "+1-859-815-3333", "email": "orders@ashland.com", "address": "Wilmington, USA", "status": "Active", "payment_terms": "LC 90 days", "currency": "USD"},
    ]
    for v in vendors:
        v["created_at"] = now_iso()
    await db.entities.insert_many(vendors)
    print(f"  Created {len(vendors)} vendors")

    # ═══════════════════════════════════════════════════════════
    # 4. CUSTOMERS (ENTITIES)
    # ═══════════════════════════════════════════════════════════
    print("\n[4/8] Seeding Customers...")
    customers = [
        {"id": "C001", "name": "Asian Paints Ltd.", "entity_type": "customer", "gstin": "27AAACA4321A1Z2", "segment": "Paints & Coatings", "address": "Mumbai", "credit_limit": 5000000, "currency": "INR", "status": "Active"},
        {"id": "C002", "name": "L&T Construction", "entity_type": "customer", "gstin": "27AAACL8765B1Z9", "segment": "Infrastructure", "address": "Mumbai", "credit_limit": 7500000, "currency": "INR", "status": "Active"},
        {"id": "C003", "name": "Motherson Sumi Systems", "entity_type": "customer", "gstin": "09AAACM2109C1Z6", "segment": "Automotive", "address": "Noida", "credit_limit": 4000000, "currency": "INR", "status": "Active"},
        {"id": "C004", "name": "Gulf Chemical Industries", "entity_type": "customer", "gstin": "EXPORT", "segment": "Export - GCC", "address": "Dubai, UAE", "credit_limit": 3000000, "currency": "USD", "status": "Active"},
        {"id": "C005", "name": "PT Chemindo Interbuana", "entity_type": "customer", "gstin": "EXPORT", "segment": "Export - SEA", "address": "Jakarta, Indonesia", "credit_limit": 2000000, "currency": "USD", "status": "Active"},
        {"id": "C006", "name": "Pidilite Industries", "entity_type": "customer", "gstin": "27AAABP5432D1Z3", "segment": "Adhesives", "address": "Mumbai", "credit_limit": 3500000, "currency": "INR", "status": "Active"},
        {"id": "C007", "name": "Berger Paints India", "entity_type": "customer", "gstin": "19AAACB6789E1Z7", "segment": "Paints & Coatings", "address": "Kolkata", "credit_limit": 2500000, "currency": "INR", "status": "Active"},
        {"id": "C008", "name": "Kansai Nerolac Paints", "entity_type": "customer", "gstin": "27AAACK1234F1Z4", "segment": "Paints & Coatings", "address": "Mumbai", "credit_limit": 3000000, "currency": "INR", "status": "Active"},
        {"id": "C009", "name": "Wacker Chemie India", "entity_type": "customer", "gstin": "27AAACW9876G1Z1", "segment": "Specialty Chemical", "address": "Mumbai", "credit_limit": 2000000, "currency": "INR", "status": "Active"},
        {"id": "C010", "name": "HUL - Industrial Division", "entity_type": "customer", "gstin": "27AAACH4567H1Z8", "segment": "FMCG-Industrial", "address": "Mumbai", "credit_limit": 6000000, "currency": "INR", "status": "Active"},
    ]
    for c in customers:
        c["created_at"] = now_iso()
        # Also seed to customers collection
        await db.customers.insert_one({"id": uid(), "customer_name": c["name"], "credit_limit": c.get("credit_limit", 0), "gstin": c["gstin"], "created_at": now_iso()})
    await db.entities.insert_many(customers)
    print(f"  Created {len(customers)} customers")

    # ═══════════════════════════════════════════════════════════
    # 5. ITEMS (RM + FG)
    # ═══════════════════════════════════════════════════════════
    print("\n[5/8] Seeding Items...")
    items = [
        # Raw Materials
        {"item_code": "RM-BPA", "item_name": "Bisphenol-A (BPA)", "item_type": "Raw Material", "uom": "KG", "valuation_rate": 185, "current_stock": 0, "reorder_level": 2000, "hsn": "2907"},
        {"item_code": "RM-ECH", "item_name": "Epichlorohydrin (ECH)", "item_type": "Raw Material", "uom": "KG", "valuation_rate": 210, "current_stock": 0, "reorder_level": 1500, "hsn": "2910", "hazmat": True},
        {"item_code": "RM-MDI", "item_name": "MDI (Diphenylmethane diisocyanate)", "item_type": "Raw Material", "uom": "KG", "valuation_rate": 262, "current_stock": 0, "reorder_level": 1000, "hsn": "2929"},
        {"item_code": "RM-TDI", "item_name": "TDI (Toluene diisocyanate)", "item_type": "Raw Material", "uom": "KG", "valuation_rate": 291, "current_stock": 0, "reorder_level": 500, "hsn": "2929", "hazmat": True},
        {"item_code": "RM-POL", "item_name": "Polyol", "item_type": "Raw Material", "uom": "KG", "valuation_rate": 145, "current_stock": 0, "reorder_level": 3000, "hsn": "3907"},
        {"item_code": "RM-ACE", "item_name": "Acetone", "item_type": "Raw Material", "uom": "KG", "valuation_rate": 72, "current_stock": 0, "reorder_level": 5000, "hsn": "2914"},
        {"item_code": "RM-TiO2", "item_name": "Titanium Dioxide", "item_type": "Raw Material", "uom": "KG", "valuation_rate": 260, "current_stock": 0, "reorder_level": 500, "hsn": "2823"},
        {"item_code": "RM-PKG", "item_name": "HDPE Drums 200L", "item_type": "Packaging", "uom": "PCS", "valuation_rate": 850, "current_stock": 0, "reorder_level": 200, "hsn": "3923"},
        # Finished Goods
        {"item_code": "EP-1000", "item_name": "EP-1000 Epoxy Resin", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 320, "selling_rate": 520, "current_stock": 0, "hsn": "3907"},
        {"item_code": "EP-2500", "item_name": "EP-2500 High-Clarity Epoxy", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 480, "selling_rate": 780, "current_stock": 0, "hsn": "3907"},
        {"item_code": "PU-C450", "item_name": "PU-C450 Polyurethane Coating", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 350, "selling_rate": 630, "current_stock": 0, "hsn": "3909"},
        {"item_code": "PU-F200", "item_name": "PU-F200 Flexible PU Foam", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 280, "selling_rate": 450, "current_stock": 0, "hsn": "3909"},
        {"item_code": "SA-700", "item_name": "SA-700 Structural Adhesive", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 410, "selling_rate": 850, "current_stock": 0, "hsn": "3506"},
        {"item_code": "SA-350", "item_name": "SA-350 Industrial Adhesive", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 290, "selling_rate": 510, "current_stock": 0, "hsn": "3506"},
        {"item_code": "SV-120", "item_name": "SV-120 Chlorinated Solvent", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 95, "selling_rate": 160, "current_stock": 0, "hsn": "2903"},
        {"item_code": "SV-200", "item_name": "SV-200 Acetone Blend", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 68, "selling_rate": 130, "current_stock": 0, "hsn": "2914"},
        {"item_code": "HB-50", "item_name": "HB-50 Hardener Base", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 380, "selling_rate": 670, "current_stock": 0, "hsn": "2921"},
        {"item_code": "CB-10", "item_name": "CB-10 Catalyst Blend", "item_type": "Finished Good", "uom": "KG", "valuation_rate": 820, "selling_rate": 1450, "current_stock": 0, "hsn": "3815"},
    ]
    for it in items:
        it["id"] = uid()
        it["created_at"] = now_iso()
    await db.items.insert_many(items)
    # Build valuation rate lookup for FG
    val_rates = {it["item_code"]: it["valuation_rate"] for it in items}
    print(f"  Created {len(items)} items (RM + FG)")

    # ═══════════════════════════════════════════════════════════
    # 6. EMPLOYEES
    # ═══════════════════════════════════════════════════════════
    print("\n[6/8] Seeding Employees...")
    employees = [
        {"employee_id": "EMP001", "name": "Arpit Shah", "designation": "VP - Operations", "department": "Production-U1", "gross_salary": 145000, "pf": True, "bank": "ICICI"},
        {"employee_id": "EMP002", "name": "Kavita Nair", "designation": "GM - Sales & Marketing", "department": "Sales & Marketing", "gross_salary": 120000, "pf": True, "bank": "HDFC"},
        {"employee_id": "EMP003", "name": "Rajan Pillai", "designation": "Export Manager", "department": "Sales & Marketing", "gross_salary": 91840, "pf": True, "bank": "ICICI"},
        {"employee_id": "EMP007", "name": "Pradeep Mehra", "designation": "QC Head", "department": "QC & R&D", "gross_salary": 96800, "pf": True, "bank": "SBI"},
        {"employee_id": "EMP010", "name": "Sanjay Kadam", "designation": "Warehouse Supervisor", "department": "Logistics", "gross_salary": 38000, "pf": True, "bank": "BOB"},
        {"employee_id": "EMP011", "name": "Mukesh Patel", "designation": "Plant Operator", "department": "Production-U1", "gross_salary": 35000, "pf": True, "bank": "SBI"},
        {"employee_id": "EMP013", "name": "Harsh Trivedi", "designation": "Managing Director", "department": "Corporate", "gross_salary": 350000, "pf": False, "bank": "HDFC"},
        {"employee_id": "EMP014", "name": "Vikram Desai", "designation": "Lab Technician (Resigned)", "department": "QC & R&D", "gross_salary": 42000, "status": "Resigned"},
        {"employee_id": "EMP016", "name": "Geeta Sharma", "designation": "Accounts Assistant (New)", "department": "Finance & Admin", "gross_salary": 40000, "pf": True, "joining_date": "2026-03-05", "bank": "HDFC"},
    ]
    for e in employees:
        e["id"] = uid()
        e["status"] = e.get("status", "Active")
        e["created_at"] = now_iso()
    await db.employees.insert_many(employees)
    print(f"  Created {len(employees)} employees")

    # ═══════════════════════════════════════════════════════════
    # 7. CRM: LEADS + OPPORTUNITIES
    # ═══════════════════════════════════════════════════════════
    print("\n[7/8] Seeding CRM (Leads & Opportunities)...")
    leads = [
        {"id": uid(), "company": "Asian Paints R&D Centre", "contact_name": "Dr. Suchit Sharma", "designation": "Head - Formulation",
         "phone": "9820334455", "email": "suchit.sharma@asianpaints.com", "source": "Industry Conference (PaintIndia 2026)",
         "interest": "EP-2500 High-Clarity Epoxy", "est_value": 2800000, "stage": "Won", "assigned_to": "Kavita Nair",
         "notes": "Lab test approved. PO: APRL/PO/2026/1122. Converted to SO-DOM-2026-011.", "created_at": "2026-03-01T09:00:00Z"},
        {"id": uid(), "company": "Gulf Chemical Industries Dubai", "contact_name": "Ahmad Al-Rashid",
         "phone": "+971-50-1234567", "source": "Export Portal (Chemexcil)",
         "interest": "EP-1000 Epoxy Resin 50MT/month", "est_value": 13182000, "stage": "Won", "assigned_to": "Rajan Pillai",
         "currency": "USD", "est_value_usd": 156000, "notes": "Won at USD 6.05/KG. SO-EXP-2026-001 created. Advance USD 81,675 received.", "created_at": "2026-03-01T10:00:00Z"},
        {"id": uid(), "company": "PT Chemindo Interbuana, Jakarta", "contact_name": "Budi Santoso",
         "phone": "+62-21-5551234", "source": "SEA Distributor Network",
         "interest": "PU-C450 Coating + SA-700 Adhesive", "est_value": 7533175, "stage": "Won", "assigned_to": "Rajan Pillai",
         "currency": "USD", "est_value_usd": 89150, "notes": "Won. SO-EXP-2026-002. Advance 50% received.", "created_at": "2026-03-04T09:00:00Z"},
        {"id": uid(), "company": "L&T Construction - Infra Division", "contact_name": "Rajiv Mehrotra",
         "phone": "9833445566", "source": "LinkedIn outreach",
         "interest": "SA-700 Structural Adhesive", "est_value": 4500000, "stage": "Won", "assigned_to": "Kavita Nair",
         "notes": "Won. PO: LTCI/PO/2026/3345. SO-DOM-2026-015. 40% advance received.", "created_at": "2026-03-05T09:00:00Z"},
        {"id": uid(), "company": "Motherson Sumi Systems - Pune Plant", "contact_name": "Anand Kulkarni",
         "phone": "9822334455", "source": "Referral from Pidilite",
         "interest": "SA-700 (IATF 16949 compliant)", "est_value": 2200000, "stage": "Technical Evaluation", "assigned_to": "Kavita Nair",
         "notes": "IATF audit scheduled. Plant visit done. Awaiting audit result by 5-Apr.", "created_at": "2026-03-15T09:00:00Z"},
        {"id": uid(), "company": "Kansai Nerolac Paints", "contact_name": "",
         "source": "Existing", "interest": "EP-1000 equivalent", "est_value": 0, "stage": "Lost",
         "notes": "Lost to Atul Ltd. Price gap ₹30/KG. Revisit Q2.", "created_at": "2026-03-09T09:00:00Z"},
        {"id": uid(), "company": "HUL - Industrial Division", "contact_name": "Pramod Agarwal",
         "phone": "9820112233", "source": "Trade show follow-up",
         "interest": "SV-200 Acetone Blend 20,000 LTR/month", "est_value": 2600000, "stage": "Qualified", "assigned_to": "Kavita Nair",
         "notes": "Existing vendor relationship. Large volume.", "created_at": "2026-03-30T09:00:00Z"},
    ]
    await db.leads.insert_many(leads)
    print(f"  Created {len(leads)} CRM leads")

    # ═══════════════════════════════════════════════════════════
    # 8. TRANSACTIONS (POs, GRNs, Invoices, Payments, JEs, WOs, SOs)
    # ═══════════════════════════════════════════════════════════
    print("\n[8/8] Seeding Transactions...")

    # Helper to post journal entries
    async def post_je(entries, narration, date, cost_center="General", ref_type="", ref_id=""):
        entry = {
            "id": uid(), "entry_type": "Auto Generated", "posting_date": date,
            "cost_center": cost_center, "journal_entries": entries, "narration": narration,
            "ref_doc_type": ref_type, "ref_doc_id": ref_id, "voucher_type": "Journal Entry",
            "status": "Posted", "user_id": "system", "created_at": now_iso(), "posted_at": now_iso()
        }
        await db.manual_journal_entries.insert_one(entry)
        for je in entries:
            jdoc = {"id": uid(), "transaction_id": entry["id"], "account": je["account"],
                    "debit": je.get("debit", 0), "credit": je.get("credit", 0),
                    "description": je.get("description", ""), "posting_date": date,
                    "cost_center": cost_center, "created_at": now_iso()}
            await db.journal_entries.insert_one(jdoc)
            net = je.get("debit", 0) - je.get("credit", 0)
            await db.chart_of_accounts.update_one({"ledger_name": je["account"]}, {"$inc": {"current_balance": net}})
        return entry["id"]

    tx_count = 0

    # --- PURCHASE ORDERS ---
    po_data = [
        {"po_number": "PO-DOM-2026-0301", "vendor": "INEOS India", "items": [{"item_code": "RM-BPA", "item_name": "Bisphenol-A (BPA)", "qty": 5000, "rate": 185, "amount": 925000}], "gst_rate": 18, "cost_center": "Production-U1", "date": "2026-03-01"},
        {"po_number": "PO-DOM-2026-0302", "vendor": "Jubilant Chem Solutions", "items": [{"item_code": "RM-ECH", "item_name": "Epichlorohydrin (ECH)", "qty": 3000, "rate": 210, "amount": 630000}], "gst_rate": 18, "cost_center": "Production-U1", "date": "2026-03-01"},
        {"po_number": "PO-DOM-2026-0303", "vendor": "Gujarat Containers Ltd.", "items": [{"item_code": "RM-PKG", "item_name": "HDPE Drums 200L", "qty": 500, "rate": 850, "amount": 425000}], "gst_rate": 12, "cost_center": "Production-U1", "date": "2026-03-02"},
        {"po_number": "PO-DOM-2026-0304", "vendor": "Reliance Petrochemicals", "items": [{"item_code": "RM-ACE", "item_name": "Acetone", "qty": 8000, "rate": 72, "amount": 576000}], "gst_rate": 18, "cost_center": "Production-U2", "date": "2026-03-03"},
        {"po_number": "PO-DOM-2026-0306", "vendor": "LANXESS India", "items": [{"item_code": "RM-TiO2", "item_name": "Titanium Dioxide", "qty": 1500, "rate": 260, "amount": 390000}], "gst_rate": 18, "cost_center": "Production-U2", "date": "2026-03-12"},
        {"po_number": "PO-DOM-2026-0307", "vendor": "Reliance Petrochemicals", "items": [{"item_code": "RM-POL", "item_name": "Polyol", "qty": 6000, "rate": 145, "amount": 870000}], "gst_rate": 18, "cost_center": "Production-U2", "date": "2026-03-19"},
        {"po_number": "PO-DOM-2026-0309", "vendor": "Reliance Petrochemicals", "items": [{"item_code": "RM-ACE", "item_name": "Acetone (2nd batch)", "qty": 5000, "rate": 74, "amount": 370000}], "gst_rate": 18, "cost_center": "Production-U2", "date": "2026-03-25"},
        {"po_number": "PO-IMP-2026-006", "vendor": "Huntsman Corp Singapore", "items": [{"item_code": "RM-MDI", "item_name": "MDI (Import)", "qty": 4000, "rate": 262, "amount": 1048000}], "gst_rate": 18, "cost_center": "Production-U1", "date": "2026-03-01"},
        {"po_number": "PO-IMP-2026-007", "vendor": "Ashland Global Holdings", "items": [{"item_code": "RM-TDI", "item_name": "TDI (Import)", "qty": 2000, "rate": 291, "amount": 582000}], "gst_rate": 18, "cost_center": "Production-U1", "date": "2026-03-02"},
        {"po_number": "PO-CAPEX-2026-001", "vendor": "Thermax Engineering", "items": [{"item_code": "PP-REACT-005", "item_name": "5KL SS Reactor Vessel Upgrade", "qty": 1, "rate": 1850000, "amount": 1850000}], "gst_rate": 18, "cost_center": "Production-U1", "date": "2026-03-03"},
    ]
    for po in po_data:
        subtotal = sum(i["amount"] for i in po["items"])
        gst_amount = round(subtotal * po["gst_rate"] / 100, 2)
        doc = {
            "id": uid(), "po_number": po["po_number"], "vendor": po["vendor"],
            "transaction_date": po["date"], "items": po["items"],
            "subtotal": subtotal, "gst_rate": po["gst_rate"], "gst_amount": gst_amount,
            "grand_total": round(subtotal + gst_amount, 2),
            "cost_center": po["cost_center"], "status": "Submitted",
            "grn_status": "Pending", "invoice_status": "Pending",
            "created_at": now_iso()
        }
        await db.purchase_orders.insert_one(doc)
        tx_count += 1

    # --- GRN (Confirm Receipt) ---
    grn_data = [
        {"po_number": "PO-DOM-2026-0304", "grn_number": "GRN-ACE-001", "date": "2026-03-04", "vendor": "Reliance Petrochemicals", "items": [{"item_code": "RM-ACE", "qty": 8000, "rate": 72, "amount": 576000}], "gst_rate": 18},
        {"po_number": "PO-DOM-2026-0303", "grn_number": "GRN-PKG-001", "date": "2026-03-05", "vendor": "Gujarat Containers Ltd.", "items": [{"item_code": "RM-PKG", "qty": 500, "rate": 850, "amount": 425000}], "gst_rate": 12},
        {"po_number": "PO-DOM-2026-0302", "grn_number": "GRN-ECH-001", "date": "2026-03-07", "vendor": "Jubilant Chem Solutions", "items": [{"item_code": "RM-ECH", "qty": 3000, "rate": 210, "amount": 630000}], "gst_rate": 18},
        {"po_number": "PO-DOM-2026-0301", "grn_number": "GRN-BPA-001", "date": "2026-03-07", "vendor": "INEOS India", "items": [{"item_code": "RM-BPA", "qty": 4985, "rate": 185, "amount": 922225}], "gst_rate": 18},
        {"po_number": "PO-IMP-2026-006", "grn_number": "GRN-MDI-001", "date": "2026-03-14", "vendor": "Huntsman Corp Singapore", "items": [{"item_code": "RM-MDI", "qty": 4000, "rate": 295, "amount": 1180580}], "gst_rate": 0},
        {"po_number": "PO-DOM-2026-0306", "grn_number": "GRN-TIO2-001", "date": "2026-03-15", "vendor": "LANXESS India", "items": [{"item_code": "RM-TiO2", "qty": 1500, "rate": 260, "amount": 390000}], "gst_rate": 18},
        {"po_number": "PO-IMP-2026-007", "grn_number": "GRN-TDI-001", "date": "2026-03-16", "vendor": "Ashland Global Holdings", "items": [{"item_code": "RM-TDI", "qty": 2000, "rate": 291, "amount": 582000}], "gst_rate": 0},
        {"po_number": "PO-DOM-2026-0307", "grn_number": "GRN-POL-001", "date": "2026-03-22", "vendor": "Reliance Petrochemicals", "items": [{"item_code": "RM-POL", "qty": 6000, "rate": 145, "amount": 870000}], "gst_rate": 18},
        {"po_number": "PO-DOM-2026-0309", "grn_number": "GRN-ACE-002", "date": "2026-03-26", "vendor": "Reliance Petrochemicals", "items": [{"item_code": "RM-ACE", "qty": 5000, "rate": 74, "amount": 370000}], "gst_rate": 18},
    ]
    for g in grn_data:
        subtotal = sum(i["amount"] for i in g["items"])
        gst_amount = round(subtotal * g["gst_rate"] / 100, 2)
        grand_total = round(subtotal + gst_amount, 2)
        grn_doc = {
            "id": uid(), "grn_number": g["grn_number"], "po_number": g["po_number"],
            "vendor": g["vendor"], "posting_date": g["date"], "items": g["items"],
            "subtotal": subtotal, "gst_rate": g["gst_rate"], "gst_amount": gst_amount,
            "grand_total": grand_total, "invoice_status": "Invoiced",
            "status": "Received", "created_at": now_iso()
        }
        await db.goods_receipt_notes.insert_one(grn_doc)
        # Update stock
        for item in g["items"]:
            await db.items.update_one({"item_code": item["item_code"]}, {"$inc": {"current_stock": item["qty"]}})
        # Post GRN JE
        je = [
            {"account": "Raw Material Inventory", "debit": subtotal, "credit": 0, "description": f"GRN {g['grn_number']}"},
        ]
        if gst_amount > 0:
            je.append({"account": "GST Input", "debit": gst_amount, "credit": 0, "description": f"GST on GRN {g['grn_number']}"})
        je.append({"account": "Accounts Payable", "debit": 0, "credit": grand_total, "description": f"AP: {g['vendor']}"})
        await post_je(je, f"GRN: {g['grn_number']} from {g['vendor']}", g["date"], "Production-U1", "GRN", g["grn_number"])
        # Update PO status
        await db.purchase_orders.update_one({"po_number": g["po_number"]}, {"$set": {"grn_status": "Received", "invoice_status": "Invoiced", "status": "Completed"}})
        tx_count += 1

    # --- PURCHASE INVOICES (from GRN) ---
    pi_data = [
        {"inv_number": "PI-2026-0304", "vendor": "Reliance Petrochemicals", "grn": "GRN-ACE-001", "po": "PO-DOM-2026-0304", "amount": 576000, "gst_rate": 18, "date": "2026-03-05"},
        {"inv_number": "PI-2026-0301", "vendor": "INEOS India", "grn": "GRN-BPA-001", "po": "PO-DOM-2026-0301", "amount": 922225, "gst_rate": 18, "date": "2026-03-28"},
        {"inv_number": "PI-2026-0302", "vendor": "Jubilant Chem Solutions", "grn": "GRN-ECH-001", "po": "PO-DOM-2026-0302", "amount": 630000, "gst_rate": 18, "date": "2026-03-28"},
        {"inv_number": "PI-2026-0306", "vendor": "LANXESS India", "grn": "GRN-TIO2-001", "po": "PO-DOM-2026-0306", "amount": 338000, "gst_rate": 18, "date": "2026-03-28"},
        {"inv_number": "PI-2026-0309", "vendor": "Reliance Petrochemicals", "grn": "GRN-ACE-002", "po": "PO-DOM-2026-0309", "amount": 370000, "gst_rate": 18, "date": "2026-03-28"},
        {"inv_number": "PI-2026-0307", "vendor": "Reliance Petrochemicals", "grn": "GRN-POL-001", "po": "PO-DOM-2026-0307", "amount": 870000, "gst_rate": 18, "date": "2026-03-28"},
    ]
    for pi in pi_data:
        gst = round(pi["amount"] * pi["gst_rate"] / 100, 2)
        doc = {
            "id": uid(), "invoice_number": pi["inv_number"], "vendor": pi["vendor"],
            "grn_number": pi["grn"], "po_number": pi["po"],
            "posting_date": pi["date"], "subtotal": pi["amount"],
            "gst_rate": pi["gst_rate"], "gst_amount": gst,
            "grand_total": round(pi["amount"] + gst, 2),
            "status": "Unpaid", "amount_paid": 0, "payment_status": "Unpaid",
            "created_at": now_iso()
        }
        await db.purchase_invoices.insert_one(doc)
        tx_count += 1

    # --- VENDOR PAYMENTS ---
    vp_data = [
        {"vendor": "Reliance Petrochemicals", "invoice": "PI-2026-0304", "amount": 679680, "date": "2026-03-18", "mode": "NEFT"},
    ]
    for vp in vp_data:
        doc = {"id": uid(), "payment_number": f"VP-{uid()[:8].upper()}", "vendor": vp["vendor"],
               "invoice_number": vp["invoice"], "amount": vp["amount"],
               "payment_date": vp["date"], "payment_mode": vp["mode"], "created_at": now_iso()}
        await db.vendor_payments.insert_one(doc)
        await post_je([
            {"account": "Accounts Payable", "debit": vp["amount"], "credit": 0, "description": f"Payment to {vp['vendor']}"},
            {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": vp["amount"], "description": f"VP for {vp['invoice']}"},
        ], f"Vendor Payment: {vp['vendor']}", vp["date"], "Finance & Admin", "Vendor Payment", vp["invoice"])
        await db.purchase_invoices.update_one({"invoice_number": vp["invoice"]}, {"$set": {"status": "Paid", "amount_paid": vp["amount"]}})
        tx_count += 1

    # --- SALES ORDERS ---
    so_data = [
        {"so_number": "SO-EXP-2026-001", "customer": "Gulf Chemical Industries", "items": [{"item_code": "EP-1000", "item_name": "EP-1000 Epoxy Resin", "qty": 45000, "rate": 511.28, "amount": 23007600}], "gst_rate": 0, "date": "2026-03-10", "cost_center": "Sales & Marketing"},
        {"so_number": "SO-DOM-2026-011", "customer": "Asian Paints Ltd.", "items": [{"item_code": "EP-2500", "item_name": "EP-2500 High-Clarity Epoxy", "qty": 2000, "rate": 780, "amount": 1560000}], "gst_rate": 18, "date": "2026-03-11", "cost_center": "Sales & Marketing"},
        {"so_number": "SO-EXP-2026-002", "customer": "PT Chemindo Interbuana", "items": [{"item_code": "PU-C450", "item_name": "PU-C450 Coating", "qty": 8000, "rate": 629.46, "amount": 5035700}, {"item_code": "SA-700", "item_name": "SA-700 Adhesive", "qty": 3000, "rate": 832.49, "amount": 2497475}], "gst_rate": 0, "date": "2026-03-19", "cost_center": "Sales & Marketing"},
        {"so_number": "SO-DOM-2026-015", "customer": "L&T Construction", "items": [{"item_code": "SA-700", "item_name": "SA-700 Structural Adhesive", "qty": 5000, "rate": 850, "amount": 4250000}], "gst_rate": 18, "date": "2026-03-18", "cost_center": "Sales & Marketing"},
        {"so_number": "SO-DOM-2026-008", "customer": "Pidilite Industries", "items": [{"item_code": "SA-350", "item_name": "SA-350 Industrial Adhesive", "qty": 5000, "rate": 510, "amount": 2550000}], "gst_rate": 18, "date": "2026-03-10", "cost_center": "Sales & Marketing"},
        {"so_number": "SO-DOM-2026-009", "customer": "Berger Paints India", "items": [{"item_code": "EP-1000", "item_name": "EP-1000 Epoxy Resin", "qty": 1500, "rate": 520, "amount": 780000}], "gst_rate": 18, "date": "2026-03-11", "cost_center": "Sales & Marketing"},
        {"so_number": "SOR-2026-003", "customer": "HUL - Industrial Division", "items": [{"item_code": "SV-200", "item_name": "SV-200 Acetone Blend", "qty": 4000, "rate": 130, "amount": 520000}], "gst_rate": 18, "date": "2026-03-03", "cost_center": "Sales & Marketing"},
        {"so_number": "SO-DOM-2026-019", "customer": "Wacker Chemie India", "items": [{"item_code": "HB-50", "item_name": "HB-50 Hardener Base", "qty": 500, "rate": 670, "amount": 335000}, {"item_code": "CB-10", "item_name": "CB-10 Catalyst Blend", "qty": 100, "rate": 1450, "amount": 145000}], "gst_rate": 18, "date": "2026-03-25", "cost_center": "Sales & Marketing"},
    ]
    for so in so_data:
        subtotal = sum(i["amount"] for i in so["items"])
        gst = round(subtotal * so["gst_rate"] / 100, 2)
        doc = {
            "id": uid(), "so_number": so["so_number"], "customer": so["customer"],
            "transaction_date": so["date"], "items": so["items"],
            "subtotal": subtotal, "gst_rate": so["gst_rate"], "gst_amount": gst,
            "grand_total": round(subtotal + gst, 2),
            "total_qty": sum(i["qty"] for i in so["items"]),
            "delivery_status": "Fully Delivered", "billing_status": "Fully Billed",
            "status": "Completed", "cost_center": so["cost_center"],
            "created_at": now_iso()
        }
        await db.selling_sales_orders.insert_one(doc)
        tx_count += 1

    # --- DELIVERY NOTES (from SO) ---
    for so in so_data:
        subtotal = sum(i["amount"] for i in so["items"])
        gst = round(subtotal * so["gst_rate"] / 100, 2)
        dn_doc = {
            "id": uid(), "dn_number": f"DN-{so['so_number'].replace('SO-','').replace('SOR-','')}", "so_number": so["so_number"],
            "customer": so["customer"], "posting_date": so["date"],
            "items": so["items"], "total_qty": sum(i["qty"] for i in so["items"]),
            "subtotal": subtotal, "gst_rate": so["gst_rate"], "gst_amount": gst,
            "grand_total": round(subtotal + gst, 2),
            "invoice_status": "Invoiced", "status": "Delivered", "created_at": now_iso()
        }
        await db.selling_delivery_notes.insert_one(dn_doc)
        tx_count += 1

    # --- SALES INVOICES ---
    si_data = [
        {"inv_number": "SI-DOM-2026-009", "customer": "Berger Paints India", "so": "SO-DOM-2026-009", "amount": 780000, "gst_rate": 18, "cogs": 480000, "date": "2026-03-14", "status": "Paid"},
        {"inv_number": "EXP-SI-2026-001", "customer": "Gulf Chemical Industries", "so": "SO-EXP-2026-001", "amount": 1431430, "gst_rate": 0, "cogs": 896000, "date": "2026-03-16", "status": "Partially Paid"},
        {"inv_number": "SI-DOM-2026-015", "customer": "L&T Construction", "so": "SO-DOM-2026-015", "amount": 4250000, "gst_rate": 18, "cogs": 2050000, "date": "2026-03-18", "status": "Partially Paid"},
        {"inv_number": "SI-DOM-2026-008", "customer": "Pidilite Industries", "so": "SO-DOM-2026-008", "amount": 2550000, "gst_rate": 18, "cogs": 1450000, "date": "2026-03-20", "status": "Paid"},
        {"inv_number": "SI-DOM-2026-021", "customer": "HUL - Industrial Division", "so": "SOR-2026-003", "amount": 520000, "gst_rate": 18, "cogs": 272000, "date": "2026-03-22", "status": "Paid"},
        {"inv_number": "EXP-SI-2026-002", "customer": "PT Chemindo Interbuana", "so": "SO-EXP-2026-002", "amount": 7533175, "gst_rate": 0, "cogs": 4580000, "date": "2026-03-22", "status": "Paid"},
        {"inv_number": "SI-DOM-2026-011", "customer": "Asian Paints Ltd.", "so": "SO-DOM-2026-011", "amount": 1560000, "gst_rate": 18, "cogs": 960000, "date": "2026-03-14", "status": "Unpaid"},
        {"inv_number": "SI-DOM-2026-019", "customer": "Wacker Chemie India", "so": "SO-DOM-2026-019", "amount": 480000, "gst_rate": 18, "cogs": 272000, "date": "2026-03-26", "status": "Unpaid"},
    ]
    for si in si_data:
        gst = round(si["amount"] * si["gst_rate"] / 100, 2)
        grand = round(si["amount"] + gst, 2)
        paid_map = {"Paid": grand, "Partially Paid": round(grand * 0.4, 2), "Unpaid": 0}
        doc = {
            "id": uid(), "invoice_number": si["inv_number"], "customer": si["customer"],
            "so_number": si["so"], "posting_date": si["date"],
            "subtotal": si["amount"], "gst_rate": si["gst_rate"], "gst_amount": gst,
            "grand_total": grand, "cogs_total": si["cogs"],
            "status": si["status"], "amount_paid": paid_map.get(si["status"], 0),
            "payment_status": si["status"], "created_at": now_iso()
        }
        await db.selling_invoices.insert_one(doc)
        # Post Sales JE
        entries = [
            {"account": "Accounts Receivable", "debit": grand, "credit": 0, "description": f"AR: {si['inv_number']}"},
            {"account": "Sales Revenue" if si["gst_rate"] > 0 else "Export Revenue", "debit": 0, "credit": si["amount"], "description": f"Revenue: {si['inv_number']}"},
        ]
        if gst > 0:
            entries.append({"account": "GST Output", "debit": 0, "credit": gst, "description": f"GST: {si['inv_number']}"})
        if si["cogs"] > 0:
            entries.append({"account": "Cost of Goods Sold", "debit": si["cogs"], "credit": 0, "description": f"COGS: {si['inv_number']}"})
            entries.append({"account": "Finished Goods Inventory", "debit": 0, "credit": si["cogs"], "description": f"FG: {si['inv_number']}"})
        await post_je(entries, f"Sales Invoice: {si['inv_number']} to {si['customer']}", si["date"], "Sales & Marketing", "Sales Invoice", si["inv_number"])
        tx_count += 1

    # --- CUSTOMER PAYMENTS ---
    cp_data = [
        {"customer": "HUL - Industrial Division", "invoice": "SI-DOM-2026-021", "amount": 613600, "date": "2026-03-04", "mode": "NEFT"},
        {"customer": "Gulf Chemical Industries", "invoice": "EXP-SI-2026-001", "amount": 6901538, "date": "2026-03-10", "mode": "Wire Transfer"},
        {"customer": "PT Chemindo Interbuana", "invoice": "EXP-SI-2026-002", "amount": 3766588, "date": "2026-03-19", "mode": "TT"},
        {"customer": "L&T Construction", "invoice": "SI-DOM-2026-015", "amount": 2006000, "date": "2026-03-18", "mode": "RTGS"},
        {"customer": "Berger Paints India", "invoice": "SI-DOM-2026-009", "amount": 920400, "date": "2026-03-21", "mode": "NEFT"},
        {"customer": "Pidilite Industries", "invoice": "SI-DOM-2026-008", "amount": 3009000, "date": "2026-03-28", "mode": "RTGS"},
        {"customer": "PT Chemindo Interbuana", "invoice": "EXP-SI-2026-002", "amount": 3780060, "date": "2026-03-29", "mode": "TT"},
        {"customer": "L&T Construction", "invoice": "SI-DOM-2026-015", "amount": 2968880, "date": "2026-03-28", "mode": "RTGS"},
    ]
    for cp in cp_data:
        doc = {"id": uid(), "payment_number": f"CR-{uid()[:8].upper()}", "customer": cp["customer"],
               "invoice_number": cp["invoice"], "amount": cp["amount"],
               "payment_date": cp["date"], "payment_mode": cp["mode"], "created_at": now_iso()}
        await db.customer_payments.insert_one(doc)
        await post_je([
            {"account": "Cash & Bank (HDFC Current)", "debit": cp["amount"], "credit": 0, "description": f"Receipt from {cp['customer']}"},
            {"account": "Accounts Receivable", "debit": 0, "credit": cp["amount"], "description": f"AR: {cp['invoice']}"},
        ], f"Customer Payment: {cp['customer']}", cp["date"], "Sales & Marketing", "Customer Payment", cp["invoice"])
        tx_count += 1

    # --- MANUFACTURING WORK ORDERS ---
    wo_data = [
        {"wo_number": "WO-EP-001", "item": "EP-1000", "name": "EP-1000 Epoxy Resin", "qty_planned": 3000, "qty_produced": 2820, "status": "Completed",
         "bom": [{"item_code": "RM-BPA", "item_name": "BPA", "qty": 2000, "rate": 185}, {"item_code": "RM-ECH", "item_name": "ECH", "qty": 1200, "rate": 210}],
         "start": "2026-03-02", "end": "2026-03-04"},
        {"wo_number": "WO-EP-002", "item": "EP-2500", "name": "EP-2500 High-Clarity Epoxy", "qty_planned": 2500, "qty_produced": 2380, "status": "Completed",
         "bom": [{"item_code": "RM-BPA", "item_name": "BPA-HP", "qty": 1500, "rate": 195}, {"item_code": "RM-ECH", "item_name": "ECH", "qty": 900, "rate": 210}],
         "start": "2026-03-07", "end": "2026-03-10"},
        {"wo_number": "WO-PU-001", "item": "PU-C450", "name": "PU-C450 Coating", "qty_planned": 4000, "qty_produced": 3820, "status": "Completed",
         "bom": [{"item_code": "RM-MDI", "item_name": "MDI", "qty": 1500, "rate": 262}, {"item_code": "RM-POL", "item_name": "Polyol", "qty": 3000, "rate": 145}, {"item_code": "RM-TiO2", "item_name": "TiO2", "qty": 1200, "rate": 260}],
         "start": "2026-03-10", "end": "2026-03-16"},
        {"wo_number": "WO-SA-001", "item": "SA-700", "name": "SA-700 Structural Adhesive", "qty_planned": 3500, "qty_produced": 3480, "status": "Completed",
         "bom": [{"item_code": "RM-ECH", "item_name": "ECH Resin", "qty": 1800, "rate": 210}],
         "start": "2026-03-15", "end": "2026-03-21"},
        {"wo_number": "WO-SV-001", "item": "SV-200", "name": "SV-200 Acetone Blend", "qty_planned": 12000, "qty_produced": 11880, "status": "Completed",
         "bom": [{"item_code": "RM-ACE", "item_name": "Acetone", "qty": 9600, "rate": 72}],
         "start": "2026-03-18", "end": "2026-03-19"},
        {"wo_number": "WO-PUF-001", "item": "PU-F200", "name": "PU-F200 Flexible PU Foam", "qty_planned": 2000, "qty_produced": 1920, "status": "Completed",
         "bom": [{"item_code": "RM-TDI", "item_name": "TDI", "qty": 600, "rate": 291}, {"item_code": "RM-POL", "item_name": "Polyol", "qty": 1200, "rate": 145}],
         "start": "2026-03-23", "end": "2026-03-26"},
        {"wo_number": "WO-HB-001", "item": "HB-50", "name": "HB-50 Hardener Base", "qty_planned": 1000, "qty_produced": 985, "status": "Completed",
         "bom": [{"item_code": "RM-ACE", "item_name": "Amine Base", "qty": 700, "rate": 72}],
         "start": "2026-03-30", "end": "2026-03-30"},
        {"wo_number": "WO-EP-003", "item": "EP-1000", "name": "EP-1000 Epoxy Resin (Batch 2)", "qty_planned": 2000, "qty_produced": 0, "status": "In Progress",
         "bom": [{"item_code": "RM-BPA", "item_name": "BPA", "qty": 1200, "rate": 185}, {"item_code": "RM-ECH", "item_name": "ECH", "qty": 700, "rate": 210}],
         "start": "2026-03-31", "end": ""},
    ]
    for wo in wo_data:
        total_rm = sum(b["qty"] * b["rate"] for b in wo["bom"])
        doc = {
            "id": uid(), "wo_number": wo["wo_number"], "production_item": wo["item"],
            "production_item_name": wo["name"], "qty_to_produce": wo["qty_planned"],
            "qty_produced": wo["qty_produced"], "qty_rejected": wo["qty_planned"] - wo["qty_produced"] if wo["qty_produced"] > 0 else 0,
            "bom_items": wo["bom"], "total_rm_cost": total_rm,
            "cost_per_unit": round(total_rm / wo["qty_planned"], 2),
            "planned_start": wo["start"], "planned_end": wo["end"],
            "actual_start": wo["start"] if wo["status"] != "Draft" else None,
            "actual_end": wo["end"] if wo["status"] == "Completed" else None,
            "status": wo["status"], "cost_center": "Production-U1", "created_at": now_iso()
        }
        await db.work_orders.insert_one(doc)
        # Add FG to inventory for completed WOs
        if wo["qty_produced"] > 0:
            await db.items.update_one({"item_code": wo["item"]}, {"$inc": {"current_stock": wo["qty_produced"]}})
            # FG valued at standard cost (valuation_rate * qty_produced)
            fg_value = wo["qty_produced"] * val_rates.get(wo["item"], 0)
            overhead = fg_value - total_rm
            # Start JE: DR WIP, CR Raw Material Inventory
            await post_je([
                {"account": "Work-in-Progress (WIP)", "debit": total_rm, "credit": 0, "description": f"WO Start: {wo['wo_number']}"},
                {"account": "Raw Material Inventory", "debit": 0, "credit": total_rm, "description": f"RM consumed: {wo['wo_number']}"},
            ], f"WO Start: {wo['wo_number']} - {wo['name']}", wo["start"], "Production-U1", "Work Order", wo["wo_number"])
            # Complete JE: DR FG at standard cost, CR WIP at RM cost, CR Mfg Overhead for difference
            je_entries = [
                {"account": "Finished Goods Inventory", "debit": fg_value, "credit": 0, "description": f"FG produced: {wo['wo_number']}"},
                {"account": "Work-in-Progress (WIP)", "debit": 0, "credit": total_rm, "description": f"WO Complete: {wo['wo_number']}"},
            ]
            if overhead > 0:
                je_entries.append({"account": "Manufacturing Overhead", "debit": 0, "credit": overhead, "description": f"Overhead absorbed: {wo['wo_number']}"})
            await post_je(je_entries, f"WO Complete: {wo['wo_number']} - {wo['name']}", wo["end"], "Production-U1", "Work Order", wo["wo_number"])
        elif wo["status"] == "In Progress":
            # WO started but not completed - only consume RM to WIP
            await post_je([
                {"account": "Work-in-Progress (WIP)", "debit": total_rm, "credit": 0, "description": f"WO Start: {wo['wo_number']}"},
                {"account": "Raw Material Inventory", "debit": 0, "credit": total_rm, "description": f"RM consumed: {wo['wo_number']}"},
            ], f"WO Start: {wo['wo_number']} - {wo['name']}", wo["start"], "Production-U1", "Work Order", wo["wo_number"])
        tx_count += 1

    # --- KEY JOURNAL ENTRIES (Advances, Expenses, Accruals, Depreciation, Tax) ---
    je_list = [
        {"date": "2026-03-03", "narration": "Advance to Reliance Petro for Acetone PO", "entries": [
            {"account": "Advance to Vendors", "debit": 203904, "credit": 0}, {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 203904}]},
        {"date": "2026-03-03", "narration": "Advance for Thermax Reactor CapEx", "entries": [
            {"account": "Capital Work-in-Progress", "debit": 740000, "credit": 0}, {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 740000}]},
        {"date": "2026-03-05", "narration": "March Term Loan EMI (Principal + Interest)", "entries": [
            {"account": "Term Loan - HDFC", "debit": 100000, "credit": 0}, {"account": "Interest Expense", "debit": 36400, "credit": 0},
            {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 136400}]},
        {"date": "2026-03-10", "narration": "LC Margin blocked for Huntsman Import", "entries": [
            {"account": "LC Margin Account", "debit": 223925, "credit": 0}, {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 223925}]},
        {"date": "2026-03-10", "narration": "LC Opening + Bank Charges", "entries": [
            {"account": "Bank Charges", "debit": 26700, "credit": 0}, {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 26700}]},
        {"date": "2026-03-12", "narration": "Sample dispatch freight to PT Chemindo Jakarta", "entries": [
            {"account": "Selling Expense", "debit": 18500, "credit": 0}, {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 18500}]},
        {"date": "2026-03-15", "narration": "Accrued Interest on FD", "entries": [
            {"account": "Accrued Interest Receivable", "debit": 19913, "credit": 0}, {"account": "Interest Income", "debit": 0, "credit": 19913}]},
        {"date": "2026-03-16", "narration": "Q4 Advance Tax + Interest u/s 234C", "entries": [
            {"account": "Advance Tax", "debit": 700000, "credit": 0}, {"account": "Interest Expense (Sec 234C)", "debit": 583, "credit": 0},
            {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 700583}]},
        {"date": "2026-03-20", "narration": "Monthly Depreciation - March 2026", "entries": [
            {"account": "Depreciation Expense", "debit": 205000, "credit": 0}, {"account": "Accumulated Depreciation", "debit": 0, "credit": 205000}]},
        {"date": "2026-03-22", "narration": "Thermax Reactor commissioned - WIP to Fixed Asset", "entries": [
            {"account": "Plant & Machinery", "debit": 1850000, "credit": 0}, {"account": "Capital Work-in-Progress", "debit": 0, "credit": 1850000}]},
        {"date": "2026-03-24", "narration": "Corporate expense paid for sister LLP", "entries": [
            {"account": "Receivable from Related Party (LLP)", "debit": 45000, "credit": 0}, {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 45000}]},
        {"date": "2026-03-27", "narration": "Provision for Doubtful Debts - Wacker Chemie", "entries": [
            {"account": "Bad Debt Expense", "debit": 142500, "credit": 0}, {"account": "Provision for Doubtful Debts", "debit": 0, "credit": 142500}]},
        {"date": "2026-03-28", "narration": "Henkel advance payment EUR 8,500", "entries": [
            {"account": "Advance to Vendors", "debit": 775200, "credit": 0}, {"account": "Cash & Bank (HDFC Current)", "debit": 0, "credit": 775200}]},
        {"date": "2026-03-29", "narration": "ROU Asset Amortization & Lease Interest", "entries": [
            {"account": "ROU Asset Amortization", "debit": 24028, "credit": 0}, {"account": "Lease Interest Expense", "debit": 12500, "credit": 0},
            {"account": "Right-of-Use Asset", "debit": 0, "credit": 24028}, {"account": "Lease Liability", "debit": 0, "credit": 12500}]},
        {"date": "2026-03-30", "narration": "Warranty Provision for March Sales (0.5%)", "entries": [
            {"account": "Warranty Expense", "debit": 29050, "credit": 0}, {"account": "Warranty Provision", "debit": 0, "credit": 29050}]},
        {"date": "2026-03-30", "narration": "Accrued Purchases (freight + storage partial)", "entries": [
            {"account": "Inward Freight", "debit": 42000, "credit": 0}, {"account": "Warehousing Expense", "debit": 32500, "credit": 0},
            {"account": "Accrued Purchases", "debit": 0, "credit": 74500}]},
        {"date": "2026-03-31", "narration": "Monthly Payroll - March 2026", "entries": [
            {"account": "Salary Expense", "debit": 1182400, "credit": 0}, {"account": "PF Payable", "debit": 0, "credit": 167762},
            {"account": "TDS Payable", "debit": 0, "credit": 105500}, {"account": "Salary Payable", "debit": 0, "credit": 909138}]},
        {"date": "2026-03-31", "narration": "Salary disbursement NEFT", "entries": [
            {"account": "Salary Payable", "debit": 985000, "credit": 0}, {"account": "Cash & Bank (ICICI Current)", "debit": 0, "credit": 985000}]},
        {"date": "2026-03-31", "narration": "Forex MTM Revaluation", "entries": [
            {"account": "Forex Loss", "debit": 2975, "credit": 0}, {"account": "Accounts Payable", "debit": 0, "credit": 2975},
            {"account": "Accounts Receivable", "debit": 14947, "credit": 0}, {"account": "Forex Gain", "debit": 0, "credit": 14947}]},
        {"date": "2026-03-31", "narration": "Income Tax Provision FY 2025-26", "entries": [
            {"account": "Income Tax Expense", "debit": 1308840, "credit": 0}, {"account": "Provision for Tax", "debit": 0, "credit": 1308840}]},
        {"date": "2026-03-31", "narration": "Deferred Tax Movement", "entries": [
            {"account": "Deferred Tax Asset", "debit": 44047, "credit": 0}, {"account": "Deferred Tax Expense", "debit": 0, "credit": 44047}]},
        {"date": "2026-03-31", "narration": "ERP Subscription Amortization", "entries": [
            {"account": "Software Subscription Expense", "debit": 20000, "credit": 0}, {"account": "Prepaid Expenses", "debit": 0, "credit": 20000}]},
        {"date": "2026-03-31", "narration": "Export Incentive RoDTEP Receivable", "entries": [
            {"account": "RoDTEP Receivable", "debit": 102024, "credit": 0}, {"account": "Other Income", "debit": 0, "credit": 102024}]},
    ]
    for je in je_list:
        await post_je(je["entries"], je["narration"], je["date"])
        tx_count += 1

    print(f"\n  Total transactions seeded: {tx_count}")

    # --- Verify Trial Balance ---
    print("\n" + "=" * 60)
    print("VERIFYING TRIAL BALANCE...")
    print("=" * 60)
    all_accounts = await db.chart_of_accounts.find({}, {"_id": 0, "ledger_name": 1, "category": 1, "current_balance": 1}).to_list(200)
    total_dr = sum(a["current_balance"] for a in all_accounts if a["current_balance"] > 0)
    total_cr = sum(abs(a["current_balance"]) for a in all_accounts if a["current_balance"] < 0)
    diff = round(total_dr - total_cr, 2)
    print(f"  Total Debits:  {total_dr:>15,.2f}")
    print(f"  Total Credits: {total_cr:>15,.2f}")
    print(f"  Difference:    {diff:>15,.2f}")
    if abs(diff) < 1:
        print("  TB BALANCED!")
    else:
        print(f"  WARNING: TB not balanced (diff: {diff})")

    # Print key balances
    print("\n  KEY BALANCES:")
    for a in sorted(all_accounts, key=lambda x: abs(x["current_balance"]), reverse=True)[:15]:
        print(f"    {a['ledger_name']:<45} {a['current_balance']:>15,.2f}")

    client.close()
    print("\n" + "=" * 60)
    print("SEED COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed())
