import request from '@/utils/request'
import type { PasswordLoginRequest, TokenResponse, ApiResponse } from './type'

export const passwordLogin = (
  req: PasswordLoginRequest,
): Promise<TokenResponse> => {
  return request.post(
    '/api/v1/auth/login/password',
    req,
    { ignoreToken: true }
  )
}

export const refreshToken = (
  refreshToken: string
): Promise<TokenResponse> => {
  return request.post(
    '/api/v1/auth/refresh-token',
    { refresh_token: refreshToken },
    { ignoreToken: true }
  )
}

export const logout = (): Promise<void> => {
  return request.post('/api/v1/auth/logout')
}

export const getCurrentUser = (): Promise<ApiResponse<any>> => {
  return request.get('/api/v1/auth/me')
}
