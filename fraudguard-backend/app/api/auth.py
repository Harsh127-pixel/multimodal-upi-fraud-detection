from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import logging

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()
logger = logging.getLogger(__name__)

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_pwd)
    db.add(user)
    await db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 7 days expiry as requested
    access_token = create_access_token(subject=user.email)
    refresh_token = create_access_token(subject=user.email, expires_delta=timedelta(days=30))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "id": str(user.id)
        }
    }

from app.api.deps import get_current_user
from sqlalchemy import func
from app.models.transaction import Transaction
from datetime import datetime

@router.get("/me")
async def get_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Calculate account age in days
    age_days = (datetime.utcnow() - current_user.created_at).days

    # Calculate tx count and avg amount
    stmt = select(func.count(Transaction.id), func.avg(Transaction.amount)).where(Transaction.upi_id == current_user.email)
    result = await db.execute(stmt)
    row = result.one_or_none()
    
    tx_count = row[0] if row and row[0] is not None else 0
    avg_amount = row[1] if row and row[1] is not None else 0.0

    return {
        "email": current_user.email,
        "account_age_days": max(1, age_days),
        "tx_count": tx_count,
        "avg_amount": float(avg_amount)
    }
