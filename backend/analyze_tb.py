#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def analyze():
    client = AsyncIOMotorClient('mongodb://mongo:27017')
    db = client.nexora_erp
    
    accounts = await db.chart_of_accounts.find({}).to_list(100)
    
    debit_accounts = [a for a in accounts if a['current_balance'] > 0]
    credit_accounts = [a for a in accounts if a['current_balance'] < 0]
    
    debit_total = sum(a['current_balance'] for a in debit_accounts)
    credit_total = sum(abs(a['current_balance']) for a in credit_accounts)
    
    print(f"\nDEBIT SIDE ACCOUNTS ({len(debit_accounts)}):")
    for a in sorted(debit_accounts, key=lambda x: x['current_balance'], reverse=True):
        print(f"  {a['ledger_name']:40s} {a['current_balance']:>12,.0f}")
    print(f"{'TOTAL DEBIT':40s} {debit_total:>12,.0f}")
    
    print(f"\nCREDIT SIDE ACCOUNTS ({len(credit_accounts)}):")
    for a in sorted(credit_accounts, key=lambda x: x['current_balance']):
        print(f"  {a['ledger_name']:40s} {abs(a['current_balance']):>12,.0f}")
    print(f"{'TOTAL CREDIT':40s} {credit_total:>12,.0f}")
    
    print(f"\nDIFFERENCE: {debit_total - credit_total:>12,.0f}")
    print(f"IN BALANCE: {abs(debit_total - credit_total) < 1}")
    
    # Check transactions
    txns = await db.erp_transactions.find({}).to_list(1000)
    txn_debits = sum(t.get('debit', 0) for t in txns)
    txn_credits = sum(t.get('credit', 0) for t in txns)
    print(f"\nTRANSACTION TOTALS:")
    print(f"  Debit entries:  {txn_debits:>12,.0f}")
    print(f"  Credit entries: {txn_credits:>12,.0f}")
    print(f"  Difference:     {txn_debits - txn_credits:>12,.0f}")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(analyze())
