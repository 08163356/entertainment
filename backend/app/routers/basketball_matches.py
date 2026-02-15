from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
import json

from app.database import get_db
from app.models_basketball import BasketballMatch, BasketballRound, BasketballPlayer
from app.schemas_basketball import (
    MatchResponse, MatchListResponse, RoundResponse, ScoreResponse,
    SettlementResponse, PlayerStatSummary, TransferDetail,
    BasketballPlayerStats
)

router = APIRouter()


def build_match_response(match: BasketballMatch, rounds: list) -> MatchResponse:
    """构建比赛响应对象"""
    rounds_response = []
    for r in rounds:
        scores_response = [ScoreResponse(**s) for s in r.scores]
        rounds_response.append(RoundResponse(
            roundNumber=r.round_number,
            scores=scores_response,
            timestamp=r.created_at.isoformat()
        ))
    
    settlement = None
    if match.status == "settled":
        # 计算每个玩家统计
        player_stats = {}
        for p in match.players:
            player_stats[p] = {"totalShots": 0, "totalMade": 0}
        
        for r in rounds:
            for score in r.scores:
                if score["player"] in player_stats:
                    player_stats[score["player"]]["totalShots"] += score["total"]
                    player_stats[score["player"]]["totalMade"] += score["made"]
        
        stats_list = []
        for name, stats in player_stats.items():
            accuracy = (stats["totalMade"] / stats["totalShots"] * 100) if stats["totalShots"] > 0 else 0
            stats_list.append(PlayerStatSummary(
                name=name,
                totalShots=stats["totalShots"],
                totalMade=stats["totalMade"],
                accuracy=round(accuracy, 1)
            ))
        
        sorted_stats = sorted(stats_list, key=lambda x: x.totalMade, reverse=True)
        
        # 优先从数据库读取 transfers
        transfers = []
        if match.settlement_details:
            for t in match.settlement_details:
                transfers.append(TransferDetail(
                    fromPlayer=t.get("fromPlayer", ""),
                    toPlayer=t.get("toPlayer", ""),
                    amount=t.get("amount", 0),
                    shotsDiff=t.get("shotsDiff", 0)
                ))
        
        # 如果数据库中没有 transfers，但有不同进球数的玩家，则重新计算
        if not transfers and len(sorted_stats) > 1 and match.price_per_ball > 0:
            winner = sorted_stats[0]
            if winner.totalMade > 0:
                for stat in sorted_stats[1:]:
                    shots_diff = winner.totalMade - stat.totalMade
                    amount = shots_diff * match.price_per_ball
                    if shots_diff > 0:
                        transfers.append(TransferDetail(
                            fromPlayer=stat.name,
                            toPlayer=winner.name,
                            amount=amount,
                            shotsDiff=shots_diff
                        ))
        
        # 确定 winner：进球最多的玩家（如果有 transfers 说明有差距）
        winner_name = match.settlement_winner
        if not winner_name and transfers:
            winner_name = sorted_stats[0].name
        
        total_amount = match.settlement_total_amount or sum(t.amount for t in transfers)
        
        settlement = SettlementResponse(
            winner=winner_name,
            playerStats=sorted_stats,
            transfers=transfers,
            totalAmount=total_amount
        )
    
    return MatchResponse(
        id=match.id,
        roomId=match.room_id,
        owner=match.owner,
        players=match.players,
        rounds=rounds_response,
        ballsPerRound=match.balls_per_round,
        pricePerBall=match.price_per_ball,
        totalRounds=match.total_rounds,
        settlement=settlement,
        createdAt=match.created_at.isoformat(),
        settledAt=match.settled_at.isoformat() if match.settled_at else None
    )


# ========== 固定路径的路由必须放在动态路径之前 ==========

@router.get("/players", response_model=list)
async def get_players(db: AsyncSession = Depends(get_db)):
    """获取所有投篮玩家"""
    result = await db.execute(select(BasketballPlayer))
    players = result.scalars().all()
    
    player_list = []
    for p in players:
        # 统计比赛次数
        count_result = await db.execute(
            select(func.count(BasketballMatch.id))
            .where(BasketballMatch.status == "settled")
            .where(BasketballMatch._players.contains(p.name))
        )
        match_count = count_result.scalar()
        
        player_list.append({
            "name": p.name,
            "isPreset": p.is_preset,
            "matchCount": match_count
        })
    
    return player_list


@router.get("/players/{player_name}/stats", response_model=BasketballPlayerStats)
async def get_player_stats(player_name: str, db: AsyncSession = Depends(get_db)):
    """获取玩家战绩统计"""
    # 获取玩家所有已结算比赛
    result = await db.execute(
        select(BasketballMatch)
        .where(BasketballMatch.status == "settled")
        .where(BasketballMatch._players.contains(player_name))
        .order_by(desc(BasketballMatch.settled_at))
    )
    matches = result.scalars().all()
    
    total_matches = len(matches)
    total_wins = 0
    total_shots = 0
    total_made = 0
    net_amount = 0.0
    
    match_responses = []
    for match in matches[:10]:  # 最近10场
        rounds_result = await db.execute(
            select(BasketballRound)
            .where(BasketballRound.match_id == match.id)
            .order_by(BasketballRound.round_number)
        )
        rounds = rounds_result.scalars().all()
        
        # 统计该玩家在这场比赛的数据
        for r in rounds:
            for score in r.scores:
                if score["player"] == player_name:
                    total_shots += score["total"]
                    total_made += score["made"]
        
        # 判断胜负和金额
        if match.settlement_winner == player_name:
            total_wins += 1
            net_amount += match.settlement_total_amount or 0
        else:
            # 查找该玩家需要支付的金额
            for t in (match.settlement_details or []):
                if t.get("fromPlayer") == player_name:
                    net_amount -= t.get("amount", 0)
        
        match_responses.append(build_match_response(match, rounds))
    
    win_rate = (total_wins / total_matches * 100) if total_matches > 0 else 0
    avg_accuracy = (total_made / total_shots * 100) if total_shots > 0 else 0
    
    return BasketballPlayerStats(
        name=player_name,
        totalMatches=total_matches,
        totalWins=total_wins,
        winRate=round(win_rate, 1),
        totalShots=total_shots,
        totalMade=total_made,
        avgAccuracy=round(avg_accuracy, 1),
        netAmount=round(net_amount, 2),
        recentMatches=match_responses
    )


@router.get("", response_model=MatchListResponse)
async def get_matches(
    player: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取比赛记录列表"""
    query = select(BasketballMatch).where(BasketballMatch.status == "settled")
    count_query = select(func.count(BasketballMatch.id)).where(BasketballMatch.status == "settled")
    
    if player:
        query = query.where(BasketballMatch._players.contains(player))
        count_query = count_query.where(BasketballMatch._players.contains(player))
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    query = query.order_by(desc(BasketballMatch.settled_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    matches = result.scalars().all()
    
    match_responses = []
    for match in matches:
        rounds_result = await db.execute(
            select(BasketballRound)
            .where(BasketballRound.match_id == match.id)
            .order_by(BasketballRound.round_number)
        )
        rounds = rounds_result.scalars().all()
        match_responses.append(build_match_response(match, rounds))
    
    return MatchListResponse(total=total, matches=match_responses)


# ========== 动态路径路由放在最后 ==========

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str, db: AsyncSession = Depends(get_db)):
    """获取单场比赛详情"""
    result = await db.execute(select(BasketballMatch).where(BasketballMatch.id == match_id))
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    rounds_result = await db.execute(
        select(BasketballRound)
        .where(BasketballRound.match_id == match.id)
        .order_by(BasketballRound.round_number)
    )
    rounds = rounds_result.scalars().all()
    
    return build_match_response(match, rounds)
