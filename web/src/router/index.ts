import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuard } from './guard'
import { staticRoutes } from './static'

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes
})

// 配置路由守卫
setupRouterGuard(router)

export default router
