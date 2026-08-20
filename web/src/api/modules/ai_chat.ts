/**
 * AI 对话模块 API 接口
 * @module api/modules/aiChat
 * @since 2026-08-10
 */
import type { IChatRequest } from '@/types/modules/aiChat'
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
