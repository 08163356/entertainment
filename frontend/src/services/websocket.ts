import { useRoomStore } from '@/stores/room'
import type { Room, RoundRecord } from '@/types/billiards'

type MessageHandler = (data: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private roomId: string = ''
  private userName: string = ''
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private handlers: Map<string, MessageHandler[]> = new Map()

  connect(roomId: string, userName: string) {
    this.roomId = roomId
    this.userName = userName
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/entertainment/ws/${roomId}?userName=${encodeURIComponent(userName)}`
    
    this.ws = new WebSocket(wsUrl)
    
    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      const roomStore = useRoomStore()
      roomStore.setConnected(true)
    }
    
    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      const roomStore = useRoomStore()
      roomStore.setConnected(false)
      this.attemptReconnect()
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  private handleMessage(message: { type: string; data: any }) {
    const roomStore = useRoomStore()
    
    switch (message.type) {
      case 'room_update':
        roomStore.setRoom(message.data as Room)
        break
      case 'round_added':
        roomStore.addRound(message.data as RoundRecord)
        break
      case 'round_undone':
        roomStore.undoLastRound()
        break
      case 'operators_updated':
        roomStore.updateOperators(message.data.operators)
        break
      case 'owner_transferred':
        roomStore.updateOwner(message.data.owner, message.data.operators)
        break
      case 'room_settled':
        roomStore.setRoom(message.data as Room)
        break
      case 'user_joined':
      case 'user_left':
        // 用户加入/离开，更新房间信息
        if (message.data.room) {
          roomStore.setRoom(message.data.room)
        }
        break
    }
    
    // 触发自定义处理器
    const handlers = this.handlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => handler(message.data))
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => {
        this.connect(this.roomId, this.userName)
      }, 2000 * this.reconnectAttempts)
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, [])
    }
    this.handlers.get(type)!.push(handler)
  }

  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  send(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.handlers.clear()
  }
}

export const wsService = new WebSocketService()
