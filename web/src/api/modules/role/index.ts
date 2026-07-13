import request from '@/utils/request'
import type { IRoleInfo, RoleCreateRequest, RoleUpdateRequest, RoleUpdateStatusRequest, IRoleListQueryParam, IPageResult, IRoleAssignPermsRequest, IRolePermission } from '@/types'

export const getRoleInfo = (role_id: number): Promise<IRoleInfo> => {
  return request.get(`/role/${role_id}`)
}

export const getRoleList = (query: IRoleListQueryParam): Promise<IPageResult<IRoleInfo>> => {
  // 暂不调用接口，直接返回模拟数据
  return request.post('/role/list', query)
}

export const createRole = (req: RoleCreateRequest): Promise<IRoleInfo> => {
  return request.post('/role', req)
}

export const updateRole = (req: RoleUpdateRequest): Promise<IRoleInfo> => {
  return request.put('/role', req)
}

export const deleteRole = (role_id: number): Promise<void> => {
  return request.deleteRequest(`/role/${role_id}`)
}

export const assignRolePermissions = (role_id: number, req: IRoleAssignPermsRequest): Promise<void> => {
  return request.post(`/role/${role_id}/permissions`, req)
}

export const getRolePermissions = (role_id: number): Promise<IRolePermission[]> => {
  return request.get(`/role/${role_id}/permissions`)
}