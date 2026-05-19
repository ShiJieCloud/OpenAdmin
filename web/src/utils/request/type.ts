import type { AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'

/**
 * 自定义请求配置接口
 * 扩展 Axios 原生请求配置，增加业务常用字段
 */
export interface RequestConfig extends AxiosRequestConfig {
  /**
   * 是否显示全局 loading 加载动画
   * @default true 默认开启
   */
  showLoading?: boolean

  /**
   * 是否开启取消重复请求（相同地址+参数+方法）
   * @default true 默认开启
   */
  cancelRepeat?: boolean

  /**
   * 是否跳过自动携带 Token
   * @default false 默认不跳过
   */
  ignoreToken?: boolean

  /**
   * 自定义当前接口超时时间（优先级 > 全局默认超时）
   * 单位：毫秒
   */
  timeoutCustom?: number
}

/**
 * 拦截器内部使用（必须交叉，不能extends）
 */
export type CustomInternalRequestConfig = InternalAxiosRequestConfig & Partial<RequestConfig>

/**
 * 全局统一后端响应结构体
 * 所有接口返回数据均遵循该格式
 * @template T 泛型，指定 data 字段的具体数据类型
 */
export interface Response<T = any> {
  /**
   * 业务状态码
   * @description 后端自定义业务状态码，用于判断接口业务逻辑是否成功
   */
  code: string

  /**
   * 响应信息
   * @description 接口返回的提示信息（成功/失败描述）
   */
  message: string

  /**
   * 响应数据
   * @description 接口实际返回的业务数据，类型由泛型 T 决定
   */
  data: T
}