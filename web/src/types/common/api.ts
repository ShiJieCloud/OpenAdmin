// 通用响应体
export interface ApiResponse<T = any> {
  code: string
  message: string
  timestamp: number
  data: T
}

/**
 * 分页查询参数（传给后端）
 */
export interface PageQuery {
  pageNum: number
  pageSize: number
}

/**
 * 分页结果（后端返回）
 */
export interface PageResult<T> {
  records: T[] // 列表数据
  total: number // 总条数
  pages?: number // 总页数（可选）
  size?: number // 当前页条数
  current?: number // 当前页
}