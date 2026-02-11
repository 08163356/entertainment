import axios from 'axios'
import type { 
  Room, MatchRecord, PlayerStats, 
  PracticeRecord, PlayerPracticeStats 
} from '@/types/basketball'

const api = axios.create({
  baseURL: '/entertainment/api/basketball',
  timeout: 10000
})

// 房间相关
export const basketballRoomApi = {
  // 创建房间
  create(data: {
    owner: string
    players: { name: string; isPreset: boolean }[]
    ballsPerRound: number
    pricePerBall: number
    totalRounds?: number | null
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

  // 提交玩家本轮得分
  submitScore(roomId: string, data: {
    playerName: string
    shotType: string
    made: number
    total: number
  }): Promise<{ success: boolean; currentRoundStatus: CurrentRoundStatus }> {
    return api.post(`/rooms/${roomId}/submit-score`, data).then(res => res.data)
  },

  // 取消玩家本轮提交
  cancelScore(roomId: string, playerName: string): Promise<{ success: boolean; currentRoundStatus: CurrentRoundStatus }> {
    return api.post(`/rooms/${roomId}/cancel-score`, { playerName }).then(res => res.data)
  },

  // 获取当前轮次状态
  getCurrentRoundStatus(roomId: string): Promise<CurrentRoundStatus> {
    return api.get(`/rooms/${roomId}/current-round`).then(res => res.data)
  },

  // 确认本轮
  confirmRound(roomId: string): Promise<{ success: boolean; round: any }> {
    return api.post(`/rooms/${roomId}/confirm-round`).then(res => res.data)
  },

  // 记录一轮（旧接口，保留兼容）
  addRound(roomId: string, data: { 
    scores: { player: string; shotType: string; made: number; total: number }[] 
  }): Promise<void> {
    return api.post(`/rooms/${roomId}/rounds`, data).then(res => res.data)
  },

  // 撤销上一轮
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

  // 转移房主
  transferOwner(roomId: string, userName: string): Promise<void> {
    return api.post(`/rooms/${roomId}/transfer-owner`, { userName }).then(res => res.data)
  },

  // 结算房间
  settle(roomId: string): Promise<MatchRecord> {
    return api.post(`/rooms/${roomId}/settle`).then(res => res.data)
  },

  // 获取进行中的房间
  getActiveRooms(): Promise<{ roomId: string; players: string[]; roundCount: number; playerScores: Record<string, number> }[]> {
    return api.get('/rooms/active').then(res => res.data)
  }
}

// 当前轮次状态类型
export interface CurrentRoundStatus {
  submitted: {
    name: string
    shotType: string
    made: number
    total: number
    submitted: boolean
  }[]
  pending: string[]
  allSubmitted: boolean
}

// 历史记录相关
export const basketballHistoryApi = {
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
export const basketballPlayerApi = {
  // 获取所有玩家列表
  getPlayers(): Promise<{ name: string; isPreset: boolean; matchCount: number }[]> {
    return api.get('/matches/players').then(res => res.data)
  },

  // 获取玩家详细统计
  getStats(playerName: string): Promise<PlayerStats> {
    return api.get(`/matches/players/${encodeURIComponent(playerName)}/stats`).then(res => res.data)
  }
}

// 个人练习相关
export const basketballPracticeApi = {
  // 记录一次练习
  create(data: {
    playerName: string
    shotType: string
    totalShots: number
    shotsMade: number
  }): Promise<PracticeRecord> {
    return api.post('/practices', data).then(res => res.data)
  },

  // 获取练习记录列表
  getList(params?: {
    player?: string
    shotType?: string
    limit?: number
    offset?: number
  }): Promise<{ total: number; practices: PracticeRecord[] }> {
    return api.get('/practices', { params }).then(res => res.data)
  },

  // 删除练习记录
  delete(practiceId: number): Promise<void> {
    return api.delete(`/practices/${practiceId}`).then(res => res.data)
  },

  // 获取玩家练习统计
  getStats(playerName: string, period?: string): Promise<PlayerPracticeStats> {
    return api.get(`/practices/stats/${encodeURIComponent(playerName)}`, { 
      params: { period } 
    }).then(res => res.data)
  }
}

export default api
