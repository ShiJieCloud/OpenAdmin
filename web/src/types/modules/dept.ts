/**
 * 部门信息
 */
export interface IDeptInfo {
  id: number
  parent_id: number
  dept_name: string
  sort: number
  status: number
  create_time: string
  update_time: string
  children?: IDeptInfo[]
}

/**
 * 创建部门请求
 */
export interface IDeptCreateRequest {
  parent_id?: number
  dept_name: string
  sort?: number
  status?: number
}

/**
 * 编辑部门请求
 */
export interface IDeptUpdateRequest {
  dept_id: number
  parent_id?: number
  dept_name?: string
  sort?: number
  status?: number
}