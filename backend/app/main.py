import asyncio
import sqlite3
from collections.abc import AsyncIterable
from contextlib import asynccontextmanager, closing
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from fastapi.staticfiles import StaticFiles

from app import auction
from app.auction import AuctionError
from app.db import connect, get_conn, init_schema
from app.schemas import AcceptRequest, Auction, Bid, BidRequest, Player, StartRequest, Team
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    with closing(connect()) as conn:
        init_schema(conn)
        seed_if_empty(conn)
    yield


app = FastAPI(title="GPL Auction API", lifespan=lifespan)
Conn = Annotated[sqlite3.Connection, Depends(get_conn)]

# bumped on every write; open event streams watch it (works for a single server process)
_version = 0


def notify() -> None:
    global _version
    _version += 1


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


@app.exception_handler(AuctionError)
async def on_auction_error(request: Request, exc: AuctionError):
    return error(exc.status, exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def on_validation_error(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    # loc is like ("body", "amount")
    field = ".".join(str(part) for part in first["loc"][1:]) or "body"
    return error(422, "VALIDATION_ERROR", f"{field}: {first['msg']}")


def require_role(role: str):
    # no real auth (out of scope): the client sends its role in X-Role
    def check(x_role: Annotated[str | None, Header()] = None):
        if x_role != role:
            raise AuctionError(403, "FORBIDDEN", f"Only the {role} can do this.")

    return Depends(check)


# reads


@app.get("/api/players", response_model=list[Player])
def list_players(conn: Conn):
    return auction.list_players(conn)


@app.get("/api/teams", response_model=list[Team])
def list_teams(conn: Conn):
    return auction.list_teams(conn)


@app.get("/api/auction", response_model=Auction)
def get_auction(conn: Conn):
    return auction.current_auction(conn)


# writes


@app.post("/api/auction/start", response_model=Auction, dependencies=[require_role("auctioneer")])
def start_auction(body: StartRequest, conn: Conn):
    result = auction.start_auction(conn, body.player_id)
    notify()
    return result


@app.post(
    "/api/auction/bids", response_model=Bid, status_code=201, dependencies=[require_role("manager")]
)
def place_bid(body: BidRequest, conn: Conn):
    result = auction.place_bid(conn, body.team_id, body.amount)
    notify()
    return result


@app.post("/api/auction/accept", response_model=Player, dependencies=[require_role("auctioneer")])
def accept_bid(body: AcceptRequest, conn: Conn):
    result = auction.accept_bid(conn, body.bid_id)
    notify()
    return result


@app.post("/api/auction/reject", response_model=Player, dependencies=[require_role("auctioneer")])
def reject_round(conn: Conn):
    result = auction.reject_round(conn)
    notify()
    return result


# live updates

TICK = 0.25
PING_EVERY = 15  # seconds without changes before a ping


@app.get("/api/events", response_class=EventSourceResponse)
async def events() -> AsyncIterable[ServerSentEvent]:
    seen, quiet = None, 0.0
    while True:
        if seen != _version:
            seen, quiet = _version, 0.0
            with closing(connect()) as conn:
                state = auction.snapshot(conn)
            yield ServerSentEvent(event="state", data=state)
        elif quiet >= PING_EVERY:
            # lets the browser notice a dead connection
            quiet = 0.0
            yield ServerSentEvent(event="ping", data=1)
        await asyncio.sleep(TICK)
        quiet += TICK


# serve the built frontend (npm run build) from the same server
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
