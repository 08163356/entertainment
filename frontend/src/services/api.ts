import axios from 'axios'
import type { Room, MatchRecord, PlayerStats } from '@/types/billiards'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 房间相关
export const roomApi = {
  // 创建房间
  create(data: {
    gameType: string
    owner: string
    players: { name: string; isPreset: boolean }[]
    pricePerBall: number
  }): Promise<{ roomId: string }> {
    return api.post('/rooms', data).then(res => res.data)
  },

  // 获取房间信息
  get(roomId: string): Promise<Room> {
    return api.get(`/rooms/${roomId}`).then(res => res.data)
  },

  // 加入房间
  join(roomId: string, userName: string): Promise<Room> {
    return api.post(`/rooms/${roomId}/join`, { userName }).then(res => res.data)
  },

  // 记录一局
  addRound(roomId: string, data: { winner: string; ballsWon: number }): Promise<void> {
    return api.post(`/rooms/${roomId}/rounds`, data).then(res => res.data)
  },

  // 撤销上一局
  undoRound(roomId: string): Promise<void> {
    return api.delete(`/rooms/${roomId}/rounds/last`).then(res => res.data)
  },

  // 授权操作权限
  grantOperator(roomId: string, userName: string): Promise<void> {
    return api.post(`/rooms/${roomId}/operators`, { userName }).then(res => res.data)
  },

  // 撤销操作权限
  revokeOperator(roomId: string, userName: string): Promise<void> {
    return api.delete(`/rooms/${roomId}/operators/${userName}`).then(res => res.data)
  },

  // 结算房间
  settle(roomId: string): Promise<MatchRecord> {
    return api.post(`/rooms/${roomId}/settle`).then(res => res.data)
  }
}

// 历史记录相关
export const historyApi = {
  // 获取所有比赛记录
  getMatches(params?: { 
    player?: string
    limit?: number 
    offset?: number 
  }): Promise<{ total: number; matches: MatchRecord[] }> {
    return api.get('/matches', { params }).then(res => res.data)
  },

  // 获取单场比赛详情
  getMatch(matchId: string): Promise<MatchRecord> {
    return api.get(`/matches/${matchId}`).then(res => res.data)
  }
}

// 玩家统计相关
export const playerApi = {
  // 获取所有玩家列表
  getPlayers(): Promise<{ name: string; matchCount: number }[]> {
    return api.get('/players').then(res => res.data)
  },

  // 获取玩家详细统计
  getStats(playerName: string): Promise<PlayerStats> {
    return api.get(`/players/${encodeURIComponent(playerName)}/stats`).then(res => res.data)
  }
}

export default api
