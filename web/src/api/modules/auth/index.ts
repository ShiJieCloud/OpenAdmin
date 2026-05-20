import request from '@/utils/request'
import type { PasswordLoginRequest, TokenResponse, CaptchaResponse, RefreshTokenRequest } from '@/types'

export const passwordLogin = (req: PasswordLoginRequest): Promise<TokenResponse> => {
  return request.post(
    '/auth/login/password',
    req,
    { ignoreToken: true }
  )
}

export const refreshTokenApi = (
  req: RefreshTokenRequest
): Promise<TokenResponse> => {
  return request.post(
    '/auth/refresh-token',
    req,
    { ignoreToken: true }
  )
}

export const getCaptcha = (): Promise<CaptchaResponse> => {
  return request.get('/auth/captcha')
}