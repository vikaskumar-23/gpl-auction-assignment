from app.seed import PLAYERS, TEAMS, TOTAL_BUDGET


def test_lists_preloaded_players_all_available(client):
    players = client.get("/api/players").json()
    assert len(players) == len(PLAYERS)
    assert {p["status"] for p in players} == {"available"}
    assert set(players[0]) == {
        "id",
        "name",
        "skill",
        "base_price",
        "status",
        "sold_price",
        "team_id",
    }


def test_lists_four_teams_with_full_budgets_and_empty_rosters(client):
    teams = client.get("/api/teams").json()
    assert [t["name"] for t in teams] == TEAMS
    for t in teams:
        assert t["total_budget"] == t["remaining_budget"] == TOTAL_BUDGET
        assert t["players"] == []


def test_no_auction_running_initially(client):
    assert client.get("/api/auction").json() == {"player": None, "bids": []}
