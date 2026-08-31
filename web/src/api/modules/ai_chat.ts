/**
 * AI 对话模块 API 接口
 * @module api/modules/aiChat
 * @since 2026-08-10
 */
import type {
  IChatRequest,
  ISessionMeta,
  ISessionMessage,
} from '@/types/modules/aiChat'
import request from '@/utils/request'

/**
 * SSE 事件类型定义
 */
export interface SSEEvent {
  type: 'content' | 'reasoning' | 'tool_call' | 'tool_result' | 'error'
  content?: string
  reasoning?: string
  tool_calls?: Array<{
    name: string
    args: Record<string, any>
    id: string
  }>
  tool_call_id?: string
  message?: string
}

/**
 * 发送对话消息（流式）- 支持多事件类型
 * @param data 对话请求参数
 * @param onEvent 接收 SSE 事件的回调
 * @param signal AbortSignal 用于取消请求
 * @returns Promise<void>
 */
export const sendChatMessageStream = async (
  data: IChatRequest,
  onEvent: (event: SSEEvent) => void,
  signal?: AbortSignal
): Promise<void> => {
  const baseURL = import.meta.env.VITE_API_BASE_URL
  const token = localStorage.getItem('access_token') || ''

  const response = await fetch(`${baseURL}/ai/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ ...data, stream: true }),
    signal
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('Response body is not readable')
  }

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // 解析 SSE 数据
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      const trimLine = line.trim()
      if (!trimLine) continue

      if (trimLine.startsWith('data: ')) {
        const rawJson = trimLine.slice(6)
        if (rawJson === '[DONE]') {
          return
        }
        try {
          const event: SSEEvent = JSON.parse(rawJson)
          onEvent(event)
        } catch (e) {
          console.warn('sse parse error', e, rawJson)
        }
      }
    }
  }
}

/**
 * 获取可用模型列表
 * @returns 模型标识列表
 */
export const getModelList = (): Promise<string[]> => {
  return request.get('/ai/models')
}

/**
 * 创建会话（获取会话 ID 并在 Redis 注册元数据）
 * 前端进入页面或清空对话时调用，获取 session_id 用于后续流式对话的记忆隔离。
 * @param model_id 模型标识
 * @returns 会话 ID（32 位十六进制，无连字符）
 */
export const createChatSession = (model_id: string): Promise<string> => {
  return request.post('/ai/chat/session', {
    model_id,
  })
}

/**
 * 获取用户会话列表
 * @param limit 返回数量上限
 * @returns 会话元数据列表
 */
export const getSessionList = (limit = 100): Promise<ISessionMeta[]> => {
  return request.get('/ai/chat/sessions', {
    params: { limit },
  })
}

/**
 * 获取会话消息历史
 * @param session_id 会话 ID
 * @param limit 返回数量上限
 * @returns 消息历史列表
 */
export const getSessionMessages = (session_id: string, limit = 200): Promise<ISessionMessage[]> => {
  return request.get(`/ai/chat/sessions/${session_id}/messages`, {
    params: { limit },  
  })
}

/**
 * 删除会话
 * @param session_id 会话 ID
 * @returns 删除结果
 */
export const deleteSession = (session_id: string): Promise<boolean> => {
  return request.deleteRequest(`/ai/chat/sessions/${session_id}`, undefined)
}
