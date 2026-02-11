<template>
  <div class="player-stats-page">
    <header class="header">
      <t-button variant="text" @click="router.push('/basketball')">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <h1>{{ playerName }} 的战绩</h1>
      <div></div>
    </header>

    <main class="main-content">
      <t-loading :loading="loading">
        <div v-if="stats" class="stats-content">
          <!-- 总览 -->
          <div class="overview-section">
            <div class="player-header">
              <div class="player-avatar player-1">
                {{ playerName[0] }}
              </div>
              <div class="player-name">{{ playerName }}</div>
            </div>
            
            <div class="stats-grid">
              <div class="stat-card">
                <div class="value">{{ stats.totalMatches }}</div>
                <div class="label">总场次</div>
              </div>
              <div class="stat-card">
                <div class="value">{{ stats.totalWins }}</div>
                <div class="label">胜场</div>
              </div>
              <div class="stat-card win-rate">
                <div class="value">{{ stats.winRate }}%</div>
                <div class="label">胜率</div>
              </div>
              <div class="stat-card">
                <div class="value">{{ stats.totalMade }}</div>
                <div class="label">总进球</div>
              </div>
              <div class="stat-card">
                <div class="value">{{ stats.avgAccuracy }}%</div>
                <div class="label">平均命中</div>
              </div>
              <div class="stat-card" :class="{ positive: stats.netAmount > 0, negative: stats.netAmount < 0 }">
                <div class="value">
                  {{ stats.netAmount >= 0 ? '+' : '' }}¥{{ stats.netAmount }}
                </div>
                <div class="label">净收益</div>
              </div>
            </div>
          </div>

          <!-- 最近比赛 -->
          <div class="action-panel" v-if="stats.recentMatches.length > 0">
            <div 
              class="panel-header"
              :class="{ active: expandedRecent }"
              @click="expandedRecent = !expandedRecent"
            >
              <div class="panel-title">
                <t-icon name="time" />
                <span>最近比赛</span>
                <t-badge :count="stats.recentMatches.length" />
              </div>
              <t-icon :name="expandedRecent ? 'chevron-up' : 'chevron-down'" class="arrow" />
            </div>
            <t-collapse-transition>
              <div class="panel-content" v-show="expandedRecent">
                <div class="match-list">
                  <div 
                    v-for="match in stats.recentMatches" 
                    :key="match.id"
                    class="match-item"
                    :class="{ win: match.settlement?.winner === playerName }"
                  >
                    <div class="match-result">
                      <span class="result-badge" :class="match.settlement?.winner === playerName ? 'win' : 'lose'">
                        {{ match.settlement?.winner === playerName ? '胜' : '负' }}
                      </span>
                    </div>
                    <div class="match-info">
                      <div class="opponents">
                        vs {{ match.players.filter(p => p !== playerName).join(', ') }}
                      </div>
                      <div class="my-stats">
                        {{ getMyStats(match).made }}球 | {{ getMyStats(match).accuracy }}%
                      </div>
                    </div>
                    <div class="match-meta">
                      <span class="date">{{ formatDate(match.settledAt) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </t-collapse-transition>
          </div>
        </div>
        
        <div v-else class="empty-state">
          <p>暂无战绩数据</p>
        </div>
      </t-loading>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { basketballPlayerApi } from '@/services/basketballApi'
import type { PlayerStats, MatchRecord } from '@/types/basketball'

const route = useRoute()
const router = useRouter()

const playerName = computed(() => decodeURIComponent(route.params.name as string))
const loading = ref(false)
const stats = ref<PlayerStats | null>(null)
const expandedRecent = ref(false)

async function loadStats() {
  loading.value = true
  try {
    stats.value = await basketballPlayerApi.getStats(playerName.value)
  } catch (e) {
    console.error('加载战绩失败', e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

function getMyStats(match: MatchRecord) {
  let made = 0
  let total = 0
  
  for (const round of match.rounds) {
    for (const score of round.scores) {
      if (score.player === playerName.value) {
        made += score.made
        total += score.total
      }
    }
  }
  
  const accuracy = total > 0 ? Math.round((made / total) * 100 * 10) / 10 : 0
  return { made, total, accuracy }
}

onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.player-stats-page {
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
    font-size: 20px;
    color: var(--text-color);
  }
}

.main-content {
  max-width: 600px;
  margin: 0 auto;
}

.overview-section {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  
  .player-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 24px;
    
    .player-avatar {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      font-weight: bold;
      color: white;
      margin-bottom: 12px;
      
      &.player-1 { background: linear-gradient(135deg, #f59e0b, #d97706); }
    }
    
    .player-name {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-color);
    }
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    
    .stat-card {
      text-align: center;
      padding: 16px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      
      .value {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-color);
      }
      
      .label {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 4px;
      }
      
      &.win-rate .value {
        color: #f59e0b;
      }
      
      &.positive .value {
        color: var(--success-color);
      }
      
      &.negative .value {
        color: var(--error-color);
      }
    }
  }
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
  
  .panel-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-color);
    
    .t-icon {
      font-size: 22px;
      color: #60a5fa;
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
  
  .match-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .match-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 16px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border-left: 4px solid transparent;
    
    &.win {
      border-color: var(--success-color);
    }
    
    .match-result {
      .result-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        
        &.win {
          background: rgba(16, 185, 129, 0.2);
          color: var(--success-color);
        }
        
        &.lose {
          background: rgba(239, 68, 68, 0.2);
          color: var(--error-color);
        }
      }
    }
    
    .match-info {
      flex: 1;
      
      .opponents {
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 4px;
      }
      
      .my-stats {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
    
    .match-meta {
      .date {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}
</style>
