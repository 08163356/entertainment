from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid
import random
import string

from app.database import get_db
from app.models_basketball import BasketballMatch, BasketballRound, BasketballPlayer
from app.schemas_basketball import (
    RoomCreate, RoomJoin, RoomResponse, RoundCreate, 
    RoundResponse, ScoreResponse, OperatorGrant, 
    SettlementResponse, MatchResponse, PlayerStatSummary, TransferDetail,
    PlayerScoreSubmit, PlayerScoreCancel, CurrentRoundStatus
)
from app.services.basketball_room_manager import basketball_room_manager

router = APIRouter()


def generate_room_id() -> str:
    """生成4位数字房间号"""
    return ''.join(random.choices(string.digits, k=4))


@router.get("/active", response_model=list)
async def get_active_rooms(db: AsyncSession = Depends(get_db)):
    """获取所有进行中的房间（只返回内存中存在的）"""
    # 只从内存获取，内存中没有的房间说明服务器重启后丢失了
    active_rooms = []
    for room_id, room in basketball_room_manager.rooms.items():
        if room["status"] == "playing":
            player_scores = {}
            for p in room["players"]:
                player_scores[p["name"]] = 0
            
            for r in room["rounds"]:
                for score in r.get("scores", []):
                    if score["player"] in player_scores:
                        player_scores[score["player"]] += score["made"]
            
            active_rooms.append({
                "roomId": room_id,
                "players": [p["name"] for p in room["players"]],
                "roundCount": len(room["rounds"]),
                "playerScores": player_scores
            })
    
    # 清理数据库中内存不存在的 playing 状态比赛（标记为 abandoned）
    result = await db.execute(
        select(BasketballMatch).where(BasketballMatch.status == "playing")
    )
    db_matches = result.scalars().all()
    
    existing_room_ids = {r["roomId"] for r in active_rooms}
    
    for match in db_matches:
        if match.room_id not in existing_room_ids:
            # 内存中不存在，标记为已放弃
            match.status = "abandoned"
            match.settled_at = datetime.utcnow()
    
    await db.commit()
    
    return active_rooms


@router.post("", response_model=dict)
async def create_room(data: RoomCreate, db: AsyncSession = Depends(get_db)):
    """创建房间"""
    room_id = generate_room_id()
    
    # 确保房间号不重复
    while basketball_room_manager.get_room(room_id):
        room_id = generate_room_id()
    
    # 确保玩家存在于数据库
    for player in data.players:
        result = await db.execute(select(BasketballPlayer).where(BasketballPlayer.name == player.name))
        existing = result.scalar_one_or_none()
        if not existing:
            db_player = BasketballPlayer(name=player.name, is_preset=player.isPreset)
            db.add(db_player)
    
    await db.commit()
    
    # 创建比赛记录
    match_id = str(uuid.uuid4())
    db_match = BasketballMatch(
        id=match_id,
        room_id=room_id,
        owner=data.owner,
        players=[p.name for p in data.players],
        balls_per_round=data.ballsPerRound,
        price_per_ball=data.pricePerBall,
        total_rounds=data.totalRounds,
        status="playing"
    )
    db.add(db_match)
    await db.commit()
    
    # 创建房间状态
    basketball_room_manager.create_room(
        room_id=room_id,
        match_id=match_id,
        owner=data.owner,
        players=data.players,
        balls_per_round=data.ballsPerRound,
        price_per_ball=data.pricePerBall,
        total_rounds=data.totalRounds
    )
    
    return {"roomId": room_id}


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str):
    """获取房间信息"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在或已关闭")
    return room


@router.post("/{room_id}/join", response_model=RoomResponse)
async def join_room(room_id: str, data: RoomJoin, db: AsyncSession = Depends(get_db)):
    """加入房间"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在或已关闭")
    
    # 检查是否是参赛玩家
    is_player = any(p["name"] == data.userName for p in room["players"])
    
    # 只有参赛玩家才记录到数据库
    if is_player:
        result = await db.execute(select(BasketballPlayer).where(BasketballPlayer.name == data.userName))
        existing = result.scalar_one_or_none()
        if not existing:
            db_player = BasketballPlayer(name=data.userName, is_preset=False)
            db.add(db_player)
            await db.commit()
    
    basketball_room_manager.add_spectator(room_id, data.userName)
    return basketball_room_manager.get_room(room_id)


@router.post("/{room_id}/submit-score")
async def submit_player_score(room_id: str, data: PlayerScoreSubmit):
    """玩家提交本轮得分"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room["status"] != "playing":
        raise HTTPException(status_code=400, detail="比赛已结束")
    
    # 检查是否达到轮数上限
    if room["totalRounds"] and len(room["rounds"]) >= room["totalRounds"]:
        raise HTTPException(status_code=400, detail="已达到轮数上限")
    
    success = basketball_room_manager.submit_player_score(room_id, data.playerName, {
        "shotType": data.shotType,
        "made": data.made,
        "total": data.total
    })
    
    if not success:
        raise HTTPException(status_code=400, detail="提交失败，可能不是参赛玩家")
    
    # 获取当前状态
    status = basketball_room_manager.get_current_round_status(room_id)
    
    # 广播更新
    await basketball_room_manager.broadcast(room_id, {
        "type": "player_score_submitted",
        "data": {
            "playerName": data.playerName,
            "shotType": data.shotType,
            "made": data.made,
            "total": data.total,
            "currentRoundStatus": status
        }
    })
    
    return {"success": True, "currentRoundStatus": status}


@router.post("/{room_id}/cancel-score")
async def cancel_player_score(room_id: str, data: PlayerScoreCancel):
    """取消玩家本轮提交"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    success = basketball_room_manager.cancel_player_score(room_id, data.playerName)
    
    if not success:
        raise HTTPException(status_code=400, detail="取消失败")
    
    status = basketball_room_manager.get_current_round_status(room_id)
    
    await basketball_room_manager.broadcast(room_id, {
        "type": "player_score_cancelled",
        "data": {
            "playerName": data.playerName,
            "currentRoundStatus": status
        }
    })
    
    return {"success": True, "currentRoundStatus": status}


@router.get("/{room_id}/current-round", response_model=CurrentRoundStatus)
async def get_current_round_status(room_id: str):
    """获取当前轮次状态"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    return basketball_room_manager.get_current_round_status(room_id)


@router.post("/{room_id}/confirm-round")
async def confirm_round(room_id: str, db: AsyncSession = Depends(get_db)):
    """确认本轮（所有人完成后调用）"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room["status"] != "playing":
        raise HTTPException(status_code=400, detail="比赛已结束")
    
    status = basketball_room_manager.get_current_round_status(room_id)
    if not status["allSubmitted"]:
        raise HTTPException(status_code=400, detail="还有玩家未完成记录")
    
    match_id = basketball_room_manager.get_match_id(room_id)
    
    # 确认并获取轮次数据
    round_data = basketball_room_manager.confirm_round(room_id)
    
    if not round_data:
        raise HTTPException(status_code=400, detail="确认失败")
    
    # 保存到数据库
    db_round = BasketballRound(
        match_id=match_id,
        round_number=round_data["roundNumber"],
        scores=round_data["scores"]
    )
    db.add(db_round)
    await db.commit()
    
    # 广播更新
    await basketball_room_manager.broadcast(room_id, {
        "type": "round_confirmed",
        "data": round_data
    })
    
    return {"success": True, "round": round_data}


@router.post("/{room_id}/rounds")
async def add_round(room_id: str, data: RoundCreate, db: AsyncSession = Depends(get_db)):
    """记录一轮投篮"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room["status"] != "playing":
        raise HTTPException(status_code=400, detail="比赛已结束")
    
    # 检查是否达到轮数上限
    if room["totalRounds"] and len(room["rounds"]) >= room["totalRounds"]:
        raise HTTPException(status_code=400, detail="已达到轮数上限")
    
    match_id = basketball_room_manager.get_match_id(room_id)
    round_number = len(room["rounds"]) + 1
    
    # 构建分数数据
    scores_data = []
    for score in data.scores:
        accuracy = (score.made / score.total * 100) if score.total > 0 else 0
        scores_data.append({
            "player": score.player,
            "shotType": score.shotType,
            "made": score.made,
            "total": score.total,
            "accuracy": round(accuracy, 1)
        })
    
    # 保存到数据库
    db_round = BasketballRound(
        match_id=match_id,
        round_number=round_number,
        scores=scores_data
    )
    db.add(db_round)
    await db.commit()
    
    # 更新房间状态
    round_data = {
        "roundNumber": round_number,
        "scores": scores_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    basketball_room_manager.add_round(room_id, round_data)
    
    # 广播更新
    await basketball_room_manager.broadcast(room_id, {
        "type": "round_added",
        "data": round_data
    })
    
    return {"success": True}


@router.delete("/{room_id}/rounds/last")
async def undo_round(room_id: str, db: AsyncSession = Depends(get_db)):
    """撤销上一轮"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if not room["rounds"]:
        raise HTTPException(status_code=400, detail="没有可撤销的记录")
    
    match_id = basketball_room_manager.get_match_id(room_id)
    result = await db.execute(
        select(BasketballRound)
        .where(BasketballRound.match_id == match_id)
        .order_by(BasketballRound.round_number.desc())
        .limit(1)
    )
    last_round = result.scalar_one_or_none()
    if last_round:
        await db.delete(last_round)
        await db.commit()
    
    basketball_room_manager.remove_last_round(room_id)
    
    await basketball_room_manager.broadcast(room_id, {
        "type": "round_undone",
        "data": {}
    })
    
    return {"success": True}


@router.post("/{room_id}/operators")
async def grant_operator(room_id: str, data: OperatorGrant):
    """授权操作权限"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    basketball_room_manager.add_operator(room_id, data.userName)
    
    await basketball_room_manager.broadcast(room_id, {
        "type": "operators_updated",
        "data": {"operators": basketball_room_manager.get_room(room_id)["operators"]}
    })
    
    return {"success": True}


@router.delete("/{room_id}/operators/{user_name}")
async def revoke_operator(room_id: str, user_name: str):
    """撤销操作权限"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    basketball_room_manager.remove_operator(room_id, user_name)
    
    await basketball_room_manager.broadcast(room_id, {
        "type": "operators_updated",
        "data": {"operators": basketball_room_manager.get_room(room_id)["operators"]}
    })
    
    return {"success": True}


@router.post("/{room_id}/transfer-owner")
async def transfer_owner(room_id: str, data: OperatorGrant):
    """转移房主"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    success = basketball_room_manager.transfer_owner(room_id, data.userName)
    if not success:
        raise HTTPException(status_code=400, detail="转移失败，目标用户必须是参赛玩家")
    
    updated_room = basketball_room_manager.get_room(room_id)
    await basketball_room_manager.broadcast(room_id, {
        "type": "owner_transferred",
        "data": {
            "owner": updated_room["owner"],
            "operators": updated_room["operators"]
        }
    })
    
    return {"success": True}


@router.post("/{room_id}/settle", response_model=MatchResponse)
async def settle_room(room_id: str, db: AsyncSession = Depends(get_db)):
    """结算房间"""
    room = basketball_room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room["status"] == "settled":
        raise HTTPException(status_code=400, detail="比赛已结算")
    
    # 计算每个玩家的统计
    players = room["players"]
    player_stats = {}
    
    for p in players:
        player_stats[p["name"]] = {"totalShots": 0, "totalMade": 0}
    
    for r in room["rounds"]:
        for score in r.get("scores", []):
            if score["player"] in player_stats:
                player_stats[score["player"]]["totalShots"] += score["total"]
                player_stats[score["player"]]["totalMade"] += score["made"]
    
    # 检查是否都是0球
    total_made = sum(ps["totalMade"] for ps in player_stats.values())
    is_zero_match = total_made == 0
    
    if is_zero_match:
        match_id = basketball_room_manager.get_match_id(room_id)
        result = await db.execute(select(BasketballMatch).where(BasketballMatch.id == match_id))
        db_match = result.scalar_one_or_none()
        if db_match:
            await db.delete(db_match)
            await db.commit()
        
        basketball_room_manager.settle_room(room_id)
        
        await basketball_room_manager.broadcast(room_id, {
            "type": "room_settled",
            "data": basketball_room_manager.get_room(room_id),
            "isZeroMatch": True
        })
        
        return MatchResponse(
            id="",
            roomId=room_id,
            owner=room["owner"],
            players=[p["name"] for p in players],
            rounds=[],
            ballsPerRound=room["ballsPerRound"],
            pricePerBall=room["pricePerBall"],
            totalRounds=room["totalRounds"],
            settlement=None,
            createdAt=room["createdAt"],
            settledAt=datetime.utcnow().isoformat(),
            isZeroMatch=True
        )
    
    # 计算结算
    price_per_ball = room["pricePerBall"]
    
    # 构建玩家统计列表
    stats_list = []
    for name, stats in player_stats.items():
        accuracy = (stats["totalMade"] / stats["totalShots"] * 100) if stats["totalShots"] > 0 else 0
        stats_list.append(PlayerStatSummary(
            name=name,
            totalShots=stats["totalShots"],
            totalMade=stats["totalMade"],
            accuracy=round(accuracy, 1)
        ))
    
    # 按进球数排序
    sorted_stats = sorted(stats_list, key=lambda x: x.totalMade, reverse=True)
    
    # 计算转账（赢家通吃）
    transfers = []
    winner = sorted_stats[0] if sorted_stats else None
    total_amount = 0
    
    if winner and winner.totalMade > 0:
        for stat in sorted_stats[1:]:
            shots_diff = winner.totalMade - stat.totalMade
            amount = shots_diff * price_per_ball
            if amount > 0:
                transfers.append(TransferDetail(
                    fromPlayer=stat.name,
                    toPlayer=winner.name,
                    amount=amount,
                    shotsDiff=shots_diff
                ))
                total_amount += amount
    
    # 更新数据库
    match_id = basketball_room_manager.get_match_id(room_id)
    result = await db.execute(select(BasketballMatch).where(BasketballMatch.id == match_id))
    db_match = result.scalar_one()
    
    db_match.status = "settled"
    db_match.settlement_winner = winner.name if winner else None
    db_match.settlement_total_amount = total_amount
    db_match.settlement_details = [t.model_dump() for t in transfers]
    db_match.settled_at = datetime.utcnow()
    
    await db.commit()
    
    basketball_room_manager.settle_room(room_id)
    
    settlement = SettlementResponse(
        winner=winner.name if winner else None,
        playerStats=sorted_stats,
        transfers=transfers,
        totalAmount=total_amount
    )
    
    # 构建 rounds 响应
    rounds_response = []
    for r in room["rounds"]:
        scores_response = [ScoreResponse(**s) for s in r.get("scores", [])]
        rounds_response.append(RoundResponse(
            roundNumber=r["roundNumber"],
            scores=scores_response,
            timestamp=r["timestamp"]
        ))
    
    match_response = MatchResponse(
        id=match_id,
        roomId=room_id,
        owner=room["owner"],
        players=[p["name"] for p in players],
        rounds=rounds_response,
        ballsPerRound=room["ballsPerRound"],
        pricePerBall=room["pricePerBall"],
        totalRounds=room["totalRounds"],
        settlement=settlement,
        createdAt=room["createdAt"],
        settledAt=datetime.utcnow().isoformat()
    )
    
    await basketball_room_manager.broadcast(room_id, {
        "type": "room_settled",
        "data": basketball_room_manager.get_room(room_id),
        "settlement": settlement.model_dump()
    })
    
    return match_response
