"""
tests/test_reports.py

Tests for POST /api/reports/submit and GET /api/reports/blacklist.
DB and Redis are fully mocked so no live services are needed.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from app.core.database import get_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_db_session():
    """Return a fully-mocked AsyncSession."""
    session = AsyncMock()

    # UPIProfile will not exist (returns None) → new profile path
    select_result = MagicMock()
    select_result.scalar_one_or_none.return_value = None
    session.execute.return_value = select_result

    session.add = MagicMock()
    session.commit = AsyncMock()

    # refresh assigns a real UUID to the report
    async def fake_refresh(obj):
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = uuid.uuid4()

    session.refresh = fake_refresh
    return session


async def override_get_db():
    yield make_db_session()


class MockRedis:
    """Minimal async Redis stub."""

    async def sadd(self, key, member):
        return 1

    async def publish(self, channel, message):
        return 1

    async def scard(self, key):
        return 3

    async def sscan(self, key, count=10):
        return (0, ["fraudster@upi", "scammer@bank"])

    async def close(self):
        pass


REPORT_PAYLOAD = {
    "upi_id": "fraudster@upi",
    "fraud_type": "fake_qr",
    "amount_lost": 1500.0,
    "utr_number": "UTR123456789",
    "description": "Paid via fake QR code",
    "evidence_url": "https://img.example.com/ev.png",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_submit_report_returns_case_id():
    """POST /api/reports/submit → 200 with case_id."""
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.api.reports.redis.from_url", return_value=MockRedis()):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/api/reports/submit", json=REPORT_PAYLOAD)

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Report submitted"
    assert "case_id" in data and data["case_id"]
    assert data["upi_id"] == REPORT_PAYLOAD["upi_id"]
    assert isinstance(data["blacklisted"], bool)


@pytest.mark.anyio
async def test_blacklist_count_increases():
    """GET /api/reports/blacklist → count >= 1 and recent is a list."""
    with patch("app.api.reports.redis.from_url", return_value=MockRedis()):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/reports/blacklist")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["count"] >= 1
    assert isinstance(data["recent"], list)
