from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import csv
import io

router = APIRouter(prefix="/bank-recon", tags=["Bank Reconciliation"])

db = None

def set_db(database):
    global db
    db = database

# Models
class BankStatementRow(BaseModel):
    date: str
    description: str
    debit: float = 0.0
    credit: float = 0.0
    balance: float = 0.0

class MatchRequest(BaseModel):
    bank_entry_id: str
    book_entry_id: str
    account: str

class UnmatchRequest(BaseModel):
    bank_entry_id: str
    account: str

# Helper function to parse CSV
def parse_bank_statement_csv(content: str) -> List[dict]:
    """
    Parse bank statement CSV. Expected columns:
    Date, Description, Debit, Credit, Balance
    """
    rows = []
    reader = csv.DictReader(io.StringIO(content))
    
    for row in reader:
        try:
            # Handle various column name formats
            date_str = row.get('Date') or row.get('date') or row.get('DATE') or ""
            description = row.get('Description') or row.get('description') or row.get('DESCRIPTION') or row.get('Narration') or ""
            debit_str = row.get('Debit') or row.get('debit') or row.get('DEBIT') or row.get('Withdrawal') or "0"
            credit_str = row.get('Credit') or row.get('credit') or row.get('CREDIT') or row.get('Deposit') or "0"
            balance_str = row.get('Balance') or row.get('balance') or row.get('BALANCE') or "0"
            
            # Clean and convert amounts
            debit = float(debit_str.replace(',', '').strip() or 0)
            credit = float(credit_str.replace(',', '').strip() or 0)
            balance = float(balance_str.replace(',', '').strip() or 0)
            
            # Parse date (try multiple formats)
            date_obj = None
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    break
                except ValueError:
                    continue
            
            if not date_obj:
                continue  # Skip invalid date rows
            
            rows.append({
                'date': date_obj.strftime('%Y-%m-%d'),
                'description': description.strip(),
                'debit': debit,
                'credit': credit,
                'balance': balance
            })
        except Exception:
            # Skip malformed rows
            continue
    
    return rows

# Endpoint 1: Upload bank statement
@router.post("/statements")
async def upload_bank_statement(account: str, file: UploadFile = File(...)):
    """
    Upload and parse bank statement CSV.
    Creates unmatched bank entries in bank_statements collection.
    """
    try:
        # Validate account exists
        account_doc = await db.chart_of_accounts.find_one({"ledger_name": account})
        if not account_doc:
            raise HTTPException(status_code=404, detail=f"Account '{account}' not found")
        
        # Read and parse CSV
        content = await file.read()
        csv_content = content.decode('utf-8')
        parsed_rows = parse_bank_statement_csv(csv_content)
        
        if not parsed_rows:
            raise HTTPException(status_code=400, detail="No valid rows found in CSV")
        
        # Store bank statement rows
        inserted_count = 0
        for row in parsed_rows:
            # Check if entry already exists (same account, date, amount, description)
            existing = await db.bank_statements.find_one({
                "account": account,
                "date": row['date'],
                "debit": row['debit'],
                "credit": row['credit'],
                "description": row['description']
            })
            
            if not existing:
                bank_entry = {
                    "id": str(uuid.uuid4()),
                    "account": account,
                    "date": row['date'],
                    "description": row['description'],
                    "debit": row['debit'],
                    "credit": row['credit'],
                    "balance": row['balance'],
                    "matched": False,
                    "matched_with": None,
                    "matched_date": None,
                    "uploaded_at": datetime.now(timezone.utc).isoformat()
                }
                await db.bank_statements.insert_one(bank_entry)
                inserted_count += 1
        
        return {
            "message": "Bank statement uploaded successfully",
            "total_rows": len(parsed_rows),
            "inserted_rows": inserted_count,
            "account": account
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 2: Get unmatched entries
@router.get("/unmatched")
async def get_unmatched_entries(account: str):
    """
    Get unmatched bank and book entries for an account.
    Auto-match algorithm: compare amount and date within 3 days.
    """
    try:
        # Validate account
        account_doc = await db.chart_of_accounts.find_one({"ledger_name": account})
        if not account_doc:
            raise HTTPException(status_code=404, detail=f"Account '{account}' not found")
        
        # Get unmatched bank entries
        bank_entries = await db.bank_statements.find(
            {"account": account, "matched": False},
            {"_id": 0}
        ).sort("date", -1).to_list(length=1000)
        
        # Get unmatched book entries (from erp_transactions)
        book_entries = await db.erp_transactions.find(
            {"account": account, "bank_reconciled": {"$ne": True}},
            {"_id": 0}
        ).sort("date", -1).to_list(length=1000)
        
        # Auto-match suggestions
        suggestions = []
        matched_bank_ids = set()
        matched_book_ids = set()
        
        for bank_entry in bank_entries:
            if bank_entry['id'] in matched_bank_ids:
                continue
            
            bank_date = datetime.strptime(bank_entry['date'], '%Y-%m-%d')
            bank_amount = bank_entry['credit'] - bank_entry['debit']  # Net amount
            
            for book_entry in book_entries:
                if book_entry['id'] in matched_book_ids:
                    continue
                
                book_date = datetime.strptime(book_entry['date'], '%Y-%m-%d')
                book_amount = book_entry['credit'] - book_entry['debit']  # Net amount
                
                # Check if amounts match
                if abs(bank_amount - book_amount) < 0.01:  # Floating point tolerance
                    # Check if dates are within 3 days
                    date_diff = abs((bank_date - book_date).days)
                    if date_diff <= 3:
                        suggestions.append({
                            "bank_entry_id": bank_entry['id'],
                            "book_entry_id": book_entry['id'],
                            "amount": bank_amount,
                            "bank_date": bank_entry['date'],
                            "book_date": book_entry['date'],
                            "date_diff_days": date_diff,
                            "confidence": "high" if date_diff == 0 else "medium"
                        })
                        matched_bank_ids.add(bank_entry['id'])
                        matched_book_ids.add(book_entry['id'])
                        break
        
        return {
            "account": account,
            "unmatched_bank_entries": len(bank_entries),
            "unmatched_book_entries": len(book_entries),
            "auto_match_suggestions": len(suggestions),
            "bank_entries": bank_entries,
            "book_entries": book_entries,
            "suggestions": suggestions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 3: Match entries
@router.post("/match")
async def match_entries(request: MatchRequest):
    """
    Match a bank entry with a book entry.
    """
    try:
        # Validate account
        account_doc = await db.chart_of_accounts.find_one({"name": request.account})
        if not account_doc:
            raise HTTPException(status_code=404, detail=f"Account '{request.account}' not found")
        
        # Get bank entry
        bank_entry = await db.bank_statements.find_one(
            {"id": request.bank_entry_id, "account": request.account}
        )
        if not bank_entry:
            raise HTTPException(status_code=404, detail="Bank entry not found")
        
        if bank_entry.get('matched'):
            raise HTTPException(status_code=400, detail="Bank entry already matched")
        
        # Get book entry
        book_entry = await db.erp_transactions.find_one(
            {"id": request.book_entry_id, "account": request.account}
        )
        if not book_entry:
            raise HTTPException(status_code=404, detail="Book entry not found")
        
        if book_entry.get('bank_reconciled'):
            raise HTTPException(status_code=400, detail="Book entry already reconciled")
        
        # Validate amounts match (within tolerance)
        bank_amount = bank_entry['credit'] - bank_entry['debit']
        book_amount = book_entry['credit'] - book_entry['debit']
        
        if abs(bank_amount - book_amount) >= 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Amounts do not match. Bank: {bank_amount}, Book: {book_amount}"
            )
        
        # Update bank entry
        matched_date = datetime.now(timezone.utc).isoformat()
        await db.bank_statements.update_one(
            {"id": request.bank_entry_id},
            {
                "$set": {
                    "matched": True,
                    "matched_with": request.book_entry_id,
                    "matched_date": matched_date
                }
            }
        )
        
        # Update book entry
        await db.erp_transactions.update_one(
            {"id": request.book_entry_id},
            {
                "$set": {
                    "bank_reconciled": True,
                    "bank_reconciled_with": request.bank_entry_id,
                    "bank_reconciled_date": matched_date
                }
            }
        )
        
        return {
            "message": "Entries matched successfully",
            "bank_entry_id": request.bank_entry_id,
            "book_entry_id": request.book_entry_id,
            "matched_date": matched_date
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 4: Reconciliation summary
@router.get("/summary")
async def get_reconciliation_summary(account: str):
    """
    Get reconciliation summary for an account.
    """
    try:
        # Validate account
        account_doc = await db.chart_of_accounts.find_one({"ledger_name": account})
        if not account_doc:
            raise HTTPException(status_code=404, detail=f"Account '{account}' not found")
        
        # Calculate book balance (from erp_transactions)
        book_transactions = await db.erp_transactions.find(
            {"account": account}
        ).to_list(length=10000)
        
        book_balance = 0.0
        for txn in book_transactions:
            book_balance += txn.get('debit', 0) - txn.get('credit', 0)
        
        # Get latest bank balance (from last bank statement entry)
        latest_bank_entry = await db.bank_statements.find_one(
            {"account": account},
            sort=[("date", -1), ("uploaded_at", -1)]
        )
        
        bank_balance = latest_bank_entry.get('balance', 0.0) if latest_bank_entry else 0.0
        
        # Count unmatched entries
        unmatched_bank_count = await db.bank_statements.count_documents(
            {"account": account, "matched": False}
        )
        
        unmatched_book_count = await db.erp_transactions.count_documents(
            {"account": account, "bank_reconciled": {"$ne": True}}
        )
        
        # Count matched entries
        matched_bank_count = await db.bank_statements.count_documents(
            {"account": account, "matched": True}
        )
        
        matched_book_count = await db.erp_transactions.count_documents(
            {"account": account, "bank_reconciled": True}
        )
        
        # Calculate difference
        difference = book_balance - bank_balance
        
        # Get unmatched amounts
        unmatched_bank_entries = await db.bank_statements.find(
            {"account": account, "matched": False},
            {"_id": 0, "debit": 1, "credit": 1}
        ).to_list(length=10000)
        
        unmatched_bank_amount = sum(
            entry.get('credit', 0) - entry.get('debit', 0)
            for entry in unmatched_bank_entries
        )
        
        unmatched_book_entries = await db.erp_transactions.find(
            {"account": account, "bank_reconciled": {"$ne": True}},
            {"_id": 0, "debit": 1, "credit": 1}
        ).to_list(length=10000)
        
        unmatched_book_amount = sum(
            entry.get('debit', 0) - entry.get('credit', 0)
            for entry in unmatched_book_entries
        )
        
        return {
            "account": account,
            "book_balance": round(book_balance, 2),
            "bank_balance": round(bank_balance, 2),
            "difference": round(difference, 2),
            "unmatched_bank_count": unmatched_bank_count,
            "unmatched_book_count": unmatched_book_count,
            "matched_bank_count": matched_bank_count,
            "matched_book_count": matched_book_count,
            "unmatched_bank_amount": round(unmatched_bank_amount, 2),
            "unmatched_book_amount": round(unmatched_book_amount, 2),
            "reconciliation_status": "reconciled" if difference == 0 and unmatched_bank_count == 0 and unmatched_book_count == 0 else "pending",
            "last_bank_statement_date": latest_bank_entry.get('date') if latest_bank_entry else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 5: Unmatch entries
@router.post("/unmatch")
async def unmatch_entries(request: UnmatchRequest):
    """
    Unmatch a previously matched bank entry.
    """
    try:
        # Validate account
        account_doc = await db.chart_of_accounts.find_one({"name": request.account})
        if not account_doc:
            raise HTTPException(status_code=404, detail=f"Account '{request.account}' not found")
        
        # Get bank entry
        bank_entry = await db.bank_statements.find_one(
            {"id": request.bank_entry_id, "account": request.account}
        )
        if not bank_entry:
            raise HTTPException(status_code=404, detail="Bank entry not found")
        
        if not bank_entry.get('matched'):
            raise HTTPException(status_code=400, detail="Bank entry is not matched")
        
        book_entry_id = bank_entry.get('matched_with')
        
        # Update bank entry
        await db.bank_statements.update_one(
            {"id": request.bank_entry_id},
            {
                "$set": {
                    "matched": False,
                    "matched_with": None,
                    "matched_date": None
                }
            }
        )
        
        # Update book entry if exists
        if book_entry_id:
            await db.erp_transactions.update_one(
                {"id": book_entry_id},
                {
                    "$set": {
                        "bank_reconciled": False,
                        "bank_reconciled_with": None,
                        "bank_reconciled_date": None
                    }
                }
            )
        
        return {
            "message": "Entries unmatched successfully",
            "bank_entry_id": request.bank_entry_id,
            "book_entry_id": book_entry_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
