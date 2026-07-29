import request from '@/utils/request'
import type {
  IUserInfo,
  IUserCreateRequest,
  IUserUpdateRequest,
  IUserUpdateStatusRequest,
  IUserResetPasswordRequest,
  IUserListQueryParam,
  IUserRoleAssignRequest,
} from '@/types/modules/user'
import type { IPageResult } from '@/types/common/api'

/**
 * 获取用户列表（分页）
 * @param params - 查询参数
 * @returns 用户分页列表
 */
export const getUserList = (params?: IUserListQueryParam): Promise<IPageResult<IUserInfo>> => {
  return request.post('/user/list', params)
}

/**
 * 获取用户详情
 * @param userId - 用户ID
 * @returns 用户信息
 */
export const getUserInfo = (userId: number): Promise<IUserInfo> => {
  return request.get(`/user/${userId}`)
}

/**
 * 创建用户
 * @param data - 创建用户请求
 * @returns 创建后的用户信息
 */
export const createUser = (data: IUserCreateRequest): Promise<IUserInfo> => {
  return request.post('/user', data)
}

/**
 * 编辑用户
 * @param data - 编辑用户请求
 * @returns 更新后的用户信息
 */
export const updateUser = (data: IUserUpdateRequest): Promise<IUserInfo> => {
  return request.put('/user', data)
}

/**
 * 修改用户状态
 * @param data - 修改用户状态请求
 */
export const updateUserStatus = (data: IUserUpdateStatusRequest): Promise<void> => {
  return request.put('/user/status', data)
}

/**
 * 重置用户密码
 * @param data - 重置密码请求
 */
export const resetUserPassword = (data: IUserResetPasswordRequest): Promise<void> => {
  return request.post('/user/reset-password', data)
}

/**
 * 分配用户角色
 * @param userId - 用户ID
 * @param roleIds - 角色ID列表
 * @returns 分配后的角色ID列表
 */
export const assignUserRoles = (userId: number, roleIds: number[]): Promise<number[]> => {
  return request.post('/user/roles/assign', { user_id: userId, role_ids: roleIds })
}

/**
 * 获取用户已绑定角色ID列表
 * @param userId - 用户ID
 * @returns 用户已绑定的角色ID列表
 */
export const getUserRoles = (userId: number): Promise<number[]> => {
  return request.get(`/user/${userId}/roles`)
}
