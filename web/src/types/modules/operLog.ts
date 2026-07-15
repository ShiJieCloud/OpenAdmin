import type { IPageQuery } from '@/types'

export interface IOperLogInfo {
  id: number
  trace_id: string
  request_method: string
  api_path: string
  api_name: string | null
  module: string | null
  operator_id: string | null
  client_ip: string
  ip_country: string | null
  ip_province: string | null
  ip_city: string | null
  ip_location: string | null
  response_code: string | null
  response_msg: string | null
  request_body: string | null
  response_data: string | null
  cost_time: number
  create_time: string
}

export interface IOperLogListQueryParam extends IPageQuery {
  trace_id?: string
  request_method?: string[]
  api_path?: string
  api_name?: string
  module?: string
  operator_id?: string
  client_ip?: string
  response_code?: string
  start_time?: string
  end_time?: string
}
