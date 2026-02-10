export interface Player {
  name: string
  isPreset: boolean
}

export interface RoundRecord {
  roundNumber: number
  winner: string
  ballsWon: number
  timestamp: string
}

export interface Room {
  id: string
  gameType: 'eight-ball' | 'nine-ball' | 'snooker'
  owner: string
  players: Player[]
  operators: string[]
  spectators: string[]
  rounds: RoundRecord[]
  pricePerBall: number
  status: 'playing' | 'settled'
  createdAt: string
}

export interface MatchRecord {
  id: string
  roomId: string
  gameType: string
  players: string[]
  rounds: RoundRecord[]
  settlement: {
    score: string
    winner: string | null
    loser: string | null
    ballDiff: number
    amount: number
  }
  createdAt: string
  settledAt: string
}

export interface PlayerStats {
  name: string
  totalMatches: number
  totalWins: number
  totalLosses: number
  totalDraws: number
  winRate: number
  totalBallsWon: number
  totalBallsLost: number
  netBalls: number
  netAmount: number
  recentMatches: MatchRecord[]
  opponentStats: {
    opponent: string
    matches: number
    wins: number
    losses: number
    winRate: number
    netBalls: number
    netAmount: number
  }[]
}

export const PRESET_PLAYERS: Player[] = [
  { name: '阿兴', isPreset: true },
  { name: '老爸', isPreset: true },
  { name: '元礼', isPreset: true }
]

export const GAME_TYPES = [
  { value: 'eight-ball', label: '中式黑八' },
  { value: 'nine-ball', label: '九球' },
  { value: 'snooker', label: '斯诺克' }
]
