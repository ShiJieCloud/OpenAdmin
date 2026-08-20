import type { IMenuItem } from '@/types/modules/menu'

/**
 * 嵌套结构静态菜单配置
 * 全系统通用固定菜单，所有登录用户默认挂载，不走后端接口返回
 * @field children 嵌套子菜单，运行时会自动扁平化并回填 parent_id
 */
const nestedStaticMenuList: (IMenuItem & { children?: IMenuItem[] })[] = [
  {
    id: 10001,
    name: 'Dashboard',
    path: '/dashboard',
    label: '首页',
    icon: 'iconamoon:home',
    sort: 0,
    component: 'dashboard/index',
    type: 1,
    is_hidden: 0,
    is_frame: 0,
    status: 0,
  },
  {
    id: 10002,
    name: 'AiChat',
    path: '/ai-chat',
    label: 'AI 助手',
    icon: 'solar:chat-round-line-broken',
    sort: 1,
    component: 'aichat/index',
    type: 1,
    is_hidden: 0,
    is_frame: 0,
    status: 0,
  },
  {
    id: 10003,
    name: 'About',
    label: '关于',
    icon: 'solar:info-square-broken',
    path: '/about',
    component: 'about/index',
    sort: 99,
    type: 1,
    is_hidden: 0,
    is_frame: 0,
    status: 0,
  }
]

/**
 * 递归将嵌套树形菜单扁平化，自动赋值 parent_id 父子关联
 * @param menuList 原始嵌套菜单数组
 * @param parentId 当前层级父菜单ID，默认顶层父ID=0
 * @returns 一维扁平化菜单数组，结构对齐后端菜单数据格式
 */
function flattenNestedMenu(
  menuList: (IMenuItem & { children?: IMenuItem[] })[],
  parentId: number = 0
): IMenuItem[] {
  const flatResult: IMenuItem[] = []

  for (const menuItem of menuList) {
    // 剔除children字段，注入父级ID
    const { children, ...menuInfo } = menuItem
    flatResult.push({
      ...menuInfo,
      parent_id: parentId,
      children: []
    })

    // 存在子菜单则递归处理，绑定当前菜单ID为子菜单父ID
    if (Array.isArray(children) && children.length > 0) {
      flatResult.push(...flattenNestedMenu(children, menuItem.id))
    }
  }

  return flatResult
}

/**
 * 对外导出扁平化静态菜单
 * 格式和后端下发菜单结构完全一致，鉴权、菜单渲染逻辑可以复用同一套处理逻辑
 */
export const staticMenuList: IMenuItem[] = flattenNestedMenu(nestedStaticMenuList)
