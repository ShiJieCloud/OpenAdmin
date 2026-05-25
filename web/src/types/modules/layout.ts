/**
 * 布局模式常量定义
 * 用于统一管理所有布局类型，避免魔法字符串，保证类型安全
 */
export const LAYOUT = {
  /** 经典布局：左侧侧边栏 + 右侧内容 */
  CLASSIC: 'classic',
  /** 混合布局：顶部导航 + 侧边子菜单 */
  MIX: 'mix',
  /** 分栏布局：双列菜单模式 */
  COLUMN: 'column',
  /** 超级布局：聚合式菜单 */
  MEGA: 'mega',
} as const

/**
 * 布局类型
 * 从 LAYOUT 自动推导的联合类型：'classic' | 'mix' | 'column' | 'mega'
 * 用于约束变量、状态、函数参数的类型
 */
export type LayoutMode = (typeof LAYOUT)[keyof typeof LAYOUT]

/**
 * 布局配置列表（可直接用于 v-for 循环渲染）
 * 包含值、显示名称、描述说明，支持下拉菜单、切换面板、设置项使用
 */
export const layoutList = [
  {
    value: LAYOUT.CLASSIC,
    label: '经典布局',
    desc: '左侧菜单，右侧内容',
  },
  {
    value: LAYOUT.MIX,
    label: '混合布局',
    desc: '顶部主菜单，侧边子菜单',
  },
  {
    value: LAYOUT.COLUMN,
    label: '分栏布局',
    desc: '双列菜单，左侧主菜单，右侧次级菜单',
  },
  {
    value: LAYOUT.MEGA,
    label: '超级菜单布局',
    desc: '聚合式菜单',
  },
] as const