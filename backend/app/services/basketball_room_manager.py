"""投篮房间内存管理器"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio


class BasketballRoomManager:
    def __init__(self):
        self.rooms: Dict[str, dict] = {}
        self.match_ids: Dict[str, str] = {}  # room_id -> match_id
        self.connections: Dict[str, List[Any]] = {}  # room_id -> [websocket]
    
    def create_room(
        self,
        room_id: str,
        match_id: str,
        owner: str,
        players: List[dict],
        balls_per_round: int = 10,
        price_per_ball: float = 2.0,
        total_rounds: Optional[int] = None
    ):
        self.rooms[room_id] = {
            "id": room_id,
            "owner": owner,
            "players": [{"name": p.name, "isPreset": p.isPreset} for p in players],
            "operators": [owner] + [p.name for p in players],  # 所有参赛者默认有权限
            "spectators": [],
            "rounds": [],
            "ballsPerRound": balls_per_round,
            "pricePerBall": price_per_ball,
            "totalRounds": total_rounds,
            "status": "playing",
            "createdAt": datetime.utcnow().isoformat(),
            # 当前轮次临时数据
            "currentRound": {}  # player_name -> { shotType, made, total, submitted }
        }
        self.match_ids[room_id] = match_id
        self.connections[room_id] = []
    
    def get_room(self, room_id: str) -> Optional[dict]:
        return self.rooms.get(room_id)
    
    def get_match_id(self, room_id: str) -> Optional[str]:
        return self.match_ids.get(room_id)
    
    def add_spectator(self, room_id: str, user_name: str):
        room = self.rooms.get(room_id)
        if room:
            # 检查是否已经是玩家或观众
            is_player = any(p["name"] == user_name for p in room["players"])
            is_spectator = user_name in room["spectators"]
            
            if not is_player and not is_spectator:
                room["spectators"].append(user_name)
    
    def add_round(self, room_id: str, round_data: dict):
        room = self.rooms.get(room_id)
        if room:
            room["rounds"].append(round_data)
    
    def remove_last_round(self, room_id: str):
        room = self.rooms.get(room_id)
        if room and room["rounds"]:
            room["rounds"].pop()
    
    def submit_player_score(self, room_id: str, player_name: str, score_data: dict) -> bool:
        """提交玩家本轮得分"""
        room = self.rooms.get(room_id)
        if not room:
            return False
        
        # 检查是否是参赛玩家
        is_player = any(p["name"] == player_name for p in room["players"])
        if not is_player:
            return False
        
        room["currentRound"][player_name] = {
            "shotType": score_data.get("shotType", "two"),
            "made": score_data.get("made", 0),
            "total": score_data.get("total", room["ballsPerRound"]),
            "submitted": True
        }
        return True
    
    def cancel_player_score(self, room_id: str, player_name: str) -> bool:
        """取消玩家本轮提交"""
        room = self.rooms.get(room_id)
        if not room:
            return False
        
        if player_name in room["currentRound"]:
            del room["currentRound"][player_name]
            return True
        return False
    
    def get_current_round_status(self, room_id: str) -> dict:
        """获取当前轮次状态"""
        room = self.rooms.get(room_id)
        if not room:
            return {"submitted": [], "pending": []}
        
        submitted = []
        pending = []
        
        for p in room["players"]:
            player_name = p["name"]
            if player_name in room["currentRound"] and room["currentRound"][player_name].get("submitted"):
                submitted.append({
                    "name": player_name,
                    **room["currentRound"][player_name]
                })
            else:
                pending.append(player_name)
        
        return {
            "submitted": submitted,
            "pending": pending,
            "allSubmitted": len(pending) == 0 and len(submitted) == len(room["players"])
        }
    
    def confirm_round(self, room_id: str) -> Optional[dict]:
        """确认本轮（所有人完成后调用）"""
        room = self.rooms.get(room_id)
        if not room:
            return None
        
        status = self.get_current_round_status(room_id)
        if not status["allSubmitted"]:
            return None
        
        # 构建轮次数据
        round_number = len(room["rounds"]) + 1
        scores = []
        
        for p in room["players"]:
            player_name = p["name"]
            data = room["currentRound"].get(player_name, {})
            made = data.get("made", 0)
            total = data.get("total", room["ballsPerRound"])
            accuracy = (made / total * 100) if total > 0 else 0
            
            scores.append({
                "player": player_name,
                "shotType": data.get("shotType", "two"),
                "made": made,
                "total": total,
                "accuracy": round(accuracy, 1)
            })
        
        round_data = {
            "roundNumber": round_number,
            "scores": scores,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 添加到轮次记录并清空当前轮次
        room["rounds"].append(round_data)
        room["currentRound"] = {}
        
        return round_data
    
    def add_operator(self, room_id: str, user_name: str):
        room = self.rooms.get(room_id)
        if room and user_name not in room["operators"]:
            room["operators"].append(user_name)
    
    def remove_operator(self, room_id: str, user_name: str):
        room = self.rooms.get(room_id)
        if room and user_name in room["operators"]:
            # 不能移除房主权限
            if user_name != room["owner"]:
                room["operators"].remove(user_name)
    
    def transfer_owner(self, room_id: str, new_owner: str) -> bool:
        room = self.rooms.get(room_id)
        if room:
            # 检查新房主是否是参赛玩家
            is_player = any(p["name"] == new_owner for p in room["players"])
            if is_player:
                room["owner"] = new_owner
                # 确保新房主有操作权限
                if new_owner not in room["operators"]:
                    room["operators"].append(new_owner)
                return True
        return False
    
    def settle_room(self, room_id: str):
        room = self.rooms.get(room_id)
        if room:
            room["status"] = "settled"
    
    def delete_room(self, room_id: str):
        if room_id in self.rooms:
            del self.rooms[room_id]
        if room_id in self.match_ids:
            del self.match_ids[room_id]
        if room_id in self.connections:
            del self.connections[room_id]
    
    # WebSocket 相关
    def add_connection(self, room_id: str, websocket):
        if room_id not in self.connections:
            self.connections[room_id] = []
        self.connections[room_id].append(websocket)
    
    def remove_connection(self, room_id: str, websocket):
        if room_id in self.connections:
            try:
                self.connections[room_id].remove(websocket)
            except ValueError:
                pass
    
    async def broadcast(self, room_id: str, message: dict):
        """广播消息给房间内所有连接"""
        if room_id in self.connections:
            for ws in self.connections[room_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass


basketball_room_manager = BasketballRoomManager()
