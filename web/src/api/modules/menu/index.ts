import type { IMenuItem, IMenuCreateRequest, IMenuUpdateRequest } from "@/types"
import request from '@/utils/request'

// 获取用户菜单列表
export const getCurrentUserMenuList = (): Promise<IMenuItem[]> => {
  return request.get('/menu/current/list')
}

// 获取系统菜单树
export const getSystemMenuTree = (): Promise<IMenuItem[]> => {
  return request.get('/menu/tree')
}

// 创建菜单
export const createMenu = (data: IMenuCreateRequest): Promise<IMenuItem> => {
  return request.post('/menu', data)
}

// 更新菜单
export const updateMenu = (menuId: number, data: IMenuUpdateRequest): Promise<void> => {
  return request.put(`/menu/${menuId}`, data)
}

// 更新菜单状态
export const updateMenuStatus = (menuId: number, status: number): Promise<void> => {
  return request.put(`/menu/status/${menuId}`, { status })
}

// 删除菜单
export const deleteMenu = (menuId: number): Promise<void> => {
  return request.deleteRequest(`/menu/${menuId}`)
}

// 批量删除菜单
export const batchDeleteMenus = (menuIds: number[]): Promise<void> => {
  return request.deleteRequest('/menu/batch', { menu_ids: menuIds })
}

// 获取菜单详情
export const getMenuDetail = (menuId: number): Promise<IMenuItem> => {
  return request.get(`/menu/${menuId}`)
}