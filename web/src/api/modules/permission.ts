import type { IPermissionInfo } from '@/types/modules/permission'
import request from '@/utils/request'


export const fetchSystemPermissionList = (): Promise<IPermissionInfo[]> => {
  return request.get('/permission')
}
