import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upi_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    score = Column(Integer, nullable=False)
    is_fraud = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    device_id = Column(String, nullable=False)
    post_call_flag = Column(Boolean, default=False, nullable=False)
