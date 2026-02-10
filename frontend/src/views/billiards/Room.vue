<template>
  <div class="room-page" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- 顶部栏 -->
    <header class="header" v-show="!isFullscreen">
      <t-button variant="text" @click="handleBack">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <div class="room-info">
        <span class="room-id">房间号: {{ roomId }}</span>
        <t-tag :theme="connected ? 'success' : 'danger'" size="small">
          {{ connected ? '已连接' : '断开连接' }}
        </t-tag>
      </div>
      <div class="header-actions">
        <t-button variant="text" shape="circle" @click="showShare = true">
          <t-icon name="share" />
        </t-button>
        <t-button variant="text" shape="circle" @click="toggleFullscreen">
          <t-icon :name="isFullscreen ? 'fullscreen-exit' : 'fullscreen'" />
        </t-button>
        <t-dropdown :options="themeOptions" @click="handleThemeChange">
          <t-button variant="text" shape="circle">
            <t-icon name="palette" />
          </t-button>
        </t-dropdown>
      </div>
    </header>

    <!-- 全屏模式下的退出按钮 -->
    <t-button 
      v-show="isFullscreen" 
      class="exit-fullscreen-btn"
      variant="text" 
      @click="toggleFullscreen"
    >
      <t-icon name="fullscreen-exit" />
    </t-button>

    <!-- 主记分板 -->
    <main class="scoreboard">
      <!-- 玩家1 -->
      <div 
        class="player-section player-1"
        :class="{ winner: isWinner(players[0]?.name), selectable: canOperate && showRoundInput }"
        @click="canOperate && showRoundInput && selectWinner(players[0]?.name)"
      >
        <div class="player-avatar">{{ players[0]?.name?.[0] || '?' }}</div>
        <div class="player-name">{{ players[0]?.name || '玩家1' }}</div>
        <div class="player-stats">
          <div class="stat-item">
            <span class="stat-value">{{ getPlayerWins(players[0]?.name) }}</span>
            <span class="stat-label">局</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ getPlayerBalls(players[0]?.name) }}</span>
            <span class="stat-label">球</span>
          </div>
        </div>
      </div>

      <!-- 中间比分 -->
      <div class="score-center">
        <div class="score-display large">
          {{ getPlayerWins(players[0]?.name) }} : {{ getPlayerWins(players[1]?.name) }}
        </div>
        <div class="round-info">第 {{ rounds.length + 1 }} 局</div>
        <div class="ball-diff">
          球数差: {{ Math.abs(getPlayerBalls(players[0]?.name) - getPlayerBalls(players[1]?.name)) }}
        </div>
      </div>

      <!-- 玩家2 -->
      <div 
        class="player-section player-2"
        :class="{ winner: isWinner(players[1]?.name), selectable: canOperate && showRoundInput }"
        @click="canOperate && showRoundInput && selectWinner(players[1]?.name)"
      >
        <div class="player-avatar">{{ players[1]?.name?.[0] || '?' }}</div>
        <div class="player-name">{{ players[1]?.name || '玩家2' }}</div>
        <div class="player-stats">
          <div class="stat-item">
            <span class="stat-value">{{ getPlayerWins(players[1]?.name) }}</span>
            <span class="stat-label">局</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ getPlayerBalls(players[1]?.name) }}</span>
            <span class="stat-label">球</span>
          </div>
        </div>
      </div>
    </main>

    <!-- 操作按钮区 -->
    <footer class="actions" v-if="room?.status === 'playing'">
      <template v-if="canOperate">
        <t-button 
          v-if="!showRoundInput"
          theme="primary" 
          size="large" 
          class="big-btn"
          @click="showRoundInput = true"
        >
          记录本局
        </t-button>
        
        <t-button 
          v-if="rounds.length > 0"
          theme="default" 
          size="large"
          @click="handleUndo"
        >
          撤销上局
        </t-button>
        
        <t-button 
          theme="danger" 
          size="large"
          @click="showSettleConfirm = true"
        >
          结算
        </t-button>
      </template>
      
      <div v-else class="spectator-tip">
        👁 观战中 - 只有房主或授权者可操作
      </div>
    </footer>

    <!-- 已结算状态 -->
    <div v-if="room?.status === 'settled'" class="settled-banner">
      <h2>比赛已结算</h2>
      <t-button @click="router.push('/billiards/history')">查看历史记录</t-button>
    </div>

    <!-- 记录本局弹窗 -->
    <t-dialog
      v-model:visible="showRoundInput"
      header="记录本局"
      :footer="false"
      width="90%"
      :style="{ maxWidth: '400px' }"
    >
      <div class="round-input-panel">
        <div class="winner-select">
          <div class="label">本局胜者</div>
          <div class="winner-options">
            <div 
              v-for="player in players" 
              :key="player.name"
              class="winner-option"
              :class="{ selected: roundInput.winner === player.name }"
              @click="roundInput.winner = player.name"
            >
              <div class="player-avatar small">{{ player.name[0] }}</div>
              <span>{{ player.name }}</span>
            </div>
          </div>
        </div>
        
        <div class="balls-select" v-if="roundInput.winner">
          <div class="label">赢球数</div>
          <div class="balls-options">
            <t-button 
              v-for="n in 7" 
              :key="n"
              :theme="roundInput.ballsWon === n ? 'primary' : 'default'"
              size="large"
              @click="roundInput.ballsWon = n"
            >
              {{ n }}
            </t-button>
          </div>
          <div class="custom-input">
            <t-input-number 
              v-model="roundInput.ballsWon" 
              :min="1" 
              :max="15"
              placeholder="自定义"
            />
          </div>
        </div>
        
        <div class="confirm-actions">
          <t-button theme="default" @click="showRoundInput = false">取消</t-button>
          <t-button 
            theme="primary" 
            :disabled="!roundInput.winner || !roundInput.ballsWon"
            @click="confirmRound"
          >
            确认
          </t-button>
        </div>
      </div>
    </t-dialog>

    <!-- 结算确认弹窗 -->
    <t-dialog
      v-model:visible="showSettleConfirm"
      header="确认结算"
      @confirm="handleSettle"
    >
      <div class="settle-preview" v-if="settlement">
        <div class="final-score">
          最终比分: <strong>{{ settlement.score }}</strong>
        </div>
        <div class="ball-result">
          球数: {{ settlement.player1.balls }} vs {{ settlement.player2.balls }}
          (差 {{ settlement.ballDiff }} 球)
        </div>
        <div class="money-result" v-if="settlement.winner">
          <span class="loser">{{ settlement.loser }}</span>
          需支付
          <span class="amount">¥{{ settlement.amount }}</span>
          给
          <span class="winner">{{ settlement.winner }}</span>
        </div>
        <div class="draw-result" v-else>
          平局！不需要转账
        </div>
      </div>
    </t-dialog>

    <!-- 分享弹窗 -->
    <t-dialog
      v-model:visible="showShare"
      header="分享房间"
      :footer="false"
    >
      <div class="share-content">
        <div class="share-info">
          <div class="room-id-display">{{ roomId }}</div>
          <t-button @click="copyRoomId">复制房间号</t-button>
        </div>
        <div class="share-link">
          <t-input :value="shareLink" readonly />
          <t-button @click="copyShareLink">复制链接</t-button>
        </div>
      </div>
    </t-dialog>

    <!-- 权限管理（仅房主可见） -->
    <t-drawer
      v-model:visible="showOperators"
      header="权限管理"
      placement="right"
      size="300px"
    >
      <div class="operators-panel">
        <div class="section">
          <h4>房主</h4>
          <div class="user-item owner">
            <span>{{ room?.owner }}</span>
            <t-tag theme="warning">👑</t-tag>
          </div>
        </div>
        
        <div class="section">
          <h4>可操作者</h4>
          <div 
            v-for="op in room?.operators.filter(o => o !== room?.owner)" 
            :key="op"
            class="user-item"
          >
            <span>{{ op }}</span>
            <t-button size="small" theme="danger" @click="revokeOperator(op)">
              移除
            </t-button>
          </div>
        </div>
        
        <div class="section">
          <h4>观众</h4>
          <div 
            v-for="spec in room?.spectators" 
            :key="spec"
            class="user-item"
          >
            <span>{{ spec }}</span>
            <t-button size="small" @click="grantOperator(spec)">
              授权
            </t-button>
          </div>
        </div>
      </div>
    </t-drawer>

    <!-- 房主操作入口 -->
    <t-button 
      v-if="isOwner && room?.status === 'playing'"
      class="operators-btn"
      shape="circle"
      @click="showOperators = true"
    >
      <t-icon name="usergroup" />
    </t-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { useRoomStore } from '@/stores/room'
import { useThemeStore } from '@/stores/theme'
import { roomApi } from '@/services/api'
import { wsService } from '@/services/websocket'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const themeStore = useThemeStore()

const roomId = computed(() => route.params.roomId as string)
const room = computed(() => roomStore.room)
const connected = computed(() => roomStore.connected)
const isOwner = computed(() => roomStore.isOwner)
const canOperate = computed(() => roomStore.canOperate)
const players = computed(() => roomStore.players)
const rounds = computed(() => roomStore.rounds)
const settlement = computed(() => roomStore.settlement)

const isFullscreen = ref(false)
const showRoundInput = ref(false)
const showSettleConfirm = ref(false)
const showShare = ref(false)
const showOperators = ref(false)

const roundInput = ref({
  winner: '',
  ballsWon: 1
})

const themeOptions = computed(() => 
  themeStore.themes.map(t => ({
    content: t.label,
    value: t.value
  }))
)

const shareLink = computed(() => 
  `${window.location.origin}/entertainment/billiards/room/${roomId.value}`
)

function getPlayerWins(name: string | undefined) {
  if (!name) return 0
  return rounds.value.filter(r => r.winner === name).length
}

function getPlayerBalls(name: string | undefined) {
  if (!name) return 0
  return rounds.value
    .filter(r => r.winner === name)
    .reduce((sum, r) => sum + r.ballsWon, 0)
}

function isWinner(name: string | undefined) {
  if (!name || !showRoundInput.value) return false
  return roundInput.value.winner === name
}

function selectWinner(name: string | undefined) {
  if (name) {
    roundInput.value.winner = name
  }
}

async function confirmRound() {
  try {
    await roomApi.addRound(roomId.value, {
      winner: roundInput.value.winner,
      ballsWon: roundInput.value.ballsWon
    })
    showRoundInput.value = false
    roundInput.value = { winner: '', ballsWon: 1 }
    MessagePlugin.success('记录成功')
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '记录失败')
  }
}

async function handleUndo() {
  try {
    await roomApi.undoRound(roomId.value)
    MessagePlugin.success('已撤销')
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '撤销失败')
  }
}

async function handleSettle() {
  try {
    await roomApi.settle(roomId.value)
    showSettleConfirm.value = false
    MessagePlugin.success('结算完成')
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '结算失败')
  }
}

async function grantOperator(userName: string) {
  try {
    await roomApi.grantOperator(roomId.value, userName)
    MessagePlugin.success(`已授权 ${userName}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '授权失败')
  }
}

async function revokeOperator(userName: string) {
  try {
    await roomApi.revokeOperator(roomId.value, userName)
    MessagePlugin.success(`已移除 ${userName} 的权限`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '操作失败')
  }
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
}

function handleThemeChange(data: { value: string }) {
  themeStore.setTheme(data.value as any)
}

function copyRoomId() {
  navigator.clipboard.writeText(roomId.value)
  MessagePlugin.success('已复制房间号')
}

function copyShareLink() {
  navigator.clipboard.writeText(shareLink.value)
  MessagePlugin.success('已复制链接')
}

function handleBack() {
  router.push('/billiards')
}

onMounted(async () => {
  const userName = roomStore.currentUser || localStorage.getItem('userName')
  
  if (!userName) {
    MessagePlugin.warning('请先选择你的身份')
    router.push('/billiards')
    return
  }
  
  try {
    const roomData = await roomApi.get(roomId.value)
    roomStore.setRoom(roomData)
    wsService.connect(roomId.value, userName)
  } catch (e: any) {
    MessagePlugin.error('房间不存在或已关闭')
    router.push('/billiards')
  }
})

onUnmounted(() => {
  wsService.disconnect()
  roomStore.reset()
})
</script>

<style lang="scss" scoped>
.room-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  position: relative;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .room-info {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .room-id {
      font-weight: bold;
      color: var(--text-color);
    }
  }
  
  .header-actions {
    display: flex;
    gap: 4px;
  }
}

.exit-fullscreen-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100;
}

.scoreboard {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 40px 20px;
}

.player-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 30px;
  border-radius: 20px;
  background: var(--card-bg);
  transition: all 0.3s;
  
  &.selectable {
    cursor: pointer;
    
    &:hover {
      transform: scale(1.02);
    }
  }
  
  &.winner {
    box-shadow: 0 0 0 4px var(--primary-color);
  }
  
  .player-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: bold;
    color: white;
  }
  
  &.player-1 .player-avatar {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }
  
  &.player-2 .player-avatar {
    background: linear-gradient(135deg, #f093fb, #f5576c);
  }
  
  .player-name {
    font-size: 24px;
    font-weight: bold;
    color: var(--text-color);
  }
  
  .player-stats {
    display: flex;
    gap: 30px;
    
    .stat-item {
      text-align: center;
      
      .stat-value {
        display: block;
        font-size: 36px;
        font-weight: bold;
        color: var(--text-color);
      }
      
      .stat-label {
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
  }
}

.score-center {
  text-align: center;
  
  .score-display {
    font-size: 48px;
    font-weight: bold;
    color: var(--text-color);
  }
  
  .round-info {
    font-size: 16px;
    color: var(--text-secondary);
    margin: 8px 0;
  }
  
  .ball-diff {
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  flex-wrap: wrap;
  
  .spectator-tip {
    color: var(--text-secondary);
    font-size: 16px;
  }
}

.settled-banner {
  text-align: center;
  padding: 40px;
  
  h2 {
    margin-bottom: 20px;
    color: var(--text-color);
  }
}

.round-input-panel {
  .label {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 12px;
  }
  
  .winner-options {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    
    .winner-option {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 16px;
      border-radius: 12px;
      border: 2px solid var(--border-color);
      cursor: pointer;
      transition: all 0.2s;
      
      &:hover {
        border-color: var(--primary-color);
      }
      
      &.selected {
        border-color: var(--primary-color);
        background: rgba(26, 93, 26, 0.1);
      }
      
      .player-avatar.small {
        width: 50px;
        height: 50px;
        font-size: 20px;
      }
    }
  }
  
  .balls-options {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
  }
  
  .custom-input {
    margin-bottom: 24px;
  }
  
  .confirm-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

.settle-preview {
  text-align: center;
  
  .final-score {
    font-size: 24px;
    margin-bottom: 16px;
    
    strong {
      color: var(--primary-color);
    }
  }
  
  .ball-result {
    margin-bottom: 16px;
    color: var(--text-secondary);
  }
  
  .money-result {
    font-size: 18px;
    
    .loser { color: var(--error-color); }
    .winner { color: var(--success-color); }
    .amount { 
      font-size: 24px;
      font-weight: bold;
      color: var(--warning-color);
    }
  }
  
  .draw-result {
    font-size: 18px;
    color: var(--text-secondary);
  }
}

.share-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  .share-info {
    text-align: center;
    
    .room-id-display {
      font-size: 36px;
      font-weight: bold;
      letter-spacing: 4px;
      margin-bottom: 12px;
    }
  }
  
  .share-link {
    display: flex;
    gap: 8px;
  }
}

.operators-panel {
  .section {
    margin-bottom: 24px;
    
    h4 {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }
  }
  
  .user-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-radius: 8px;
    background: var(--card-bg);
    margin-bottom: 8px;
    
    &.owner {
      background: rgba(250, 173, 20, 0.1);
    }
  }
}

.operators-btn {
  position: fixed;
  bottom: 100px;
  right: 20px;
}

// 全屏模式
.fullscreen-mode {
  .scoreboard {
    height: 100vh;
    padding: 60px 40px;
  }
  
  .score-center .score-display {
    font-size: 72px;
  }
  
  .player-section {
    .player-avatar {
      width: 120px;
      height: 120px;
      font-size: 48px;
    }
    
    .player-name {
      font-size: 32px;
    }
    
    .player-stats .stat-item .stat-value {
      font-size: 48px;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .scoreboard {
    flex-direction: column;
    padding: 20px 10px;
  }
  
  .player-section {
    width: 100%;
    padding: 20px;
    
    .player-stats {
      gap: 40px;
    }
  }
  
  .score-center {
    order: -1;
    margin-bottom: 20px;
  }
  
  .fullscreen-mode {
    .scoreboard {
      padding: 20px;
    }
    
    .score-center .score-display {
      font-size: 56px;
    }
  }
}
</style>
