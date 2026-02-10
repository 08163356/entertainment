<template>
  <div class="player-stats-page">
    <header class="header">
      <t-button variant="text" @click="router.push('/billiards')">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <h1>{{ playerName }} 的战绩</h1>
      <div></div>
    </header>

    <main class="main-content">
      <t-loading :loading="loading">
        <!-- 总览卡片 -->
        <div class="stats-overview">
          <div class="stat-card">
            <div class="stat-value">{{ stats?.totalMatches || 0 }}</div>
            <div class="stat-label">总场次</div>
          </div>
          <div class="stat-card win">
            <div class="stat-value">{{ stats?.totalWins || 0 }}</div>
            <div class="stat-label">胜</div>
          </div>
          <div class="stat-card lose">
            <div class="stat-value">{{ stats?.totalLosses || 0 }}</div>
            <div class="stat-label">负</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ winRatePercent }}%</div>
            <div class="stat-label">胜率</div>
          </div>
        </div>

        <!-- 盈亏统计 -->
        <div class="card profit-section">
          <h3>盈亏统计</h3>
          <div class="profit-display" :class="profitClass">
            <span class="label">累计盈亏</span>
            <span class="value">{{ profitText }}</span>
          </div>
          <div class="ball-stats">
            <div class="ball-item">
              <span class="label">赢球总数</span>
              <span class="value">{{ stats?.totalBallsWon || 0 }}</span>
            </div>
            <div class="ball-item">
              <span class="label">输球总数</span>
              <span class="value">{{ stats?.totalBallsLost || 0 }}</span>
            </div>
            <div class="ball-item">
              <span class="label">净球数</span>
              <span class="value" :class="{ positive: (stats?.netBalls || 0) > 0, negative: (stats?.netBalls || 0) < 0 }">
                {{ stats?.netBalls || 0 }}
              </span>
            </div>
          </div>
        </div>

        <!-- 对手分析 -->
        <div class="card opponents-section">
          <h3>对手战绩</h3>
          <div class="opponents-chart" ref="opponentsChartRef"></div>
          <div class="opponents-list">
            <div 
              v-for="op in stats?.opponentStats" 
              :key="op.opponent"
              class="opponent-item"
            >
              <div class="opponent-name">{{ op.opponent }}</div>
              <div class="opponent-record">
                {{ op.wins }}胜 {{ op.losses }}负 ({{ (op.winRate * 100).toFixed(0) }}%)
              </div>
              <div class="opponent-profit" :class="{ positive: op.netAmount > 0, negative: op.netAmount < 0 }">
                {{ op.netAmount > 0 ? '+' : '' }}¥{{ op.netAmount }}
              </div>
            </div>
          </div>
        </div>

        <!-- 走势图 -->
        <div class="card trend-section">
          <h3>盈亏走势</h3>
          <div class="trend-chart" ref="trendChartRef"></div>
        </div>

        <!-- 最近比赛 -->
        <div class="card recent-section">
          <h3>最近比赛</h3>
          <div class="recent-list">
            <div 
              v-for="match in stats?.recentMatches" 
              :key="match.id"
              class="recent-item"
            >
              <div class="match-info">
                <span class="opponent">vs {{ getOpponent(match) }}</span>
                <span class="date">{{ formatDate(match.settledAt) }}</span>
              </div>
              <div class="match-result" :class="getResultClass(match)">
                {{ getResultText(match) }}
              </div>
            </div>
          </div>
        </div>
      </t-loading>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { playerApi } from '@/services/api'
import type { PlayerStats, MatchRecord } from '@/types/billiards'

const route = useRoute()
const router = useRouter()

const playerName = computed(() => decodeURIComponent(route.params.name as string))
const loading = ref(false)
const stats = ref<PlayerStats | null>(null)

const opponentsChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
let opponentsChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

const winRatePercent = computed(() => {
  if (!stats.value) return 0
  return (stats.value.winRate * 100).toFixed(1)
})

const profitClass = computed(() => {
  const amount = stats.value?.netAmount || 0
  return { positive: amount > 0, negative: amount < 0 }
})

const profitText = computed(() => {
  const amount = stats.value?.netAmount || 0
  if (amount > 0) return `+¥${amount}`
  if (amount < 0) return `-¥${Math.abs(amount)}`
  return '¥0'
})

async function loadStats() {
  loading.value = true
  try {
    stats.value = await playerApi.getStats(playerName.value)
    await nextTick()
    renderCharts()
  } catch (e) {
    console.error('加载统计数据失败', e)
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  renderOpponentsChart()
  renderTrendChart()
}

function renderOpponentsChart() {
  if (!opponentsChartRef.value || !stats.value?.opponentStats?.length) return
  
  if (!opponentsChart) {
    opponentsChart = echarts.init(opponentsChartRef.value)
  }
  
  const data = stats.value.opponentStats.map(op => ({
    name: op.opponent,
    value: op.matches
  }))
  
  opponentsChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}场 ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data,
      label: {
        show: true,
        formatter: '{b}'
      }
    }]
  })
}

function renderTrendChart() {
  if (!trendChartRef.value || !stats.value?.recentMatches?.length) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  // 计算累计盈亏
  let cumulative = 0
  const matches = [...stats.value.recentMatches].reverse()
  const data = matches.map(match => {
    const isWinner = match.settlement.winner === playerName.value
    const amount = isWinner ? match.settlement.amount : -match.settlement.amount
    cumulative += amount
    return {
      date: formatDate(match.settledAt),
      value: cumulative
    }
  })
  
  trendChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>累计: ¥{c}'
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [{
      type: 'line',
      data: data.map(d => d.value),
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      itemStyle: {
        color: '#1a5d1a'
      }
    }]
  })
}

function getOpponent(match: MatchRecord) {
  return match.players.find(p => p !== playerName.value) || '未知'
}

function getResultClass(match: MatchRecord) {
  if (match.settlement.winner === playerName.value) return 'win'
  if (match.settlement.loser === playerName.value) return 'lose'
  return 'draw'
}

function getResultText(match: MatchRecord) {
  if (match.settlement.winner === playerName.value) {
    return `胜 +¥${match.settlement.amount}`
  }
  if (match.settlement.loser === playerName.value) {
    return `负 -¥${match.settlement.amount}`
  }
  return '平'
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(() => {
  loadStats()
})

watch(() => route.params.name, () => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.player-stats-page {
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
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  
  .stat-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    
    &.win .stat-value { color: var(--success-color); }
    &.lose .stat-value { color: var(--error-color); }
    
    .stat-value {
      font-size: 28px;
      font-weight: bold;
      color: var(--text-color);
    }
    
    .stat-label {
      font-size: 14px;
      color: var(--text-secondary);
      margin-top: 4px;
    }
  }
}

.card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
  
  h3 {
    font-size: 18px;
    margin-bottom: 16px;
    color: var(--text-color);
  }
}

.profit-section {
  .profit-display {
    text-align: center;
    padding: 24px;
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
    
    &.positive .value { color: var(--success-color); }
    &.negative .value { color: var(--error-color); }
    
    .label {
      display: block;
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .value {
      font-size: 36px;
      font-weight: bold;
    }
  }
  
  .ball-stats {
    display: flex;
    justify-content: space-around;
    
    .ball-item {
      text-align: center;
      
      .label {
        display: block;
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 4px;
      }
      
      .value {
        font-size: 20px;
        font-weight: bold;
        
        &.positive { color: var(--success-color); }
        &.negative { color: var(--error-color); }
      }
    }
  }
}

.opponents-section {
  .opponents-chart {
    height: 200px;
    margin-bottom: 16px;
  }
  
  .opponents-list {
    .opponent-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid var(--border-color);
      
      &:last-child {
        border-bottom: none;
      }
      
      .opponent-name {
        font-weight: bold;
      }
      
      .opponent-record {
        color: var(--text-secondary);
        font-size: 14px;
      }
      
      .opponent-profit {
        font-weight: bold;
        
        &.positive { color: var(--success-color); }
        &.negative { color: var(--error-color); }
      }
    }
  }
}

.trend-section {
  .trend-chart {
    height: 250px;
  }
}

.recent-section {
  .recent-list {
    .recent-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid var(--border-color);
      
      &:last-child {
        border-bottom: none;
      }
      
      .match-info {
        .opponent {
          display: block;
          font-weight: bold;
        }
        
        .date {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
      
      .match-result {
        font-weight: bold;
        
        &.win { color: var(--success-color); }
        &.lose { color: var(--error-color); }
        &.draw { color: var(--text-secondary); }
      }
    }
  }
}

@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
