from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PlayerCreate(BaseModel):
    name: str
    isPreset: bool = False


class ScoreCreate(BaseModel):
    """单个玩家的投篮记录"""
    player: str
    shotType: str  # three, two, free
    made: int  # 进球数
    total: int  # 总投球数


class RoundCreate(BaseModel):
    """一轮比赛的所有记录"""
    scores: List[ScoreCreate]


class ScoreResponse(BaseModel):
    player: str
    shotType: str
    made: int
    total: int
    accuracy: float = 0.0


class RoundResponse(BaseModel):
    roundNumber: int
    scores: List[ScoreResponse]
    timestamp: str


class RoomCreate(BaseModel):
    owner: str
    players: List[PlayerCreate]
    ballsPerRound: int = 10
    pricePerBall: float = 2.0
    totalRounds: Optional[int] = None  # None 表示不限轮数


class RoomJoin(BaseModel):
    userName: str


class OperatorGrant(BaseModel):
    userName: str


class PlayerScoreSubmit(BaseModel):
    """玩家提交本轮得分"""
    playerName: str
    shotType: str = "two"
    made: int
    total: int


class PlayerScoreCancel(BaseModel):
    """取消玩家本轮提交"""
    playerName: str


class CurrentRoundStatus(BaseModel):
    """当前轮次状态"""
    submitted: List[dict]
    pending: List[str]
    allSubmitted: bool


class PlayerResponse(BaseModel):
    name: str
    isPreset: bool = False


class RoomResponse(BaseModel):
    id: str
    owner: str
    players: List[PlayerResponse]
    operators: List[str]
    spectators: List[str]
    rounds: List[RoundResponse]
    ballsPerRound: int
    pricePerBall: float
    totalRounds: Optional[int]
    status: str
    createdAt: str
    currentRound: Optional[dict] = None  # 当前轮次临时数据


class TransferDetail(BaseModel):
    """转账详情"""
    fromPlayer: str
    toPlayer: str
    amount: float
    shotsDiff: int


class PlayerStatSummary(BaseModel):
    """玩家统计摘要"""
    name: str
    totalShots: int = 0
    totalMade: int = 0
    accuracy: float = 0.0


class SettlementResponse(BaseModel):
    winner: Optional[str]
    playerStats: List[PlayerStatSummary]
    transfers: List[TransferDetail]
    totalAmount: float


class MatchResponse(BaseModel):
    id: str
    roomId: str
    owner: str
    players: List[str]
    rounds: List[RoundResponse]
    ballsPerRound: int
    pricePerBall: float
    totalRounds: Optional[int]
    settlement: Optional[SettlementResponse]
    createdAt: str
    settledAt: Optional[str]
    isZeroMatch: bool = False


class MatchListResponse(BaseModel):
    total: int
    matches: List[MatchResponse]


# 个人练习相关
class PracticeCreate(BaseModel):
    playerName: str
    shotType: str  # three, two, free
    totalShots: int
    shotsMade: int


class PracticeResponse(BaseModel):
    id: int
    playerName: str
    shotType: str
    totalShots: int
    shotsMade: int
    accuracy: float
    createdAt: str


class PracticeListResponse(BaseModel):
    total: int
    practices: List[PracticeResponse]


class PracticeStats(BaseModel):
    """练习统计（按类型分组）"""
    shotType: str
    totalSessions: int
    totalShots: int
    totalMade: int
    avgAccuracy: float
    bestAccuracy: float


class PracticeChartData(BaseModel):
    """图表数据"""
    date: str
    shotType: str
    accuracy: float
    totalShots: int
    shotsMade: int


class PlayerPracticeStats(BaseModel):
    """玩家练习统计总览"""
    playerName: str
    totalSessions: int
    statsByType: List[PracticeStats]
    chartData: List[PracticeChartData]


# 玩家战绩
class BasketballPlayerStats(BaseModel):
    name: str
    totalMatches: int
    totalWins: int
    winRate: float
    totalShots: int
    totalMade: int
    avgAccuracy: float
    netAmount: float
    recentMatches: List[MatchResponse]
