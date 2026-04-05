from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, cast, Date
from datetime import datetime, timedelta
import os
import redis.asyncio as redis
import logging

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.transaction import Transaction
from app.models.fraud_report import FraudReport

router = APIRouter()
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    # 1. Total Transactions
    total_tx_stmt = select(func.count(Transaction.id))
    total_tx_res = await db.execute(total_tx_stmt)
    total_transactions = total_tx_res.scalar() or 0

    # 2. Total Frauds Blocked (is_fraud = True or score >= 75)
    total_fraud_stmt = select(func.count(Transaction.id)).where(Transaction.is_fraud == True)
    total_fraud_res = await db.execute(total_fraud_stmt)
    total_frauds_blocked = total_fraud_res.scalar() or 0

    # 3. Total Amount Protected (sum amount of fraud transactions)
    sum_amt_stmt = select(func.sum(Transaction.amount)).where(Transaction.is_fraud == True)
    sum_amt_res = await db.execute(sum_amt_stmt)
    total_amount_protected = sum_amt_res.scalar() or 0.0

    # 4. Community Reports
    community_reports_stmt = select(func.count(FraudReport.id))
    community_reports_res = await db.execute(community_reports_stmt)
    community_reports = community_reports_res.scalar() or 0

    # 5. Blacklisted UPI Count (SCARD "community_blacklist")
    blacklisted_upi_count = 0
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        blacklisted_upi_count = await r.scard("community_blacklist")
        await r.close()
    except Exception as e:
        logger.warning(f"Redis integration failed for SCARD: {str(e)}")
        blacklisted_upi_count = 0

    # 6. Fraud by Type
    fraud_by_type_stmt = select(FraudReport.fraud_type, func.count(FraudReport.id)).group_by(FraudReport.fraud_type)
    fraud_by_type_res = await db.execute(fraud_by_type_stmt)
    fraud_by_type_rows = fraud_by_type_res.all()
    
    fraud_by_type_dict = {
        "fake_qr": 0, "impersonation": 0, "lottery": 0, "investment": 0, "other": 0
    }
    for f_type, count in fraud_by_type_rows:
        if f_type in fraud_by_type_dict:
            fraud_by_type_dict[f_type] = count
        else:
            fraud_by_type_dict["other"] += count

    # 7. Daily Fraud Attempts (Last 30 Days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_fraud_stmt = (
        select(cast(Transaction.timestamp, Date).label("date"), func.count(Transaction.id))
        .where(Transaction.is_fraud == True)
        .where(Transaction.timestamp >= thirty_days_ago)
        .group_by(cast(Transaction.timestamp, Date))
        .order_by(cast(Transaction.timestamp, Date))
    )
    daily_fraud_res = await db.execute(daily_fraud_stmt)
    daily_fraud_rows = daily_fraud_res.all()
    # Ensure it's JSON serializable (str(date))
    daily_fraud_attempts = [{"date": str(row[0]), "count": row[1]} for row in daily_fraud_rows]

    # 8. Score Distribution
    distribution_stmt = select(
        func.count(Transaction.id).filter(Transaction.score < 40).label("low"),
        func.count(Transaction.id).filter((Transaction.score >= 40) & (Transaction.score < 75)).label("medium"),
        func.count(Transaction.id).filter(Transaction.score >= 75).label("high")
    )
    distribution_res = await db.execute(distribution_stmt)
    row = distribution_res.one_or_none()
    
    score_distribution = {
        "low": row.low if row else 0,
        "medium": row.medium if row else 0,
        "high": row.high if row else 0
    }

    return {
        "total_transactions": total_transactions,
        "total_frauds_blocked": total_frauds_blocked,
        "total_amount_protected": float(total_amount_protected),
        "community_reports": community_reports,
        "blacklisted_upi_count": blacklisted_upi_count,
        "fraud_by_type": fraud_by_type_dict,
        "daily_fraud_attempts": daily_fraud_attempts,
        "score_distribution": score_distribution
    }
