import type { IPageQuery } from '@/types'

/**
 * 在线用户信息
 */
export interface IOnlineUserInfo {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  login_ip: string | null
  login_address: string | null
  login_time: string | null
}

/**
 * 在线用户列表查询参数
 */
export interface IOnlineUserListQueryParam extends IPageQuery {}
