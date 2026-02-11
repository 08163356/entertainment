import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '娱乐工具集' }
  },
  // 台球模块
  {
    path: '/billiards',
    name: 'Billiards',
    component: () => import('@/views/billiards/Index.vue'),
    meta: { title: '台球记分' }
  },
  {
    path: '/billiards/room/:roomId',
    name: 'BilliardsRoom',
    component: () => import('@/views/billiards/Room.vue'),
    meta: { title: '比赛进行中' }
  },
  {
    path: '/billiards/history',
    name: 'BilliardsHistory',
    component: () => import('@/views/billiards/History.vue'),
    meta: { title: '历史记录' }
  },
  {
    path: '/billiards/player/:name',
    name: 'PlayerStats',
    component: () => import('@/views/billiards/PlayerStats.vue'),
    meta: { title: '玩家统计' }
  },
  // 投篮模块
  {
    path: '/basketball',
    name: 'Basketball',
    component: () => import('@/views/basketball/Index.vue'),
    meta: { title: '投篮记分' }
  },
  {
    path: '/basketball/room/:roomId',
    name: 'BasketballRoom',
    component: () => import('@/views/basketball/Room.vue'),
    meta: { title: '投篮比赛' }
  },
  {
    path: '/basketball/practice',
    name: 'BasketballPractice',
    component: () => import('@/views/basketball/Practice.vue'),
    meta: { title: '个人练习' }
  },
  {
    path: '/basketball/history',
    name: 'BasketballHistory',
    component: () => import('@/views/basketball/History.vue'),
    meta: { title: '投篮历史' }
  },
  {
    path: '/basketball/player/:name',
    name: 'BasketballPlayerStats',
    component: () => import('@/views/basketball/PlayerStats.vue'),
    meta: { title: '玩家战绩' }
  }
]

const router = createRouter({
  history: createWebHistory('/entertainment/'),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = (to.meta.title as string) || '娱乐工具集'
  next()
})

export default router
