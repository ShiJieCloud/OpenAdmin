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
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '首页'
        },
      },
      {
        path: '/system',
        name: 'System',
        redirect: '/system/user',
        meta: {
          title: '系统管理'
        },
        children: [
          {
            path: '/system/user',
            name: 'User',
            redirect: '/system/user/online',
            meta: {
              title: '用户管理'
            },
            children: [
              {
                path: '/system/user/online',
                name: 'UserOnline',
                component: () => import('@/views/system/user/OnlineUser.vue'),
                meta: {
                  title: '在线用户'
                },
              }
            ]
          }
        ]
      },
      {
        path: '/data',
        name: 'Data',
        component: () => import('@/views/data/index.vue'),
        meta: {
          title: '数据管理'
        },
      }
    ]
  },
]
