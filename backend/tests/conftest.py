import pytest
from fastapi.testclient import TestClient

from app.main import app

AUCTIONEER = {"X-Role": "auctioneer"}
MANAGER = {"X-Role": "manager"}


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    # fresh database for every test
    monkeypatch.setenv("GPL_DB_PATH", str(tmp_path / "test.db"))


@pytest.fixture
def client():
    with TestClient(app) as c:  # runs startup: schema + seed
        yield c


@pytest.fixture
def start(client):
    return lambda player_id: client.post(
        "/api/auction/start", json={"player_id": player_id}, headers=AUCTIONEER
    )


@pytest.fixture
def bid(client):
    return lambda team_id, amount: client.post(
        "/api/auction/bids", json={"team_id": team_id, "amount": amount}, headers=MANAGER
    )


@pytest.fixture
def accept(client):
    def _accept(bid_id=None):
        if bid_id is None:  # default: the current highest bid
            bid_id = client.get("/api/auction").json()["bids"][0]["id"]
        return client.post("/api/auction/accept", json={"bid_id": bid_id}, headers=AUCTIONEER)

    return _accept


@pytest.fixture
def reject(client):
    return lambda: client.post("/api/auction/reject", headers=AUCTIONEER)
