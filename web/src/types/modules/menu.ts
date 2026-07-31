/**
 * 菜单项类型定义
 */
export interface IMenuItem {
    id: number
    name: string
    label: string
    description?: string
    icon?: string
    path?: string
    component?: string
    parent_id?: number
    children?: IMenuItem[]
}

/**
 * 聚合式菜单组件（MegaMenu）
 * @description 适用于后台系统的多级聚合菜单，支持 hover 弹窗、子菜单搜索
 */
export interface MegaMenuProps {
  /**
   * 菜单数据源（递归结构）
   */
  treeMenuList?: IMenuItem[];
  /**
   * 当前激活的根菜单 ID
   */
  currentRootMenuId?: number | string;
  /**
   * 当前激活的子菜单 ID
   */
  currentSubMenuId?: number | string;
}

/**
 * 组件事件
 */
export type MegaMenuEmits = {
  /**
   * 根菜单点击事件
   * @param menuId 点击的根菜单 ID（字符串格式）
   */
  'root-click': [menuId: string];
  /**
   * 子菜单点击事件
   * @param menuId 点击的子菜单 ID（字符串格式）
   */
  'item-click': [menuId: string];
};