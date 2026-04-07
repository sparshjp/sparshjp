"""Multi-Currency & Forex — Exchange rates, forex gain/loss, revaluation."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid
import httpx

router = APIRouter(prefix="/forex")
db = None

DEFAULT_RATES = {"USD": 84.50, "GBP": 106.80, "EUR": 92.30, "AUD": 55.60, "CAD": 62.10, "SGD": 63.20, "JPY": 0.56, "AED": 23.01}

def set_db(database):
    global db
    db = database

@router.get("/rates")
async def get_rates():
    saved = await db.forex_rates.find({}, {"_id": 0}).sort("date", -1).to_list(1)
    if saved:
        return saved[0]
    return {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "base": "INR", "rates": DEFAULT_RATES}

@router.post("/rates")
async def update_rates(body: dict):
    record = {
        "id": str(uuid.uuid4()),
        "date": body.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "base": "INR",
        "rates": body.get("rates", DEFAULT_RATES),
        "source": body.get("source", "manual"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.forex_rates.insert_one(record)
    record.pop("_id", None)
    return record

@router.post("/rates/fetch-live")
async def fetch_live_rates():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://api.exchangerate-api.com/v4/latest/INR")
            if resp.status_code == 200:
                data = resp.json()
                raw_rates = data.get("rates", {})
                rates = {cur: round(1 / raw_rates.get(cur, 1), 2) for cur in DEFAULT_RATES if cur in raw_rates}
                record = {"id": str(uuid.uuid4()), "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "base": "INR", "rates": rates, "source": "exchangerate-api", "updated_at": datetime.now(timezone.utc).isoformat()}
                await db.forex_rates.insert_one(record)
                record.pop("_id", None)
                return record
    except Exception:
        pass
    return {"status": "fallback", "rates": DEFAULT_RATES, "source": "default"}

@router.get("/transactions")
async def list_forex_transactions():
    return await db.forex_transactions.find({}, {"_id": 0}).sort("date", -1).to_list(200)

@router.post("/transactions")
async def create_forex_transaction(body: dict):
    txn = {
        "id": str(uuid.uuid4()),
        "type": body.get("type", "invoice"),
        "reference_id": body.get("reference_id", ""),
        "reference_name": body.get("reference_name", ""),
        "currency": body.get("currency", "USD"),
        "foreign_amount": body.get("foreign_amount", 0),
        "booking_rate": body.get("booking_rate", 0),
        "booking_inr": body.get("foreign_amount", 0) * body.get("booking_rate", 0),
        "settlement_rate": body.get("settlement_rate"),
        "settlement_inr": None,
        "forex_gain_loss": None,
        "date": body.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "settled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.forex_transactions.insert_one(txn)
    txn.pop("_id", None)
    return txn

@router.post("/transactions/{txn_id}/settle")
async def settle_forex(txn_id: str, body: dict):
    txn = await db.forex_transactions.find_one({"id": txn_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    settlement_rate = body.get("settlement_rate", 0)
    settlement_inr = txn["foreign_amount"] * settlement_rate
    gain_loss = settlement_inr - txn["booking_inr"]
    await db.forex_transactions.update_one({"id": txn_id}, {"$set": {
        "settlement_rate": settlement_rate, "settlement_inr": settlement_inr,
        "forex_gain_loss": round(gain_loss, 2), "settled": True,
        "settled_at": datetime.now(timezone.utc).isoformat(),
    }})
    return await db.forex_transactions.find_one({"id": txn_id}, {"_id": 0})

@router.get("/revaluation")
async def unrealized_revaluation():
    unsettled = await db.forex_transactions.find({"settled": False}, {"_id": 0}).to_list(500)
    rates_doc = await db.forex_rates.find_one({}, {"_id": 0}, sort=[("date", -1)])
    current_rates = rates_doc.get("rates", DEFAULT_RATES) if rates_doc else DEFAULT_RATES
    result = []
    total_unrealized = 0
    for txn in unsettled:
        cur = txn.get("currency", "USD")
        current_rate = current_rates.get(cur, txn.get("booking_rate", 0))
        current_inr = txn["foreign_amount"] * current_rate
        unrealized = current_inr - txn["booking_inr"]
        total_unrealized += unrealized
        result.append({**txn, "current_rate": current_rate, "current_inr": round(current_inr, 2), "unrealized_gain_loss": round(unrealized, 2)})
    return {"transactions": result, "total_unrealized_gain_loss": round(total_unrealized, 2), "as_of": datetime.now(timezone.utc).isoformat()}
