import sqlite3
from contextlib import asynccontextmanager, closing
from typing import Annotated

from fastapi import Depends, FastAPI

from app import auction
from app.db import connect, get_conn, init_schema
from app.schemas import Auction, Player, Team
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    with closing(connect()) as conn:
        init_schema(conn)
        seed_if_empty(conn)
    yield


app = FastAPI(title="GPL Auction API", lifespan=lifespan)
Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


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
