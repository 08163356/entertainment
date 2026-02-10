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
      <!-- 进行中的对局（折叠面板） -->
      <div class="action-panel">
        <div 
          class="panel-header"
          :class="{ active: expandedPanel === 'active', hasItems: activeRooms.length > 0 }"
          @click="togglePanel('active')"
        >
          <div class="panel-title">
            <t-icon name="play-circle" />
            <span>进行中的比赛</span>
            <t-badge v-if="activeRooms.length > 0" :count="activeRooms.length" />
          </div>
          <t-icon :name="expandedPanel === 'active' ? 'chevron-up' : 'chevron-down'" class="arrow" />
        </div>
        <t-collapse-transition>
          <div class="panel-content" v-show="expandedPanel === 'active'">
            <div v-if="activeRooms.length > 0" class="room-list">
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
            <div v-else class="empty-tip">暂无进行中的比赛</div>
          </div>
        </t-collapse-transition>
      </div>

      <!-- 创建新比赛（折叠面板） -->
      <div class="action-panel">
        <div 
          class="panel-header create"
          :class="{ active: expandedPanel === 'create' }"
          @click="togglePanel('create')"
        >
          <div class="panel-title">
            <t-icon name="add-circle" />
            <span>创建新比赛</span>
          </div>
          <t-icon :name="expandedPanel === 'create' ? 'chevron-up' : 'chevron-down'" class="arrow" />
        </div>
        <t-collapse-transition>
          <div class="panel-content" v-show="expandedPanel === 'create'">
            <t-form :data="formData" ref="formRef" @submit="handleCreate">
              <t-form-item label="比赛类型">
                <t-select v-model="formData.gameType" :options="gameTypeOptions" />
              </t-form-item>
              
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
              
              <t-form-item label="默认比分展示">
                <t-radio-group v-model="formData.defaultScoreMode">
                  <t-radio value="rounds">对局比分</t-radio>
                  <t-radio value="balls">球数比</t-radio>
                </t-radio-group>
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
        </t-collapse-transition>
      </div>

      <!-- 加入房间（折叠面板） -->
      <div class="action-panel">
        <div 
          class="panel-header join"
          :class="{ active: expandedPanel === 'join' }"
          @click="togglePanel('join')"
        >
          <div class="panel-title">
            <t-icon name="enter" />
            <span>加入房间</span>
          </div>
          <t-icon :name="expandedPanel === 'join' ? 'chevron-up' : 'chevron-down'" class="arrow" />
        </div>
        <t-collapse-transition>
          <div class="panel-content" v-show="expandedPanel === 'join'">
            <t-form @submit="handleJoin">
              <t-form-item label="房间号或链接">
                <t-input 
                  v-model="joinInput" 
                  placeholder="输入房间号(如:1234)或分享链接"
                  clearable
                />
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
        </t-collapse-transition>
      </div>

      <!-- 玩家战绩（折叠面板） -->
      <div class="action-panel">
        <div 
          class="panel-header stats"
          :class="{ active: expandedPanel === 'stats' }"
          @click="togglePanel('stats')"
        >
          <div class="panel-title">
            <t-icon name="chart-bar" />
            <span>玩家战绩</span>
          </div>
          <t-icon :name="expandedPanel === 'stats' ? 'chevron-up' : 'chevron-down'" class="arrow" />
        </div>
        <t-collapse-transition>
          <div class="panel-content" v-show="expandedPanel === 'stats'">
            <div class="player-list" v-if="allPlayersWithStats.length > 0">
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
            <div v-else class="empty-tip">暂无玩家数据</div>
          </div>
        </t-collapse-transition>
      </div>
    </main>

    <!-- 进入比赛身份选择弹窗 -->
    <t-dialog
      v-model:visible="showJoinDialog"
      header="选择身份进入比赛"
      :footer="false"
      width="90%"
      :style="{ maxWidth: '400px' }"
    >
      <div class="join-dialog-content" v-if="selectedRoom">
        <div class="room-preview">
          <div class="match-players">
            <span v-for="(p, i) in selectedRoom.players" :key="p">
              {{ p }}{{ i < selectedRoom.players.length - 1 ? ' vs ' : '' }}
            </span>
          </div>
          <div class="match-info">房间号: {{ selectedRoom.roomId }}</div>
        </div>
        
        <div class="identity-options">
          <div 
            class="identity-option spectator"
            @click="joinAsSpectator"
          >
            <t-icon name="browse" />
            <span>游客观战</span>
            <small>只能查看比赛进程</small>
          </div>
          
          <div class="identity-option player-option">
            <div class="option-header">
              <t-icon name="user" />
              <span>我是参赛人员</span>
            </div>
            <div class="player-buttons">
              <t-button 
                v-for="(player, index) in selectedRoom.players" 
                :key="player"
                :theme="index % 2 === 0 ? 'primary' : 'danger'"
                size="large"
                block
                @click="joinAsPlayer(player)"
              >
                {{ player }}
              </t-button>
            </div>
          </div>
        </div>
      </div>
    </t-dialog>
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

// 展开的面板（null 表示都不展开）
const expandedPanel = ref<'active' | 'create' | 'join' | 'stats' | null>(null)

const formRef = ref()
const formData = ref({
  gameType: 'eight-ball',
  players: ['阿兴', '老爸'],
  pricePerBall: 5,
  currentUser: '阿兴',
  defaultScoreMode: 'rounds'  // 默认显示对局比分
})

const joinInput = ref('')  // 支持房间号或链接
const joinUserName = ref(localStorage.getItem('userName') || '')

const allPlayersWithStats = ref<{ name: string; matchCount: number }[]>([])
const activeRooms = ref<{ roomId: string; players: string[]; roundCount: number }[]>([])

// 身份选择弹窗
const showJoinDialog = ref(false)
const selectedRoom = ref<{ roomId: string; players: string[] } | null>(null)

const gameTypeOptions = GAME_TYPES.map(t => ({ label: t.label, value: t.value }))

const allPlayerOptions = computed(() => {
  const names = new Set([
    ...PRESET_PLAYERS.map(p => p.name),
    ...allPlayersWithStats.value.map(p => p.name)
  ])
  return Array.from(names).map(name => ({ label: name, value: name }))
})

function getPlayerOptions(currentIndex: number) {
  const selectedPlayers = formData.value.players.filter((_, i) => i !== currentIndex)
  return allPlayerOptions.value.filter(opt => !selectedPlayers.includes(opt.value))
}

const currentUserOptions = computed(() => 
  formData.value.players
    .filter(p => p)
    .map(p => ({ label: p, value: p }))
)

function togglePanel(panel: 'active' | 'create' | 'join' | 'stats') {
  expandedPanel.value = expandedPanel.value === panel ? null : panel
}

function addPlayer() {
  if (formData.value.players.length < 4) {
    formData.value.players.push('')
  }
}

function removePlayer(index: number) {
  if (formData.value.players.length > 2) {
    formData.value.players.splice(index, 1)
    if (!formData.value.players.includes(formData.value.currentUser)) {
      formData.value.currentUser = formData.value.players[0] || ''
    }
  }
}

// 从输入中解析房间号（支持链接或纯房间号）
function parseRoomId(input: string): string {
  if (!input) return ''
  
  // 尝试从链接中提取房间号
  // 支持格式: 
  // - https://xxx/billiards/room/1234
  // - /billiards/room/1234
  // - room/1234
  // - 1234
  const patterns = [
    /\/room\/(\d{4})/,           // URL 格式
    /room\/(\d{4})/,             // 部分 URL
    /^(\d{4})$/                  // 纯房间号
  ]
  
  for (const pattern of patterns) {
    const match = input.match(pattern)
    if (match) {
      return match[1]
    }
  }
  
  // 如果都不匹配，返回去除空格后的输入
  return input.trim()
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
      pricePerBall: formData.value.pricePerBall,
      defaultScoreMode: formData.value.defaultScoreMode
    })
    
    roomStore.setCurrentUser(formData.value.currentUser)
    router.push(`/billiards/room/${roomId}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '创建房间失败')
  }
}

async function handleJoin() {
  const roomId = parseRoomId(joinInput.value)
  
  if (!roomId) {
    MessagePlugin.warning('请输入房间号或分享链接')
    return
  }
  if (!joinUserName.value) {
    MessagePlugin.warning('请输入你的名字')
    return
  }
  
  try {
    await roomApi.join(roomId, joinUserName.value)
    roomStore.setCurrentUser(joinUserName.value)
    router.push(`/billiards/room/${roomId}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '加入房间失败')
  }
}

async function quickJoin(room: { roomId: string; players: string[] }) {
  // 打开身份选择弹窗
  selectedRoom.value = room
  showJoinDialog.value = true
}

// 以游客身份进入
async function joinAsSpectator() {
  if (!selectedRoom.value) return
  
  const guestName = `游客${Math.floor(Math.random() * 1000)}`
  
  try {
    await roomApi.join(selectedRoom.value.roomId, guestName)
    roomStore.setCurrentUser(guestName)
    showJoinDialog.value = false
    router.push(`/billiards/room/${selectedRoom.value.roomId}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '进入房间失败')
  }
}

// 以参赛人员身份进入
async function joinAsPlayer(playerName: string) {
  if (!selectedRoom.value) return
  
  try {
    await roomApi.join(selectedRoom.value.roomId, playerName)
    roomStore.setCurrentUser(playerName)
    localStorage.setItem('userName', playerName)
    showJoinDialog.value = false
    router.push(`/billiards/room/${selectedRoom.value.roomId}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '进入房间失败')
  }
}

async function loadData() {
  try {
    const players = await playerApi.getPlayers()
    const presetNames = PRESET_PLAYERS.map(p => p.name)
    
    allPlayersWithStats.value = [
      ...PRESET_PLAYERS.map(p => ({
        name: p.name,
        matchCount: players.find(x => x.name === p.name)?.matchCount || 0
      })),
      ...players.filter(p => !presetNames.includes(p.name))
    ]
    
    try {
      const rooms = await roomApi.getActiveRooms()
      activeRooms.value = rooms
      // 如果有进行中的房间，自动展开
      if (rooms.length > 0) {
        expandedPanel.value = 'active'
      }
    } catch {
      // API不存在时忽略
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
  gap: 16px;
}

// 折叠面板
.action-panel {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }
  
  &.active {
    background: rgba(255, 255, 255, 0.08);
  }
  
  &.hasItems {
    background: linear-gradient(135deg, rgba(82, 196, 26, 0.15), rgba(82, 196, 26, 0.05));
    
    .panel-title .t-icon {
      color: var(--success-color);
    }
  }
  
  &.create .panel-title .t-icon {
    color: var(--primary-color);
  }
  
  &.join .panel-title .t-icon {
    color: #60a5fa;
  }
  
  &.stats .panel-title .t-icon {
    color: #f59e0b;
  }
  
  .panel-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    
    .t-icon {
      font-size: 22px;
    }
  }
  
  .arrow {
    color: var(--text-secondary);
    transition: transform 0.3s;
  }
}

.panel-content {
  padding: 0 20px 20px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

// 进行中房间
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

.empty-tip {
  text-align: center;
  padding: 24px;
  color: var(--text-secondary);
  font-size: 14px;
}

// 身份选择弹窗
.join-dialog-content {
  .room-preview {
    text-align: center;
    padding: 16px;
    margin-bottom: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    
    .match-players {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-color);
      margin-bottom: 8px;
    }
    
    .match-info {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
  
  .identity-options {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .identity-option {
    padding: 16px;
    border-radius: 12px;
    border: 2px solid var(--border-color);
    transition: all 0.3s;
    
    &.spectator {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      
      &:hover {
        border-color: var(--primary-color);
        background: rgba(255, 255, 255, 0.05);
      }
      
      .t-icon {
        font-size: 24px;
        color: #60a5fa;
      }
      
      span {
        font-weight: 600;
        color: var(--text-color);
      }
      
      small {
        margin-left: auto;
        color: var(--text-secondary);
        font-size: 12px;
      }
    }
    
    &.player-option {
      .option-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        
        .t-icon {
          font-size: 24px;
          color: var(--success-color);
        }
        
        span {
          font-weight: 600;
          color: var(--text-color);
        }
      }
      
      .player-buttons {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
    }
  }
}

// 响应式
@media (max-width: 480px) {
  .billiards-page {
    padding: 16px;
  }
  
  .header h1 {
    font-size: 20px;
  }
  
  .panel-header {
    padding: 14px 16px;
  }
  
  .panel-content {
    padding: 0 16px 16px;
    padding-top: 16px;
  }
}
</style>
