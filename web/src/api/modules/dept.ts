import request from '@/utils/request'
import type { IDeptInfo, IDeptCreateRequest, IDeptUpdateRequest } from '@/types/modules/dept'
import type { IPostInfo } from '@/types/modules/post'
import type { RequestConfig } from '@/utils/request/type'


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

/**
 * 批量删除部门
 * @param deptIds - 部门ID列表
 */
export const batchDeleteDept = (deptIds: number[]): Promise<void> => {
  return request.deleteRequest('/dept/batch', { dept_ids: deptIds })
}

/**
 * 获取部门下的所有岗位
 * @param deptId - 部门ID
 * @returns 部门下的岗位列表
 */
export const listPostsByDeptId = (deptId: number, config?: RequestConfig): Promise<IPostInfo[]> => {
  return request.get(`/dept/${deptId}/posts`, {}, config)
}