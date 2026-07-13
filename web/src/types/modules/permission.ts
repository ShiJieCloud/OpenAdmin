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
  /** 权限类型 */
  type: string
  /** 排序序号 */
  sort: number
  /** 权限描述（可选） */
  description?: string
}
