from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.database import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    is_preset = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(String(36), primary_key=True, index=True)
    room_id = Column(String(10), index=True, nullable=False)
    game_type = Column(String(20), default="eight-ball")
    _players = Column("players", Text, nullable=False)  # JSON string: ["玩家1", "玩家2"]
    
    @property
    def players(self):
        return json.loads(self._players) if self._players else []
    
    @players.setter
    def players(self, value):
        self._players = json.dumps(value, ensure_ascii=False)
    price_per_ball = Column(Float, default=5.0)
    status = Column(String(20), default="playing")  # playing, settled
    
    # 结算结果
    settlement_score = Column(String(20), nullable=True)  # "5:3"
    settlement_winner = Column(String(50), nullable=True)
    settlement_loser = Column(String(50), nullable=True)
    settlement_ball_diff = Column(Integer, nullable=True)
    settlement_amount = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)
    
    rounds = relationship("Round", back_populates="match", cascade="all, delete-orphan")

class Round(Base):
    __tablename__ = "rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    winner = Column(String(50), nullable=False)
    balls_won = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    match = relationship("Match", back_populates="rounds")
