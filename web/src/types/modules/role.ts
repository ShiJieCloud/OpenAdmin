import type { IPageQuery } from '@/types'


export interface IRoleInfo {
  id: number
  role_name: string
  role_code: string
  sort: number
  description: string | null
  status: number
  create_time: string
  update_time: string
}

export interface RoleCreateRequest {
  role_name: string
  role_code: string
  sort?: number
  description?: string | null
  status?: number
}

export interface RoleUpdateRequest {
  role_id: number
  role_name?: string
  role_code?: string
  sort?: number
  description?: string | null
  status?: number
}

export interface RoleUpdateStatusRequest {
  role_id: number
  status: number
}

export interface IRoleListQueryParam extends IPageQuery {
  role_name?: string
  role_code?: string
  status?: number
}

export interface IRoleAssignPermsRequest {
  perm_ids: number[]
}
