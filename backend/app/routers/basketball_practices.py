from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models_basketball import BasketballPractice, BasketballPlayer
from app.schemas_basketball import (
    PracticeCreate, PracticeResponse, PracticeListResponse,
    PlayerPracticeStats, PracticeStats, PracticeChartData
)

router = APIRouter()


@router.post("", response_model=PracticeResponse)
async def create_practice(data: PracticeCreate, db: AsyncSession = Depends(get_db)):
    """记录一次练习"""
    # 确保玩家存在
    result = await db.execute(select(BasketballPlayer).where(BasketballPlayer.name == data.playerName))
    existing = result.scalar_one_or_none()
    if not existing:
        db_player = BasketballPlayer(name=data.playerName, is_preset=False)
        db.add(db_player)
        await db.commit()
    
    accuracy = (data.shotsMade / data.totalShots * 100) if data.totalShots > 0 else 0
    
    practice = BasketballPractice(
        player_name=data.playerName,
        shot_type=data.shotType,
        total_shots=data.totalShots,
        shots_made=data.shotsMade,
        accuracy=round(accuracy, 1)
    )
    db.add(practice)
    await db.commit()
    await db.refresh(practice)
    
    return PracticeResponse(
        id=practice.id,
        playerName=practice.player_name,
        shotType=practice.shot_type,
        totalShots=practice.total_shots,
        shotsMade=practice.shots_made,
        accuracy=practice.accuracy,
        createdAt=practice.created_at.isoformat()
    )


@router.get("", response_model=PracticeListResponse)
async def get_practices(
    player: Optional[str] = None,
    shotType: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取练习记录列表"""
    query = select(BasketballPractice)
    count_query = select(func.count(BasketballPractice.id))
    
    if player:
        query = query.where(BasketballPractice.player_name == player)
        count_query = count_query.where(BasketballPractice.player_name == player)
    
    if shotType:
        query = query.where(BasketballPractice.shot_type == shotType)
        count_query = count_query.where(BasketballPractice.shot_type == shotType)
    
    # 总数
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 分页查询
    query = query.order_by(desc(BasketballPractice.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    practices = result.scalars().all()
    
    return PracticeListResponse(
        total=total,
        practices=[
            PracticeResponse(
                id=p.id,
                playerName=p.player_name,
                shotType=p.shot_type,
                totalShots=p.total_shots,
                shotsMade=p.shots_made,
                accuracy=p.accuracy,
                createdAt=p.created_at.isoformat()
            )
            for p in practices
        ]
    )


@router.delete("/{practice_id}")
async def delete_practice(practice_id: int, db: AsyncSession = Depends(get_db)):
    """删除练习记录"""
    result = await db.execute(select(BasketballPractice).where(BasketballPractice.id == practice_id))
    practice = result.scalar_one_or_none()
    
    if not practice:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    await db.delete(practice)
    await db.commit()
    
    return {"success": True}


@router.get("/stats/{player_name}", response_model=PlayerPracticeStats)
async def get_player_practice_stats(
    player_name: str,
    period: str = "all",  # all, week, month
    db: AsyncSession = Depends(get_db)
):
    """获取玩家练习统计"""
    query = select(BasketballPractice).where(BasketballPractice.player_name == player_name)
    
    # 时间筛选
    if period == "week":
        start_date = datetime.utcnow() - timedelta(days=7)
        query = query.where(BasketballPractice.created_at >= start_date)
    elif period == "month":
        start_date = datetime.utcnow() - timedelta(days=30)
        query = query.where(BasketballPractice.created_at >= start_date)
    
    result = await db.execute(query.order_by(BasketballPractice.created_at))
    practices = result.scalars().all()
    
    # 按类型分组统计
    type_stats = {}
    for p in practices:
        if p.shot_type not in type_stats:
            type_stats[p.shot_type] = {
                "totalSessions": 0,
                "totalShots": 0,
                "totalMade": 0,
                "bestAccuracy": 0
            }
        
        stats = type_stats[p.shot_type]
        stats["totalSessions"] += 1
        stats["totalShots"] += p.total_shots
        stats["totalMade"] += p.shots_made
        if p.accuracy > stats["bestAccuracy"]:
            stats["bestAccuracy"] = p.accuracy
    
    stats_by_type = []
    for shot_type, stats in type_stats.items():
        avg_accuracy = (stats["totalMade"] / stats["totalShots"] * 100) if stats["totalShots"] > 0 else 0
        stats_by_type.append(PracticeStats(
            shotType=shot_type,
            totalSessions=stats["totalSessions"],
            totalShots=stats["totalShots"],
            totalMade=stats["totalMade"],
            avgAccuracy=round(avg_accuracy, 1),
            bestAccuracy=stats["bestAccuracy"]
        ))
    
    # 图表数据（按日期聚合）
    chart_data = []
    for p in practices:
        chart_data.append(PracticeChartData(
            date=p.created_at.strftime("%Y-%m-%d %H:%M"),
            shotType=p.shot_type,
            accuracy=p.accuracy,
            totalShots=p.total_shots,
            shotsMade=p.shots_made
        ))
    
    return PlayerPracticeStats(
        playerName=player_name,
        totalSessions=len(practices),
        statsByType=stats_by_type,
        chartData=chart_data
    )
