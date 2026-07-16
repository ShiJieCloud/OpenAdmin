import type { IMenuItem } from "@/types"
import request from '@/utils/request'

// 获取用户菜单列表
export const getCurrentUserMenuList = (): Promise<IMenuItem[]> => {
  return request.get('/menu/current/list')
}

// 获取系统菜单树
export const getSystemMenuTree = (): Promise<IMenuItem[]> => {
  return request.get('/menu/tree')
}