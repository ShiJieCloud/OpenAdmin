import axios, {
  type AxiosInstance,
  type AxiosResponse
} from 'axios'
import { ElMessage } from 'element-plus'
import type { CustomInternalRequestConfig,RequestConfig } from './type'



const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const service: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// 请求拦截器
service.interceptors.request.use(
  (config: CustomInternalRequestConfig) => {

    // 1. 自定义超时时间优先使用接口自身配置
    if (config.timeoutCustom) {
      config.timeout = config.timeoutCustom
    }


    // 4. Token
    const ignoreToken = config.ignoreToken ?? false
    if (!ignoreToken) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message, data } = response.data as { code: string; message: string; data: any }
    
    if (code === '0000000') {
      return data
    }
    
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },
  (error) => {
    const { response } = error
    if (response) {
      const { status, data } = response
      if (status === 401) {
        window.location.href = '/login'
      }
      ElMessage.error(data.message || `请求失败 ${status}`)
      return Promise.reject(new Error(data.message || `Error ${status}`))
    }
    ElMessage.error('网络错误')
    return Promise.reject(new Error('Network error'))
  }
)

const request = {
  get<T = any>(url: string, params?: object): Promise<T> {
    return service.get(url, { params })
  },

  post<T = any>(url: string, data?: object, config?: RequestConfig): Promise<T> {
    return service.post(url, data, config)
  },

  put<T = any>(url: string, data?: object): Promise<T> {
    return service.put(url, data)
  },

  delete<T = any>(url: string, params?: object): Promise<T> {
    return service.delete(url, { params })
  },

  patch<T = any>(url: string, data?: object): Promise<T> {
    return service.patch(url, data)
  },
}

export default request
export { service }
