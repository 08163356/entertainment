from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db
from app.models import Match, Round
from app.schemas import MatchResponse, MatchListResponse, RoundResponse, SettlementResponse

router = APIRouter()

@router.get("", response_model=MatchListResponse)
async def get_matches(
    player: Optional[str] = Query(None, description="筛选玩家"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """获取比赛历史"""
    query = select(Match).where(Match.status == "settled")
    
    # 总数
    count_query = select(func.count()).select_from(Match).where(Match.status == "settled")
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    query = query.order_by(Match.settled_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # 构建响应（如果有 player 过滤，在内存中过滤）
    match_responses = []
    for match in matches:
        # 如果有玩家过滤条件
        if player and player not in match.players:
            continue
            
        # 获取 rounds
        rounds_result = await db.execute(
            select(Round)
            .where(Round.match_id == match.id)
            .order_by(Round.round_number)
        )
        rounds = rounds_result.scalars().all()
        
        match_responses.append(MatchResponse(
            id=match.id,
            roomId=match.room_id,
            gameType=match.game_type,
            players=match.players,
            rounds=[
                RoundResponse(
                    roundNumber=r.round_number,
                    winner=r.winner,
                    ballsWon=r.balls_won,
                    timestamp=r.created_at.isoformat()
                )
                for r in rounds
            ],
            settlement=SettlementResponse(
                score=match.settlement_score or "0:0",
                winner=match.settlement_winner,
                loser=match.settlement_loser,
                ballDiff=match.settlement_ball_diff or 0,
                amount=match.settlement_amount or 0
            ),
            createdAt=match.created_at.isoformat(),
            settledAt=match.settled_at.isoformat() if match.settled_at else ""
        ))
    
    return MatchListResponse(total=total, matches=match_responses)

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str, db: AsyncSession = Depends(get_db)):
    """获取单场比赛详情"""
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 获取 rounds
    rounds_result = await db.execute(
        select(Round)
        .where(Round.match_id == match.id)
        .order_by(Round.round_number)
    )
    rounds = rounds_result.scalars().all()
    
    return MatchResponse(
        id=match.id,
        roomId=match.room_id,
        gameType=match.game_type,
        players=match.players,
        rounds=[
            RoundResponse(
                roundNumber=r.round_number,
                winner=r.winner,
                ballsWon=r.balls_won,
                timestamp=r.created_at.isoformat()
            )
            for r in rounds
        ],
        settlement=SettlementResponse(
            score=match.settlement_score or "0:0",
            winner=match.settlement_winner,
            loser=match.settlement_loser,
            ballDiff=match.settlement_ball_diff or 0,
            amount=match.settlement_amount or 0
        ),
        createdAt=match.created_at.isoformat(),
        settledAt=match.settled_at.isoformat() if match.settled_at else ""
    )
