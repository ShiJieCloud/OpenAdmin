/**
 * 菜单项类型定义
 */
export interface IMenuItem {
    id: number
    name: string
    label: string
    icon?: string
    path?: string
    component?: string
    parent_id?: number
    children?: IMenuItem[]
}