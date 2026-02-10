<template>
  <div class="billiards-page">
    <header class="header">
      <t-button variant="text" @click="router.push('/')">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <h1>🎱 台球记分</h1>
      <div class="header-actions">
        <t-button variant="text" @click="router.push('/billiards/history')">
          历史记录
        </t-button>
      </div>
    </header>

    <main class="main-content">
      <!-- 创建房间 -->
      <div class="card create-room">
        <h2>创建新比赛</h2>
        
        <t-form :data="formData" :rules="formRules" ref="formRef" @submit="handleCreate">
          <t-form-item label="比赛类型" name="gameType">
            <t-select v-model="formData.gameType" :options="gameTypeOptions" />
          </t-form-item>
          
          <t-form-item label="玩家1" name="player1">
            <t-select
              v-model="formData.player1"
              :options="playerOptions"
              filterable
              creatable
              placeholder="选择或输入玩家名"
            />
          </t-form-item>
          
          <t-form-item label="玩家2" name="player2">
            <t-select
              v-model="formData.player2"
              :options="playerOptions"
              filterable
              creatable
              placeholder="选择或输入玩家名"
            />
          </t-form-item>
          
          <t-form-item label="单价（元/球）" name="pricePerBall">
            <t-input-number v-model="formData.pricePerBall" :min="0" :max="1000" />
          </t-form-item>
          
          <t-form-item label="你是谁" name="currentUser">
            <t-select v-model="formData.currentUser" :options="currentUserOptions" />
          </t-form-item>
          
          <t-form-item>
            <t-button theme="primary" type="submit" block size="large">
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
              :options="playerOptions"
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
            v-for="player in PRESET_PLAYERS" 
            :key="player.name"
            class="player-item"
            @click="router.push(`/billiards/player/${encodeURIComponent(player.name)}`)"
          >
            <div class="player-avatar" :class="`player-${PRESET_PLAYERS.indexOf(player) + 1}`">
              {{ player.name[0] }}
            </div>
            <span>{{ player.name }}</span>
            <t-icon name="chevron-right" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { roomApi } from '@/services/api'
import { useRoomStore } from '@/stores/room'
import { PRESET_PLAYERS, GAME_TYPES } from '@/types/billiards'

const router = useRouter()
const roomStore = useRoomStore()

const formRef = ref()
const formData = ref({
  gameType: 'eight-ball',
  player1: '阿兴',
  player2: '老爸',
  pricePerBall: 5,
  currentUser: '阿兴'
})

const formRules = {
  player1: [{ required: true, message: '请选择玩家1' }],
  player2: [{ required: true, message: '请选择玩家2' }],
  currentUser: [{ required: true, message: '请选择你是谁' }]
}

const joinRoomId = ref('')
const joinUserName = ref(localStorage.getItem('userName') || '')

const gameTypeOptions = GAME_TYPES.map(t => ({ label: t.label, value: t.value }))

const playerOptions = computed(() => 
  PRESET_PLAYERS.map(p => ({ label: p.name, value: p.name }))
)

const currentUserOptions = computed(() => [
  { label: formData.value.player1, value: formData.value.player1 },
  { label: formData.value.player2, value: formData.value.player2 }
].filter(o => o.value))

async function handleCreate() {
  if (formData.value.player1 === formData.value.player2) {
    MessagePlugin.warning('两位玩家不能是同一人')
    return
  }
  
  try {
    const isPreset = (name: string) => PRESET_PLAYERS.some(p => p.name === name)
    
    const { roomId } = await roomApi.create({
      gameType: formData.value.gameType,
      owner: formData.value.currentUser,
      players: [
        { name: formData.value.player1, isPreset: isPreset(formData.value.player1) },
        { name: formData.value.player2, isPreset: isPreset(formData.value.player2) }
      ],
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
  border-radius: 16px;
  padding: 24px;
  
  h2 {
    font-size: 18px;
    margin-bottom: 20px;
    color: var(--text-color);
  }
}

.player-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.player-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.05);
  }
  
  .player-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: bold;
    color: white;
    
    &.player-1 { background: linear-gradient(135deg, #667eea, #764ba2); }
    &.player-2 { background: linear-gradient(135deg, #f093fb, #f5576c); }
    &.player-3 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
  }
  
  span {
    flex: 1;
    font-size: 16px;
  }
}
</style>
