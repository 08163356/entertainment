<template>
  <div class="practice-page">
    <header class="header">
      <t-button variant="text" @click="router.push('/basketball')">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <h1>🏀 个人练习</h1>
      <div></div>
    </header>

    <main class="main-content">
      <!-- 记录练习 -->
      <div class="action-panel">
        <div 
          class="panel-header record"
          :class="{ active: expandedPanel === 'record' }"
          @click="togglePanel('record')"
        >
          <div class="panel-title">
            <t-icon name="edit-1" />
            <span>记录练习</span>
          </div>
          <t-icon :name="expandedPanel === 'record' ? 'chevron-up' : 'chevron-down'" class="arrow" />
        </div>
        <t-collapse-transition>
          <div class="panel-content" v-show="expandedPanel === 'record'">
            <t-form :data="formData" @submit="handleSubmit">
              <t-form-item label="你的名字">
                <t-select
                  v-model="formData.playerName"
                  :options="playerOptions"
                  filterable
                  creatable
                  placeholder="选择或输入名字"
                />
              </t-form-item>
              
              <t-form-item label="投篮类型">
                <t-radio-group v-model="formData.shotType">
                  <t-radio-button 
                    v-for="type in SHOT_TYPES" 
                    :key="type.value" 
                    :value="type.value"
                  >
                    {{ type.label }}
                  </t-radio-button>
                </t-radio-group>
              </t-form-item>
              
              <t-form-item label="总投球数">
                <t-input-number v-model="formData.totalShots" :min="1" :max="100" />
              </t-form-item>
              
              <t-form-item label="进球数">
                <div class="made-input">
                  <t-input-number 
                    v-model="formData.shotsMade" 
                    :min="0" 
                    :max="formData.totalShots" 
                  />
                  <div class="quick-buttons">
                    <t-button 
                      v-for="n in [0, 5, 10, 15, 20]" 
                      :key="n"
                      size="small"
                      :theme="formData.shotsMade === n ? 'primary' : 'default'"
                      :disabled="n > formData.totalShots"
                      @click="formData.shotsMade = Math.min(n, formData.totalShots)"
                    >
                      {{ n }}
                    </t-button>
                  </div>
                </div>
              </t-form-item>
              
              <t-form-item>
                <div class="accuracy-preview">
                  命中率预览: <strong>{{ accuracyPreview }}%</strong>
                </div>
              </t-form-item>
              
              <t-form-item>
                <t-button theme="primary" type="submit" block size="large">
                  保存记录
                </t-button>
              </t-form-item>
            </t-form>
          </div>
        </t-collapse-transition>
      </div>

      <!-- 统计图表 -->
      <div class="action-panel" v-if="formData.playerName">
        <div 
          class="panel-header stats"
          :class="{ active: expandedPanel === 'stats' }"
          @click="togglePanel('stats')"
        >
          <div class="panel-title">
            <t-icon name="chart-bar" />
            <span>练习统计</span>
          </div>
          <t-icon :name="expandedPanel === 'stats' ? 'chevron-up' : 'chevron-down'" class="arrow" />
        </div>
        <t-collapse-transition>
          <div class="panel-content" v-show="expandedPanel === 'stats'">
            <div class="period-selector">
              <t-radio-group v-model="statsPeriod" size="small">
                <t-radio-button value="week">近7天</t-radio-button>
                <t-radio-button value="month">近30天</t-radio-button>
                <t-radio-button value="all">全部</t-radio-button>
              </t-radio-group>
            </div>
            
            <t-loading :loading="loadingStats">
              <div v-if="practiceStats" class="stats-content">
                <!-- 总览卡片 -->
                <div class="stats-overview">
                  <div class="overview-card">
                    <div class="value">{{ practiceStats.totalSessions }}</div>
                    <div class="label">练习次数</div>
                  </div>
                  <div class="overview-card">
                    <div class="value">{{ totalShots }}</div>
                    <div class="label">总投球</div>
                  </div>
                  <div class="overview-card">
                    <div class="value">{{ totalMade }}</div>
                    <div class="label">总进球</div>
                  </div>
                  <div class="overview-card">
                    <div class="value">{{ overallAccuracy }}%</div>
                    <div class="label">总命中率</div>
                  </div>
                </div>
                
                <!-- 按类型分组 -->
                <div class="type-stats" v-if="practiceStats.statsByType.length > 0">
                  <h3>按投篮类型</h3>
                  <t-table
                    :data="practiceStats.statsByType"
                    :columns="typeTableColumns"
                    row-key="shotType"
                    size="small"
                    bordered
                    stripe
                    class="type-table"
                  />
                </div>
                
                <!-- 趋势图表 -->
                <div class="chart-section" v-if="practiceStats.chartData.length > 0">
                  <h3>命中率趋势</h3>
                  <div class="chart-container">
                    <div class="chart-bars">
                      <div 
                        v-for="(data, index) in chartDataLimited" 
                        :key="index"
                        class="chart-bar-wrapper"
                      >
                        <div 
                          class="chart-bar" 
                          :class="data.shotType"
                          :style="{ height: `${data.accuracy}%` }"
                        >
                          <span class="bar-value">{{ data.accuracy }}%</span>
                        </div>
                        <span class="bar-label">{{ formatChartDate(data.date) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="chart-legend">
                    <span class="legend-item three">
                      <span class="dot"></span>三分
                    </span>
                    <span class="legend-item two">
                      <span class="dot"></span>两分
                    </span>
                    <span class="legend-item free">
                      <span class="dot"></span>罚球
                    </span>
                  </div>
                </div>
              </div>
              
              <div v-else class="empty-stats">
                暂无练习数据，开始记录吧！
              </div>
            </t-loading>
          </div>
        </t-collapse-transition>
      </div>

      <!-- 最近记录 -->
      <div class="action-panel">
        <div 
          class="panel-header history"
          :class="{ active: expandedPanel === 'history' }"
          @click="togglePanel('history')"
        >
          <div class="panel-title">
            <t-icon name="time" />
            <span>最近记录</span>
            <t-badge v-if="recentPractices.length > 0" :count="recentPractices.length" />
          </div>
          <t-icon :name="expandedPanel === 'history' ? 'chevron-up' : 'chevron-down'" class="arrow" />
        </div>
        <t-collapse-transition>
          <div class="panel-content" v-show="expandedPanel === 'history'">
            <t-loading :loading="loadingHistory">
              <div v-if="recentPractices.length > 0" class="practice-list">
                <div 
                  v-for="practice in recentPractices" 
                  :key="practice.id"
                  class="practice-item"
                >
                  <div class="practice-main">
                    <span class="player">{{ practice.playerName }}</span>
                    <t-tag 
                      size="small" 
                      :theme="getShotTypeTheme(practice.shotType)"
                    >
                      {{ getShotTypeLabel(practice.shotType) }}
                    </t-tag>
                  </div>
                  <div class="practice-stats">
                    <span class="shots">{{ practice.shotsMade }}/{{ practice.totalShots }}</span>
                    <span class="accuracy">{{ practice.accuracy }}%</span>
                  </div>
                  <div class="practice-meta">
                    <span class="date">{{ formatDate(practice.createdAt) }}</span>
                    <t-button 
                      variant="text" 
                      theme="danger" 
                      size="small"
                      @click="handleDelete(practice.id)"
                    >
                      <t-icon name="delete" />
                    </t-button>
                  </div>
                </div>
              </div>
              <div v-else class="empty-history">
                暂无练习记录
              </div>
            </t-loading>
          </div>
        </t-collapse-transition>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { basketballPracticeApi, basketballPlayerApi } from '@/services/basketballApi'
import { SHOT_TYPES, PRESET_PLAYERS } from '@/types/basketball'
import type { PracticeRecord, PlayerPracticeStats } from '@/types/basketball'

const router = useRouter()

const expandedPanel = ref<'record' | 'stats' | 'history'>('record')

function togglePanel(panel: 'record' | 'stats' | 'history') {
  expandedPanel.value = expandedPanel.value === panel ? panel : panel
}

const formData = ref({
  playerName: localStorage.getItem('basketballUserName') || '',
  shotType: 'two',
  totalShots: 10,
  shotsMade: 0
})

const statsPeriod = ref<'week' | 'month' | 'all'>('month')
const loadingStats = ref(false)
const loadingHistory = ref(false)
const practiceStats = ref<PlayerPracticeStats | null>(null)
const recentPractices = ref<PracticeRecord[]>([])
const allPlayers = ref<string[]>([])

const playerOptions = computed(() => {
  const names = new Set([
    ...PRESET_PLAYERS.map(p => p.name),
    ...allPlayers.value
  ])
  return Array.from(names).map(name => ({ label: name, value: name }))
})

const accuracyPreview = computed(() => {
  if (formData.value.totalShots === 0) return '0.0'
  return ((formData.value.shotsMade / formData.value.totalShots) * 100).toFixed(1)
})

const totalShots = computed(() => 
  practiceStats.value?.statsByType.reduce((sum, s) => sum + s.totalShots, 0) || 0
)

const totalMade = computed(() => 
  practiceStats.value?.statsByType.reduce((sum, s) => sum + s.totalMade, 0) || 0
)

const overallAccuracy = computed(() => {
  if (totalShots.value === 0) return '0.0'
  return ((totalMade.value / totalShots.value) * 100).toFixed(1)
})

const chartDataLimited = computed(() => {
  const data = practiceStats.value?.chartData || []
  return data.slice(-15)  // 最多显示15条
})

const typeTableColumns = [
  { 
    colKey: 'shotType', 
    title: '类型', 
    width: 80,
    cell: (h: any, { row }: any) => getShotTypeLabel(row.shotType)
  },
  { colKey: 'totalSessions', title: '次数', width: 60 },
  { 
    colKey: 'totalMade', 
    title: '进球', 
    width: 100,
    cell: (h: any, { row }: any) => `${row.totalMade}/${row.totalShots}`
  },
  { 
    colKey: 'avgAccuracy', 
    title: '平均', 
    width: 70,
    cell: (h: any, { row }: any) => `${row.avgAccuracy}%`
  },
  { 
    colKey: 'bestAccuracy', 
    title: '最佳', 
    width: 70,
    cell: (h: any, { row }: any) => `${row.bestAccuracy}%`
  }
]

function getShotTypeLabel(type: string): string {
  return SHOT_TYPES.find(t => t.value === type)?.label || type
}

function getShotTypeTheme(type: string): string {
  const themes: Record<string, string> = {
    three: 'primary',
    two: 'danger',
    free: 'success'
  }
  return themes[type] || 'default'
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatChartDate(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

async function handleSubmit() {
  if (!formData.value.playerName) {
    MessagePlugin.warning('请输入你的名字')
    return
  }
  
  try {
    await basketballPracticeApi.create({
      playerName: formData.value.playerName,
      shotType: formData.value.shotType,
      totalShots: formData.value.totalShots,
      shotsMade: formData.value.shotsMade
    })
    
    localStorage.setItem('basketballUserName', formData.value.playerName)
    MessagePlugin.success('记录成功')
    
    formData.value.shotsMade = 0
    loadStats()
    loadHistory()
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '记录失败')
  }
}

async function handleDelete(practiceId: number) {
  try {
    await basketballPracticeApi.delete(practiceId)
    MessagePlugin.success('已删除')
    loadStats()
    loadHistory()
  } catch (e: any) {
    MessagePlugin.error(e.response?.data?.detail || '删除失败')
  }
}

async function loadStats() {
  if (!formData.value.playerName) return
  
  loadingStats.value = true
  try {
    practiceStats.value = await basketballPracticeApi.getStats(
      formData.value.playerName, 
      statsPeriod.value
    )
  } catch (e) {
    console.error('加载统计失败', e)
  } finally {
    loadingStats.value = false
  }
}

async function loadHistory() {
  loadingHistory.value = true
  try {
    const result = await basketballPracticeApi.getList({ limit: 20 })
    recentPractices.value = result.practices
  } catch (e) {
    console.error('加载历史失败', e)
  } finally {
    loadingHistory.value = false
  }
}

async function loadPlayers() {
  try {
    const players = await basketballPlayerApi.getPlayers()
    allPlayers.value = players.map(p => p.name)
  } catch (e) {
    console.error('加载玩家失败', e)
  }
}

watch([() => formData.value.playerName, statsPeriod], () => {
  loadStats()
  loadHistory()
})

onMounted(() => {
  loadPlayers()
  loadHistory()
  if (formData.value.playerName) {
    loadStats()
  }
})
</script>

<style lang="scss" scoped>
.practice-page {
  min-height: 100vh;
  padding: 20px;
  background: 
    url('@/assets/basketball/bg-main_4.png') center center / cover no-repeat fixed,
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
  margin-bottom: 24px;
  
  h1 {
    font-size: 22px;
    color: var(--text-color);
  }
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-panel {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
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
  
  &.record .panel-title .t-icon {
    color: #f59e0b;
  }
  
  &.stats .panel-title .t-icon {
    color: #ec4899;
  }
  
  &.history .panel-title .t-icon {
    color: #60a5fa;
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
  }
}

.panel-content {
  padding: 0 20px 20px;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

.period-selector {
  margin-bottom: 20px;
}

.made-input {
  .quick-buttons {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    flex-wrap: wrap;
  }
}

.accuracy-preview {
  font-size: 16px;
  color: var(--text-secondary);
  
  strong {
    font-size: 24px;
    color: #f59e0b;
  }
}

// 统计区域

.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
  
  .overview-card {
    text-align: center;
    padding: 16px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    
    .value {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-color);
    }
    
    .label {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
    }
  }
}

.type-stats {
  margin-bottom: 24px;
  
  h3 {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 12px;
  }
  
  .type-table {
    :deep(.t-table) {
      background: rgba(0, 0, 0, 0.3);
      border-radius: 8px;
    }
    
    :deep(.t-table__header th) {
      background: rgba(0, 0, 0, 0.5) !important;
      color: #2e2222;
      font-weight: 600;
      border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    :deep(.t-table__body td) {
      color: #564e4e;
      background: transparent !important;
      border-color: rgba(255, 255, 255, 0.08) !important;
    }
    
    :deep(.t-table__body tr:hover td) {
      background: rgba(255, 255, 255, 0.05) !important;
    }
    
    :deep(.t-table--striped .t-table__body tr:nth-child(even) td) {
      background: rgba(255, 255, 255, 0.02) !important;
    }
  }
}

.chart-section {
  h3 {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }
  
  .chart-container {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 12px;
    padding: 20px;
    height: 200px;
    overflow-x: auto;
  }
  
  .chart-bars {
    display: flex;
    align-items: flex-end;
    height: 100%;
    gap: 8px;
    min-width: max-content;
  }
  
  .chart-bar-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 40px;
    height: 100%;
    
    .chart-bar {
      width: 100%;
      max-width: 30px;
      border-radius: 4px 4px 0 0;
      position: relative;
      min-height: 20px;
      transition: height 0.3s;
      
      &.three { background: linear-gradient(180deg, #667eea, #764ba2); }
      &.two { background: linear-gradient(180deg, #f5576c, #f093fb); }
      &.free { background: linear-gradient(180deg, #52c41a, #a8e063); }
      
      .bar-value {
        position: absolute;
        top: -20px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 10px;
        color: var(--text-secondary);
        white-space: nowrap;
      }
    }
    
    .bar-label {
      font-size: 10px;
      color: var(--text-secondary);
      margin-top: 8px;
    }
  }
  
  .chart-legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 16px;
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-secondary);
      
      .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
      }
      
      &.three .dot { background: #667eea; }
      &.two .dot { background: #f5576c; }
      &.free .dot { background: #52c41a; }
    }
  }
}

.empty-stats {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

// 历史记录
.practice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.practice-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  
  .practice-main {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .player {
      font-weight: 600;
      color: var(--text-color);
    }
  }
  
  .practice-stats {
    flex: 1;
    text-align: center;
    
    .shots {
      font-weight: 600;
      color: var(--text-color);
      margin-right: 12px;
    }
    
    .accuracy {
      font-weight: 700;
      color: #f59e0b;
    }
  }
  
  .practice-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .date {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

.empty-history {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

@media (max-width: 600px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
