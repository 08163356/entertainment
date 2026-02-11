<template>
  <div class="room-page">
    <!-- 顶部栏 -->
    <header class="header">
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
        <t-dropdown :options="themeOptions" @click="handleThemeChange">
          <t-button variant="text" shape="circle">
            <t-icon name="palette" />
          </t-button>
        </t-dropdown>
        <t-button variant="text" shape="circle" @click="showShare = true">
          <t-icon name="share" />
        </t-button>
      </div>
    </header>

    <!-- 轮次信息 -->
    <div class="round-banner">
      <span class="round-number">第 {{ rounds.length + 1 }} 轮</span>
      <span class="round-limit" v-if="room?.totalRounds">
        / {{ room.totalRounds }} 轮
      </span>
      <span class="balls-info">每轮 {{ room?.ballsPerRound || 10 }} 球</span>
      <div class="round-progress">
        <span class="progress-text">
          已完成 {{ roomStore.currentRoundStatus.submitted.length }} / {{ players.length }}
        </span>
      </div>
    </div>

    <!-- 玩家卡片网格 -->
    <main class="scoreboard">
      <div class="players-grid" :class="`players-${players.length}`">
        <div 
          v-for="(player, index) in players"
          :key="player.name"
          class="player-card"
          :class="[
            `player-theme-${(index % 6) + 1}`, 
            { 
              leading: isLeading(player.name),
              submitted: isPlayerSubmitted(player.name),
              clickable: canClickCard(player.name)
            }
          ]"
          @click="handleCardClick(player.name)"
        >
          <!-- 已提交标记 -->
          <div class="submitted-badge" v-if="isPlayerSubmitted(player.name)">
            <t-icon name="check" />
          </div>
          
          <div class="player-avatar" :class="`player-${(index % 6) + 1}`">
            {{ player.name[0] }}
          </div>
          <div class="player-name">{{ player.name }}</div>
          <div class="player-stats">
            <div class="stat-main">
              <span class="stat-value">{{ roomStore.getPlayerTotalMade(player.name) }}</span>
              <span class="stat-label">进球</span>
            </div>
            <div class="stat-sub">
              <span class="accuracy">{{ roomStore.getPlayerAccuracy(player.name) }}%</span>
            </div>
          </div>
          
          <!-- 本轮已提交的数据预览 -->
          <div class="current-round-preview" v-if="isPlayerSubmitted(player.name)">
            <span class="preview-made">+{{ getPlayerSubmittedScore(player.name)?.made || 0 }}</span>
            <span class="preview-type">{{ getShotTypeLabel(getPlayerSubmittedScore(player.name)?.shotType) }}</span>
          </div>
          
          <div class="leading-badge" v-if="isLeading(player.name)">
            <img src="@/assets/basketball/flame-effect.png" alt="leading" class="flame-img" />
          </div>
          
          <!-- 高命中率装饰 -->
          <div class="star-badge" v-if="roomStore.getPlayerAccuracy(player.name) >= 80 && roomStore.getPlayerTotalMade(player.name) > 0">
            <img src="@/assets/basketball/star-effect.png" alt="high accuracy" class="star-img" />
          </div>
          
          <!-- 篮球装饰图标 -->
          <div class="basketball-decor">
            <img src="@/assets/basketball/basketball-icon.png" alt="" class="basketball-icon" />
          </div>
          
          <!-- 点击提示 -->
          <div class="click-tip" v-if="canClickCard(player.name) && !isPlayerSubmitted(player.name)">
            点击记录
          </div>
        </div>
      </div>
    </main>

    <!-- 操作按钮区 -->
    <footer class="actions" v-if="room?.status === 'playing'">
      <t-button 
        v-if="canOperate"

        :theme="!roomStore.currentRoundStatus.allSubmitted ? 'text' : 'primary'"
        size="large" 
        class="big-btn"
        :disabled="!roomStore.currentRoundStatus.allSubmitted"
        @click="handleConfirmRound"
      >
        <!-- <t-icon name="check-double" /> -->
         下一轮
      </t-button>
      
      <t-button 
        v-if="rounds.length > 0 && canOperate"
        size="small"
        ghost 
        @click="handleUndo"
      >
        撤销上轮
      </t-button>
      
      <t-button 
        v-if="canOperate"
        theme="danger" 
        size="large"
        @click="showSettleConfirm = true"
      >
        结算
      </t-button>
      
      <div v-if="!isPlayer && !roomStore.isSelfEditOnly" class="spectator-tip">
        观战中 - 只有参赛者可记录
      </div>
      
      <div v-if="roomStore.isSelfEditOnly" class="spectator-tip self-edit-tip">
        仅可编辑自己的得分
      </div>
    </footer>

    <!-- 已结算状态 -->
    <div v-if="room?.status === 'settled'" class="settled-banner">
      <h2>🎉 比赛已结算</h2>
      <t-button @click="router.push('/basketball/history')">查看历史记录</t-button>
    </div>

    <!-- 记录得分弹窗 -->
    <t-dialog
      v-model:visible="showScoreDialog"
      :header="`${editingPlayer} - 记录本轮`"
      :footer="false"
      width="90%"
      :style="{ maxWidth: '400px' }"
    >
      <div class="score-input-panel">
        <div class="input-group">
          <label>投篮类型</label>
          <t-radio-group v-model="scoreInput.shotType" variant="default-filled">
            <t-radio-button value="two">两分球</t-radio-button>
            <t-radio-button value="three">三分球</t-radio-button>
            <t-radio-button value="free">罚球</t-radio-button>
          </t-radio-group>
        </div>
        
        <div class="input-group">
          <label>进球数</label>
          <div class="quick-buttons">
            <t-button 
              v-for="n in quickButtons" 
              :key="n"
              size="small"
              :theme="scoreInput.made === n ? 'primary' : 'default'"
              @click="scoreInput.made = n"
            >
              {{ n }}
            </t-button>
          </div>
          <t-input-number
            v-model="scoreInput.made"
            :min="0"
            :max="scoreInput.total"
            size="large"
            theme="column"
            class="made-input"
          />
        </div>
        
        <div class="input-group">
          <label>总投球数</label>
          <t-input-number
            v-model="scoreInput.total"
            :min="1"
            :max="50"
            size="large"
            theme="column"
          />
        </div>
        
        <div class="accuracy-preview">
          命中率: {{ ((scoreInput.made / scoreInput.total) * 100).toFixed(1) }}%
        </div>
        
        <div class="confirm-actions">
          <t-button theme="default" @click="showScoreDialog = false">取消</t-button>
          <t-button theme="primary" @click="handleSubmitScore">
            完成
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
        <div class="winner-section" v-if="settlementPreview.winner">
          <img src="@/assets/basketball/trophy.png" alt="trophy" class="trophy-img" />
          <div class="winner-badge">冠军</div>
          <div class="winner-name">{{ settlementPreview.winner }}</div>
          <div class="winner-stats">
            {{ settlementPreview.winnerMade }} 进球 | 
            {{ settlementPreview.winnerAccuracy }}% 命中率
          </div>
        </div>
        
        <div class="stats-list">
          <div 
            v-for="(stat, index) in settlementPreview.playerStats" 
            :key="stat.name"
            class="stat-item"
            :class="{ winner: stat.name === settlementPreview.winner }"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="name">{{ stat.name }}</span>
            <span class="made">{{ stat.totalMade }}球</span>
            <span class="accuracy">{{ stat.accuracy }}%</span>
          </div>
        </div>
        
        <div class="transfers-section" v-if="settlementPreview.transfers.length > 0">
          <div class="section-title">
            <img src="@/assets/basketball/coin-icon.png" alt="coin" class="coin-icon" />
            转账明细
          </div>
          <div 
            v-for="(transfer, idx) in settlementPreview.transfers" 
            :key="idx"
            class="transfer-item"
          >
            <span class="from">{{ transfer.from }}</span>
            <div class="transfer-arrow">
              <span class="diff">差{{ transfer.shotsDiff }}球</span>
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
      :z-index="2000"
      attach="body"
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
              <!-- 权限标签 -->
              <t-tag 
                v-if="room?.operators.includes(player.name)"
                theme="success" 
                size="small"
              >
                完整权限
              </t-tag>
              <t-tag 
                v-else-if="room?.selfEditOnly?.includes(player.name)"
                theme="warning" 
                size="small"
              >
                仅编辑自己
              </t-tag>
              <t-tag v-else theme="default" size="small">仅观看</t-tag>
              
              <!-- 房主操作按钮 -->
              <template v-if="isOwner && player.name !== room?.owner">
                <t-dropdown 
                  :options="getPermissionOptions(player.name)" 
                  @click="(item: any) => handlePermissionChange(player.name, item.value)"
                >
                  <t-button size="small" variant="outline">
                    权限设置
                    <t-icon name="chevron-down" />
                  </t-button>
                </t-dropdown>
                
                <t-button 
                  size="small" 
                  theme="warning"
                  variant="text"
                  @click="handleTransferOwner(player.name)"
                >
                  转让房主
                </t-button>
              </template>
              
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
          <p>💡 <strong>完整权限</strong>：可编辑所有人、下一轮、撤销、结算</p>
          <p>💡 <strong>仅编辑自己</strong>：只能编辑自己的得分</p>
          <p>💡 <strong>仅观看</strong>：不能进行任何编辑操作</p>
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
import { useBasketballRoomStore } from '@/stores/basketballRoom'
import { useThemeStore } from '@/stores/theme'
import { basketballRoomApi } from '@/services/basketballApi'
import { basketballWsService } from '@/services/basketballWebsocket'
import { SHOT_TYPES } from '@/types/basketball'

const route = useRoute()
const router = useRouter()
const roomStore = useBasketballRoomStore()
const themeStore = useThemeStore()

const roomId = computed(() => route.params.roomId as string)
const room = computed(() => roomStore.room)
const connected = computed(() => roomStore.connected)
const isOwner = computed(() => roomStore.isOwner)
const canOperate = computed(() => roomStore.canOperate)
const isPlayer = computed(() => roomStore.isPlayer)
const players = computed(() => roomStore.players)
const rounds = computed(() => roomStore.rounds)

const showScoreDialog = ref(false)
const showSettleConfirm = ref(false)
const showShare = ref(false)
const showOperators = ref(false)

const editingPlayer = ref('')
const quickButtons = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const scoreInput = ref({
  shotType: 'two',
  made: 0,
  total: 10
})

const shareLink = computed(() => 
  `${window.location.origin}/entertainment/basketball/room/${roomId.value}`
)

const themeOptions = computed(() => 
  themeStore.themes.map(t => ({
    content: t.label,
    value: t.value
  }))
)

function handleThemeChange(data: { value: string }) {
  themeStore.setTheme(data.value as any)
}

// 获取投篮类型标签
function getShotTypeLabel(shotType?: string): string {
  const type = SHOT_TYPES.find(t => t.value === shotType)
  return type?.label || '两分球'
}

// 判断是否领先
function isLeading(playerName: string): boolean {
  if (players.value.length < 2) return false
  const myMade = roomStore.getPlayerTotalMade(playerName)
  const maxMade = Math.max(...players.value.map(p => roomStore.getPlayerTotalMade(p.name)))
  return myMade === maxMade && myMade > 0
}

// 玩家是否已提交本轮
function isPlayerSubmitted(playerName: string): boolean {
  return roomStore.currentRoundStatus.submitted.some(s => s.name === playerName)
}

// 获取玩家已提交的分数
function getPlayerSubmittedScore(playerName: string) {
  return roomStore.currentRoundStatus.submitted.find(s => s.name === playerName)
}

// 是否可以点击卡片
function canClickCard(playerName: string): boolean {
  if (room.value?.status !== 'playing') return false
  // 房主可以编辑所有人的数据
  if (isOwner.value) return true
  // 完整权限用户可以编辑所有人
  if (canOperate.value) return true
  // selfEditOnly 用户只能编辑自己
  if (roomStore.isSelfEditOnly && playerName === roomStore.currentUser) return true
  // 普通玩家如果在 operators 里可以编辑
  if (isPlayer.value && playerName === roomStore.currentUser) return true
  return false
}

// 点击卡片
function handleCardClick(playerName: string) {
  if (!canClickCard(playerName)) return
  
  if (isPlayerSubmitted(playerName)) {
    // 已提交，询问是否取消重新录入
    const submittedScore = getPlayerSubmittedScore(playerName)
    editingPlayer.value = playerName
    // 填充已提交的数据
    scoreInput.value = {
      shotType: submittedScore?.shotType || 'two',
      made: submittedScore?.made || 0,
      total: submittedScore?.total || room.value?.ballsPerRound || 10
    }
    showScoreDialog.value = true
  } else {
    // 未提交，打开输入弹窗
    editingPlayer.value = playerName
    scoreInput.value = {
      shotType: 'two',
      made: 0,
      total: room.value?.ballsPerRound || 10
    }
    showScoreDialog.value = true
  }
}

// 提交分数
async function handleSubmitScore() {
  try {
    // 如果已经提交过，先取消再重新提交
    if (isPlayerSubmitted(editingPlayer.value)) {
      await basketballRoomApi.cancelScore(roomId.value, editingPlayer.value)
    }
    
    await basketballRoomApi.submitScore(roomId.value, {
      playerName: editingPlayer.value,
      shotType: scoreInput.value.shotType,
      made: scoreInput.value.made,
      total: scoreInput.value.total
    })
    showScoreDialog.value = false
    MessagePlugin.success('记录成功')
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '提交失败')
  }
}

// 取消提交
async function handleCancelScore(playerName: string) {
  try {
    await basketballRoomApi.cancelScore(roomId.value, playerName)
    MessagePlugin.success('已取消')
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '取消失败')
  }
}

// 确认本轮
async function handleConfirmRound() {
  try {
    await basketballRoomApi.confirmRound(roomId.value)
    MessagePlugin.success('进入下一轮')
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '确认失败')
  }
}

// 结算预览
const settlementPreview = computed(() => {
  if (!room.value || players.value.length < 1) return null
  
  const pricePerBall = room.value.pricePerBall
  
  const playerStats = players.value.map(p => {
    const totalMade = roomStore.getPlayerTotalMade(p.name)
    const totalShots = roomStore.getPlayerTotalShots(p.name)
    const accuracy = roomStore.getPlayerAccuracy(p.name)
    return { name: p.name, totalMade, totalShots, accuracy }
  })
  
  const sorted = [...playerStats].sort((a, b) => b.totalMade - a.totalMade)
  const winner = sorted[0]?.totalMade > 0 ? sorted[0] : null
  
  const transfers: { from: string; to: string; amount: number; shotsDiff: number }[] = []
  
  if (winner) {
    for (let i = 1; i < sorted.length; i++) {
      const loser = sorted[i]
      const shotsDiff = winner.totalMade - loser.totalMade
      const amount = shotsDiff * pricePerBall
      if (amount > 0) {
        transfers.push({
          from: loser.name,
          to: winner.name,
          amount,
          shotsDiff
        })
      }
    }
  }
  
  return {
    winner: winner?.name || null,
    winnerMade: winner?.totalMade || 0,
    winnerAccuracy: winner?.accuracy || 0,
    playerStats: sorted,
    transfers
  }
})

async function handleUndo() {
  try {
    await basketballRoomApi.undoRound(roomId.value)
    MessagePlugin.success('已撤销')
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '撤销失败')
  }
}

async function handleSettle() {
  try {
    const result = await basketballRoomApi.settle(roomId.value)
    showSettleConfirm.value = false
    
    if (result.isZeroMatch) {
      MessagePlugin.info('0球比赛不计入战绩，已返回')
      router.push('/basketball')
    } else {
      MessagePlugin.success('结算完成')
    }
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '结算失败')
  }
}

async function grantOperator(userName: string) {
  try {
    await basketballRoomApi.grantOperator(roomId.value, userName)
    MessagePlugin.success(`已授权 ${userName} 完整权限`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '授权失败')
  }
}

async function revokeOperator(userName: string) {
  try {
    await basketballRoomApi.revokeOperator(roomId.value, userName)
    MessagePlugin.success(`已移除 ${userName} 的权限`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '操作失败')
  }
}

async function setSelfEditOnly(userName: string) {
  try {
    await basketballRoomApi.setSelfEditOnly(roomId.value, userName)
    MessagePlugin.success(`已设置 ${userName} 为仅编辑自己`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '操作失败')
  }
}

function getPermissionOptions(playerName: string) {
  const currentPermission = room.value?.operators.includes(playerName) 
    ? 'full' 
    : room.value?.selfEditOnly?.includes(playerName) 
      ? 'self' 
      : 'none'
  
  return [
    { content: '✅ 完整权限', value: 'full', disabled: currentPermission === 'full' },
    { content: '📝 仅编辑自己', value: 'self', disabled: currentPermission === 'self' },
    { content: '👀 仅观看', value: 'none', disabled: currentPermission === 'none' }
  ]
}

async function handlePermissionChange(playerName: string, permission: string) {
  switch (permission) {
    case 'full':
      await grantOperator(playerName)
      break
    case 'self':
      await setSelfEditOnly(playerName)
      break
    case 'none':
      await revokeOperator(playerName)
      break
  }
}

async function handleTransferOwner(userName: string) {
  try {
    await basketballRoomApi.transferOwner(roomId.value, userName)
    MessagePlugin.success(`已将房主转让给 ${userName}`)
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '转让失败')
  }
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
  router.push('/basketball')
}

// 初始化当前轮次状态
async function loadCurrentRoundStatus() {
  try {
    const status = await basketballRoomApi.getCurrentRoundStatus(roomId.value)
    roomStore.updateCurrentRoundStatus(status)
  } catch (e) {
    console.error('加载当前轮次状态失败', e)
  }
}

onMounted(async () => {
  const userName = roomStore.currentUser || localStorage.getItem('basketballUserName')
  
  if (!userName) {
    MessagePlugin.warning('请先选择你的身份')
    router.push('/basketball')
    return
  }
  
  try {
    const roomData = await basketballRoomApi.get(roomId.value)
    roomStore.setRoom(roomData)
    roomStore.setCurrentUser(userName)
    basketballWsService.connect(roomId.value, userName)
    
    // 加载当前轮次状态
    await loadCurrentRoundStatus()
  } catch (e: any) {
    MessagePlugin.error('房间不存在或已关闭')
    router.push('/basketball')
  }
})

onUnmounted(() => {
  basketballWsService.disconnect()
  roomStore.reset()
})
</script>

<style lang="scss" scoped>
.room-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: 
    url('@/assets/basketball/bg-main_3.png') center center / cover no-repeat fixed,
    linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  
  &::before {
    content: '';
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    pointer-events: none;
    z-index: 0;
  }
  
  > * {
    position: relative;
    z-index: 1;
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
    }
  }
}

.round-banner {
  text-align: center;
  padding: 16px;
  background: rgba(245, 158, 11, 0.15);
  border-radius: 12px;
  margin-bottom: 20px;
  
  .round-number {
    font-size: 24px;
    font-weight: 700;
    color: #f59e0b;
  }
  
  .round-limit {
    font-size: 18px;
    color: var(--text-secondary);
  }
  
  .balls-info {
    display: block;
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: 4px;
  }
  
  .round-progress {
    margin-top: 8px;
    
    .progress-text {
      font-size: 13px;
      color: var(--text-secondary);
      background: rgba(255, 255, 255, 0.1);
      padding: 4px 12px;
      border-radius: 20px;
    }
  }
}

.scoreboard {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.players-grid {
  display: grid;
  gap: 16px;
  width: 100%;
  max-width: 800px;
  
  &.players-1 {
    grid-template-columns: 1fr;
    max-width: 300px;
  }
  
  &.players-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  &.players-3 {
    grid-template-columns: repeat(3, 1fr);
  }
  
  &.players-4 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  &.players-5, &.players-6 {
    grid-template-columns: repeat(3, 1fr);
  }
}

.player-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 16px;
  border-radius: 20px;
  background: var(--card-bg);
  border: 2px solid transparent;
  transition: all 0.3s;
  position: relative;
  
  &.leading {
    border-color: #f59e0b;
    box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);
  }
  
  &.submitted {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.1);
  }
  
  &.clickable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    
    &:active {
      transform: translateY(-2px);
    }
  }
  
  .submitted-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #10b981;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
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
    
    &.player-1 { background: linear-gradient(135deg, #f59e0b, #d97706); }
    &.player-2 { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    &.player-3 { background: linear-gradient(135deg, #10b981, #059669); }
    &.player-4 { background: linear-gradient(135deg, #ec4899, #db2777); }
    &.player-5 { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
    &.player-6 { background: linear-gradient(135deg, #ef4444, #dc2626); }
  }
  
  .player-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
  }
  
  .player-stats {
    text-align: center;
    
    .stat-main {
      display: flex;
      align-items: baseline;
      justify-content: center;
      gap: 4px;
      
      .stat-value {
        font-size: 48px;
        font-weight: 800;
        color: var(--text-color);
      }
      
      .stat-label {
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
    
    .stat-sub {
      margin-top: 4px;
      
      .accuracy {
        font-size: 16px;
        font-weight: 600;
        color: #f59e0b;
      }
    }
  }
  
  .current-round-preview {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: rgba(16, 185, 129, 0.2);
    border-radius: 20px;
    
    .preview-made {
      font-size: 16px;
      font-weight: 700;
      color: #10b981;
    }
    
    .preview-type {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
  
  .leading-badge {
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 2;
    
    .flame-img {
      width: 80px;
      height: auto;
      opacity: 0.9;
    }
  }
  
  .star-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    z-index: 2;
    
    .star-img {
      width: 40px;
      height: auto;
    }
  }
  
  .basketball-decor {
    position: absolute;
    top: 8px;
    left: 8px;
    opacity: 0.3;
    
    .basketball-icon {
      width: 24px;
      height: auto;
    }
  }
  
  .click-tip {
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
  }
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  flex-wrap: wrap;
  
  .big-btn {
    
    min-width: 30px;
  }
  
  .spectator-tip {
    color: var(--text-secondary);
    padding: 12px 24px;
    background: var(--card-bg);
    border-radius: 12px;
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

// 记录得分弹窗
.score-input-panel {
  .input-group {
    margin-bottom: 20px;
    
    label {
      display: block;
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .quick-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }
    
    .made-input {
      width: 100%;
    }
  }
  
  .accuracy-preview {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    color: #f59e0b;
    padding: 12px;
    background: rgba(245, 158, 11, 0.1);
    border-radius: 12px;
    margin-bottom: 20px;
  }
  
  .confirm-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

// 结算预览
.settle-preview {
  .winner-section {
    text-align: center;
    padding: 20px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.05));
    border-radius: 16px;
    
    .trophy-img {
      width: 80px;
      height: auto;
      margin-bottom: 8px;
    }
    
    .winner-badge {
      font-size: 14px;
      color: #f59e0b;
      margin-bottom: 8px;
    }
    
    .winner-name {
      font-size: 28px;
      font-weight: 800;
      color: var(--text-color);
    }
    
    .winner-stats {
      font-size: 14px;
      color: var(--text-secondary);
      margin-top: 8px;
    }
  }
  
  .stats-list {
    margin-bottom: 20px;
    
    .stat-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 8px;
      background: rgba(255, 255, 255, 0.03);
      
      &.winner {
        background: rgba(245, 158, 11, 0.1);
      }
      
      .rank {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: var(--card-bg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
      }
      
      .name {
        flex: 1;
        font-weight: 600;
        color: var(--text-color);
      }
      
      .made {
        font-weight: 700;
        color: #f59e0b;
      }
      
      .accuracy {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
  
  .transfers-section {
    .section-title {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      
      .coin-icon {
        width: 24px;
        height: auto;
      }
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
      }
      
      .transfer-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        
        .diff {
          font-size: 11px;
          color: var(--text-secondary);
        }
        
        .t-icon {
          color: #f59e0b;
        }
      }
      
      .to {
        color: var(--success-color);
        font-weight: 600;
      }
      
      .amount {
        font-size: 20px;
        font-weight: 800;
        color: #f59e0b;
      }
    }
  }
  
  .draw-result {
    text-align: center;
    padding: 20px;
    color: var(--text-secondary);
  }
}

// 分享弹窗
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
    color: var(--text-color);
    
    &.owner {
      background: rgba(250, 173, 20, 0.15);
      
      span {
        color: var(--text-color);
      }
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
    background: var(--card-bg);
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
  z-index: 100;
}

@media (max-width: 600px) {
  .players-grid {
    &.players-3 {
      grid-template-columns: repeat(2, 1fr);
      
      .player-card:last-child {
        grid-column: span 2;
        max-width: 200px;
        margin: 0 auto;
      }
    }
    
    &.players-5 {
      grid-template-columns: repeat(2, 1fr);
      
      .player-card:last-child {
        grid-column: span 2;
        max-width: 200px;
        margin: 0 auto;
      }
    }
  }
  
  .player-card {
    padding: 16px 12px;
    
    .player-stats .stat-main .stat-value {
      font-size: 36px;
    }
  }
}
</style>
