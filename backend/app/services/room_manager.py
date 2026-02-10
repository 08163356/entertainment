from typing import Dict, List, Optional, Any
from fastapi import WebSocket
from datetime import datetime
import asyncio

class RoomManager:
    """房间状态管理器"""
    
    def __init__(self):
        # 房间状态 {room_id: room_data}
        self.rooms: Dict[str, dict] = {}
        # WebSocket 连接 {room_id: {user_name: websocket}}
        self.connections: Dict[str, Dict[str, WebSocket]] = {}
        # 房间对应的 match_id
        self.room_match_map: Dict[str, str] = {}
    
    def create_room(
        self, 
        room_id: str, 
        match_id: str,
        game_type: str,
        owner: str, 
        players: List[dict],
        price_per_ball: float
    ):
        """创建房间"""
        self.rooms[room_id] = {
            "id": room_id,
            "gameType": game_type,
            "owner": owner,
            "players": [{"name": p.name, "isPreset": p.isPreset} for p in players],
            "operators": [owner],  # 房主默认有操作权限
            "spectators": [],
            "rounds": [],
            "pricePerBall": price_per_ball,
            "status": "playing",
            "createdAt": datetime.utcnow().isoformat()
        }
        self.connections[room_id] = {}
        self.room_match_map[room_id] = match_id
    
    def get_room(self, room_id: str) -> Optional[dict]:
        """获取房间信息"""
        return self.rooms.get(room_id)
    
    def get_match_id(self, room_id: str) -> Optional[str]:
        """获取房间对应的 match_id"""
        return self.room_match_map.get(room_id)
    
    def add_spectator(self, room_id: str, user_name: str):
        """添加观众"""
        room = self.rooms.get(room_id)
        if room and user_name not in room["spectators"]:
            # 检查是否是玩家
            is_player = any(p["name"] == user_name for p in room["players"])
            if not is_player and user_name not in room["spectators"]:
                room["spectators"].append(user_name)
    
    def remove_spectator(self, room_id: str, user_name: str):
        """移除观众"""
        room = self.rooms.get(room_id)
        if room and user_name in room["spectators"]:
            room["spectators"].remove(user_name)
    
    def add_operator(self, room_id: str, user_name: str):
        """添加操作权限"""
        room = self.rooms.get(room_id)
        if room and user_name not in room["operators"]:
            room["operators"].append(user_name)
            # 如果是观众，从观众列表移除
            if user_name in room["spectators"]:
                room["spectators"].remove(user_name)
    
    def remove_operator(self, room_id: str, user_name: str):
        """移除操作权限"""
        room = self.rooms.get(room_id)
        if room and user_name in room["operators"] and user_name != room["owner"]:
            room["operators"].remove(user_name)
    
    def add_round(self, room_id: str, round_data: Any):
        """添加一局记录"""
        room = self.rooms.get(room_id)
        if room:
            room["rounds"].append(round_data.model_dump())
    
    def remove_last_round(self, room_id: str):
        """移除最后一局"""
        room = self.rooms.get(room_id)
        if room and room["rounds"]:
            room["rounds"].pop()
    
    def settle_room(self, room_id: str):
        """结算房间"""
        room = self.rooms.get(room_id)
        if room:
            room["status"] = "settled"
    
    def remove_room(self, room_id: str):
        """移除房间"""
        if room_id in self.rooms:
            del self.rooms[room_id]
        if room_id in self.connections:
            del self.connections[room_id]
        if room_id in self.room_match_map:
            del self.room_match_map[room_id]
    
    def add_connection(self, room_id: str, user_name: str, websocket: WebSocket):
        """添加 WebSocket 连接"""
        if room_id not in self.connections:
            self.connections[room_id] = {}
        self.connections[room_id][user_name] = websocket
    
    def remove_connection(self, room_id: str, user_name: str):
        """移除 WebSocket 连接"""
        if room_id in self.connections and user_name in self.connections[room_id]:
            del self.connections[room_id][user_name]
        # 同时从观众列表移除
        self.remove_spectator(room_id, user_name)
    
    async def broadcast(self, room_id: str, message: dict, exclude: WebSocket = None):
        """广播消息到房间所有连接"""
        if room_id not in self.connections:
            return
        
        dead_connections = []
        
        for user_name, ws in self.connections[room_id].items():
            if ws == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(user_name)
        
        # 清理断开的连接
        for user_name in dead_connections:
            self.remove_connection(room_id, user_name)

# 全局单例
room_manager = RoomManager()
