<template>
  <t-config-provider :global-config="globalConfig">
    <div class="app-container" :class="themeClass">
      <router-view />
    </div>
  </t-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const themeClass = computed(() => `theme-${themeStore.currentTheme}`)

const globalConfig = {
  classPrefix: 't'
}
</script>

<style lang="scss">
.app-container {
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
}
</style>
