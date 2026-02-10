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
              <t-tag size="small">{{ getGameTypeLabel(match.gameType) }}</t-tag>
            </div>
            
            <div class="match-players">
              <div class="player" :class="{ winner: match.settlement.winner === match.players[0] }">
                <span class="name">{{ match.players[0] }}</span>
                <span class="wins">{{ getPlayerWins(match, match.players[0]) }}局</span>
                <span class="balls">{{ getPlayerBalls(match, match.players[0]) }}球</span>
              </div>
              <div class="vs">VS</div>
              <div class="player" :class="{ winner: match.settlement.winner === match.players[1] }">
                <span class="name">{{ match.players[1] }}</span>
                <span class="wins">{{ getPlayerWins(match, match.players[1]) }}局</span>
                <span class="balls">{{ getPlayerBalls(match, match.players[1]) }}球</span>
              </div>
            </div>
            
            <div class="match-result">
              <div class="score">{{ match.settlement.score }}</div>
              <div class="settlement" v-if="match.settlement.winner">
                <span class="loser">{{ match.settlement.loser }}</span>
                支付
                <span class="amount">¥{{ match.settlement.amount }}</span>
                给
                <span class="winner">{{ match.settlement.winner }}</span>
              </div>
              <div class="settlement draw" v-else>平局</div>
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
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  
  .empty-icon {
    font-size: 64px;
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
  border-radius: 16px;
  padding: 20px;
  
  .match-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .match-date {
      color: var(--text-secondary);
      font-size: 14px;
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
      
      &.winner {
        .name {
          color: var(--success-color);
        }
      }
      
      .name {
        display: block;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 4px;
      }
      
      .wins, .balls {
        font-size: 14px;
        color: var(--text-secondary);
        margin-right: 8px;
      }
    }
    
    .vs {
      padding: 0 20px;
      color: var(--text-secondary);
      font-weight: bold;
    }
  }
  
  .match-result {
    text-align: center;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
    
    .score {
      font-size: 28px;
      font-weight: bold;
      margin-bottom: 8px;
    }
    
    .settlement {
      font-size: 14px;
      
      .loser { color: var(--error-color); }
      .winner { color: var(--success-color); }
      .amount { 
        font-weight: bold;
        color: var(--warning-color);
      }
      
      &.draw {
        color: var(--text-secondary);
      }
    }
  }
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
