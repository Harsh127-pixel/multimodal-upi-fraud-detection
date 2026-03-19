import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class FraudReport(Base):
    __tablename__ = "fraud_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upi_id = Column(String, index=True, nullable=False)
    fraud_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    utr_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    evidence_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
