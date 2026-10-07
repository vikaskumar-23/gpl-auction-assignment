from fastapi.testclient import TestClient

from app.main import app
from app.seed import TOTAL_BUDGET

PLAYER, OTHER_PLAYER = 9, 14  # Meera Shetye (base 50), Neel Parab (base 20)


def code(resp):
    return resp.json()["error"]["code"]


def test_auctioneer_starts_an_auction_for_one_player(client, start):
    r = start(PLAYER)
    assert r.status_code == 200
    assert r.json()["player"]["id"] == PLAYER
    assert r.json()["player"]["status"] == "in_auction"
    assert r.json()["bids"] == []
    assert client.get("/api/auction").json()["player"]["id"] == PLAYER


def test_only_one_auction_at_a_time(start):
    start(PLAYER)
    r = start(OTHER_PLAYER)
    assert r.status_code == 409 and code(r) == "AUCTION_IN_PROGRESS"


def test_unknown_player_cannot_be_auctioned(start):
    r = start(999)
    assert r.status_code == 404 and code(r) == "PLAYER_NOT_FOUND"


def test_only_the_auctioneer_can_start(client):
    for headers in ({}, {"X-Role": "viewer"}, {"X-Role": "manager"}):
        r = client.post("/api/auction/start", json={"player_id": PLAYER}, headers=headers)
        assert r.status_code == 403 and code(r) == "FORBIDDEN"


def test_malformed_start_request_gets_a_readable_error(client):
    r = client.post(
        "/api/auction/start",
        json={"player_id": "abc"},
        headers={"X-Role": "auctioneer"},
    )
    assert r.status_code == 422 and code(r) == "VALIDATION_ERROR"
    assert r.json()["error"]["message"].startswith("player_id:")


def test_accept_moves_player_onto_the_winning_team_roster(client, start, bid, accept):
    base = start(PLAYER).json()["player"]["base_price"]
    bid(2, base + 10)
    bid(3, base + 25)

    r = accept()
    assert r.status_code == 200
    sold = r.json()
    assert (sold["status"], sold["team_id"], sold["sold_price"]) == ("sold", 3, base + 25)

    teams = {t["id"]: t for t in client.get("/api/teams").json()}
    assert [(p["id"], p["sold_price"]) for p in teams[3]["players"]] == [(PLAYER, base + 25)]
    assert teams[3]["remaining_budget"] == TOTAL_BUDGET - (base + 25)
    assert teams[2]["remaining_budget"] == TOTAL_BUDGET and teams[2]["players"] == []

    available = [p["id"] for p in client.get("/api/players").json() if p["status"] == "available"]
    assert PLAYER not in available
    assert client.get("/api/auction").json() == {"player": None, "bids": []}


def test_accept_needs_a_bid(start, accept):
    start(PLAYER)
    r = accept(bid_id=1)
    assert r.status_code == 409 and code(r) == "NO_BIDS"


def test_accept_refuses_a_bid_that_was_just_outbid(client, start, bid, accept):
    base = start(PLAYER).json()["player"]["base_price"]
    first = bid(1, base + 10).json()["id"]
    bid(2, base + 20)
    r = accept(bid_id=first)
    assert r.status_code == 409 and code(r) == "BID_NOT_HIGHEST"
    assert client.get("/api/auction").json()["player"]["id"] == PLAYER  # still on the block


def test_sold_player_cannot_be_auctioned_again(start, bid, accept):
    base = start(PLAYER).json()["player"]["base_price"]
    bid(1, base + 10)
    accept()
    r = start(PLAYER)
    assert r.status_code == 409 and code(r) == "PLAYER_NOT_AVAILABLE"


def test_reject_leaves_player_available_and_unassigned(client, start, bid, reject):
    base = start(PLAYER).json()["player"]["base_price"]
    bid(1, base + 10)

    r = reject()
    assert r.status_code == 200
    player = r.json()
    assert (player["status"], player["team_id"], player["sold_price"]) == ("available", None, None)
    for t in client.get("/api/teams").json():
        assert t["remaining_budget"] == TOTAL_BUDGET and t["players"] == []
    assert client.get("/api/auction").json()["player"] is None


def test_rejected_bids_do_not_carry_into_the_next_round(start, bid, reject):
    base = start(PLAYER).json()["player"]["base_price"]
    bid(1, base + 50)
    reject()
    assert start(PLAYER).json()["bids"] == []
    assert bid(1, base + 1).status_code == 201


def test_accept_or_reject_needs_an_active_auction(accept, reject):
    for r in (accept(bid_id=1), reject()):
        assert r.status_code == 409 and code(r) == "NO_ACTIVE_AUCTION"


def test_only_the_auctioneer_can_accept_or_reject(client):
    manager = {"X-Role": "manager"}
    assert (
        client.post("/api/auction/accept", json={"bid_id": 1}, headers=manager).status_code == 403
    )
    assert client.post("/api/auction/reject", headers=manager).status_code == 403


def test_rosters_and_budgets_survive_a_restart(client, start, bid, accept):
    base = start(PLAYER).json()["player"]["base_price"]
    bid(4, base + 30)
    accept()
    before = client.get("/api/teams").json()

    with TestClient(app) as restarted:  # new app instance, same db file
        assert restarted.get("/api/teams").json() == before
