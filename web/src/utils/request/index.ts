/**
 * Axios 请求统一封装模块
 *
 * @description
 * 基于 Axios 封装的统一 HTTP 请求层，提供以下核心能力：
 * - 请求拦截：自动注入 Bearer Token 到 Authorization 请求头
 * - 响应拦截：统一解析业务响应结构，区分业务成功/失败/Token 过期
 * - Token 无感刷新：Token 过期（BAU0002）时自动调用刷新接口，并原请求重发
 * - 并发控制：多请求同时过期时，通过互斥锁 + 发布-订阅队列保证只刷新一次
 * - HTTP 异常处理：统一映射 HTTP 状态码、网络异常、超时等错误
 *
 * @module utils/request
 * @author sjzhao
 * @version 1.1.0
 * @since 1.0.0
 * @license MIT
 *
 * @example
 * ```ts
 * import request from '@/utils/request'
 *
 * // GET 请求
 * const users = await request.get<UserList>('/api/users', { page: 1 })
 *
 * // POST 请求
 * await request.post('/api/users', { name: 'foo' })
 * ```
 */

import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage } from 'element-plus'
import type { RequestConfig } from './type'

import type { ApiResponse } from '@/types'

import { useUserStore } from '@/store'

/**
 * Token 刷新互斥锁
 * @description 防止并发请求同时触发多次 Token 刷新，保证同一时刻只有一个刷新请求在执行
 * @private
 */
let isRefreshing = false

/**
 * Token 刷新等待队列
 * @description 存储因 Token 过期而挂起的请求回调，刷新完成后统一通知重发
 * @private
 */
let refreshSubscribers: Array<(token: string) => void> = []

/**
 * 将挂起的请求回调加入刷新等待队列
 *
 * @description 当 Token 正在刷新时，后续过期请求不会重复发起刷新，
 * 而是将"换 Token + 重发"的回调注册到队列中，等待刷新完成后统一执行
 *
 * @param callback - 刷新完成后执行的回调，接收新的 accessToken 参数
 * @private
 */
const addRefreshSubscriber = (callback: (token: string) => void): void => {
  refreshSubscribers.push(callback)
}

/**
 * 通知所有等待的请求并清空队列
 *
 * @description Token 刷新成功后调用，遍历队列中的回调函数，
 * 将新 Token 传递给每个回调以完成请求重发，随后清空队列
 *
 * @param token - 刷新后的新 accessToken
 * @private
 */
const notifyRefreshSubscribers = (token: string): void => {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

/** Axios 请求实例 */
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 3000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

/**
 * 请求拦截器
 * - 自动从 Pinia 用户仓库读取 accessToken 并注入 Authorization 请求头
 * - 未登录时（accessToken 为空）不注入，由后端返回鉴权错误
 */
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    const accessToken = userStore.accessToken
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 *
 * 统一处理后端业务响应与 HTTP 异常：
 * - 业务成功（code === '0000000'）：直接返回 data 字段，解包业务数据
 * - Token 过期（code === 'BAU0002'）：自动刷新 Token 并重发原请求，支持并发控制
 * - 业务失败：弹出错误提示并 reject
 * - HTTP 异常：按状态码映射友好错误信息
 */
request.interceptors.response.use(
  async (response: AxiosResponse<ApiResponse>) => {
    const userStore = useUserStore()
    const { code, message, data } = response.data

    // 业务成功：解包返回 data 字段
    if (code === '0000000') {
      return data
    }

    // Token 过期：自动刷新并重发原请求
    if (code === 'BAU0002') {
      const originalRequest = response.config

      // 场景1：已有刷新任务进行中，将当前请求挂入等待队列
      if (isRefreshing) {
        return new Promise((resolve) => {
          addRefreshSubscriber((newToken: string) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            resolve(request(originalRequest))
          })
        })
      }

      // 场景2：首个过期请求触发刷新，加锁阻止后续并发刷新
      isRefreshing = true

      try {
        await userStore.renewToken()
        const newToken = userStore.accessToken

        // 通知队列中所有挂起的请求，使用新 Token 重发
        notifyRefreshSubscribers(newToken)

        // 重发触发本次刷新的原始请求
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return request(originalRequest)
      } catch (refreshError) {
        // 刷新失败（refreshToken 过期 / 后端校验失败 / 网络异常）
        refreshSubscribers = []
        ElMessage.error('登录已过期，请重新登录')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 业务失败
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },

  /**
   * HTTP 异常处理
   *
   * 错误处理优先级：主动取消 > 后端响应错误 > 超时 > 网络异常
   * - 主动取消（axios.Cancel）：静默 reject，不弹提示
   * - 有 response：按 HTTP 状态码映射错误信息
   * - 无 response：区分超时和网络断开
   */
  (error) => {
    // 主动取消的请求，静默处理
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    const { response, message } = error
    let errMsg = '网络异常，请稍后重试'

    if (response) {
      errMsg = response.data?.message || response.statusText

      switch (response.status) {
        case 400:
          errMsg = '请求参数错误'
          break
        case 404:
          errMsg = '请求地址不存在'
          break
        case 500:
          errMsg = '服务器内部错误'
          break
        case 502:
          errMsg = '网关错误'
          break
        case 503:
          errMsg = '服务不可用'
          break
      }
    } else if (message.includes('timeout')) {
      errMsg = '请求超时，请重试'
    } else if (message.includes('Network Error')) {
      errMsg = '网络连接失败，请检查网络'
    }

    ElMessage.error(errMsg)
    console.error('🔴 请求异常：', error)
    return Promise.reject(new Error(errMsg))
  }
)

/**
 * 发送 GET 请求
 *
 * @example
 * ```ts
 * // 仅 URL
 * await get('/api/users')
 *
 * // URL + 查询参数
 * await get('/api/users', { page: 1, size: 10 })
 *
 * // URL + 查询参数 + 配置（signal / headers / timeout）
 * await get('/api/users', { page: 1 }, { signal: abortController.signal })
 * ```
 */
// 重载1：仅 url
function get<T = any>(url: string): Promise<T>
// 重载2：url + 查询参数
function get<T = any>(url: string, params: Record<string, unknown>): Promise<T>
// 重载3：url + 查询参数 + 配置（signal / headers / timeout）
function get<T = any>(url: string, params: Record<string, unknown>, config?: RequestConfig): Promise<T>
// 实现体（响应拦截器已解包 data，需断言为 T）
function get<T = any>(url: string, params?: Record<string, unknown>, config?: RequestConfig): Promise<T> {
  return request.get(url, { params, ...config }) as Promise<T>
}

/** 发送 POST 请求 */
const post = <T = any>(url: string, data?: object, config?: RequestConfig): Promise<T> => {
  return request.post(url, data, config)
}

/** 发送 PUT 请求 */
const put = <T = any>(url: string, data?: object): Promise<T> => {
  return request.put(url, data)
}

/** 发送 DELETE 请求 */
const deleteRequest = <T = any>(url: string,data?: object, params?: object, config?: RequestConfig): Promise<T> => {
  // return request.delete(url, { params })
  const axiosConfig: RequestConfig = {
    ...config,
    params,
  }
  // 如果传入data，挂载到config.data，delete才能携带body
  if (data) {
    axiosConfig.data = data
  }
  return request.delete(url, axiosConfig)
}


/** 发送 PATCH 请求 */
const patch = <T = any>(url: string, data?: object): Promise<T> => {
  return request.patch(url, data)
}

export default { request, get, post, put, deleteRequest, patch }
