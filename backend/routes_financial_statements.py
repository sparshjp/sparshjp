# Kairos Accounting - Schedule III Financial Statements
# Companies Act 2013 - Division I compliant BS & P&L

from fastapi import APIRouter, HTTPException, Response
from datetime import datetime, timezone
from typing import Optional
from io import BytesIO
import uuid
import json

router = APIRouter(prefix="/financial-statements", tags=["financial-statements"])
db = None

def set_db(database):
    global db
    db = database

# ═══════════════════════════════════════════════════════
# SCHEDULE III - CHART OF ACCOUNTS MAPPING
# Maps each ledger to the Schedule III hierarchy
# ═══════════════════════════════════════════════════════

SCHEDULE_III_BS_MAP = {
    # EQUITY & LIABILITIES
    "shareholders_funds": {
        "share_capital": ["Share Capital"],
        "reserves_and_surplus": ["Retained Earnings"],
    },
    "non_current_liabilities": {
        "long_term_borrowings": ["Bank Loan (HDFC Term)"],
        "deferred_tax_liabilities": [],
        "other_long_term_liabilities": [],
        "long_term_provisions": [],
    },
    "current_liabilities": {
        "short_term_borrowings": [],
        "trade_payables": ["Accounts Payable"],
        "other_current_liabilities": ["GST Payable", "GST Output", "Salary Payable", "PF Payable", "Advance from Customer", "Accrued Expenses"],
        "short_term_provisions": [],
    },
    # ASSETS
    "non_current_assets": {
        "property_plant_equipment": ["Plant & Equipment"],
        "accumulated_depreciation": ["Accumulated Depreciation"],
        "capital_wip": [],
        "non_current_investments": [],
        "deferred_tax_assets": [],
        "long_term_loans_advances": [],
        "other_non_current_assets": ["Prepaid Expenses"],
    },
    "current_assets": {
        "current_investments": [],
        "inventories": ["Raw Material Inventory", "WIP Inventory", "Finished Goods Inventory"],
        "trade_receivables": ["Accounts Receivable"],
        "cash_and_equivalents": ["Cash & Bank (HDFC Current)"],
        "short_term_loans_advances": ["GST Input"],
        "other_current_assets": [],
    }
}

SCHEDULE_III_PL_MAP = {
    "revenue_from_operations": ["Sales Revenue"],
    "other_income": ["Inventory Adjustment"],
    "cost_of_materials_consumed": ["Raw Material / Consumables"],
    "purchases_of_stock_in_trade": [],
    "changes_in_inventories": [],
    "employee_benefits": ["Salary Expense", "PF Employer Expense"],
    "finance_costs": ["Interest Expense"],
    "depreciation_amortisation": ["Depreciation Expense"],
    "other_expenses": ["Utility Expense", "Professional Fees", "R&D Expense", "Cost of Goods Sold", "Scrap/Loss"],
}


async def get_account_balance(ledger_name: str) -> float:
    """Get current balance for a ledger from CoA"""
    acc = await db.chart_of_accounts.find_one({"ledger_name": ledger_name}, {"_id": 0})
    return acc.get("current_balance", 0) if acc else 0

async def get_account_balances_map() -> dict:
    """Get all CoA balances as a map"""
    accounts = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(1000)
    return {a["ledger_name"]: a.get("current_balance", 0) for a in accounts}


# ═══════════════════════════════════════════════════════
# BALANCE SHEET - Schedule III Format
# ═══════════════════════════════════════════════════════
@router.get("/balance-sheet")
async def get_balance_sheet(as_of_date: Optional[str] = None):
    """Generate Balance Sheet per Schedule III Companies Act 2013"""
    balances = await get_account_balances_map()

    def sum_accounts(account_list):
        return sum(balances.get(a, 0) for a in account_list)

    # I. EQUITY AND LIABILITIES
    # 1. Shareholders' Funds
    share_capital = abs(sum_accounts(SCHEDULE_III_BS_MAP["shareholders_funds"]["share_capital"]))
    reserves_surplus = abs(sum_accounts(SCHEDULE_III_BS_MAP["shareholders_funds"]["reserves_and_surplus"]))

    # Calculate current year P&L to add to reserves
    revenue_accounts = SCHEDULE_III_PL_MAP["revenue_from_operations"] + SCHEDULE_III_PL_MAP["other_income"]
    expense_accounts = (SCHEDULE_III_PL_MAP["cost_of_materials_consumed"] +
                       SCHEDULE_III_PL_MAP["employee_benefits"] +
                       SCHEDULE_III_PL_MAP["finance_costs"] +
                       SCHEDULE_III_PL_MAP["depreciation_amortisation"] +
                       SCHEDULE_III_PL_MAP["other_expenses"])
    total_revenue = abs(sum_accounts(revenue_accounts))
    total_expenses = sum_accounts(expense_accounts)
    current_year_pl = total_revenue - total_expenses
    reserves_surplus += current_year_pl

    shareholders_funds = share_capital + reserves_surplus

    # 3. Non-current Liabilities
    long_term_borrowings = abs(sum_accounts(SCHEDULE_III_BS_MAP["non_current_liabilities"]["long_term_borrowings"]))
    deferred_tax_liab = abs(sum_accounts(SCHEDULE_III_BS_MAP["non_current_liabilities"]["deferred_tax_liabilities"]))
    other_lt_liab = abs(sum_accounts(SCHEDULE_III_BS_MAP["non_current_liabilities"]["other_long_term_liabilities"]))
    lt_provisions = abs(sum_accounts(SCHEDULE_III_BS_MAP["non_current_liabilities"]["long_term_provisions"]))
    non_current_liabilities = long_term_borrowings + deferred_tax_liab + other_lt_liab + lt_provisions

    # 4. Current Liabilities
    st_borrowings = abs(sum_accounts(SCHEDULE_III_BS_MAP["current_liabilities"]["short_term_borrowings"]))
    trade_payables = abs(sum_accounts(SCHEDULE_III_BS_MAP["current_liabilities"]["trade_payables"]))
    other_cl = abs(sum_accounts(SCHEDULE_III_BS_MAP["current_liabilities"]["other_current_liabilities"]))
    st_provisions = abs(sum_accounts(SCHEDULE_III_BS_MAP["current_liabilities"]["short_term_provisions"]))
    current_liabilities = st_borrowings + trade_payables + other_cl + st_provisions

    total_equity_liabilities = shareholders_funds + non_current_liabilities + current_liabilities

    # II. ASSETS
    # 1. Non-current Assets
    ppe_gross = sum_accounts(SCHEDULE_III_BS_MAP["non_current_assets"]["property_plant_equipment"])
    acc_dep = abs(sum_accounts(SCHEDULE_III_BS_MAP["non_current_assets"]["accumulated_depreciation"]))
    ppe_net = ppe_gross - acc_dep
    capital_wip = sum_accounts(SCHEDULE_III_BS_MAP["non_current_assets"]["capital_wip"])
    nc_investments = sum_accounts(SCHEDULE_III_BS_MAP["non_current_assets"]["non_current_investments"])
    dta = sum_accounts(SCHEDULE_III_BS_MAP["non_current_assets"]["deferred_tax_assets"])
    lt_loans = sum_accounts(SCHEDULE_III_BS_MAP["non_current_assets"]["long_term_loans_advances"])
    other_nca = sum_accounts(SCHEDULE_III_BS_MAP["non_current_assets"]["other_non_current_assets"])
    non_current_assets = ppe_net + capital_wip + nc_investments + dta + lt_loans + other_nca

    # 2. Current Assets
    curr_investments = sum_accounts(SCHEDULE_III_BS_MAP["current_assets"]["current_investments"])
    inventories = sum_accounts(SCHEDULE_III_BS_MAP["current_assets"]["inventories"])
    trade_receivables = sum_accounts(SCHEDULE_III_BS_MAP["current_assets"]["trade_receivables"])
    cash_equivalents = sum_accounts(SCHEDULE_III_BS_MAP["current_assets"]["cash_and_equivalents"])
    st_loans = sum_accounts(SCHEDULE_III_BS_MAP["current_assets"]["short_term_loans_advances"])
    other_ca = sum_accounts(SCHEDULE_III_BS_MAP["current_assets"]["other_current_assets"])
    current_assets = curr_investments + inventories + trade_receivables + cash_equivalents + st_loans + other_ca

    total_assets = non_current_assets + current_assets

    return {
        "report_type": "Balance Sheet",
        "format": "Schedule III - Companies Act 2013 (Division I)",
        "company_name": "NanoChip Industries Pvt. Ltd.",
        "as_of_date": as_of_date or datetime.now(timezone.utc).date().isoformat(),
        "currency": "INR",

        "equity_and_liabilities": {
            "shareholders_funds": {
                "label": "1. Shareholders' Funds",
                "share_capital": {"label": "(a) Share Capital", "amount": round(share_capital, 2), "note": 1},
                "reserves_and_surplus": {"label": "(b) Reserves and Surplus", "amount": round(reserves_surplus, 2), "note": 2,
                                         "details": {"retained_earnings_opening": round(reserves_surplus - current_year_pl, 2),
                                                    "current_year_profit_loss": round(current_year_pl, 2)}},
                "total": round(shareholders_funds, 2)
            },
            "non_current_liabilities": {
                "label": "3. Non-current Liabilities",
                "long_term_borrowings": {"label": "(a) Long-term Borrowings", "amount": round(long_term_borrowings, 2), "note": 3},
                "deferred_tax_liabilities": {"label": "(b) Deferred Tax Liabilities (Net)", "amount": round(deferred_tax_liab, 2)},
                "other_long_term_liabilities": {"label": "(c) Other Long-term Liabilities", "amount": round(other_lt_liab, 2)},
                "long_term_provisions": {"label": "(d) Long-term Provisions", "amount": round(lt_provisions, 2)},
                "total": round(non_current_liabilities, 2)
            },
            "current_liabilities": {
                "label": "4. Current Liabilities",
                "trade_payables": {"label": "(b) Trade Payables", "amount": round(trade_payables, 2), "note": 4},
                "other_current_liabilities": {"label": "(c) Other Current Liabilities", "amount": round(other_cl, 2), "note": 5},
                "short_term_provisions": {"label": "(d) Short-term Provisions", "amount": round(st_provisions, 2)},
                "total": round(current_liabilities, 2)
            },
            "total": round(total_equity_liabilities, 2)
        },

        "assets": {
            "non_current_assets": {
                "label": "1. Non-current Assets",
                "property_plant_equipment": {
                    "label": "(a) Property, Plant and Equipment",
                    "gross_block": round(ppe_gross, 2),
                    "accumulated_depreciation": round(acc_dep, 2),
                    "net_block": round(ppe_net, 2),
                    "note": 6
                },
                "capital_wip": {"label": "Capital Work-in-Progress", "amount": round(capital_wip, 2)},
                "non_current_investments": {"label": "(b) Non-current Investments", "amount": round(nc_investments, 2)},
                "deferred_tax_assets": {"label": "(c) Deferred Tax Assets (Net)", "amount": round(dta, 2)},
                "long_term_loans_advances": {"label": "(d) Long-term Loans and Advances", "amount": round(lt_loans, 2)},
                "other_non_current_assets": {"label": "(e) Other Non-current Assets", "amount": round(other_nca, 2), "note": 7},
                "total": round(non_current_assets, 2)
            },
            "current_assets": {
                "label": "2. Current Assets",
                "inventories": {"label": "(b) Inventories", "amount": round(inventories, 2), "note": 8,
                                "details": {
                                    "raw_materials": round(balances.get("Raw Material Inventory", 0), 2),
                                    "work_in_progress": round(balances.get("WIP Inventory", 0), 2),
                                    "finished_goods": round(balances.get("Finished Goods Inventory", 0), 2)
                                }},
                "trade_receivables": {"label": "(c) Trade Receivables", "amount": round(trade_receivables, 2), "note": 9},
                "cash_and_equivalents": {"label": "(d) Cash and Cash Equivalents", "amount": round(cash_equivalents, 2), "note": 10},
                "short_term_loans_advances": {"label": "(e) Short-term Loans and Advances", "amount": round(st_loans, 2)},
                "other_current_assets": {"label": "(f) Other Current Assets", "amount": round(other_ca, 2)},
                "total": round(current_assets, 2)
            },
            "total": round(total_assets, 2)
        },

        "is_balanced": abs(total_equity_liabilities - total_assets) < 1,
        "difference": round(total_equity_liabilities - total_assets, 2)
    }


# ═══════════════════════════════════════════════════════
# STATEMENT OF PROFIT & LOSS - Schedule III Format
# ═══════════════════════════════════════════════════════
@router.get("/profit-and-loss")
async def get_profit_and_loss(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Generate Statement of Profit & Loss per Schedule III Companies Act 2013"""
    balances = await get_account_balances_map()

    def sum_accounts(account_list):
        return sum(abs(balances.get(a, 0)) for a in account_list)

    # I. Revenue from Operations
    revenue_operations = sum_accounts(SCHEDULE_III_PL_MAP["revenue_from_operations"])

    # II. Other Income
    other_income = sum_accounts(SCHEDULE_III_PL_MAP["other_income"])

    # III. Total Revenue
    total_revenue = revenue_operations + other_income

    # IV. Expenses
    cost_materials = sum_accounts(SCHEDULE_III_PL_MAP["cost_of_materials_consumed"])
    purchases_stock = sum_accounts(SCHEDULE_III_PL_MAP["purchases_of_stock_in_trade"])
    changes_inventory = sum_accounts(SCHEDULE_III_PL_MAP["changes_in_inventories"])
    employee_benefits = sum_accounts(SCHEDULE_III_PL_MAP["employee_benefits"])
    finance_costs = sum_accounts(SCHEDULE_III_PL_MAP["finance_costs"])
    depreciation = sum_accounts(SCHEDULE_III_PL_MAP["depreciation_amortisation"])
    other_expenses = sum_accounts(SCHEDULE_III_PL_MAP["other_expenses"])

    total_expenses = (cost_materials + purchases_stock + changes_inventory +
                     employee_benefits + finance_costs + depreciation + other_expenses)

    # V. Profit before exceptional items and tax
    profit_before_exceptional = total_revenue - total_expenses

    # IX. Profit before tax
    profit_before_tax = profit_before_exceptional

    # X. Tax expense (simplified - no deferred tax calc yet)
    current_tax = 0
    deferred_tax = 0
    total_tax = current_tax + deferred_tax

    # XI. Profit for the period
    profit_for_period = profit_before_tax - total_tax

    return {
        "report_type": "Statement of Profit and Loss",
        "format": "Schedule III - Companies Act 2013 (Division I)",
        "company_name": "NanoChip Industries Pvt. Ltd.",
        "period": {
            "from": start_date or "2026-04-01",
            "to": end_date or datetime.now(timezone.utc).date().isoformat()
        },
        "currency": "INR",

        "line_items": [
            {"sl": "I", "particular": "Revenue from Operations", "amount": round(revenue_operations, 2), "note": 11,
             "details": [{"account": a, "amount": round(abs(balances.get(a, 0)), 2)} for a in SCHEDULE_III_PL_MAP["revenue_from_operations"]]},

            {"sl": "II", "particular": "Other Income", "amount": round(other_income, 2), "note": 12,
             "details": [{"account": a, "amount": round(abs(balances.get(a, 0)), 2)} for a in SCHEDULE_III_PL_MAP["other_income"] if balances.get(a, 0) != 0]},

            {"sl": "III", "particular": "Total Revenue (I + II)", "amount": round(total_revenue, 2), "is_total": True},

            {"sl": "IV", "particular": "Expenses:", "is_header": True},
            {"sl": "", "particular": "Cost of Materials Consumed", "amount": round(cost_materials, 2), "note": 13},
            {"sl": "", "particular": "Purchases of Stock-in-Trade", "amount": round(purchases_stock, 2)},
            {"sl": "", "particular": "Changes in Inventories of FG, WIP and Stock-in-Trade", "amount": round(changes_inventory, 2)},
            {"sl": "", "particular": "Employee Benefits Expense", "amount": round(employee_benefits, 2), "note": 14,
             "details": [{"account": a, "amount": round(abs(balances.get(a, 0)), 2)} for a in SCHEDULE_III_PL_MAP["employee_benefits"] if balances.get(a, 0) != 0]},
            {"sl": "", "particular": "Finance Costs", "amount": round(finance_costs, 2), "note": 15},
            {"sl": "", "particular": "Depreciation and Amortisation Expense", "amount": round(depreciation, 2), "note": 6},
            {"sl": "", "particular": "Other Expenses", "amount": round(other_expenses, 2), "note": 16,
             "details": [{"account": a, "amount": round(abs(balances.get(a, 0)), 2)} for a in SCHEDULE_III_PL_MAP["other_expenses"] if balances.get(a, 0) != 0]},
            {"sl": "", "particular": "Total Expenses (IV)", "amount": round(total_expenses, 2), "is_total": True},

            {"sl": "V", "particular": "Profit before Exceptional and Extraordinary Items and Tax (III - IV)", "amount": round(profit_before_exceptional, 2)},
            {"sl": "VI", "particular": "Exceptional Items", "amount": 0},
            {"sl": "VII", "particular": "Profit before Extraordinary Items and Tax (V - VI)", "amount": round(profit_before_exceptional, 2)},
            {"sl": "VIII", "particular": "Extraordinary Items", "amount": 0},
            {"sl": "IX", "particular": "Profit before Tax (VII - VIII)", "amount": round(profit_before_tax, 2), "is_total": True},

            {"sl": "X", "particular": "Tax Expense:", "is_header": True},
            {"sl": "", "particular": "(1) Current Tax", "amount": round(current_tax, 2)},
            {"sl": "", "particular": "(2) Deferred Tax", "amount": round(deferred_tax, 2)},

            {"sl": "XI", "particular": "Profit (Loss) for the Period", "amount": round(profit_for_period, 2), "is_total": True, "is_final": True},
        ],

        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "profit_before_tax": round(profit_before_tax, 2),
            "tax_expense": round(total_tax, 2),
            "net_profit": round(profit_for_period, 2),
            "gross_margin_pct": round((total_revenue - cost_materials - other_expenses) / total_revenue * 100, 2) if total_revenue > 0 else 0,
        }
    }


# ═══════════════════════════════════════════════════════
# TRIAL BALANCE (Enhanced)
# ═══════════════════════════════════════════════════════
@router.get("/trial-balance")
async def get_trial_balance(as_of_date: Optional[str] = None):
    accounts = await db.chart_of_accounts.find({}, {"_id": 0}).sort("ledger_name", 1).to_list(1000)

    entries = []
    total_debit = 0
    total_credit = 0

    for acc in accounts:
        bal = acc.get("current_balance", 0)
        if bal == 0:
            continue
        debit = bal if bal > 0 else 0
        credit = abs(bal) if bal < 0 else 0
        entries.append({
            "account": acc["ledger_name"],
            "category": acc.get("category", ""),
            "debit": round(debit, 2),
            "credit": round(credit, 2),
        })
        total_debit += debit
        total_credit += credit

    return {
        "report_type": "Trial Balance",
        "company_name": "NanoChip Industries Pvt. Ltd.",
        "as_of_date": as_of_date or datetime.now(timezone.utc).date().isoformat(),
        "entries": entries,
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "difference": round(total_debit - total_credit, 2),
        "in_balance": abs(total_debit - total_credit) < 1
    }



# ═══════════════════════════════════════════════════════
# PDF & EXCEL EXPORTS
# ═══════════════════════════════════════════════════════
@router.get("/balance-sheet/export/excel")
async def export_bs_excel():
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

    data = await get_balance_sheet()
    wb = Workbook()
    ws = wb.active
    ws.title = "Balance Sheet"
    ws.column_dimensions['A'].width = 45
    ws.column_dimensions['B'].width = 8
    ws.column_dimensions['C'].width = 18

    header_font = Font(name='Arial', bold=True, size=12)
    sub_font = Font(name='Arial', size=10, italic=True)
    bold_font = Font(name='Arial', bold=True, size=10)
    num_font = Font(name='Arial', size=10)
    total_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
    thin_border = Border(bottom=Side(style='thin'))

    ws.append([data["company_name"]])
    ws.merge_cells('A1:C1')
    ws['A1'].font = header_font
    ws['A1'].alignment = Alignment(horizontal='center')
    ws.append([f"Balance Sheet as at {data['as_of_date']}"])
    ws.merge_cells('A2:C2')
    ws['A2'].font = sub_font
    ws['A2'].alignment = Alignment(horizontal='center')
    ws.append([data["format"]])
    ws.merge_cells('A3:C3')
    ws['A3'].font = Font(size=8, italic=True)
    ws['A3'].alignment = Alignment(horizontal='center')
    ws.append([])
    ws.append(["Particulars", "Note", "Amount (INR)"])
    for cell in ws[5]:
        cell.font = bold_font
        cell.border = Border(bottom=Side(style='double'))

    def add_section(title, items, total_label, total_amount):
        ws.append([title])
        ws[ws.max_row][0].font = bold_font
        for label, amount, note in items:
            row = ws.max_row + 1
            ws.append([f"  {label}", note or "", amount])
            ws[row][2].number_format = '#,##0.00'
            ws[row][2].font = num_font
        row = ws.max_row + 1
        ws.append([f"  {total_label}", "", total_amount])
        ws[row][0].font = bold_font
        ws[row][2].font = bold_font
        ws[row][2].number_format = '#,##0.00'
        for cell in ws[row]:
            cell.fill = total_fill
            cell.border = thin_border

    el = data["equity_and_liabilities"]
    ws.append(["I. EQUITY AND LIABILITIES"])
    ws[ws.max_row][0].font = Font(name='Arial', bold=True, size=11)

    add_section("1. Shareholders' Funds", [
        ("(a) Share Capital", el["shareholders_funds"]["share_capital"]["amount"], 1),
        ("(b) Reserves and Surplus", el["shareholders_funds"]["reserves_and_surplus"]["amount"], 2),
    ], "Total Shareholders' Funds", el["shareholders_funds"]["total"])

    add_section("3. Non-current Liabilities", [
        ("(a) Long-term Borrowings", el["non_current_liabilities"]["long_term_borrowings"]["amount"], 3),
    ], "Total Non-current Liabilities", el["non_current_liabilities"]["total"])

    add_section("4. Current Liabilities", [
        ("(b) Trade Payables", el["current_liabilities"]["trade_payables"]["amount"], 4),
        ("(c) Other Current Liabilities", el["current_liabilities"]["other_current_liabilities"]["amount"], 5),
    ], "Total Current Liabilities", el["current_liabilities"]["total"])

    row = ws.max_row + 1
    ws.append(["TOTAL EQUITY & LIABILITIES", "", el["total"]])
    ws[row][0].font = Font(name='Arial', bold=True, size=11)
    ws[row][2].font = Font(name='Arial', bold=True, size=11)
    ws[row][2].number_format = '#,##0.00'
    for cell in ws[row]:
        cell.border = Border(top=Side(style='double'), bottom=Side(style='double'))

    ws.append([])
    a = data["assets"]
    ws.append(["II. ASSETS"])
    ws[ws.max_row][0].font = Font(name='Arial', bold=True, size=11)

    add_section("1. Non-current Assets", [
        ("(a) Property, Plant & Equipment (Net)", a["non_current_assets"]["property_plant_equipment"]["net_block"], 6),
        ("(e) Other Non-current Assets", a["non_current_assets"]["other_non_current_assets"]["amount"], 7),
    ], "Total Non-current Assets", a["non_current_assets"]["total"])

    add_section("2. Current Assets", [
        ("(b) Inventories", a["current_assets"]["inventories"]["amount"], 8),
        ("(c) Trade Receivables", a["current_assets"]["trade_receivables"]["amount"], 9),
        ("(d) Cash and Cash Equivalents", a["current_assets"]["cash_and_equivalents"]["amount"], 10),
        ("(e) Short-term Loans & Advances", a["current_assets"]["short_term_loans_advances"]["amount"], ""),
    ], "Total Current Assets", a["current_assets"]["total"])

    row = ws.max_row + 1
    ws.append(["TOTAL ASSETS", "", a["total"]])
    ws[row][0].font = Font(name='Arial', bold=True, size=11)
    ws[row][2].font = Font(name='Arial', bold=True, size=11)
    ws[row][2].number_format = '#,##0.00'
    for cell in ws[row]:
        cell.border = Border(top=Side(style='double'), bottom=Side(style='double'))

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   headers={"Content-Disposition": "attachment; filename=Balance_Sheet_Schedule_III.xlsx"})


@router.get("/profit-and-loss/export/excel")
async def export_pl_excel():
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

    data = await get_profit_and_loss()
    wb = Workbook()
    ws = wb.active
    ws.title = "Profit & Loss"
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 50
    ws.column_dimensions['C'].width = 8
    ws.column_dimensions['D'].width = 18

    ws.append([data["company_name"]])
    ws.merge_cells('A1:D1')
    ws['A1'].font = Font(name='Arial', bold=True, size=12)
    ws['A1'].alignment = Alignment(horizontal='center')
    ws.append([f"Statement of Profit and Loss for {data['period']['from']} to {data['period']['to']}"])
    ws.merge_cells('A2:D2')
    ws['A2'].font = Font(name='Arial', size=10, italic=True)
    ws['A2'].alignment = Alignment(horizontal='center')
    ws.append([])
    ws.append(["Sl.", "Particulars", "Note", "Amount (INR)"])
    for cell in ws[4]:
        cell.font = Font(name='Arial', bold=True, size=10)
        cell.border = Border(bottom=Side(style='double'))

    for item in data["line_items"]:
        row_num = ws.max_row + 1
        ws.append([item.get("sl", ""), item.get("particular", ""), item.get("note", ""),
                   item.get("amount") if not item.get("is_header") else ""])
        if item.get("is_total") or item.get("is_final"):
            for cell in ws[row_num]:
                cell.font = Font(name='Arial', bold=True, size=10)
                cell.border = Border(top=Side(style='thin'))
        if item.get("is_final"):
            for cell in ws[row_num]:
                cell.border = Border(top=Side(style='double'), bottom=Side(style='double'))
        if ws[row_num][3].value is not None:
            ws[row_num][3].number_format = '#,##0.00'

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   headers={"Content-Disposition": "attachment; filename=Profit_Loss_Schedule_III.xlsx"})


@router.get("/trial-balance/export/excel")
async def export_tb_excel():
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side

    data = await get_trial_balance()
    wb = Workbook()
    ws = wb.active
    ws.title = "Trial Balance"
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 18

    ws.append([data["company_name"]])
    ws.merge_cells('A1:D1')
    ws['A1'].font = Font(name='Arial', bold=True, size=12)
    ws['A1'].alignment = Alignment(horizontal='center')
    ws.append([f"Trial Balance as at {data['as_of_date']}"])
    ws.merge_cells('A2:D2')
    ws['A2'].alignment = Alignment(horizontal='center')
    ws.append([])
    ws.append(["Account", "Category", "Debit (INR)", "Credit (INR)"])
    for cell in ws[4]:
        cell.font = Font(name='Arial', bold=True)
        cell.border = Border(bottom=Side(style='double'))

    for entry in data["entries"]:
        row = ws.max_row + 1
        ws.append([entry["account"], entry["category"], entry["debit"], entry["credit"]])
        ws[row][2].number_format = '#,##0.00'
        ws[row][3].number_format = '#,##0.00'

    row = ws.max_row + 1
    ws.append(["TOTAL", "", data["total_debit"], data["total_credit"]])
    for cell in ws[row]:
        cell.font = Font(name='Arial', bold=True)
        cell.border = Border(top=Side(style='double'), bottom=Side(style='double'))
    ws[row][2].number_format = '#,##0.00'
    ws[row][3].number_format = '#,##0.00'

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   headers={"Content-Disposition": "attachment; filename=Trial_Balance.xlsx"})
