from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid
import random
import string

from app.database import get_db
from app.models import Match, Round, Player
from app.schemas import (
    RoomCreate, RoomJoin, RoomResponse, RoundCreate, 
    RoundResponse, OperatorGrant, SettlementResponse, MatchResponse, PlayerCreate
)
from app.services.room_manager import room_manager

router = APIRouter()

def generate_room_id() -> str:
    """生成4位数字房间号"""
    return ''.join(random.choices(string.digits, k=4))

@router.get("/active", response_model=list)
async def get_active_rooms():
    """获取所有进行中的房间"""
    active_rooms = []
    for room_id, room in room_manager.rooms.items():
        if room["status"] == "playing":
            active_rooms.append({
                "roomId": room_id,
                "players": [p["name"] for p in room["players"]],
                "roundCount": len(room["rounds"])
            })
    return active_rooms

@router.post("", response_model=dict)
async def create_room(data: RoomCreate, db: AsyncSession = Depends(get_db)):
    """创建房间"""
    room_id = generate_room_id()
    
    # 确保房间号不重复
    while room_manager.get_room(room_id):
        room_id = generate_room_id()
    
    # 确保玩家存在于数据库
    for player in data.players:
        result = await db.execute(select(Player).where(Player.name == player.name))
        existing = result.scalar_one_or_none()
        if not existing:
            db_player = Player(name=player.name, is_preset=player.isPreset)
            db.add(db_player)
    
    await db.commit()
    
    # 创建比赛记录
    match_id = str(uuid.uuid4())
    db_match = Match(
        id=match_id,
        room_id=room_id,
        game_type=data.gameType,
        players=[p.name for p in data.players],
        price_per_ball=data.pricePerBall,
        status="playing"
    )
    db.add(db_match)
    await db.commit()
    
    # 创建房间状态
    room_manager.create_room(
        room_id=room_id,
        match_id=match_id,
        game_type=data.gameType,
        owner=data.owner,
        players=data.players,
        price_per_ball=data.pricePerBall,
        default_score_mode=data.defaultScoreMode
    )
    
    return {"roomId": room_id}

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str):
    """获取房间信息"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在或已关闭")
    return room

@router.post("/{room_id}/join", response_model=RoomResponse)
async def join_room(room_id: str, data: RoomJoin, db: AsyncSession = Depends(get_db)):
    """加入房间"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在或已关闭")
    
    # 检查是否是参赛玩家
    is_player = any(p["name"] == data.userName for p in room["players"])
    
    # 只有参赛玩家才记录到数据库（游客不记录）
    if is_player:
        result = await db.execute(select(Player).where(Player.name == data.userName))
        existing = result.scalar_one_or_none()
        if not existing:
            db_player = Player(name=data.userName, is_preset=False)
            db.add(db_player)
            await db.commit()
    
    room_manager.add_spectator(room_id, data.userName)
    return room_manager.get_room(room_id)

@router.post("/{room_id}/rounds")
async def add_round(room_id: str, data: RoundCreate, db: AsyncSession = Depends(get_db)):
    """记录一局"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room["status"] != "playing":
        raise HTTPException(status_code=400, detail="比赛已结束")
    
    # 获取 match_id
    match_id = room_manager.get_match_id(room_id)
    
    # 保存到数据库
    round_number = len(room["rounds"]) + 1
    db_round = Round(
        match_id=match_id,
        round_number=round_number,
        winner=data.winner,
        balls_won=data.ballsWon
    )
    db.add(db_round)
    await db.commit()
    
    # 更新房间状态
    round_data = RoundResponse(
        roundNumber=round_number,
        winner=data.winner,
        ballsWon=data.ballsWon,
        timestamp=datetime.utcnow().isoformat()
    )
    room_manager.add_round(room_id, round_data)
    
    # 广播更新
    await room_manager.broadcast(room_id, {
        "type": "round_added",
        "data": round_data.model_dump()
    })
    
    return {"success": True}

@router.delete("/{room_id}/rounds/last")
async def undo_round(room_id: str, db: AsyncSession = Depends(get_db)):
    """撤销上一局"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if not room["rounds"]:
        raise HTTPException(status_code=400, detail="没有可撤销的记录")
    
    # 从数据库删除
    match_id = room_manager.get_match_id(room_id)
    result = await db.execute(
        select(Round)
        .where(Round.match_id == match_id)
        .order_by(Round.round_number.desc())
        .limit(1)
    )
    last_round = result.scalar_one_or_none()
    if last_round:
        await db.delete(last_round)
        await db.commit()
    
    # 更新房间状态
    room_manager.remove_last_round(room_id)
    
    # 广播更新
    await room_manager.broadcast(room_id, {
        "type": "round_undone",
        "data": {}
    })
    
    return {"success": True}

@router.post("/{room_id}/operators")
async def grant_operator(room_id: str, data: OperatorGrant):
    """授权操作权限"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room_manager.add_operator(room_id, data.userName)
    
    await room_manager.broadcast(room_id, {
        "type": "operators_updated",
        "data": {"operators": room_manager.get_room(room_id)["operators"]}
    })
    
    return {"success": True}

@router.delete("/{room_id}/operators/{user_name}")
async def revoke_operator(room_id: str, user_name: str):
    """撤销操作权限"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room_manager.remove_operator(room_id, user_name)
    
    await room_manager.broadcast(room_id, {
        "type": "operators_updated",
        "data": {"operators": room_manager.get_room(room_id)["operators"]}
    })
    
    return {"success": True}

@router.post("/{room_id}/transfer-owner")
async def transfer_owner(room_id: str, data: OperatorGrant):
    """转移房主"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    success = room_manager.transfer_owner(room_id, data.userName)
    if not success:
        raise HTTPException(status_code=400, detail="转移失败，目标用户必须是参赛玩家")
    
    # 广播房主变更
    updated_room = room_manager.get_room(room_id)
    await room_manager.broadcast(room_id, {
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
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room["status"] == "settled":
        raise HTTPException(status_code=400, detail="比赛已结算")
    
    # 计算结算结果（支持多人）
    players = room["players"]
    player_stats = {}
    
    # 初始化每个玩家的统计
    for p in players:
        player_stats[p["name"]] = {"wins": 0, "balls": 0}
    
    # 统计每个玩家的数据
    for r in room["rounds"]:
        if r["winner"] in player_stats:
            player_stats[r["winner"]]["wins"] += 1
            player_stats[r["winner"]]["balls"] += r["ballsWon"]
    
    # 检查是否所有玩家都是0球（0:0 不计入数据库）
    total_balls = sum(ps["balls"] for ps in player_stats.values())
    is_zero_match = total_balls == 0
    
    if is_zero_match:
        # 删除数据库中的比赛记录
        match_id = room_manager.get_match_id(room_id)
        result = await db.execute(select(Match).where(Match.id == match_id))
        db_match = result.scalar_one_or_none()
        if db_match:
            await db.delete(db_match)
            await db.commit()
        
        # 关闭房间
        room_manager.settle_room(room_id)
        
        # 广播结算（0:0 比赛）
        await room_manager.broadcast(room_id, {
            "type": "room_settled",
            "data": room_manager.get_room(room_id),
            "isZeroMatch": True
        })
        
        # 返回空结算数据，而不是抛异常
        return MatchResponse(
            id="",
            roomId=room_id,
            gameType=room["gameType"],
            players=[p["name"] for p in players],
            rounds=[],
            settlement=SettlementResponse(score="0:0", winner=None, loser=None, ballDiff=0, amount=0),
            createdAt=room["createdAt"],
            settledAt=datetime.utcnow().isoformat(),
            transfers=[],
            isZeroMatch=True
        )
    
    # 计算结算（多人模式：按球数排序计算转账）
    price_per_ball = room["pricePerBall"]
    player_names = [p["name"] for p in players]
    
    # 按球数排序
    sorted_players = sorted(player_stats.items(), key=lambda x: x[1]["balls"], reverse=True)
    
    # 计算转账详情（多人模式）
    transfers = []
    if len(players) == 2:
        # 两人模式：简单计算
        p1_name, p2_name = player_names[0], player_names[1]
        p1_balls = player_stats[p1_name]["balls"]
        p2_balls = player_stats[p2_name]["balls"]
        ball_diff = abs(p1_balls - p2_balls)
        amount = ball_diff * price_per_ball
        
        if p1_balls > p2_balls:
            winner, loser = p1_name, p2_name
            transfers.append({"from": p2_name, "to": p1_name, "amount": amount, "ballDiff": ball_diff})
        elif p2_balls > p1_balls:
            winner, loser = p2_name, p1_name
            transfers.append({"from": p1_name, "to": p2_name, "amount": amount, "ballDiff": ball_diff})
        else:
            winner, loser = None, None
        
        score = f"{player_stats[p1_name]['wins']}:{player_stats[p2_name]['wins']}"
    else:
        # 多人模式：每人都要与赢最多的人结算
        winner_name = sorted_players[0][0]
        winner_balls = sorted_players[0][1]["balls"]
        winner = winner_name
        loser = sorted_players[-1][0]  # 球最少的是输家
        
        for name, stats in sorted_players[1:]:  # 跳过第一名
            ball_diff = winner_balls - stats["balls"]
            amount = ball_diff * price_per_ball
            if amount > 0:
                transfers.append({
                    "from": name, 
                    "to": winner_name, 
                    "amount": amount, 
                    "ballDiff": ball_diff
                })
        
        score = ":".join([str(player_stats[p["name"]]["wins"]) for p in players])
        ball_diff = winner_balls - sorted_players[-1][1]["balls"]
        amount = sum(t["amount"] for t in transfers)
    
    # 更新数据库
    match_id = room_manager.get_match_id(room_id)
    result = await db.execute(select(Match).where(Match.id == match_id))
    db_match = result.scalar_one()
    
    db_match.status = "settled"
    db_match.settlement_score = score
    db_match.settlement_winner = winner
    db_match.settlement_loser = loser
    db_match.settlement_ball_diff = ball_diff
    db_match.settlement_amount = amount
    db_match.settled_at = datetime.utcnow()
    
    await db.commit()
    
    # 更新房间状态
    room_manager.settle_room(room_id)
    
    # 构建响应
    settlement_data = SettlementResponse(
        score=score,
        winner=winner,
        loser=loser,
        ballDiff=ball_diff,
        amount=amount
    )
    
    match_response = MatchResponse(
        id=match_id,
        roomId=room_id,
        gameType=room["gameType"],
        players=player_names,
        rounds=[RoundResponse(**r) for r in room["rounds"]],
        settlement=settlement_data,
        createdAt=room["createdAt"],
        settledAt=datetime.utcnow().isoformat(),
        transfers=transfers  # 添加转账详情
    )
    
    # 广播结算
    await room_manager.broadcast(room_id, {
        "type": "room_settled",
        "data": room_manager.get_room(room_id),
        "transfers": transfers
    })
    
    return match_response
