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
        <!-- 总览卡片（固定显示） -->
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

        <!-- 盈亏统计（可折叠） -->
        <div class="card collapsible-section">
          <div class="section-header" @click="toggleSection('profit')">
            <h3>盈亏统计</h3>
            <t-icon :name="expandedSections.profit ? 'chevron-up' : 'chevron-down'" />
          </div>
          <t-collapse-transition>
            <div class="section-content" v-show="expandedSections.profit">
              <div class="profit-display" :class="profitClass">
                <span class="label">累计盈亏</span>
                <span class="value">{{ profitText }}</span>
              </div>
              <div class="ball-stats">
                <div class="ball-item">
                  <span class="label">赢球总数</span>
                  <span class="value positive">{{ stats?.totalBallsWon || 0 }}</span>
                </div>
                <div class="ball-item">
                  <span class="label">输球总数</span>
                  <span class="value negative">{{ stats?.totalBallsLost || 0 }}</span>
                </div>
                <div class="ball-item">
                  <span class="label">净球数</span>
                  <span class="value" :class="{ positive: (stats?.netBalls || 0) > 0, negative: (stats?.netBalls || 0) < 0 }">
                    {{ stats?.netBalls || 0 }}
                  </span>
                </div>
              </div>
            </div>
          </t-collapse-transition>
        </div>

        <!-- 对手分析（可折叠） -->
        <div class="card collapsible-section">
          <div class="section-header" @click="toggleSection('opponents')">
            <h3>对手战绩</h3>
            <t-icon :name="expandedSections.opponents ? 'chevron-up' : 'chevron-down'" />
          </div>
          <t-collapse-transition>
            <div class="section-content" v-show="expandedSections.opponents">
              <div class="opponents-chart" ref="opponentsChartRef" v-if="stats?.opponentStats?.length"></div>
              <div class="opponents-list" v-if="stats?.opponentStats?.length">
                <div 
                  v-for="op in stats.opponentStats" 
                  :key="op.opponent"
                  class="opponent-item"
                >
                  <div class="opponent-info">
                    <div class="opponent-name">{{ op.opponent }}</div>
                    <div class="opponent-record">
                      <span class="wins">{{ op.wins }}胜</span>
                      <span class="losses">{{ op.losses }}负</span>
                      <span class="rate">({{ (op.winRate * 100).toFixed(0) }}%)</span>
                    </div>
                  </div>
                  <div class="opponent-profit" :class="{ positive: op.netAmount > 0, negative: op.netAmount < 0 }">
                    {{ op.netAmount > 0 ? '+' : '' }}¥{{ op.netAmount }}
                  </div>
                </div>
              </div>
              <div class="empty-tip" v-else>暂无对战记录</div>
            </div>
          </t-collapse-transition>
        </div>

        <!-- 走势图（可折叠） -->
        <div class="card collapsible-section">
          <div class="section-header" @click="toggleSection('trend')">
            <h3>盈亏走势</h3>
            <t-icon :name="expandedSections.trend ? 'chevron-up' : 'chevron-down'" />
          </div>
          <t-collapse-transition>
            <div class="section-content" v-show="expandedSections.trend">
              <div class="trend-chart" ref="trendChartRef" v-if="stats?.recentMatches?.length"></div>
              <div class="empty-tip" v-else>暂无数据</div>
            </div>
          </t-collapse-transition>
        </div>

        <!-- 最近比赛（可折叠） -->
        <div class="card collapsible-section">
          <div class="section-header" @click="toggleSection('recent')">
            <h3>最近比赛</h3>
            <t-icon :name="expandedSections.recent ? 'chevron-up' : 'chevron-down'" />
          </div>
          <t-collapse-transition>
            <div class="section-content" v-show="expandedSections.recent">
              <div class="recent-list" v-if="stats?.recentMatches?.length">
                <div 
                  v-for="match in stats.recentMatches" 
                  :key="match.id"
                  class="recent-item"
                >
                  <div class="match-main">
                    <div class="match-info">
                      <span class="opponent">vs {{ getOpponent(match) }}</span>
                      <span class="date">{{ formatDate(match.settledAt) }}</span>
                    </div>
                    <div class="match-result" :class="getResultClass(match)">
                      {{ getResultText(match) }}
                    </div>
                  </div>
                  <!-- 赢球数图标化展示 -->
                  <div class="balls-visual">
                    <div class="balls-row player-balls">
                      <span class="label">我</span>
                      <div class="balls-icons">
                        <span 
                          v-for="n in getMyBalls(match)" 
                          :key="n" 
                          class="ball-icon win"
                        >●</span>
                        <span v-if="getMyBalls(match) === 0" class="no-balls">-</span>
                      </div>
                      <span class="count">{{ getMyBalls(match) }}</span>
                    </div>
                    <div class="balls-row opponent-balls">
                      <span class="label">{{ getOpponent(match)?.[0] }}</span>
                      <div class="balls-icons">
                        <span 
                          v-for="n in getOpponentBalls(match)" 
                          :key="n" 
                          class="ball-icon lose"
                        >●</span>
                        <span v-if="getOpponentBalls(match) === 0" class="no-balls">-</span>
                      </div>
                      <span class="count">{{ getOpponentBalls(match) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="empty-tip" v-else>暂无比赛记录</div>
            </div>
          </t-collapse-transition>
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

// 折叠状态
const expandedSections = ref({
  profit: true,
  opponents: true,
  trend: false,
  recent: true
})

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

function toggleSection(section: keyof typeof expandedSections.value) {
  expandedSections.value[section] = !expandedSections.value[section]
  
  // 展开时重新渲染图表
  if (expandedSections.value[section]) {
    nextTick(() => {
      if (section === 'opponents') renderOpponentsChart()
      if (section === 'trend') renderTrendChart()
    })
  }
}

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
  if (expandedSections.value.opponents) renderOpponentsChart()
  if (expandedSections.value.trend) renderTrendChart()
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
      formatter: '{b}: {c}场 ({d}%)',
      backgroundColor: 'rgba(20, 20, 30, 0.9)',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      textStyle: { color: '#fff' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data,
      label: {
        show: true,
        formatter: '{b}',
        color: 'rgba(255, 255, 255, 0.8)'
      },
      itemStyle: {
        borderRadius: 8,
        borderColor: 'rgba(0, 0, 0, 0.3)',
        borderWidth: 2
      }
    }]
  })
  
  opponentsChart.resize()
}

function renderTrendChart() {
  if (!trendChartRef.value || !stats.value?.recentMatches?.length) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
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
      formatter: '{b}<br/>累计: ¥{c}',
      backgroundColor: 'rgba(20, 20, 30, 0.9)',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLabel: {
        rotate: 45,
        fontSize: 10,
        color: 'rgba(255, 255, 255, 0.6)'
      },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}',
        color: 'rgba(255, 255, 255, 0.6)'
      },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    series: [{
      type: 'line',
      data: data.map(d => d.value),
      smooth: true,
      areaStyle: {
        opacity: 0.3,
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(82, 196, 26, 0.4)' },
          { offset: 1, color: 'rgba(82, 196, 26, 0)' }
        ])
      },
      lineStyle: {
        color: '#52c41a',
        width: 3
      },
      itemStyle: {
        color: '#52c41a'
      }
    }]
  })
  
  trendChart.resize()
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

// 获取我在某场比赛中的赢球数
function getMyBalls(match: MatchRecord) {
  return match.rounds
    .filter(r => r.winner === playerName.value)
    .reduce((sum, r) => sum + r.ballsWon, 0)
}

// 获取对手在某场比赛中的赢球数
function getOpponentBalls(match: MatchRecord) {
  const opponent = getOpponent(match)
  return match.rounds
    .filter(r => r.winner === opponent)
    .reduce((sum, r) => sum + r.ballsWon, 0)
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
  margin-bottom: 24px;
  
  h1 {
    font-size: 22px;
    color: var(--text-color);
    font-weight: 700;
  }
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

// 总览卡片
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  
  .stat-card {
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 20px 12px;
    text-align: center;
    
    &.win .stat-value { color: var(--success-color); }
    &.lose .stat-value { color: var(--error-color); }
    
    .stat-value {
      font-size: 28px;
      font-weight: 800;
      color: var(--text-color);
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .stat-label {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
    }
  }
}

// 可折叠卡片
.card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.collapsible-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 20px;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover {
      background: rgba(255, 255, 255, 0.03);
    }
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-color);
      margin: 0;
    }
    
    .t-icon {
      color: var(--text-secondary);
      transition: transform 0.3s;
    }
  }
  
  .section-content {
    padding: 0 20px 20px;
  }
}

// 盈亏统计
.profit-display {
  text-align: center;
  padding: 24px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
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
    font-size: 40px;
    font-weight: 800;
    text-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
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
      font-size: 24px;
      font-weight: 700;
      
      &.positive { color: var(--success-color); }
      &.negative { color: var(--error-color); }
    }
  }
}

// 对手分析
.opponents-chart {
  height: 200px;
  margin-bottom: 16px;
}

.opponents-list {
  .opponent-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid var(--border-color);
    
    &:last-child {
      border-bottom: none;
    }
    
    .opponent-info {
      .opponent-name {
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 2px;
      }
      
      .opponent-record {
        font-size: 13px;
        color: var(--text-secondary);
        
        .wins { color: var(--success-color); margin-right: 8px; }
        .losses { color: var(--error-color); margin-right: 8px; }
      }
    }
    
    .opponent-profit {
      font-size: 18px;
      font-weight: 700;
      
      &.positive { color: var(--success-color); }
      &.negative { color: var(--error-color); }
    }
  }
}

// 走势图
.trend-chart {
  height: 250px;
}

// 最近比赛
.recent-list {
  .recent-item {
    padding: 14px 0;
    border-bottom: 1px solid var(--border-color);
    
    &:last-child {
      border-bottom: none;
    }
    
    .match-main {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    
    .match-info {
      .opponent {
        display: block;
        font-weight: 600;
        color: var(--text-color);
      }
      
      .date {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
    
    .match-result {
      font-size: 16px;
      font-weight: 700;
      
      &.win { color: var(--success-color); }
      &.lose { color: var(--error-color); }
      &.draw { color: var(--text-secondary); }
    }
    
    // 赢球数图标展示
    .balls-visual {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 10px;
      padding: 10px 12px;
      
      .balls-row {
        display: flex;
        align-items: center;
        gap: 8px;
        
        &:first-child {
          margin-bottom: 6px;
        }
        
        .label {
          width: 20px;
          font-size: 12px;
          color: var(--text-secondary);
          text-align: center;
        }
        
        .balls-icons {
          flex: 1;
          display: flex;
          gap: 3px;
          
          .ball-icon {
            font-size: 10px;
            line-height: 1;
            
            &.win {
              color: var(--success-color);
            }
            
            &.lose {
              color: var(--error-color);
            }
          }
          
          .no-balls {
            color: var(--text-secondary);
            font-size: 12px;
          }
        }
        
        .count {
          min-width: 24px;
          text-align: right;
          font-size: 14px;
          font-weight: 600;
          color: var(--text-color);
        }
      }
      
      .player-balls .count {
        color: var(--success-color);
      }
      
      .opponent-balls .count {
        color: var(--error-color);
      }
    }
  }
}

.empty-tip {
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
  font-size: 14px;
}

// 响应式
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .profit-display .value {
    font-size: 32px;
  }
}
</style>
