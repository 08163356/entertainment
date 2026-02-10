<template>
  <div class="history-page">
    <header class="header">
      <t-button variant="text" @click="router.push('/billiards')">
        <t-icon name="chevron-left" /> 返回
      </t-button>
      <h1>历史记录</h1>
      <div></div>
    </header>

    <main class="main-content">
      <t-loading :loading="loading">
        <div v-if="matches.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
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
              <t-tag size="small" variant="outline">{{ getGameTypeLabel(match.gameType) }}</t-tag>
            </div>
            
            <div class="match-players">
              <div class="player" :class="{ winner: match.settlement.winner === match.players[0] }">
                <span class="name">{{ match.players[0] }}</span>
                <div class="stats">
                  <span class="wins">{{ getPlayerWins(match, match.players[0]) }}局</span>
                  <span class="balls">{{ getPlayerBalls(match, match.players[0]) }}球</span>
                </div>
              </div>
              <div class="score-badge">
                {{ match.settlement.score }}
              </div>
              <div class="player" :class="{ winner: match.settlement.winner === match.players[1] }">
                <span class="name">{{ match.players[1] }}</span>
                <div class="stats">
                  <span class="wins">{{ getPlayerWins(match, match.players[1]) }}局</span>
                  <span class="balls">{{ getPlayerBalls(match, match.players[1]) }}球</span>
                </div>
              </div>
            </div>
            
            <div class="match-settlement" v-if="match.settlement.winner">
              <span class="loser">{{ match.settlement.loser }}</span>
              <span class="arrow">→</span>
              <span class="amount">¥{{ match.settlement.amount }}</span>
              <span class="arrow">→</span>
              <span class="winner">{{ match.settlement.winner }}</span>
            </div>
            <div class="match-settlement draw" v-else>
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
import { historyApi } from '@/services/api'
import type { MatchRecord } from '@/types/billiards'
import { GAME_TYPES } from '@/types/billiards'

const router = useRouter()

const loading = ref(false)
const matches = ref<MatchRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 10

async function loadMatches() {
  loading.value = true
  try {
    const result = await historyApi.getMatches({
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

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getGameTypeLabel(type: string) {
  return GAME_TYPES.find(t => t.value === type)?.label || type
}

function getPlayerWins(match: MatchRecord, playerName: string) {
  return match.rounds.filter(r => r.winner === playerName).length
}

function getPlayerBalls(match: MatchRecord, playerName: string) {
  return match.rounds
    .filter(r => r.winner === playerName)
    .reduce((sum, r) => sum + r.ballsWon, 0)
}

onMounted(() => {
  loadMatches()
})
</script>

<style lang="scss" scoped>
.history-page {
  min-height: 100vh;
  padding: 20px;
  position: relative;
  
  // 历史记录页面背景
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('@/assets/历史记录页面装饰.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.7;
    z-index: -1;
    pointer-events: none;
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
    font-weight: 700;
  }
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  
  .empty-img {
    width: 180px;
    height: auto;
    margin-bottom: 16px;
    opacity: 0.8;
    border-radius: 12px;
  }
  
  p {
    font-size: 16px;
  }
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.match-card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
  }
  
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
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .player {
      flex: 1;
      text-align: center;
      
      &.winner .name {
        color: var(--success-color);
      }
      
      .name {
        display: block;
        font-size: 18px;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 4px;
      }
      
      .stats {
        font-size: 12px;
        color: var(--text-secondary);
        
        span {
          margin: 0 4px;
        }
      }
    }
    
    .score-badge {
      padding: 8px 20px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      font-size: 24px;
      font-weight: 800;
      color: var(--text-color);
      letter-spacing: 2px;
    }
  }
  
  .match-settlement {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    font-size: 14px;
    
    .loser { 
      color: var(--error-color); 
      font-weight: 600;
    }
    .winner { 
      color: var(--success-color); 
      font-weight: 600;
    }
    .amount { 
      font-size: 18px;
      font-weight: 700;
      color: var(--warning-color);
    }
    .arrow {
      color: var(--text-secondary);
    }
    
    &.draw {
      color: var(--text-secondary);
    }
  }
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

@media (max-width: 480px) {
  .match-card .match-players {
    flex-direction: column;
    gap: 12px;
    
    .score-badge {
      order: -1;
    }
    
    .player {
      width: 100%;
    }
  }
}
</style>
