import request from '@/utils/request'
import type { IPageResult } from '@/types/common/api'
import type {
  IUserApplyInfo,
  IUserApplyListQueryParam,
  IUserApplyPassRequest,
  IUserApplyRejectRequest,
} from '@/types/modules/userApply'

/**
 * 获取注册申请列表（分页）
 * @param params - 查询参数
 * @returns 注册申请分页列表
 */
export const getUserApplyList = (params: IUserApplyListQueryParam): Promise<IPageResult<IUserApplyInfo>> => {
  return request.get('/approval/user-register-apply/list', params)
}

/**
 * 获取注册申请详情
 * @param applyId - 申请ID
 * @returns 申请详细信息
 */
export const getUserApplyInfo = (applyId: number): Promise<IUserApplyInfo> => {
  return request.get(`/approval/user-register-apply/${applyId}`)
}

/**
 * 审批通过
 * @description 通过指定用户注册申请，同时创建对应系统用户并绑定部门/岗位
 * @param applyId - 申请ID
 * @param data - 审批通过请求，包含部门ID和岗位ID列表
 * @returns 更新后的申请详细信息
 */
export const passUserApply = (applyId: number, data: IUserApplyPassRequest): Promise<IUserApplyInfo> => {
  return request.post(`/approval/user-register-apply/${applyId}/pass`, data)
}

/**
 * 审批拒绝
 * @description 拒绝指定用户注册申请，记录拒绝原因
 * @param applyId - 申请ID
 * @param data - 拒绝请求，包含拒绝原因
 * @returns 更新后的申请详细信息
 */
export const rejectUserApply = (applyId: number, data: IUserApplyRejectRequest): Promise<IUserApplyInfo> => {
  return request.post(`/approval/user-register-apply/${applyId}/reject`, data)
}
