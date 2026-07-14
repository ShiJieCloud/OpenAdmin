import request from '@/utils/request'
import type { ILoginLogInfo, ILoginLogListQueryParam, IPageResult } from '@/types'

export const getLoginLogList = (query: ILoginLogListQueryParam): Promise<IPageResult<ILoginLogInfo>> => {
  return request.post('/login-log/list', query)
}
