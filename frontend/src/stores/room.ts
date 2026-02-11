import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Room, RoundRecord, Player } from '@/types/billiards'
import { wsService } from '@/services/websocket'

// 结算结果类型
export interface SettlementResultData {
  room: Room
  settlement: {
    score: string
    winner: string | null
    loser: string | null
    ballDiff: number
    amount: number
  }
  transfers: Array<{
    from: string
    to: string
    amount: number
    ballDiff: number
  }>
  playerStats: Array<{
    name: string
    wins: number
    balls: number
  }>
  isZeroMatch: boolean
}

export const useRoomStore = defineStore('room', () => {
  const room = ref<Room | null>(null)
  const currentUser = ref<string>('')
  const connected = ref(false)
  const settlementResult = ref<SettlementResultData | null>(null)

  const isOwner = computed(() => room.value?.owner === currentUser.value)
  
  const canOperate = computed(() => {
    if (!room.value || !currentUser.value) return false
    return room.value.owner === currentUser.value || 
           room.value.operators.includes(currentUser.value)
  })

  const players = computed(() => room.value?.players || [])
  
  const rounds = computed(() => room.value?.rounds || [])

  const settlement = computed(() => {
    if (!room.value || room.value.players.length !== 2) return null
    
    const [p1, p2] = room.value.players
    let p1Wins = 0, p2Wins = 0, p1Balls = 0, p2Balls = 0

    for (const round of room.value.rounds) {
      if (round.winner === p1.name) {
        p1Wins++
        p1Balls += round.ballsWon
      } else if (round.winner === p2.name) {
        p2Wins++
        p2Balls += round.ballsWon
      }
    }

    const ballDiff = p1Balls - p2Balls
    const pricePerBall = room.value.pricePerBall
    const amount = Math.abs(ballDiff) * pricePerBall

    return {
      player1: { name: p1.name, wins: p1Wins, balls: p1Balls },
      player2: { name: p2.name, wins: p2Wins, balls: p2Balls },
      score: `${p1Wins} : ${p2Wins}`,
      ballDiff: Math.abs(ballDiff),
      winner: ballDiff > 0 ? p1.name : ballDiff < 0 ? p2.name : null,
      loser: ballDiff > 0 ? p2.name : ballDiff < 0 ? p1.name : null,
      amount
    }
  })

  function setRoom(newRoom: Room) {
    room.value = newRoom
  }

  function setCurrentUser(name: string) {
    currentUser.value = name
    localStorage.setItem('userName', name)
  }

  function addRound(round: RoundRecord) {
    if (room.value) {
      room.value.rounds.push(round)
    }
  }

  function undoLastRound() {
    if (room.value && room.value.rounds.length > 0) {
      room.value.rounds.pop()
    }
  }

  function updateOperators(operators: string[]) {
    if (room.value) {
      room.value.operators = operators
    }
  }

  function updateOwner(owner: string, operators: string[]) {
    if (room.value) {
      room.value.owner = owner
      room.value.operators = operators
    }
  }

  function setConnected(status: boolean) {
    connected.value = status
  }

  function setSettlementResult(result: SettlementResultData | null) {
    settlementResult.value = result
  }

  function clearSettlementResult() {
    settlementResult.value = null
  }

  function reset() {
    room.value = null
    connected.value = false
    settlementResult.value = null
  }

  return {
    room,
    currentUser,
    connected,
    settlementResult,
    isOwner,
    canOperate,
    players,
    rounds,
    settlement,
    setRoom,
    setCurrentUser,
    addRound,
    undoLastRound,
    updateOperators,
    updateOwner,
    setConnected,
    setSettlementResult,
    clearSettlementResult,
    reset
  }
})
