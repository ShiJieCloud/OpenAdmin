import request from '@/utils/request'
import type { IDeptInfo, IDeptCreateRequest, IDeptUpdateRequest } from '@/types/modules/dept'

/**
 * 获取部门树形列表
 * @param status - 状态筛选（可选）
 * @returns 部门树形列表
 */
export const getDeptList = (status?: number): Promise<IDeptInfo[]> => {
  return request.get('/dept/list', { params: { status } })
}

/**
 * 获取部门详情
 * @param deptId - 部门ID
 * @returns 部门信息
 */
export const getDeptInfo = (deptId: number): Promise<IDeptInfo> => {
  return request.get(`/dept/${deptId}`)
}

/**
 * 创建部门
 * @param data - 创建部门请求
 * @returns 创建后的部门信息
 */
export const createDept = (data: IDeptCreateRequest): Promise<IDeptInfo> => {
  return request.post('/dept', data)
}

/**
 * 编辑部门
 * @param data - 编辑部门请求
 * @returns 更新后的部门信息
 */
export const updateDept = (data: IDeptUpdateRequest): Promise<IDeptInfo> => {
  return request.put('/dept', data)
}

/**
 * 删除部门
 * @param deptId - 部门ID
 */
export const deleteDept = (deptId: number): Promise<void> => {
  return request.deleteRequest(`/dept/${deptId}`)
}
