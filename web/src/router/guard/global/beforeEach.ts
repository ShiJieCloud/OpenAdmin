/**
 * @file 全局路由前置守卫
 * @desc 统一处理登录鉴权、动态路由加载、页面跳转拦截逻辑、页面标题设置
 * @author sjzhao
 * @date 2026-06-08 16:00:00
 */
import type { RouteLocationNormalized, NavigationGuardNext } from "vue-router"
import { useUserStore, useMenuStore } from '@/store'
import { loadDynamicRouter } from '@/router/helper/dynamicRouterHelper'

/**
 * 设置浏览器页面标题
 * @param {RouteLocationNormalized} route - 当前目标路由对象
 * @description 拼接路由标题与系统默认标题，统一页面标题格式
 */
const setPageTitle = (route: RouteLocationNormalized) => {
  const systemTitle = import.meta.env.VITE_APP_TITLE || '企业管理系统'
  document.title = route.meta?.title ? `${route.meta.title} - ${systemTitle}` : systemTitle
}

/**
 * 全局路由前置守卫
 * @async
 * @param {RouteLocationNormalized} to - 目标路由对象
 * @param {RouteLocationNormalized} from - 当前路由对象
 * @param {NavigationGuardNext} next - 导航守卫回调函数，控制路由流转
 * @returns {Promise<void>}
 * @description
 * 业务逻辑：
 * 1. 无登录凭证则强制跳转登录页，登录页直接放行
 * 2. 已登录但未加载动态路由，则先加载路由再重定向当前页面
 * 3. 动态路由加载异常，执行登出并跳转登录页
 * 4. 所有校验通过，正常放行路由
 */
export const beforeEach = async (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
) => {
    // 获取状态管理实例
    const userStore = useUserStore()
    const menuStore = useMenuStore()
 
    // 未登录状态：拦截并跳转到登录页
    if (!userStore.accessToken) {
        return to.path === '/login' ? next() : next('/login')
    } else if (to.path === '/login') {
        // 已登录用户访问登录页：重定向到之前访问的页面
        return next('/')
    }

    // 动态路由未加载：首次登录或刷新后加载动态路由
    if (!menuStore.isRouteLoaded) {
        try {
            // 加载用户菜单
            await menuStore.loadUserMenu()

            // 根据菜单列表注册动态路由
            loadDynamicRouter(menuStore.treeMenuList)
            // 标记路由已加载，避免重复注册
            menuStore.setIsRouteLoaded(true)
            // 重新触发当前路由匹配，确保动态路由生效
            return next({ ...to, replace: true })
        } catch (err) {
            // 路由加载失败：退出登录并跳转登录页
            userStore.logout()
            return next('/login')
        }
    }

    // 设置页面标题
    setPageTitle(to)

    // 已登录且路由已加载：放行
    next()
}
