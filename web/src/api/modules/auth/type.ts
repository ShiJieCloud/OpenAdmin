export interface PasswordLoginRequest {
  username: string
  password: string
  captcha_code?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface ApiResponse<T = any> {
  code: string
  message: string
  timestamp: number
  data: T
}
