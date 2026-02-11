import { useBasketballRoomStore } from '@/stores/basketballRoom'

class BasketballWebSocketService {
  private ws: WebSocket | null = null
  private roomId: string = ''
  private userName: string = ''
  private reconnectTimer: number | null = null
  private pingTimer: number | null = null

  connect(roomId: string, userName: string) {
    this.roomId = roomId
    this.userName = userName
    this.doConnect()
  }

  private doConnect() {
    const store = useBasketballRoomStore()
    
    // 构建 WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/entertainment/ws/basketball/${this.roomId}/${encodeURIComponent(this.userName)}`
    
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('Basketball WebSocket connected')
      store.setConnected(true)
      this.startPing()
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message', e)
      }
    }

    this.ws.onclose = () => {
      console.log('Basketball WebSocket disconnected')
      store.setConnected(false)
      this.stopPing()
      this.scheduleReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('Basketball WebSocket error', error)
    }
  }

  private handleMessage(message: { type: string; data: any }) {
    const store = useBasketballRoomStore()

    switch (message.type) {
      case 'pong':
        // 心跳响应
        break
        
      case 'round_added':
        store.addRound(message.data)
        break
        
      case 'round_confirmed':
        // 新的轮次确认
        store.addRound(message.data)
        store.clearCurrentRound()
        break
        
      case 'player_score_submitted':
        // 玩家提交得分
        store.updateCurrentRoundStatus(message.data.currentRoundStatus)
        break
        
      case 'player_score_cancelled':
        // 玩家取消提交
        store.updateCurrentRoundStatus(message.data.currentRoundStatus)
        break
        
      case 'round_undone':
        store.removeLastRound()
        break
        
      case 'operators_updated':
        store.updateOperators(message.data.operators, message.data.selfEditOnly)
        break
        
      case 'owner_transferred':
        store.updateOwner(message.data.owner, message.data.operators)
        break
        
      case 'room_settled':
        if (store.room) {
          store.room.status = 'settled'
        }
        break
        
      case 'user_joined':
      case 'user_left':
        // 可以添加用户加入/离开的通知
        break
    }
  }

  private startPing() {
    this.pingTimer = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
  }

  private stopPing() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer)
      this.pingTimer = null
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return
    
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null
      if (this.roomId && this.userName) {
        this.doConnect()
      }
    }, 3000)
  }

  disconnect() {
    this.stopPing()
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.roomId = ''
    this.userName = ''
  }
}

export const basketballWsService = new BasketballWebSocketService()
