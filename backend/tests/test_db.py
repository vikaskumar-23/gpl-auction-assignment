import sqlite3
from contextlib import closing

import pytest

from app.db import connect, init_schema
from app.seed import PLAYERS, TEAMS, TOTAL_BUDGET, seed_if_empty


@pytest.fixture
def conn():
    with closing(connect()) as c:
        init_schema(c)
        seed_if_empty(c)
        yield c


def test_seed_runs_once_with_four_teams_and_at_least_12_players(conn):
    seed_if_empty(conn)  # second call must not duplicate anything

    teams = conn.execute(
        "SELECT name, total_budget, remaining_budget FROM teams ORDER BY id"
    ).fetchall()
    assert [t["name"] for t in teams] == TEAMS and len(TEAMS) == 4
    assert all(t["total_budget"] == t["remaining_budget"] == TOTAL_BUDGET for t in teams)

    statuses = [r["status"] for r in conn.execute("SELECT status FROM players")]
    assert len(statuses) == len(PLAYERS) >= 12
    assert set(statuses) == {"available"}


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE players SET skill = 'keeping' WHERE id = 1",
        "UPDATE players SET status = 'in_auction' WHERE id IN (1, 2)",  # one auction at a time
        "UPDATE players SET status = 'sold' WHERE id = 1",  # sold needs a team and a price
        "UPDATE teams SET remaining_budget = -1 WHERE id = 1",
        "INSERT INTO bids (player_id, team_id, amount) VALUES (1, 99, 10)",  # unknown team
    ],
)
def test_schema_rejects_invalid_data(conn, sql):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql)
