import request from '@/utils/request'
import type { 
  PasswordLoginRequest,
  RegisterRequest,
  TokenResponse,
  CaptchaResponse,
  RefreshTokenRequest,
} from '@/types'

/**
 * 账号密码登录
 * @description 使用账号密码登录，获取访问令牌与刷新令牌
 * @api POST /auth/login/password
 * @param req - 登录请求参数（用户名、密码、验证码ID与验证码）
 * @returns 访问令牌与刷新令牌
 */
export const loginByPassword = (req: PasswordLoginRequest): Promise<TokenResponse> => {
  return request.post(
    '/auth/login/password',
    req,
    { ignoreToken: true }
  )
}

/**
 * 用户注册
 * @description 公开接口，用户自助注册账号，无需登录
 * @api POST /auth/register
 * @param req - 注册请求参数（用户名、手机号、密码、短信验证码）
 * @returns 创建后的用户信息
 */
export const register = (req: RegisterRequest) => {
  return request.post(
    '/auth/register',
    req,
    { ignoreToken: true }
  )
}

/**
 * 人脸识别登录
 * @description 上传摄像头抓拍的人脸图片进行识别登录，获取访问令牌与刷新令牌
 * @api POST /auth/login/face
 * @param blob - 人脸图片 Blob 对象
 * @returns 访问令牌与刷新令牌
 */
export const loginByFace = (blob: Blob): Promise<TokenResponse> => {
  const formData = new FormData()
  formData.append('face_image', blob, 'face.jpg')
  return request.post(
    '/auth/login/face',
    formData,
    { ignoreToken: true, headers: { 'Content-Type': 'multipart/form-data' } }
  )
}

/**
 * 刷新令牌
 * @description 使用刷新令牌获取新的访问令牌与刷新令牌
 * @api POST /auth/refresh-token
 * @param req - 刷新令牌请求参数（刷新令牌）
 * @returns 新的访问令牌与刷新令牌
 */
export const refreshTokenApi = (
  req: RefreshTokenRequest
): Promise<TokenResponse> => {
  return request.post(
    '/auth/refresh-token',
    req,
    { ignoreToken: true }
  )
}

/**
 * 获取验证码
 * @description 获取验证码图片
 * @api GET /auth/captcha
 * @returns 验证码图片与验证码ID
 */
export const getCaptcha = (): Promise<CaptchaResponse> => {
  return request.get('/auth/captcha')
}