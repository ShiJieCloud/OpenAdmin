import type { Router } from 'vue-router'
import { beforeEach } from './global/beforeEach'
import { afterEach, beforeResolve, onError } from './global/afterEach'

/**
 * 路由守卫配置
 * @param router - Vue Router 实例
 */
export const setupRouterGuard = (router: Router): void => {
  // 注册全局前置守卫
  router.beforeEach(beforeEach)

  // 注册全局解析守卫
  router.beforeResolve(beforeResolve)

  // 注册全局后置钩子
  router.afterEach(afterEach)

  // 注册路由错误处理
  router.onError(onError)
}
