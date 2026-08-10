import type { ILoginLogInfo, IOperLogInfo } from '@/types'
import type { ISystemOverview } from '@/types/modules/dashboard'
import request from '@/utils/request'

/**
 * 获取系统概览
 * @returns 系统概览
 */
export const getSystemOverview = (): Promise<ISystemOverview> => {
  return request.get('/dashboard/overview')
}

/**
 * 获取最近登录日志
 * @returns 最近登录日志
 */
export const getRecentLoginLogs = (): Promise<ILoginLogInfo[]> => {
  return request.get('/dashboard/recent_login_logs')
}

/**
 * 获取最近操作日志
 * @returns 最近操作日志
 */
export const getRecentOperLogs = (): Promise<IOperLogInfo[]> => {
  return request.get('/dashboard/recent_oper_logs')
}