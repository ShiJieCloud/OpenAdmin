import type { RouteLocationNormalized, RouteLocationRaw } from 'vue-router'

/**
 * 获取用户登录状态
 * 从 localStorage 中获取 token 判断是否已登录
 */
const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('token')
  return !!token
}

/**
 * 路由白名单
 * 这些路由不需要登录即可访问
 */
const whiteList: string[] = ['/login', '/register']

/**
 * 设置页面标题
 */
const setPageTitle = (title?: string): void => {
  if (title) {
    document.title = `${title} - OpenAdmin`
  } else {
    document.title = 'OpenAdmin'
  }
}

/**
 * 全局前置守卫
 * Vue Router 4 推荐使用返回值方式
 * @returns true | false | RouteLocationRaw | undefined
 */
export const beforeEach = async (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized
): Promise<boolean | RouteLocationRaw | undefined> => {

  // 记录导航日志
  console.log("全局前置守卫 beforeEach")

  return true

}
