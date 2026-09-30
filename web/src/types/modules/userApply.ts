import type { IPageQuery } from '@/types'

/**
 * 用户注册申请信息
 */
export interface IUserApplyInfo {
  /** 申请ID */
  id: number
  /** 登录账号 */
  username: string
  /** 手机号 */
  phone: string | null
  /** 审核状态：0=待审核 1=已通过 2=已拒绝 3=撤销 */
  status: number
  /** 审批管理员ID */
  audit_user_id: number | null
  /** 审批时间 */
  audit_time: string | null
  /** 审批意见/拒绝原因 */
  audit_reason: string | null
  /** 创建时间 */
  create_time: string
  /** 更新时间 */
  update_time: string
}

/**
 * 用户注册申请列表查询参数
 */
export interface IUserApplyListQueryParam extends IPageQuery {
  /** 登录账号（模糊查询） */
  username?: string
  /** 手机号（模糊查询） */
  phone?: string
  /** 审核状态：0=待审核 1=已通过 2=已拒绝 3=撤销 */
  status?: number
}

/**
 * 审批通过请求
 */
export interface IUserApplyPassRequest {
  /** 所属部门ID（表单未选择时为 undefined，提交时由校验保证非空） */
  dept_id?: number
  /** 岗位ID列表（一人多岗，必须属于上送部门，不可为空） */
  post_ids: number[]
}

/**
 * 拒绝用户注册申请请求
 */
export interface IUserApplyRejectRequest {
  /** 拒绝原因 */
  reason: string
}
