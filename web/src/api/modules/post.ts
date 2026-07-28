import request from '@/utils/request'
import type { IPostInfo, IPostCreateRequest, IPostUpdateRequest, IPostQueryParams } from '@/types/modules/post'
import type { IPageResult } from '@/types/common/api'

/**
 * 获取岗位列表（分页）
 * @param params - 查询参数
 * @returns 岗位分页列表
 */
export const getPostList = (params?: IPostQueryParams): Promise<IPageResult<IPostInfo>> => {
  return request.post('/post/list', params)
}

/**
 * 获取岗位详情
 * @param postId - 岗位ID
 * @returns 岗位信息
 */
export const getPostInfo = (postId: number): Promise<IPostInfo> => {
  return request.get(`/post/${postId}`)
}

/**
 * 创建岗位
 * @param data - 创建岗位请求
 * @returns 创建后的岗位信息
 */
export const createPost = (data: IPostCreateRequest): Promise<IPostInfo> => {
  return request.post('/post', data)
}

/**
 * 编辑岗位
 * @param data - 编辑岗位请求
 * @returns 更新后的岗位信息
 */
export const updatePost = (data: IPostUpdateRequest): Promise<IPostInfo> => {
  return request.put('/post', data)
}

/**
 * 删除岗位
 * @param postId - 岗位ID
 */
export const deletePost = (postId: number): Promise<void> => {
  return request.deleteRequest(`/post/${postId}`)
}

/**
 * 批量删除岗位
 * @param postIds - 岗位ID列表
 */
export const batchDeletePost = (postIds: number[]): Promise<void> => {
  return request.deleteRequest('/post/batch', { post_ids: postIds })
}

/**
 * 获取岗位角色列表
 * @param postId - 岗位ID
 * @returns 角色ID列表
 */
export const getPostRoles = (postId: number): Promise<number[]> => {
  return request.get(`/post/${postId}/roles`)
}

/**
 * 分配岗位角色
 * @param postId - 岗位ID
 * @param roleIds - 角色ID列表
 * @returns 分配后的角色ID列表
 */
export const assignPostRoles = (postId: number, roleIds: number[]): Promise<number[]> => {
  return request.post(`/post/${postId}/roles/assign`, { role_ids: roleIds })
}
