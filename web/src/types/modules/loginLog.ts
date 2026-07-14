import type { IPageQuery } from '@/types'

export interface ILoginLogInfo {
  id: number
  trace_id: string
  user_id: number | null
  username: string
  response_code: string | null
  response_msg: string | null
  client_ip: string
  ip_country: string | null
  ip_province: string | null
  ip_city: string | null
  os: string | null
  browser: string | null
  user_agent: string | null
  create_time: string
}

export interface ILoginLogListQueryParam extends IPageQuery {
  user_id?: number
  username?: string
  response_code?: string
  client_ip?: string
  os?: string
  browser?: string
  ip_country?: string
  ip_province?: string
  ip_city?: string
  start_time?: string
  end_time?: string
}
