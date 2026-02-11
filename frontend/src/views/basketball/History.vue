<template>
  <div class="history-page">
    <header class="header">
      <t-button variant="text" @click="router.push('/basketball')">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <h1>🏀 投篮历史</h1>
      <div></div>
    </header>

    <main class="main-content">
      <!-- 历史记录横幅 -->
      <div class="history-banner">
        <img src="@/assets/basketball/history-banner.png" alt="history" class="banner-img" />
      </div>
      
      <t-loading :loading="loading">
        <div v-if="matches.length === 0" class="empty-state">
          <img src="@/assets/basketball/empty-state.png" alt="empty" class="empty-img" />
          <p>暂无比赛记录</p>
        </div>
        
        <div v-else class="match-list">
          <div 
            v-for="match in matches" 
            :key="match.id"
            class="match-card"
          >
            <div class="match-header">
              <span class="match-date">{{ formatDate(match.settledAt) }}</span>
              <t-tag size="small" variant="outline">
                {{ match.rounds.length }}轮 | 每轮{{ match.ballsPerRound }}球
              </t-tag>
            </div>
            
            <div class="match-players">
              <div 
                v-for="(player, index) in getPlayerStats(match)" 
                :key="player.name"
                class="player-stat"
                :class="{ winner: player.name === match.settlement?.winner }"
              >
                <div class="player-avatar" :class="`player-${(index % 6) + 1}`">
                  {{ player.name[0] }}
                </div>
                <div class="player-info">
                  <span class="name">{{ player.name }}</span>
                  <span class="stats">{{ player.made }}球 | {{ player.accuracy }}%</span>
                </div>
                <span class="winner-badge" v-if="player.name === match.settlement?.winner">🏆</span>
              </div>
            </div>
            
            <div class="match-settlement" v-if="match.settlement && match.settlement.transfers.length > 0">
              <div class="settlement-title">转账明细</div>
              <div 
                v-for="(transfer, idx) in match.settlement.transfers" 
                :key="idx"
                class="transfer-row"
              >
                <span class="from">{{ transfer.fromPlayer }}</span>
                <span class="arrow">→</span>
                <span class="amount">¥{{ transfer.amount }}</span>
                <span class="arrow">→</span>
                <span class="to">{{ transfer.toPlayer }}</span>
              </div>
            </div>
            <div class="match-settlement draw" v-else-if="match.settlement">
              <span>平局</span>
            </div>
          </div>
        </div>
        
        <div class="pagination" v-if="total > pageSize">
          <t-pagination
            v-model:current="currentPage"
            :total="total"
            :page-size="pageSize"
            @current-change="loadMatches"
          />
        </div>
      </t-loading>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { basketballHistoryApi } from '@/services/basketballApi'
import type { MatchRecord } from '@/types/basketball'

const router = useRouter()

const loading = ref(false)
const matches = ref<MatchRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 10

async function loadMatches() {
  loading.value = true
  try {
    const result = await basketballHistoryApi.getMatches({
      limit: pageSize,
      offset: (currentPage.value - 1) * pageSize
    })
    matches.value = result.matches
    total.value = result.total
  } catch (e) {
    console.error('加载历史记录失败', e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getPlayerStats(match: MatchRecord) {
  const stats: Record<string, { name: string; made: number; total: number; accuracy: number }> = {}
  
  for (const player of match.players) {
    stats[player] = { name: player, made: 0, total: 0, accuracy: 0 }
  }
  
  for (const round of match.rounds) {
    for (const score of round.scores) {
      if (stats[score.player]) {
        stats[score.player].made += score.made
        stats[score.player].total += score.total
      }
    }
  }
  
  const result = Object.values(stats).map(s => ({
    ...s,
    accuracy: s.total > 0 ? Math.round((s.made / s.total) * 100 * 10) / 10 : 0
  }))
  
  return result.sort((a, b) => b.made - a.made)
}

onMounted(() => {
  loadMatches()
})
</script>

<style lang="scss" scoped>
.history-page {
  min-height: 100vh;
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
  margin-bottom: 24px;
  
  h1 {
    font-size: 22px;
    color: var(--text-color);
  }
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
}

.history-banner {
  margin-bottom: 20px;
  border-radius: 16px;
  overflow: hidden;
  
  .banner-img {
    width: 100%;
    height: auto;
    max-height: 120px;
    object-fit: cover;
    opacity: 0.85;
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  
  .empty-img {
    width: 150px;
    height: auto;
    opacity: 0.8;
    margin-bottom: 16px;
  }
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.match-card {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 20px;
  
  .match-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .match-date {
      color: var(--text-secondary);
      font-size: 13px;
    }
  }
  
  .match-players {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
    
    .player-stat {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.03);
      
      &.winner {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
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
        
        &.player-1 { background: linear-gradient(135deg, #f59e0b, #d97706); }
        &.player-2 { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
        &.player-3 { background: linear-gradient(135deg, #10b981, #059669); }
        &.player-4 { background: linear-gradient(135deg, #ec4899, #db2777); }
        &.player-5 { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
        &.player-6 { background: linear-gradient(135deg, #ef4444, #dc2626); }
      }
      
      .player-info {
        flex: 1;
        
        .name {
          display: block;
          font-weight: 600;
          color: var(--text-color);
        }
        
        .stats {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
      
      .winner-badge {
        font-size: 20px;
      }
    }
  }
  
  .match-settlement {
    padding: 12px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    
    .settlement-title {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .transfer-row {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 0;
      font-size: 14px;
      
      .from {
        color: var(--error-color);
        font-weight: 600;
      }
      
      .to {
        color: var(--success-color);
        font-weight: 600;
      }
      
      .amount {
        font-weight: 700;
        color: #f59e0b;
      }
      
      .arrow {
        color: var(--text-secondary);
      }
    }
    
    &.draw {
      text-align: center;
      color: var(--text-secondary);
    }
  }
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
