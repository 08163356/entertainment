from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.basketball_room_manager import basketball_room_manager

router = APIRouter()


@router.websocket("/ws/basketball/{room_id}/{user_name}")
async def basketball_websocket(websocket: WebSocket, room_id: str, user_name: str):
    """投篮房间 WebSocket 连接"""
    await websocket.accept()
    
    room = basketball_room_manager.get_room(room_id)
    if not room:
        await websocket.close(code=4004, reason="房间不存在")
        return
    
    basketball_room_manager.add_connection(room_id, websocket)
    
    # 广播用户加入
    await basketball_room_manager.broadcast(room_id, {
        "type": "user_joined",
        "data": {"userName": user_name}
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # 处理心跳
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        basketball_room_manager.remove_connection(room_id, websocket)
        await basketball_room_manager.broadcast(room_id, {
            "type": "user_left",
            "data": {"userName": user_name}
        })
    except Exception:
        basketball_room_manager.remove_connection(room_id, websocket)
