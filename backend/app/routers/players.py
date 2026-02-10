from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List

from app.database import get_db
from app.models import Player, Match, Round
from app.schemas import PlayerStatsResponse, MatchResponse, RoundResponse, SettlementResponse, OpponentStats

router = APIRouter()

@router.get("")
async def get_players(db: AsyncSession = Depends(get_db)):
    """获取所有玩家列表"""
    result = await db.execute(select(Player).order_by(Player.created_at))
    players = result.scalars().all()
    
    # 获取所有已结算比赛
    matches_result = await db.execute(
        select(Match).where(Match.status == "settled")
    )
    all_matches = matches_result.scalars().all()
    
    player_list = []
    for player in players:
        # 统计比赛数（在内存中统计）
        match_count = sum(1 for m in all_matches if player.name in m.players)
        
        player_list.append({
            "name": player.name,
            "matchCount": match_count
        })
    
    return player_list

@router.get("/{player_name}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(player_name: str, db: AsyncSession = Depends(get_db)):
    """获取玩家详细统计"""
    # 检查玩家是否存在
    result = await db.execute(select(Player).where(Player.name == player_name))
    player = result.scalar_one_or_none()
    
    if not player:
        # 即使不在预设中，只要参与过比赛就可以查看
        pass
    
    # 获取所有已结算比赛，在内存中筛选
    all_matches_result = await db.execute(
        select(Match)
        .where(Match.status == "settled")
        .order_by(Match.settled_at.desc())
    )
    all_matches = all_matches_result.scalars().all()
    
    # 筛选该玩家参与的比赛
    matches = [m for m in all_matches if player_name in m.players]
    
    if not matches:
        return PlayerStatsResponse(
            name=player_name,
            totalMatches=0,
            totalWins=0,
            totalLosses=0,
            totalDraws=0,
            winRate=0,
            totalBallsWon=0,
            totalBallsLost=0,
            netBalls=0,
            netAmount=0,
            recentMatches=[],
            opponentStats=[]
        )
    
    # 统计数据
    total_wins = 0
    total_losses = 0
    total_draws = 0
    total_balls_won = 0
    total_balls_lost = 0
    net_amount = 0
    opponent_data = {}  # {opponent: {matches, wins, losses, balls_won, balls_lost, net_amount}}
    
    recent_matches = []
    
    for match in matches:
        # 获取 rounds
        rounds_result = await db.execute(
            select(Round)
            .where(Round.match_id == match.id)
            .order_by(Round.round_number)
        )
        rounds = rounds_result.scalars().all()
        
        # 计算本场比赛该玩家的球数
        my_balls = sum(r.balls_won for r in rounds if r.winner == player_name)
        opponent_balls = sum(r.balls_won for r in rounds if r.winner != player_name)
        
        total_balls_won += my_balls
        total_balls_lost += opponent_balls
        
        # 判断胜负
        if match.settlement_winner == player_name:
            total_wins += 1
            net_amount += match.settlement_amount or 0
        elif match.settlement_loser == player_name:
            total_losses += 1
            net_amount -= match.settlement_amount or 0
        else:
            total_draws += 1
        
        # 对手统计
        opponent = [p for p in match.players if p != player_name][0] if len(match.players) == 2 else "未知"
        if opponent not in opponent_data:
            opponent_data[opponent] = {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "balls_won": 0,
                "balls_lost": 0,
                "net_amount": 0
            }
        
        opponent_data[opponent]["matches"] += 1
        opponent_data[opponent]["balls_won"] += my_balls
        opponent_data[opponent]["balls_lost"] += opponent_balls
        
        if match.settlement_winner == player_name:
            opponent_data[opponent]["wins"] += 1
            opponent_data[opponent]["net_amount"] += match.settlement_amount or 0
        elif match.settlement_loser == player_name:
            opponent_data[opponent]["losses"] += 1
            opponent_data[opponent]["net_amount"] -= match.settlement_amount or 0
        
        # 构建比赛记录
        recent_matches.append(MatchResponse(
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
    
    # 构建对手统计
    opponent_stats = []
    for opp, data in opponent_data.items():
        total = data["matches"]
        wins = data["wins"]
        opponent_stats.append(OpponentStats(
            opponent=opp,
            matches=total,
            wins=wins,
            losses=data["losses"],
            winRate=wins / total if total > 0 else 0,
            netBalls=data["balls_won"] - data["balls_lost"],
            netAmount=data["net_amount"]
        ))
    
    # 按比赛数排序
    opponent_stats.sort(key=lambda x: x.matches, reverse=True)
    
    total_matches = len(matches)
    
    return PlayerStatsResponse(
        name=player_name,
        totalMatches=total_matches,
        totalWins=total_wins,
        totalLosses=total_losses,
        totalDraws=total_draws,
        winRate=total_wins / total_matches if total_matches > 0 else 0,
        totalBallsWon=total_balls_won,
        totalBallsLost=total_balls_lost,
        netBalls=total_balls_won - total_balls_lost,
        netAmount=net_amount,
        recentMatches=recent_matches[:20],  # 最近20场
        opponentStats=opponent_stats
    )
