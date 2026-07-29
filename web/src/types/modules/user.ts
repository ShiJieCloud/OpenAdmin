import type { IPageQuery } from '@/types'

/**
 * 用户信息
 */
export interface IUserInfo {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  email: string | null
  phone: string | null
  sex: number
  status: number
  dept_id: number | null
  dept_name?: string
  post_ids: number[]
  remark: string | null
  create_time: string
  update_time: string
}

/**
 * 创建用户请求
 */
export interface IUserCreateRequest {
  username: string
  password: string
  nickname?: string | null
  avatar?: string | null
  email?: string | null
  phone?: string | null
  sex?: number
  dept_id?: number | null
  post_ids?: number[]
  remark?: string | null
}

/**
 * 编辑用户请求
 */
export interface IUserUpdateRequest {
  user_id: number
  nickname?: string | null
  avatar?: string | null
  email?: string | null
  phone?: string | null
  sex?: number | null
  dept_id?: number | null
  post_ids?: number[] | null
  remark?: string | null
}

/**
 * 修改用户状态请求
 */
export interface IUserUpdateStatusRequest {
  user_id: number
  status: number
}

/**
 * 重置用户密码请求
 */
export interface IUserResetPasswordRequest {
  user_id: number
  new_password: string
}

/**
 * 用户列表查询参数
 */
export interface IUserListQueryParam extends IPageQuery {
  username?: string
  nickname?: string
  email?: string
  phone?: string
  status?: number
  dept_id?: number
}

/**
 * 用户角色分配请求
 */
export interface IUserRoleAssignRequest {
  user_id: number
  role_ids: number[]
}
