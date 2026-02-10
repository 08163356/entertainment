<template>
  <div class="home-page">
    <header class="header">
      <h1>娱乐工具集</h1>
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
          <div class="card-glow"></div>
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
    
    <footer class="footer">
      <p>© 2024 Entertainment Tools</p>
    </footer>
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
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 60px;
  
  h1 {
    font-size: 32px;
    color: var(--text-color);
    font-weight: 800;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }
}

.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.tool-card {
  position: relative;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--card-border);
  border-radius: 24px;
  padding: 40px 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
    pointer-events: none;
  }
  
  .card-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, var(--primary-light) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.4s;
    pointer-events: none;
  }
  
  &:hover:not(.disabled) {
    transform: translateY(-8px) scale(1.02);
    border-color: var(--primary-color);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), 0 0 40px var(--primary-light);
    
    .card-glow {
      opacity: 0.3;
    }
    
    .tool-icon {
      transform: scale(1.1);
    }
  }
  
  &.disabled {
    opacity: 0.4;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
    }
  }
  
  .tool-icon {
    font-size: 72px;
    margin-bottom: 20px;
    transition: transform 0.3s;
    filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.3));
  }
  
  h3 {
    font-size: 24px;
    margin-bottom: 8px;
    color: var(--text-color);
    font-weight: 700;
  }
  
  p {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;
  }
}

.footer {
  text-align: center;
  padding: 40px 20px;
  
  p {
    color: var(--text-secondary);
    font-size: 12px;
    opacity: 0.6;
  }
}

@media (max-width: 768px) {
  .header {
    margin-bottom: 40px;
    
    h1 {
      font-size: 24px;
    }
  }
  
  .tool-grid {
    grid-template-columns: 1fr;
  }
  
  .tool-card {
    padding: 32px 24px;
    
    .tool-icon {
      font-size: 56px;
    }
    
    h3 {
      font-size: 20px;
    }
  }
}
</style>
