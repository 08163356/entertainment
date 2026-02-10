<template>
  <div class="home-page">
    <header class="header">
      <h1>🎱 娱乐工具集</h1>
      <t-dropdown :options="themeOptions" @click="handleThemeChange">
        <t-button variant="text" shape="circle">
          <template #icon><t-icon name="palette" /></template>
        </t-button>
      </t-dropdown>
    </header>

    <main class="main-content">
      <div class="tool-grid">
        <div class="tool-card" @click="router.push('/billiards')">
          <div class="tool-icon">🎱</div>
          <h3>台球记分</h3>
          <p>中式黑八计分板，支持实时同步</p>
        </div>
        
        <div class="tool-card disabled">
          <div class="tool-icon">🎲</div>
          <h3>桌游工具</h3>
          <p>即将上线</p>
        </div>
        
        <div class="tool-card disabled">
          <div class="tool-icon">🎯</div>
          <h3>更多工具</h3>
          <p>敬请期待</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const themeStore = useThemeStore()

const themeOptions = computed(() => 
  themeStore.themes.map(t => ({
    content: t.label,
    value: t.value
  }))
)

function handleThemeChange(data: { value: string }) {
  themeStore.setTheme(data.value as any)
}
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  
  h1 {
    font-size: 28px;
    color: var(--text-color);
  }
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.tool-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  
  &:hover:not(.disabled) {
    transform: translateY(-4px);
    border-color: var(--primary-color);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
  
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .tool-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }
  
  h3 {
    font-size: 22px;
    margin-bottom: 8px;
    color: var(--text-color);
  }
  
  p {
    color: var(--text-secondary);
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 22px;
  }
  
  .tool-card {
    padding: 24px;
    
    .tool-icon {
      font-size: 48px;
    }
  }
}
</style>
