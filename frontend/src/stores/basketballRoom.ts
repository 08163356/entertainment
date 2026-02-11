import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Room, RoundRecord, Player } from '@/types/basketball'
import type { CurrentRoundStatus } from '@/services/basketballApi'

export const useBasketballRoomStore = defineStore('basketballRoom', () => {
  const room = ref<Room | null>(null)
  const currentUser = ref<string>('')
  const connected = ref(false)
  
  // 当前轮次状态
  const currentRoundStatus = ref<CurrentRoundStatus>({
    submitted: [],
    pending: [],
    allSubmitted: false
  })

  const isOwner = computed(() => {
    if (!room.value || !currentUser.value) return false
    return room.value.owner === currentUser.value
  })

  const canOperate = computed(() => {
    if (!room.value || !currentUser.value) return false
    return room.value.operators.includes(currentUser.value)
  })
  
  // 当前用户是否只能编辑自己
  const isSelfEditOnly = computed(() => {
    if (!room.value || !currentUser.value) return false
    return room.value.selfEditOnly?.includes(currentUser.value) || false
  })
  
  // 当前用户是否是参赛玩家
  const isPlayer = computed(() => {
    if (!room.value || !currentUser.value) return false
    return room.value.players.some(p => p.name === currentUser.value)
  })
  
  // 当前用户是否已提交本轮得分
  const hasSubmitted = computed(() => {
    return currentRoundStatus.value.submitted.some(s => s.name === currentUser.value)
  })

  const players = computed(() => room.value?.players || [])
  const rounds = computed(() => room.value?.rounds || [])

  // 获取玩家总进球数
  function getPlayerTotalMade(playerName: string): number {
    if (!room.value) return 0
    let total = 0
    for (const round of room.value.rounds) {
      for (const score of round.scores) {
        if (score.player === playerName) {
          total += score.made
        }
      }
    }
    return total
  }

  // 获取玩家总投球数
  function getPlayerTotalShots(playerName: string): number {
    if (!room.value) return 0
    let total = 0
    for (const round of room.value.rounds) {
      for (const score of round.scores) {
        if (score.player === playerName) {
          total += score.total
        }
      }
    }
    return total
  }

  // 获取玩家命中率
  function getPlayerAccuracy(playerName: string): number {
    const shots = getPlayerTotalShots(playerName)
    const made = getPlayerTotalMade(playerName)
    if (shots === 0) return 0
    return Math.round((made / shots) * 100 * 10) / 10
  }

  function setRoom(data: Room) {
    room.value = data
  }

  function setCurrentUser(name: string) {
    currentUser.value = name
    localStorage.setItem('basketballUserName', name)
  }

  function setConnected(value: boolean) {
    connected.value = value
  }

  function addRound(roundData: RoundRecord) {
    if (room.value) {
      room.value.rounds.push(roundData)
    }
  }

  function removeLastRound() {
    if (room.value && room.value.rounds.length > 0) {
      room.value.rounds.pop()
    }
  }

  function updateOperators(operators: string[], selfEditOnly?: string[]) {
    if (room.value) {
      room.value.operators = operators
      if (selfEditOnly !== undefined) {
        room.value.selfEditOnly = selfEditOnly
      }
    }
  }

  function updateOwner(owner: string, operators: string[]) {
    if (room.value) {
      room.value.owner = owner
      room.value.operators = operators
    }
  }
  
  function updateCurrentRoundStatus(status: CurrentRoundStatus) {
    currentRoundStatus.value = status
  }
  
  function clearCurrentRound() {
    currentRoundStatus.value = {
      submitted: [],
      pending: room.value?.players.map(p => p.name) || [],
      allSubmitted: false
    }
  }

  function reset() {
    room.value = null
    connected.value = false
    currentRoundStatus.value = {
      submitted: [],
      pending: [],
      allSubmitted: false
    }
  }

  return {
    room,
    currentUser,
    connected,
    currentRoundStatus,
    isOwner,
    canOperate,
    isSelfEditOnly,
    isPlayer,
    hasSubmitted,
    players,
    rounds,
    getPlayerTotalMade,
    getPlayerTotalShots,
    getPlayerAccuracy,
    setRoom,
    setCurrentUser,
    setConnected,
    addRound,
    removeLastRound,
    updateOperators,
    updateOwner,
    updateCurrentRoundStatus,
    clearCurrentRound,
    reset
  }
})
