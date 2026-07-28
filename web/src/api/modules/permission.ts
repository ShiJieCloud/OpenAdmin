import type {
  IPermissionInfo,
  IPermissionListQueryParam,
  PermissionCreateRequest,
  PermissionUpdateRequest
} from '@/types/modules/permission'
import type { IPageResult } from '@/types/common/api'
import request from '@/utils/request'


/**
 * 获取所有权限列表
 * @description 获取系统中所有权限（不分页）
 * @returns 权限列表
 */
export const fetchSystemPermissionList = (): Promise<IPermissionInfo[]> => {
  return request.get('/permission')
}

/**
 * 分页查询权限列表
 * @description 根据查询参数分页获取权限列表
 * @param params 查询参数
 * @returns 分页权限列表
 */
export const getPermissionList = (params: IPermissionListQueryParam): Promise<IPageResult<IPermissionInfo>> => {
  return request.post('/permission/list', params)
}

/**
 * 创建权限
 * @description 创建新的权限
 * @param data 创建权限请求数据
 * @returns 创建后的权限信息
 */
export const createPermission = (data: PermissionCreateRequest): Promise<IPermissionInfo> => {
  return request.post('/permission', data)
}

/**
 * 更新权限
 * @description 更新权限信息
 * @param data 更新权限请求数据
 * @returns 更新后的权限信息
 */
export const updatePermission = (data: PermissionUpdateRequest): Promise<IPermissionInfo> => {
  return request.put('/permission', data)
}

/**
 * 删除权限
 * @description 删除指定权限
 * @param permId 权限ID
 * @returns 删除结果
 */
export const deletePermission = (permId: number): Promise<void> => {
  return request.deleteRequest(`/permission/${permId}`)
}
