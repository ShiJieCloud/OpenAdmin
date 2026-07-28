/**
 * 岗位信息
 */
export interface IPostInfo {
  id: number
  post_name: string
  dept_id?: number
  dept_name?: string
  sort: number
  status: number
  remark?: string
  create_time: string
  update_time: string
}

/**
 * 创建岗位请求
 */
export interface IPostCreateRequest {
  post_name: string
  dept_id?: number
  sort?: number
  status?: number
  remark?: string
}

/**
 * 编辑岗位请求
 */
export interface IPostUpdateRequest {
  post_id: number
  post_name?: string
  dept_id?: number
  sort?: number
  status?: number
  remark?: string
}

/**
 * 岗位列表查询参数
 */
export interface IPostQueryParams {
  page_num?: number
  page_size?: number
  post_name?: string
  dept_ids?: number[]
  status?: number
}
