/**
 * 动态路由辅助工具
 * 负责从菜单列表生成并注册Vue Router动态路由
 * @module dynamicRouterHelper
 */
import type { RouteRecordRaw, RouteRecordName } from 'vue-router'
import type { IMenuItem } from '@/types/modules/menu'
import router from '@/router'

// 懒加载所有视图组件
const viewModules = import.meta.glob('@/views/**/*.vue')

/**
 * 加载并注册动态路由
 * @param menuList 菜单列表数据
 */
export function loadDynamicRouter(menuList: IMenuItem[]): void {
  if (!Array.isArray(menuList) || !menuList.length) {
    console.warn('动态路由加载：菜单列表为空，跳过注册')
    return
  }

  try {
    registerRoutes(menuList)
  } catch (err) {
    console.error('动态路由注册异常：', err)
  }
}

/**
 * 批量注册动态路由
 * 过滤无效菜单后，挂载到指定父路由下，内部依托递归生成树形嵌套路由
 * @param menus 后端返回的菜单列表数据
 * @param parentName 父路由名称，默认挂载到 Layout 根布局路由
 */
export function registerRoutes(
  menus: IMenuItem[],
  parentName: RouteRecordName = 'Layout'
): void {
  // 过滤无效菜单项：必须拥有路由名称，且存在路由路径或子菜单
  const validMenus = menus.filter(item => item?.name && (item.path || item.children?.length))

  // 遍历有效菜单，逐个完成路由注册
  validMenus.forEach(menu => {
    try {
      // 将当前菜单生成的路由，挂载到指定父路由下
      router.addRoute(parentName as string, createRouteFromMenu(menu))
    } catch (err) {
      // 捕获异常，避免单条路由失败影响整体，大概率为路由重复注册
      console.warn(`路由 [${menu.name}] 注册失败，可能已存在`, err)
    }
  })
}

/**
 * 根据菜单项生成标准路由配置
 * 递归处理子菜单，构建嵌套路由结构，适配 Vue Router 路由规则
 * @param menu 后端返回的单条菜单项原始数据
 * @returns RouteRecordRaw 标准路由配置对象
 */
function createRouteFromMenu(menu: IMenuItem): RouteRecordRaw {
  // 解构菜单项字段，并设置默认值，避免空值报错
  const { id, name, path = '', component = '', label = '', icon = '', children = [] } = menu

  // 匹配预加载的组件模块，component为后端返回的@/views路径
  const routeComponent = viewModules[component] || ''

  // 构建基础路由对象
  const route: RouteRecordRaw = {
    name,
    path,
    component: routeComponent,
    meta: { title: label, icon, id: id }, // 路由元信息：页面标题、菜单图标
    children: []
  }

  // 过滤无效子菜单（仅保留包含路由路径的有效项）
  const validChildren = children.filter(c => c?.path)
  if (validChildren.length) {
    // 父路由默认重定向到第一个有效子路由
    route.redirect = validChildren[0].path
    // 递归生成子路由，构建树形嵌套结构
    route.children = validChildren.map(createRouteFromMenu)
  }

  return route
}