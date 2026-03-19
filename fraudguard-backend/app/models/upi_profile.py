from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from app.core.database import Base

class UPIProfile(Base):
    __tablename__ = "upi_profiles"

    upi_id = Column(String, primary_key=True, index=True)
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    transaction_count = Column(Integer, default=0, nullable=False)
    fraud_count = Column(Integer, default=0, nullable=False)
    risk_score = Column(Integer, default=30, nullable=False)
    blacklisted = Column(Boolean, default=False, nullable=False)
