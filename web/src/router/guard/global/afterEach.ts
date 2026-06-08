import type { RouteLocationNormalized } from 'vue-router'

/**
 * 全局路由后置守卫
 * @param to 目标路由对象，即将进入的路由
 * @param from 来源路由对象，当前离开的路由
 * @returns void
 * @description 路由跳转完成后执行，统一重置页面滚动条至顶部，保证新页面从顶部开始展示
 */
export const afterEach = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
): void => {
  // 路由切换后，将页面滚动条重置到顶部
  window.scrollTo(0, 0)
}