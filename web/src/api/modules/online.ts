import type { IOnlineUserInfo, IOnlineUserListQueryParam } from '@/types/modules/online'
import type { IPageResult } from '@/types/common/api'
import request from '@/utils/request'

/**
 * 获取在线用户列表
 * @param params - 查询参数
 * @returns 在线用户分页列表
 */
export const getOnlineUserList = (params: IOnlineUserListQueryParam): Promise<IPageResult<IOnlineUserInfo>> => {
  return request.get('/user/online/list', params)
}

/**
 * 踢出用户下线
 * @param userId - 用户ID
 * @returns 操作结果
 */
export const kickUserOffline = (userId: number): Promise<void> => {
  return request.get(`/user/online/kick/${userId}`)
}
