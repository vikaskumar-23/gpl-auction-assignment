import sqlite3

from app.db import transaction

PLAYER_COLUMNS = "id, name, skill, base_price, status, sold_price, team_id"


class AuctionError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def money(lakh: int) -> str:
    # 75 -> ₹75 L, 150 -> ₹1.5 Cr
    return f"₹{lakh / 100:g} Cr" if lakh >= 100 else f"₹{lakh} L"


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


def _require_current_player(conn) -> dict:
    player = _current_player(conn)
    if player is None:
        raise AuctionError(409, "NO_ACTIVE_AUCTION", "No player is up for auction right now.")
    return player


# writes


def start_auction(conn: sqlite3.Connection, player_id: int) -> dict:
    with transaction(conn):
        current = _current_player(conn)
        if current:
            raise AuctionError(
                409,
                "AUCTION_IN_PROGRESS",
                f"{current['name']} is already up for auction. Accept or reject that round first.",
            )
        player = _player(conn, player_id)
        if player is None:
            raise AuctionError(404, "PLAYER_NOT_FOUND", f"There is no player with id {player_id}.")
        if player["status"] != "available":
            raise AuctionError(
                409, "PLAYER_NOT_AVAILABLE", f"{player['name']} has already been sold."
            )
        conn.execute("UPDATE players SET status = 'in_auction' WHERE id = ?", (player_id,))
        return current_auction(conn)


def place_bid(conn: sqlite3.Connection, team_id: int, amount: int) -> dict:
    with transaction(conn):
        player = _require_current_player(conn)
        team = conn.execute(
            "SELECT name, remaining_budget FROM teams WHERE id = ?", (team_id,)
        ).fetchone()
        if team is None:
            raise AuctionError(404, "TEAM_NOT_FOUND", f"There is no team with id {team_id}.")
        bids = _bids(conn, player["id"])
        top = bids[0] if bids else None
        if top and top["team_id"] == team_id:
            raise AuctionError(
                409,
                "ALREADY_HIGHEST_BIDDER",
                f"{team['name']} already hold the highest bid. Wait for another team to bid.",
            )
        if amount <= player["base_price"]:
            raise AuctionError(
                400,
                "BID_NOT_ABOVE_BASE",
                f"Bid must be more than the base price of {money(player['base_price'])}.",
            )
        if top and amount <= top["amount"]:
            raise AuctionError(
                400,
                "BID_NOT_ABOVE_HIGHEST",
                f"Bid must be more than the current highest bid of {money(top['amount'])}.",
            )
        conn.execute(
            "INSERT INTO bids (player_id, team_id, amount) VALUES (?, ?, ?)",
            (player["id"], team_id, amount),
        )
        return _bids(conn, player["id"])[0]


def accept_bid(conn: sqlite3.Connection, bid_id: int) -> dict:
    # the auctioneer accepts the bid they saw; if a higher one came in meanwhile, refuse
    with transaction(conn):
        player = _require_current_player(conn)
        bids = _bids(conn, player["id"])
        if not bids:
            raise AuctionError(
                409,
                "NO_BIDS",
                f"No bids for {player['name']} yet. Reject the round to return them to the pool.",
            )
        top = bids[0]
        if top["id"] != bid_id:
            raise AuctionError(
                409,
                "BID_NOT_HIGHEST",
                f"That is no longer the highest bid: {top['team_name']} now lead "
                f"with {money(top['amount'])}.",
            )
        conn.execute(
            "UPDATE teams SET remaining_budget = remaining_budget - ? WHERE id = ?",
            (top["amount"], top["team_id"]),
        )
        conn.execute(
            "UPDATE players SET status = 'sold', sold_price = ?, team_id = ? WHERE id = ?",
            (top["amount"], top["team_id"], player["id"]),
        )
        return _player(conn, player["id"])


def reject_round(conn: sqlite3.Connection) -> dict:
    with transaction(conn):
        player = _require_current_player(conn)
        conn.execute(
            "UPDATE bids SET voided = 1 WHERE player_id = ? AND voided = 0", (player["id"],)
        )
        conn.execute("UPDATE players SET status = 'available' WHERE id = ?", (player["id"],))
        return _player(conn, player["id"])
