/**
 * 页签项
 */
export interface ITabItem {
  id: number
  path: string
  name?: string
  icon?: string
  title: string
  affix?: boolean
}
