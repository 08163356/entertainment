import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeType = 'light' | 'dark' | 'billiard-green' | 'royal-blue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref<ThemeType>(
    (localStorage.getItem('theme') as ThemeType) || 'billiard-green'
  )

  const themes: { value: ThemeType; label: string }[] = [
    { value: 'light', label: '浅色' },
    { value: 'dark', label: '深色' },
    { value: 'billiard-green', label: '台球绿' },
    { value: 'royal-blue', label: '皇家蓝' }
  ]

  function setTheme(theme: ThemeType) {
    currentTheme.value = theme
    localStorage.setItem('theme', theme)
  }

  watch(currentTheme, (newTheme) => {
    document.documentElement.setAttribute('data-theme', newTheme)
  }, { immediate: true })

  return {
    currentTheme,
    themes,
    setTheme
  }
})
