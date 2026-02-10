<template>
  <div class="billiards-page">
    <header class="header">
      <t-button variant="text" @click="router.push('/')">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <h1>台球记分</h1>
      <div class="header-actions">
        <t-button variant="text" @click="router.push('/billiards/history')">
          历史记录
        </t-button>
      </div>
    </header>

    <main class="main-content">
      <!-- 进行中的对局 -->
      <div class="card active-rooms" v-if="activeRooms.length > 0">
        <h2>进行中的对局</h2>
        <div class="room-list">
          <div 
            v-for="room in activeRooms" 
            :key="room.roomId"
            class="room-item"
            @click="quickJoin(room)"
          >
            <div class="room-players">
              <span v-for="(p, i) in room.players" :key="p">
                {{ p }}{{ i < room.players.length - 1 ? ' vs ' : '' }}
              </span>
            </div>
            <div class="room-meta">
              <t-tag theme="primary" size="small">房间 {{ room.roomId }}</t-tag>
              <span class="round-count">第 {{ room.roundCount + 1 }} 局</span>
            </div>
            <t-icon name="chevron-right" class="arrow" />
          </div>
        </div>
      </div>

      <!-- 创建房间 -->
      <div class="card create-room">
        <h2>创建新比赛</h2>
        
        <t-form :data="formData" ref="formRef" @submit="handleCreate">
          <t-form-item label="比赛类型">
            <t-select v-model="formData.gameType" :options="gameTypeOptions" />
          </t-form-item>
          
          <!-- 玩家列表 -->
          <t-form-item label="参赛玩家">
            <div class="players-section">
              <div 
                v-for="(player, index) in formData.players" 
                :key="index"
                class="player-input-row"
              >
                <div class="player-avatar-mini" :class="`player-${index + 1}`">
                  {{ index + 1 }}
                </div>
                <t-select
                  v-model="formData.players[index]"
                  :options="getPlayerOptions(index)"
                  filterable
                  creatable
                  placeholder="选择或输入玩家名"
                  class="player-select"
                />
                <t-button 
                  v-if="formData.players.length > 2"
                  variant="text" 
                  theme="danger"
                  shape="circle"
                  size="small"
                  @click="removePlayer(index)"
                >
                  <t-icon name="close" />
                </t-button>
              </div>
              
              <t-button 
                v-if="formData.players.length < 4"
                variant="dashed" 
                block
                @click="addPlayer"
                class="add-player-btn"
              >
                <t-icon name="add" /> 添加玩家（最多4人）
              </t-button>
            </div>
          </t-form-item>
          
          <t-form-item label="单价（元/球）">
            <t-input-number v-model="formData.pricePerBall" :min="0" :max="1000" />
          </t-form-item>
          
          <t-form-item label="你是谁">
            <t-select v-model="formData.currentUser" :options="currentUserOptions" />
          </t-form-item>
          
          <t-form-item>
            <t-button theme="primary" type="submit" block size="large" class="big-btn">
              创建房间开始比赛
            </t-button>
          </t-form-item>
        </t-form>
      </div>

      <!-- 加入房间 -->
      <div class="card join-room">
        <h2>加入房间</h2>
        <t-form @submit="handleJoin">
          <t-form-item label="房间号">
            <t-input v-model="joinRoomId" placeholder="输入房间号" />
          </t-form-item>
          <t-form-item label="你的名字">
            <t-select
              v-model="joinUserName"
              :options="allPlayerOptions"
              filterable
              creatable
              placeholder="选择或输入你的名字"
            />
          </t-form-item>
          <t-form-item>
            <t-button theme="default" type="submit" block size="large">
              加入房间
            </t-button>
          </t-form-item>
        </t-form>
      </div>

      <!-- 玩家统计入口 -->
      <div class="card player-stats-entry">
        <h2>玩家战绩</h2>
        <div class="player-list">
          <div 
            v-for="(player, index) in allPlayersWithStats" 
            :key="player.name"
            class="player-item"
            @click="router.push(`/billiards/player/${encodeURIComponent(player.name)}`)"
          >
            <div class="player-avatar" :class="`player-${(index % 4) + 1}`">
              {{ player.name[0] }}
            </div>
            <div class="player-info">
              <span class="name">{{ player.name }}</span>
              <span class="match-count" v-if="player.matchCount > 0">{{ player.matchCount }} 场比赛</span>
            </div>
            <t-icon name="chevron-right" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { roomApi, playerApi } from '@/services/api'
import { useRoomStore } from '@/stores/room'
import { PRESET_PLAYERS, GAME_TYPES } from '@/types/billiards'

const router = useRouter()
const roomStore = useRoomStore()

const formRef = ref()
const formData = ref({
  gameType: 'eight-ball',
  players: ['阿兴', '老爸'],  // 默认2人
  pricePerBall: 5,
  currentUser: '阿兴'
})

const joinRoomId = ref('')
const joinUserName = ref(localStorage.getItem('userName') || '')

// 所有玩家（预设+数据库中的）
const allPlayersWithStats = ref<{ name: string; matchCount: number }[]>([])

// 进行中的房间
const activeRooms = ref<{ roomId: string; players: string[]; roundCount: number }[]>([])

const gameTypeOptions = GAME_TYPES.map(t => ({ label: t.label, value: t.value }))

const allPlayerOptions = computed(() => {
  const names = new Set([
    ...PRESET_PLAYERS.map(p => p.name),
    ...allPlayersWithStats.value.map(p => p.name)
  ])
  return Array.from(names).map(name => ({ label: name, value: name }))
})

function getPlayerOptions(currentIndex: number) {
  // 过滤掉已选择的其他玩家
  const selectedPlayers = formData.value.players.filter((_, i) => i !== currentIndex)
  return allPlayerOptions.value.filter(opt => !selectedPlayers.includes(opt.value))
}

const currentUserOptions = computed(() => 
  formData.value.players
    .filter(p => p)
    .map(p => ({ label: p, value: p }))
)

function addPlayer() {
  if (formData.value.players.length < 4) {
    formData.value.players.push('')
  }
}

function removePlayer(index: number) {
  if (formData.value.players.length > 2) {
    formData.value.players.splice(index, 1)
    // 如果当前用户被移除，重置
    if (!formData.value.players.includes(formData.value.currentUser)) {
      formData.value.currentUser = formData.value.players[0] || ''
    }
  }
}

async function handleCreate() {
  const validPlayers = formData.value.players.filter(p => p.trim())
  
  if (validPlayers.length < 2) {
    MessagePlugin.warning('至少需要2名玩家')
    return
  }
  
  const uniquePlayers = new Set(validPlayers)
  if (uniquePlayers.size !== validPlayers.length) {
    MessagePlugin.warning('玩家名不能重复')
    return
  }
  
  if (!formData.value.currentUser) {
    MessagePlugin.warning('请选择你是谁')
    return
  }
  
  try {
    const isPreset = (name: string) => PRESET_PLAYERS.some(p => p.name === name)
    
    const { roomId } = await roomApi.create({
      gameType: formData.value.gameType,
      owner: formData.value.currentUser,
      players: validPlayers.map(name => ({ 
        name, 
        isPreset: isPreset(name) 
      })),
      pricePerBall: formData.value.pricePerBall
    })
    
    roomStore.setCurrentUser(formData.value.currentUser)
    router.push(`/billiards/room/${roomId}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '创建房间失败')
  }
}

async function handleJoin() {
  if (!joinRoomId.value) {
    MessagePlugin.warning('请输入房间号')
    return
  }
  if (!joinUserName.value) {
    MessagePlugin.warning('请输入你的名字')
    return
  }
  
  try {
    await roomApi.join(joinRoomId.value, joinUserName.value)
    roomStore.setCurrentUser(joinUserName.value)
    router.push(`/billiards/room/${joinRoomId.value}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '加入房间失败')
  }
}

async function quickJoin(room: { roomId: string }) {
  const userName = formData.value.currentUser || localStorage.getItem('userName')
  if (!userName) {
    MessagePlugin.warning('请先选择你的身份')
    return
  }
  
  try {
    await roomApi.join(room.roomId, userName)
    roomStore.setCurrentUser(userName)
    router.push(`/billiards/room/${room.roomId}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '加入房间失败')
  }
}

async function loadData() {
  try {
    // 加载所有玩家
    const players = await playerApi.getPlayers()
    // 合并预设玩家
    const presetNames = PRESET_PLAYERS.map(p => p.name)
    const existingNames = players.map(p => p.name)
    
    allPlayersWithStats.value = [
      ...PRESET_PLAYERS.map(p => ({
        name: p.name,
        matchCount: players.find(x => x.name === p.name)?.matchCount || 0
      })),
      ...players.filter(p => !presetNames.includes(p.name))
    ]
    
    // 加载进行中的房间
    try {
      const rooms = await roomApi.getActiveRooms()
      activeRooms.value = rooms
    } catch {
      // 可能API不存在，忽略
    }
  } catch (e) {
    console.error('加载数据失败', e)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.billiards-page {
  min-height: 100vh;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 24px;
    color: var(--text-color);
    font-weight: 700;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }
}

.main-content {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  
  h2 {
    font-size: 18px;
    margin-bottom: 20px;
    color: var(--text-color);
    font-weight: 600;
  }
}

// 进行中房间
.active-rooms {
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.15), rgba(82, 196, 26, 0.05));
  border-color: rgba(82, 196, 26, 0.3);
  
  h2 {
    color: var(--success-color);
  }
}

.room-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.room-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(4px);
  }
  
  .room-players {
    flex: 1;
    font-weight: 600;
    color: var(--text-color);
  }
  
  .room-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .round-count {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
  
  .arrow {
    color: var(--text-secondary);
  }
}

// 玩家输入区
.players-section {
  width: 100%;
}

.player-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  
  .player-avatar-mini {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
    color: white;
    flex-shrink: 0;
    
    &.player-1 { background: linear-gradient(135deg, #667eea, #764ba2); }
    &.player-2 { background: linear-gradient(135deg, #f093fb, #f5576c); }
    &.player-3 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
    &.player-4 { background: linear-gradient(135deg, #fa709a, #fee140); }
  }
  
  .player-select {
    flex: 1;
  }
}

.add-player-btn {
  margin-top: 8px;
  border-color: var(--primary-color) !important;
  color: var(--primary-color) !important;
  
  &:hover {
    background: rgba(26, 93, 26, 0.1) !important;
  }
}

// 玩家列表
.player-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.player-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.03);
  
  &:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateX(4px);
  }
  
  .player-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: bold;
    color: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    
    &.player-1 { background: linear-gradient(135deg, #667eea, #764ba2); }
    &.player-2 { background: linear-gradient(135deg, #f093fb, #f5576c); }
    &.player-3 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
    &.player-4 { background: linear-gradient(135deg, #fa709a, #fee140); }
  }
  
  .player-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    
    .name {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-color);
    }
    
    .match-count {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

// 响应式
@media (max-width: 480px) {
  .billiards-page {
    padding: 16px;
  }
  
  .card {
    padding: 20px;
  }
  
  .header h1 {
    font-size: 20px;
  }
}
</style>
