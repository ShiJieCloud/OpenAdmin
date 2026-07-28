/**
 * 权限信息实体类型
 * 用于存储菜单下单个权限的完整数据
 */
export type IPermissionInfo = {
  /** 权限唯一ID */
  id: number
  /** 所属菜单ID */
  menu_id: number
  /** 权限展示名称 */
  name: string
  /** 权限标识编码（接口鉴权code） */
  code: string
  /** 排序序号 */
  sort: number
  /** 状态：0=正常 1=停用 */
  status: number
  /** 权限描述（可选） */
  description?: string
  /** 创建时间 */
  create_time: string
  /** 更新时间 */
  update_time: string
}

/**
 * 权限列表查询参数
 */
export type IPermissionListQueryParam = {
  /** 当前页码 */
  page_num: number
  /** 每页条数 */
  page_size: number
  /** 权限名称（模糊查询） */
  name?: string
  /** 权限编码（模糊查询） */
  code?: string
  /** 状态：0=正常 1=停用 */
  status?: number
  /** 所属菜单ID列表 */
  menu_ids?: number[]
}

/**
 * 创建权限请求参数
 */
export type PermissionCreateRequest = {
  /** 所属菜单ID */
  menu_id: number
  /** 权限名称 */
  name: string
  /** 权限标识编码 */
  code: string
  /** 排序序号 */
  sort: number
  /** 状态：0=正常 1=停用 */
  status: number
  /** 权限描述 */
  description?: string
}

/**
 * 更新权限请求参数
 */
export type PermissionUpdateRequest = {
  /** 权限ID */
  perm_id: number
  /** 所属菜单ID */
  menu_id?: number
  /** 权限名称 */
  name?: string
  /** 权限标识编码 */
  code?: string
  /** 排序序号 */
  sort?: number
  /** 状态：0=正常 1=停用 */
  status?: number
  /** 权限描述 */
  description?: string
}
