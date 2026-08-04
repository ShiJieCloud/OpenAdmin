import type { RouteRecordRaw } from 'vue-router'
import Layout from '@/layout/index.vue'

/** 静态路由：仅包含独立页面和 Layout 布局壳 */
export const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    name: 'Layout',
    component: Layout,
    redirect: '/dashboard',
    children: []
  }
]
