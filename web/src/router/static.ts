import type { RouteRecordRaw } from 'vue-router'
import Layout from '@/layout/index.vue'

export const staticRoutes: RouteRecordRaw[] = [

  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录'
    }
  },
  {
    path: '/',
    redirect: '/dashboard',
    component: Layout,
    name: 'Layout',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '首页'
        },
      },
    ]
  },
]
