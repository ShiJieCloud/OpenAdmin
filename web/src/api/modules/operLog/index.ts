import request from '@/utils/request'
import type { IOperLogInfo, IOperLogListQueryParam, IPageResult } from '@/types'

export const getOperLogList = (query: IOperLogListQueryParam): Promise<IPageResult<IOperLogInfo>> => {
  return request.post('/oper-log/list', query)
}
