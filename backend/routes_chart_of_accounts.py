"""Auto-generated module: Chart Of Accounts"""
from fastapi import APIRouter
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/chart-of-accounts", tags=["Chart Of Accounts"])

db = None

def set_db(database):
    global db
    db = database

@router.get("")
async def list_accounts():
    accounts = await db.chart_of_accounts.find({}, {"_id": 0}).sort("code", 1).to_list(100)
    return accounts

@router.get("/analysis")
async def analyze_structure():
    accounts = await db.chart_of_accounts.find({}, {"_id": 0}).to_list(100)
    
    # Group by category
    by_category = {}
    for acc in accounts:
        cat = acc.get('category', 'Unknown')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(acc)
    
    # Calculate balances by category
    category_summary = {}
    for cat, accs in by_category.items():
        total_debit = sum(acc.get('balance', 0) for acc in accs if acc.get('normal_balance') == 'debit')
        total_credit = sum(acc.get('balance', 0) for acc in accs if acc.get('normal_balance') == 'credit')
        category_summary[cat] = {
            'count': len(accs),
            'total_debit': total_debit,
            'total_credit': total_credit,
            'accounts': accs
        }
    
    return {
        'total_accounts': len(accounts),
        'categories': list(by_category.keys()),
        'category_summary': category_summary,
        'tb_check': {
            'total_debit': sum(acc.get('balance', 0) for acc in accounts if acc.get('normal_balance') == 'debit'),
            'total_credit': sum(acc.get('balance', 0) for acc in accounts if acc.get('normal_balance') == 'credit')
        }
    }
