import { ref } from 'vue'
import type { IMenuItem } from "@/types"

const menuList = ref<IMenuItem[]>([
  { id: 1, parent_id: 0, name: 'dashboard', label: '首页', icon: 'iconamoon:home', path: '/dashboard', component: 'dashboard/index' },
  { id: 2, parent_id: 0, name: 'system', label: '系统管理', icon: 'ep:setting', path: '/system', component: '' },
  { id: 21, parent_id: 2, name: 'user', label: '用户管理', path: '/system/user', icon: 'iconamoon:user', component: '' },
  { id: 211, parent_id: 21, name: 'user-online', label: '在线用户', path: '/system/user/online', icon: 'iconamoon:user-online', component: 'system/user/OnlineUser' },
  { id: 4, parent_id: 0, name: 'data', label: '数据统计', icon: 'ep:data-line', path: '/data', component: 'data/index' },
])

// 获取用户菜单列表
export const getCurrentUserMenuList = (): Promise<IMenuItem[]> => {
  return Promise.resolve(menuList.value)
}