export interface Player {
  name: string
  isPreset: boolean
}

export interface Score {
  player: string
  shotType: 'three' | 'two' | 'free'
  made: number
  total: number
  accuracy: number
}

export interface RoundRecord {
  roundNumber: number
  scores: Score[]
  timestamp: string
}

export interface Room {
  id: string
  owner: string
  players: Player[]
  operators: string[]
  selfEditOnly: string[]  // 只能编辑自己的玩家列表
  spectators: string[]
  rounds: RoundRecord[]
  ballsPerRound: number
  pricePerBall: number
  totalRounds: number | null
  status: 'playing' | 'settled'
  createdAt: string
}

export interface TransferDetail {
  fromPlayer: string
  toPlayer: string
  amount: number
  shotsDiff: number
}

export interface PlayerStatSummary {
  name: string
  totalShots: number
  totalMade: number
  accuracy: number
}

export interface Settlement {
  winner: string | null
  playerStats: PlayerStatSummary[]
  transfers: TransferDetail[]
  totalAmount: number
}

export interface MatchRecord {
  id: string
  roomId: string
  owner: string
  players: string[]
  rounds: RoundRecord[]
  ballsPerRound: number
  pricePerBall: number
  totalRounds: number | null
  settlement: Settlement | null
  createdAt: string
  settledAt: string | null
  isZeroMatch?: boolean
}

export interface PracticeRecord {
  id: number
  playerName: string
  shotType: 'three' | 'two' | 'free'
  totalShots: number
  shotsMade: number
  accuracy: number
  createdAt: string
}

export interface PracticeStats {
  shotType: string
  totalSessions: number
  totalShots: number
  totalMade: number
  avgAccuracy: number
  bestAccuracy: number
}

export interface PracticeChartData {
  date: string
  shotType: string
  accuracy: number
  totalShots: number
  shotsMade: number
}

export interface PlayerPracticeStats {
  playerName: string
  totalSessions: number
  statsByType: PracticeStats[]
  chartData: PracticeChartData[]
}

export interface PlayerStats {
  name: string
  totalMatches: number
  totalWins: number
  winRate: number
  totalShots: number
  totalMade: number
  avgAccuracy: number
  netAmount: number
  recentMatches: MatchRecord[]
}

export const PRESET_PLAYERS: Player[] = [
  { name: '阿兴', isPreset: true },
  { name: '老爸', isPreset: true },
  { name: '元礼', isPreset: true }
]

export const SHOT_TYPES = [
  { value: 'three', label: '三分球', color: '#667eea' },
  { value: 'two', label: '两分球', color: '#f5576c' },
  { value: 'free', label: '罚球', color: '#52c41a' }
]
