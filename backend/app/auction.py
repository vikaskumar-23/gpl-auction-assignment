import sqlite3

PLAYER_COLUMNS = "id, name, skill, base_price, status, sold_price, team_id"


# reads


def list_players(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(f"SELECT {PLAYER_COLUMNS} FROM players ORDER BY id")
    return [dict(r) for r in rows]


def list_teams(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM teams ORDER BY id")
    teams = {r["id"]: dict(r, players=[]) for r in rows}
    sold = conn.execute(
        f"SELECT {PLAYER_COLUMNS} FROM players WHERE status = 'sold' ORDER BY sold_price DESC"
    )
    for p in sold:
        teams[p["team_id"]]["players"].append(dict(p))
    return list(teams.values())


def current_auction(conn: sqlite3.Connection) -> dict:
    player = _current_player(conn)
    return {"player": player, "bids": _bids(conn, player["id"]) if player else []}


def snapshot(conn: sqlite3.Connection) -> dict:
    return {
        "players": list_players(conn),
        "teams": list_teams(conn),
        "auction": current_auction(conn),
    }


def _player(conn, player_id: int) -> dict | None:
    row = conn.execute(
        f"SELECT {PLAYER_COLUMNS} FROM players WHERE id = ?", (player_id,)
    ).fetchone()
    return dict(row) if row else None


def _current_player(conn) -> dict | None:
    row = conn.execute(
        f"SELECT {PLAYER_COLUMNS} FROM players WHERE status = 'in_auction'"
    ).fetchone()
    return dict(row) if row else None


def _bids(conn, player_id: int) -> list[dict]:
    # current round only (rejected rounds are voided), highest first
    rows = conn.execute(
        """SELECT b.id, b.player_id, b.team_id, t.name AS team_name, b.amount, b.created_at
           FROM bids b JOIN teams t ON t.id = b.team_id
           WHERE b.player_id = ? AND b.voided = 0
           ORDER BY b.amount DESC""",
        (player_id,),
    )
    return [dict(r) for r in rows]
