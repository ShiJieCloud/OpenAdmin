import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage } from 'element-plus'
import type { RequestConfig } from './type'

import type { ApiResponse } from '@/types'

import { useUserStore } from '@/store'


const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 3000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {

    // accessToken 自动添加
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

// 响应拦截器
request.interceptors.response.use(
  async (response: AxiosResponse<ApiResponse>) => {
    const userStore = useUserStore()

    const { code, message, data } = response.data

    // ✅ 业务成功
    if (code === '0000000') {
      return data
    }
    
    if (code === 'BAU0002') {
      // Token 过期，调用刷新接口续约 Token
      await userStore.renewToken()
      return Promise.reject(new Error(message || '登录过期，请重新登录'))
    }

    // ❌ 业务失败
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },

  // HTTP 异常
  (error) => {

    // 主动取消请求不处理，不做异常处理，直接静默 reject
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    const { response, message } = error
    let errMsg = '网络异常，请稍后重试'

    if (response) {
      // 后端有返回错误信息
      errMsg = response.data?.message || response.statusText

      // HTTP 状态码处理
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

    // 错误提示
    ElMessage.error(errMsg)
    console.error('🔴 请求异常：', error) // 开发环境日志
    return Promise.reject(new Error(errMsg))
  }
)


const get = <T = any>(url: string, params?: object): Promise<T> => {
  return request.get(url, { params })
}

const post = <T = any>(url: string, data?: object, config?: RequestConfig): Promise<T> => {
  return request.post(url, data, config)
}

const put = <T = any>(url: string, data?: object): Promise<T> => {
  return request.put(url, data)
}

const deleteRequest = <T = any>(url: string, params?: object): Promise<T> => {
  return request.delete(url, { params })
}

const patch = <T = any>(url: string, data?: object): Promise<T> => {
  return request.patch(url, data)
}

export default { request, get, post, put, deleteRequest, patch }
