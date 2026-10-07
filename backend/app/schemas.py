from typing import Literal

from pydantic import BaseModel, Field


class Player(BaseModel):
    id: int
    name: str
    skill: Literal["batting", "bowling", "both"]
    base_price: int
    status: Literal["available", "in_auction", "sold"]
    sold_price: int | None
    team_id: int | None


class Team(BaseModel):
    id: int
    name: str
    total_budget: int
    remaining_budget: int
    players: list[Player]


class Bid(BaseModel):
    id: int
    player_id: int
    team_id: int
    team_name: str
    amount: int
    created_at: str


class Auction(BaseModel):
    player: Player | None
    bids: list[Bid]  # highest first


class StartRequest(BaseModel):
    player_id: int


class BidRequest(BaseModel):
    team_id: int
    amount: int = Field(gt=0)


class AcceptRequest(BaseModel):
    bid_id: int
