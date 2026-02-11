from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.database import Base


class BasketballMatch(Base):
    """投篮比赛记录"""
    __tablename__ = "basketball_matches"
    
    id = Column(String(36), primary_key=True, index=True)
    room_id = Column(String(10), index=True, nullable=False)
    owner = Column(String(50), nullable=False)
    _players = Column("players", Text, nullable=False)  # JSON: ["玩家1", "玩家2", ...]
    
    @property
    def players(self):
        return json.loads(self._players) if self._players else []
    
    @players.setter
    def players(self, value):
        self._players = json.dumps(value, ensure_ascii=False)
    
    balls_per_round = Column(Integer, default=10)  # 每轮投球数
    price_per_ball = Column(Float, default=2.0)  # 单价
    total_rounds = Column(Integer, nullable=True)  # 固定轮数（null表示不限）
    status = Column(String(20), default="playing")  # playing, settled
    
    # 结算结果
    settlement_winner = Column(String(50), nullable=True)
    settlement_total_amount = Column(Float, nullable=True)
    _settlement_details = Column("settlement_details", Text, nullable=True)  # JSON 转账详情
    
    @property
    def settlement_details(self):
        return json.loads(self._settlement_details) if self._settlement_details else []
    
    @settlement_details.setter
    def settlement_details(self, value):
        self._settlement_details = json.dumps(value, ensure_ascii=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)
    
    rounds = relationship("BasketballRound", back_populates="match", cascade="all, delete-orphan")


class BasketballRound(Base):
    """投篮比赛轮次记录"""
    __tablename__ = "basketball_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(36), ForeignKey("basketball_matches.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    _scores = Column("scores", Text, nullable=False)  # JSON: [{"player": "xx", "shotType": "three", "made": 5, "total": 10}]
    
    @property
    def scores(self):
        return json.loads(self._scores) if self._scores else []
    
    @scores.setter
    def scores(self, value):
        self._scores = json.dumps(value, ensure_ascii=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    match = relationship("BasketballMatch", back_populates="rounds")


class BasketballPractice(Base):
    """个人练习记录"""
    __tablename__ = "basketball_practices"
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(50), index=True, nullable=False)
    shot_type = Column(String(20), nullable=False)  # three, two, free
    total_shots = Column(Integer, nullable=False)  # 总投球数
    shots_made = Column(Integer, nullable=False)  # 进球数
    accuracy = Column(Float, nullable=False)  # 命中率
    created_at = Column(DateTime, default=datetime.utcnow)


class BasketballPlayer(Base):
    """投篮玩家（复用 Player 或单独管理）"""
    __tablename__ = "basketball_players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    is_preset = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
