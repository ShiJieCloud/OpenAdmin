import type { RouteLocationNormalized } from 'vue-router'

/**
 * 全局后置钩子
 * 在路由跳转完成后执行，不影响导航本身
 * 常用于页面统计、日志记录、页面滚动等
 */
export const afterEach = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized
): void => {
  // 记录导航完成日志
  console.log("全局后置钩子 afterEach")

  // 页面滚动到顶部
  // window.scrollTo({ top: 0, behavior: 'smooth' })
}

/**
 * 全局解析守卫
 * 在所有组件内守卫和异步路由组件被解析之后执行
 */
export const beforeResolve = async (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized
): Promise<boolean | RouteLocationNormalized | undefined> => {
  // 可以在这里处理一些需要等待异步操作完成的逻辑
  // 例如：获取用户信息、加载必要的配置等
   console.log("全局解析守卫 beforeResolve")

  return true
}

/**
 * 路由错误处理
 * 捕获导航过程中的错误
 */
export const onError = (error: Error): void => {
  console.error("全局错误处理 onError", error)
}
