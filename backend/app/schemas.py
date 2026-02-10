from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PlayerCreate(BaseModel):
    name: str
    isPreset: bool = False

class RoundCreate(BaseModel):
    winner: str
    ballsWon: int

class RoundResponse(BaseModel):
    roundNumber: int
    winner: str
    ballsWon: int
    timestamp: str

class RoomCreate(BaseModel):
    gameType: str = "eight-ball"
    owner: str
    players: List[PlayerCreate]
    pricePerBall: float = 5.0

class RoomJoin(BaseModel):
    userName: str

class OperatorGrant(BaseModel):
    userName: str

class PlayerResponse(BaseModel):
    name: str
    isPreset: bool = False

class RoomResponse(BaseModel):
    id: str
    gameType: str
    owner: str
    players: List[PlayerResponse]
    operators: List[str]
    spectators: List[str]
    rounds: List[RoundResponse]
    pricePerBall: float
    status: str
    createdAt: str

class SettlementResponse(BaseModel):
    score: str
    winner: Optional[str]
    loser: Optional[str]
    ballDiff: int
    amount: float

class MatchResponse(BaseModel):
    id: str
    roomId: str
    gameType: str
    players: List[str]
    rounds: List[RoundResponse]
    settlement: SettlementResponse
    createdAt: str
    settledAt: str

class MatchListResponse(BaseModel):
    total: int
    matches: List[MatchResponse]

class OpponentStats(BaseModel):
    opponent: str
    matches: int
    wins: int
    losses: int
    winRate: float
    netBalls: int
    netAmount: float

class PlayerStatsResponse(BaseModel):
    name: str
    totalMatches: int
    totalWins: int
    totalLosses: int
    totalDraws: int
    winRate: float
    totalBallsWon: int
    totalBallsLost: int
    netBalls: int
    netAmount: float
    recentMatches: List[MatchResponse]
    opponentStats: List[OpponentStats]
