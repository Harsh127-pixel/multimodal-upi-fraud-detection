import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
import asyncio

from main import app
from app.core.database import get_db

# Mock DB dependency
async def override_get_db():
    mock_session = MagicMock()
    mock_session.commit = MagicMock(return_value=asyncio.Future())
    mock_session.commit.return_value.set_result(None)
    yield mock_session

app.dependency_overrides[get_db] = override_get_db

@pytest.mark.asyncio
async def test_score_high_fraud():
    """Test 1: mock high fraud probability (0.9)"""
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.1, 0.9]]
    
    with patch("app.ml.model_registry.registry.get_m1_scorer", return_value=mock_model):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "upi_id": "new.fraud@upi",
                "amount": 15000,
                "device_id": "unknown-device",
                "timestamp": "2025-01-15T02:30:00",
                "payer_upi_id": "victim@upi",
                "payer_device_id": "victim-device",
                "payer_account_age_days": 365,
                "is_post_call": True,
                "user_avg_amount": 500,
                "user_tx_count": 10
            }
            response = await ac.post("/api/transactions/score", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["score"] == 90
            assert data["action"] == "block"
            assert "Payment initiated right after unknown call" in data["risk_signals"]

@pytest.mark.asyncio
async def test_score_low_fraud():
    """Test 2: mock low fraud probability (0.1)"""
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.9, 0.1]]
    
    with patch("app.ml.model_registry.registry.get_m1_scorer", return_value=mock_model):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "upi_id": "trusted@bank",
                "amount": 200,
                "device_id": "my-device",
                "timestamp": "2025-01-15T10:00:00",
                "payer_upi_id": "me@upi",
                "payer_device_id": "my-device",
                "payer_account_age_days": 730,
                "is_post_call": False,
                "user_avg_amount": 300,
                "user_tx_count": 2
            }
            response = await ac.post("/api/transactions/score", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["score"] == 10
            assert data["action"] == "allow"
            assert len(data["risk_signals"]) == 0
