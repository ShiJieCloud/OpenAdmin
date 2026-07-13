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
export interface IPageQuery {
  page_num: number
  page_size: number
}

/**
 * 分页结果（后端返回）
 */
export interface IPageResult<T> {
  records: T[] // 列表数据
  total: number // 总条数
  pages?: number // 总页数（可选）
  page_size?: number // 当前页条数
  page_num?: number // 当前页
}