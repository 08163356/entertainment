<template>
  <div class="room-page" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- 顶部栏 -->
    <header class="header" v-show="!isFullscreen">
      <t-button variant="text" @click="handleBack">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <div class="room-info">
        <span class="room-id">房间 {{ roomId }}</span>
        <t-tag :theme="connected ? 'success' : 'danger'" size="small">
          {{ connected ? '已连接' : '断开' }}
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

    <!-- 全屏模式退出按钮 -->
    <t-button 
      v-show="isFullscreen" 
      class="exit-fullscreen-btn"
      variant="text" 
      @click="toggleFullscreen"
    >
      <t-icon name="fullscreen-exit" />
    </t-button>

    <!-- 主记分板 -->
    <main class="scoreboard" :class="{ 'multi-player': players.length > 2 }">
      <!-- 中间大比分（2人模式） -->
      <div class="score-center" v-if="players.length === 2">
        <!-- 比分切换按钮 -->
        <div class="score-mode-switch">
          <t-button 
            :theme="scoreMode === 'rounds' ? 'primary' : 'default'"
            size="small"
            variant="outline"
            @click="scoreMode = 'rounds'"
          >
            对局
          </t-button>
          <t-button 
            :theme="scoreMode === 'balls' ? 'primary' : 'default'"
            size="small"
            variant="outline"
            @click="scoreMode = 'balls'"
          >
            球数
          </t-button>
        </div>
        
        <!-- 大比分显示 -->
        <div class="score-display-container">
          <div class="score-display large" :class="scoreMode">
            <span class="score-p1">{{ scoreMode === 'rounds' ? getPlayerWins(players[0]?.name) : getPlayerBalls(players[0]?.name) }}</span>
            <span class="score-divider">:</span>
            <span class="score-p2">{{ scoreMode === 'rounds' ? getPlayerWins(players[1]?.name) : getPlayerBalls(players[1]?.name) }}</span>
          </div>
          <div class="score-type-label">
            {{ scoreMode === 'rounds' ? '对局比分' : '球数比' }}
          </div>
        </div>
        
        <div class="round-info">第 {{ rounds.length + 1 }} 局</div>
        
        <!-- 副比分显示（显示另一种模式） -->
        <div class="sub-score" @click="toggleScoreMode">
          <span v-if="scoreMode === 'rounds'">
            球数: {{ getPlayerBalls(players[0]?.name) }} - {{ getPlayerBalls(players[1]?.name) }}
          </span>
          <span v-else>
            对局: {{ getPlayerWins(players[0]?.name) }} - {{ getPlayerWins(players[1]?.name) }}
          </span>
          <t-icon name="swap" size="14px" />
        </div>
      </div>

      <!-- 多人模式标题 -->
      <div class="multi-header" v-else>
        <div class="round-info-large">第 {{ rounds.length + 1 }} 局</div>
      </div>

      <!-- 玩家区块 -->
      <div class="players-grid" :class="`players-${players.length}`">
        <div 
          v-for="(player, index) in players"
          :key="player.name"
          class="player-card"
          :class="{ 
            'winner-selected': isWinner(player.name), 
            'selectable': canOperate && showRoundInput,
            [`player-theme-${index + 1}`]: true
          }"
          @click="canOperate && showRoundInput && selectWinner(player.name)"
        >
          <div class="player-avatar" :class="`player-${index + 1}`">
            {{ player.name?.[0] || '?' }}
          </div>
          <div class="player-name">{{ player.name || '玩家' }}</div>
          <div class="player-score">
            <div class="score-big">{{ getPlayerWins(player.name) }}</div>
            <div class="score-label">局</div>
          </div>
          <div class="player-balls">
            <span class="balls-value">{{ getPlayerBalls(player.name) }}</span>
            <span class="balls-label">球</span>
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
        观战中 - 只有房主或授权者可操作
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
      :style="{ maxWidth: '450px' }"
    >
      <div class="round-input-panel">
        <div class="winner-select">
          <div class="label">本局胜者</div>
          <div class="winner-options" :class="`options-${players.length}`">
            <div 
              v-for="(player, index) in players" 
              :key="player.name"
              class="winner-option"
              :class="{ selected: roundInput.winner === player.name }"
              @click="roundInput.winner = player.name"
            >
              <div class="player-avatar small" :class="`player-${index + 1}`">
                {{ player.name[0] }}
              </div>
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
      <div class="settle-preview" v-if="settlementPreview">
        <!-- 胜利装饰图 -->
        <div class="victory-decoration" v-if="settlementPreview.transfers.length > 0">
          <img src="@/assets/结算胜利图.png" alt="Victory" class="victory-img" />
        </div>
        
        <div class="final-score">
          最终比分: <strong>{{ settlementPreview.score }}</strong>
        </div>
        
        <!-- 球数展示 -->
        <div class="balls-summary">
          <div 
            v-for="(stat, index) in settlementPreview.playerStats" 
            :key="stat.name"
            class="ball-stat-item"
          >
            <div class="player-avatar mini" :class="`player-${index + 1}`">
              {{ stat.name[0] }}
            </div>
            <span class="name">{{ stat.name }}</span>
            <span class="balls">{{ stat.balls }}球</span>
          </div>
        </div>
        
        <!-- 转账详情 -->
        <div class="transfers-section" v-if="settlementPreview.transfers.length > 0">
          <div class="section-title">转账明细</div>
          <div 
            v-for="(transfer, index) in settlementPreview.transfers" 
            :key="index"
            class="transfer-item"
          >
            <span class="from">{{ transfer.from }}</span>
            <div class="transfer-arrow">
              <span class="diff">差{{ transfer.ballDiff }}球</span>
              <t-icon name="arrow-right" />
            </div>
            <span class="to">{{ transfer.to }}</span>
            <span class="amount">¥{{ transfer.amount }}</span>
          </div>
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

    <!-- 权限管理 -->
    <t-drawer
      v-model:visible="showOperators"
      header="权限管理"
      placement="right"
      size="320px"
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
          <h4>参赛玩家</h4>
          <div 
            v-for="player in room?.players" 
            :key="player.name"
            class="user-item player-item"
          >
            <span class="name">{{ player.name }}</span>
            <div class="user-actions">
              <!-- 权限状态 -->
              <t-tag 
                v-if="room?.operators.includes(player.name)"
                theme="success" 
                size="small"
              >
                可编辑
              </t-tag>
              <t-tag v-else theme="default" size="small">仅观看</t-tag>
              
              <!-- 房主操作 -->
              <template v-if="isOwner && player.name !== room?.owner">
                <t-button 
                  v-if="room?.operators.includes(player.name)"
                  size="small" 
                  theme="danger"
                  variant="text"
                  @click="revokeOperator(player.name)"
                >
                  取消权限
                </t-button>
                <t-button 
                  v-else
                  size="small"
                  variant="text"
                  @click="grantOperator(player.name)"
                >
                  授权
                </t-button>
                
                <t-button 
                  size="small" 
                  theme="warning"
                  variant="text"
                  @click="handleTransferOwner(player.name)"
                >
                  转让房主
                </t-button>
              </template>
              
              <!-- 房主标识 -->
              <t-tag 
                v-if="player.name === room?.owner" 
                theme="warning" 
                size="small"
              >
                房主
              </t-tag>
            </div>
          </div>
        </div>
        
        <div class="section" v-if="room?.spectators.length">
          <h4>观众</h4>
          <div 
            v-for="spec in room?.spectators" 
            :key="spec"
            class="user-item"
          >
            <span>{{ spec }}</span>
            <t-button 
              v-if="isOwner"
              size="small" 
              variant="text"
              @click="grantOperator(spec)"
            >
              授权
            </t-button>
          </div>
        </div>
        
        <div class="tips">
          <p>💡 参赛玩家默认拥有编辑权限</p>
          <p>💡 房主可以添加/取消其他人的编辑权限</p>
          <p>💡 房主可以转让房主身份给其他参赛玩家</p>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
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

// 比分显示模式（对局/球数）
const scoreMode = ref<'rounds' | 'balls'>('rounds')

function toggleScoreMode() {
  scoreMode.value = scoreMode.value === 'rounds' ? 'balls' : 'rounds'
}

// 计算结算预览（支持多人模式）
const settlementPreview = computed(() => {
  if (!room.value || players.value.length < 2) return null
  
  const pricePerBall = room.value.pricePerBall || 5
  
  // 计算每个玩家的统计
  const playerStats = players.value.map(p => {
    const wins = rounds.value.filter(r => r.winner === p.name).length
    const balls = rounds.value
      .filter(r => r.winner === p.name)
      .reduce((sum, r) => sum + r.ballsWon, 0)
    return { name: p.name, wins, balls }
  })
  
  // 按球数排序
  const sorted = [...playerStats].sort((a, b) => b.balls - a.balls)
  const score = playerStats.map(p => p.wins).join(':')
  
  // 计算转账（所有人向第一名转账）
  const transfers: { from: string; to: string; amount: number; ballDiff: number }[] = []
  
  if (sorted[0].balls > 0) {
    const winner = sorted[0]
    
    for (let i = 1; i < sorted.length; i++) {
      const loser = sorted[i]
      const ballDiff = winner.balls - loser.balls
      const amount = ballDiff * pricePerBall
      
      if (amount > 0) {
        transfers.push({
          from: loser.name,
          to: winner.name,
          amount,
          ballDiff
        })
      }
    }
  }
  
  return {
    score,
    playerStats: sorted,
    transfers
  }
})

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
    const result = await roomApi.settle(roomId.value)
    showSettleConfirm.value = false
    
    // 检查是否是 0:0 比赛
    if (result.isZeroMatch) {
      MessagePlugin.info('0:0 比赛不计入战绩，已返回')
      router.push('/billiards')
    } else {
      MessagePlugin.success('结算完成')
    }
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

async function handleTransferOwner(userName: string) {
  try {
    await roomApi.transferOwner(roomId.value, userName)
    MessagePlugin.success(`已将房主转让给 ${userName}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '转让失败')
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
    
    // 设置默认比分显示模式
    if (roomData.defaultScoreMode) {
      scoreMode.value = roomData.defaultScoreMode as 'rounds' | 'balls'
    }
    
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
  
  // 对局房间背景图
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('@/assets/对局房间背景.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.12;
    z-index: -1;
    pointer-events: none;
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  .room-info {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .room-id {
      font-weight: 600;
      color: var(--text-color);
      font-size: 14px;
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
  background: var(--card-bg) !important;
  backdrop-filter: blur(10px);
}

// 主记分板
.scoreboard {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
  padding: 20px;
}

// 中心比分（2人模式）
.score-center {
  text-align: center;
  
  .score-mode-switch {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 20px;
  }
  
  .score-display-container {
    margin-bottom: 16px;
  }
  
  .score-display {
    font-weight: 800;
    text-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    letter-spacing: 12px;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    
    &.large {
      font-size: 100px;
    }
    
    // 对局比分颜色
    &.rounds {
      .score-p1 {
        color: #667eea;
        text-shadow: 0 4px 20px rgba(102, 126, 234, 0.5);
      }
      .score-p2 {
        color: #f5576c;
        text-shadow: 0 4px 20px rgba(245, 87, 108, 0.5);
      }
      .score-divider {
        color: var(--text-color);
      }
    }
    
    // 球数比颜色
    &.balls {
      .score-p1 {
        color: #52c41a;
        text-shadow: 0 4px 20px rgba(82, 196, 26, 0.5);
      }
      .score-p2 {
        color: #faad14;
        text-shadow: 0 4px 20px rgba(250, 173, 20, 0.5);
      }
      .score-divider {
        color: var(--text-color);
      }
    }
  }
  
  .score-type-label {
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: 8px;
  }
  
  .round-info {
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }
  
  .sub-score {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--text-secondary);
    padding: 8px 16px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      background: rgba(255, 255, 255, 0.1);
    }
    
    .t-icon {
      opacity: 0.6;
    }
  }
}

// 多人模式标题
.multi-header {
  text-align: center;
  
  .round-info-large {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-color);
  }
}

// 玩家网格
.players-grid {
  display: flex;
  justify-content: center;
  gap: 20px;
  width: 100%;
  max-width: 800px;
  
  &.players-2 {
    .player-card {
      flex: 1;
      max-width: 300px;
    }
  }
  
  &.players-3, &.players-4 {
    flex-wrap: wrap;
    
    .player-card {
      width: calc(50% - 10px);
      max-width: 200px;
    }
  }
}

// 玩家卡片
.player-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-radius: 20px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--card-border);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  // 玩家卡片纹理背景
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('@/assets/玩家卡片纹理.png');
    background-size: cover;
    background-position: center;
    opacity: 0.06;
    pointer-events: none;
  }
  
  &.selectable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }
  }
  
  &.winner-selected {
    border-color: var(--primary-color);
    box-shadow: 0 0 30px var(--primary-light), 0 8px 32px rgba(0, 0, 0, 0.2);
  }
  
  .player-avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: bold;
    color: white;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    
    &.player-1 { background: linear-gradient(135deg, #667eea, #764ba2); }
    &.player-2 { background: linear-gradient(135deg, #f093fb, #f5576c); }
    &.player-3 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
    &.player-4 { background: linear-gradient(135deg, #fa709a, #fee140); }
  }
  
  .player-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .player-score {
    text-align: center;
    
    .score-big {
      font-size: 48px;
      font-weight: 800;
      color: var(--text-color);
      line-height: 1;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .score-label {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
  
  .player-balls {
    display: flex;
    align-items: baseline;
    gap: 4px;
    padding: 6px 16px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.08);
    
    .balls-value {
      font-size: 20px;
      font-weight: 700;
      color: var(--text-color);
    }
    
    .balls-label {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

// 操作区
.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  flex-wrap: wrap;
  
  .spectator-tip {
    color: var(--text-secondary);
    font-size: 14px;
    padding: 12px 24px;
    background: var(--card-bg);
    border-radius: 12px;
    backdrop-filter: blur(10px);
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

// 记录弹窗
.round-input-panel {
  .label {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 12px;
  }
  
  .winner-options {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    
    &.options-3, &.options-4 {
      .winner-option {
        width: calc(50% - 6px);
      }
    }
    
    .winner-option {
      flex: 1;
      min-width: 80px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 16px 12px;
      border-radius: 12px;
      border: 2px solid var(--border-color);
      cursor: pointer;
      transition: all 0.2s;
      background: rgba(255, 255, 255, 0.03);
      
      &:hover {
        border-color: var(--primary-color);
        background: rgba(255, 255, 255, 0.06);
      }
      
      &.selected {
        border-color: var(--primary-color);
        background: var(--primary-light);
      }
      
      .player-avatar.small {
        width: 44px;
        height: 44px;
        font-size: 18px;
      }
      
      span {
        font-size: 14px;
        color: var(--text-color);
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

// 结算预览
.settle-preview {
  .victory-decoration {
    text-align: center;
    margin-bottom: 16px;
    
    .victory-img {
      width: 120px;
      height: auto;
      opacity: 0.9;
      border-radius: 12px;
    }
  }
  
  .final-score {
    font-size: 20px;
    margin-bottom: 20px;
    text-align: center;
    
    strong {
      color: var(--primary-color);
      font-size: 28px;
    }
  }
  
  // 球数统计
  .balls-summary {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    
    .ball-stat-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 20px;
      
      .player-avatar.mini {
        width: 28px;
        height: 28px;
        font-size: 12px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        
        &.player-1 { background: linear-gradient(135deg, #667eea, #764ba2); }
        &.player-2 { background: linear-gradient(135deg, #f093fb, #f5576c); }
        &.player-3 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
        &.player-4 { background: linear-gradient(135deg, #fa709a, #fee140); }
      }
      
      .name {
        font-weight: 500;
        color: var(--text-color);
      }
      
      .balls {
        font-weight: 700;
        color: var(--primary-color);
      }
    }
  }
  
  // 转账明细
  .transfers-section {
    .section-title {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 12px;
      text-align: center;
    }
    
    .transfer-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 16px;
      margin-bottom: 10px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      
      .from {
        color: var(--error-color);
        font-weight: 600;
        min-width: 50px;
      }
      
      .transfer-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        
        .diff {
          font-size: 11px;
          color: var(--text-secondary);
          margin-bottom: 2px;
        }
        
        .t-icon {
          color: var(--warning-color);
          font-size: 20px;
        }
      }
      
      .to {
        color: var(--success-color);
        font-weight: 600;
        min-width: 50px;
        text-align: right;
      }
      
      .amount {
        font-size: 20px;
        font-weight: 800;
        color: var(--warning-color);
        margin-left: 12px;
        min-width: 70px;
        text-align: right;
      }
    }
  }
  
  .draw-result {
    font-size: 18px;
    color: var(--text-secondary);
    text-align: center;
    padding: 20px;
  }
}

// 分享内容
.share-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  .share-info {
    text-align: center;
    
    .room-id-display {
      font-size: 40px;
      font-weight: bold;
      letter-spacing: 8px;
      margin-bottom: 12px;
      color: var(--text-color);
    }
  }
  
  .share-link {
    display: flex;
    gap: 8px;
  }
}

// 权限面板
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
    
    &.player-item {
      flex-direction: column;
      align-items: stretch;
      gap: 8px;
      
      .name {
        font-weight: 500;
        color: var(--text-color);
      }
      
      .user-actions {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
      }
    }
  }
  
  .tips {
    margin-top: 24px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    
    p {
      font-size: 12px;
      color: var(--text-secondary);
      margin: 4px 0;
    }
  }
}

.operators-btn {
  position: fixed;
  bottom: 100px;
  right: 20px;
  background: var(--card-bg) !important;
  backdrop-filter: blur(10px);
}

// 全屏模式
.fullscreen-mode {
  .scoreboard {
    height: 100vh;
    padding: 40px;
  }
  
  .score-center .score-display {
    &.large {
      font-size: 160px;
    }
  }
  
  .player-card {
    padding: 32px 28px;
    
    .player-avatar {
      width: 72px;
      height: 72px;
      font-size: 32px;
    }
    
    .player-score .score-big {
      font-size: 64px;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .scoreboard {
    padding: 10px;
    gap: 20px;
  }
  
  .score-center .score-display {
    font-size: 64px;
    letter-spacing: 8px;
    
    &.large {
      font-size: 72px;
    }
  }
  
  .players-grid {
    flex-direction: column;
    align-items: center;
    
    &.players-2 .player-card {
      width: 100%;
      max-width: none;
      flex-direction: row;
      justify-content: space-between;
      padding: 16px 20px;
      
      .player-score {
        display: flex;
        align-items: baseline;
        gap: 4px;
        
        .score-big {
          font-size: 36px;
        }
      }
    }
    
    &.players-3, &.players-4 {
      flex-direction: row;
      
      .player-card {
        width: calc(50% - 8px);
        padding: 16px;
        
        .player-score .score-big {
          font-size: 32px;
        }
      }
    }
  }
  
  .fullscreen-mode {
    .score-center .score-display {
      font-size: 80px;
      
      &.large {
        font-size: 96px;
      }
    }
  }
}
</style>
