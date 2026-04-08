from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float
from app.core.database import Base

class UPIProfile(Base):
    __tablename__ = "upi_profiles"

    upi_id                 = Column(String, primary_key=True, index=True)
    registration_date      = Column(DateTime, default=datetime.utcnow, nullable=False)

    # --- legacy columns (kept for backward compat) ---
    transaction_count      = Column(Integer, default=0, nullable=False)
    fraud_count            = Column(Integer, default=0, nullable=False)
    risk_score             = Column(Integer, default=30, nullable=False)
    blacklisted            = Column(Boolean, default=False, nullable=False)

    # --- M2 feature columns ---
    account_age_days       = Column(Integer, default=0, nullable=True)
    total_tx_volume        = Column(Float,   default=0.0, nullable=True)
    unique_senders         = Column(Integer, default=0,   nullable=True)
    name_handle_similarity = Column(Float,   default=0.5, nullable=True)
    avg_tx_amount          = Column(Float,   default=0.0, nullable=True)
    tx_count_last_7d       = Column(Integer, default=0,   nullable=True)
    tx_count               = Column(Integer, default=0,   nullable=True)
