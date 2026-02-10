from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.room_manager import room_manager

router = APIRouter()

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: str,
    userName: str = Query(...)
):
    """WebSocket 连接端点"""
    room = room_manager.get_room(room_id)
    if not room:
        await websocket.close(code=4004)
        return
    
    await websocket.accept()
    
    # 注册连接
    room_manager.add_connection(room_id, userName, websocket)
    
    # 发送当前房间状态
    await websocket.send_json({
        "type": "room_update",
        "data": room_manager.get_room(room_id)
    })
    
    # 广播用户加入
    await room_manager.broadcast(room_id, {
        "type": "user_joined",
        "data": {
            "userName": userName,
            "room": room_manager.get_room(room_id)
        }
    }, exclude=websocket)
    
    try:
        while True:
            # 保持连接，接收消息（如果需要处理客户端消息）
            data = await websocket.receive_json()
            # 可以在这里处理客户端发来的消息
            
    except WebSocketDisconnect:
        # 移除连接
        room_manager.remove_connection(room_id, userName)
        
        # 广播用户离开
        await room_manager.broadcast(room_id, {
            "type": "user_left",
            "data": {
                "userName": userName,
                "room": room_manager.get_room(room_id)
            }
        })
