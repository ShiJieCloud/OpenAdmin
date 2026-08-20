/**
 * AI 对话模块类型定义
 * @module types/modules/aiChat
 * @since 2026-08-10
 */

/** 对话消息角色 */
export type ChatRole = 'user' | 'assistant' | 'system'

/** 单条对话消息 */
export interface IChatMessage {
  /** 消息唯一标识 */
  key: string
  /** 消息角色 */
  role: ChatRole
  /** 消息内容 */
  content: string
  /** 是否正在加载中（AI 回复中） */
  loading?: boolean
  /** 是否为错误消息 */
  isError?: boolean
}

/** 发送消息请求参数 */
export interface IChatRequest {
  /** 模型标识 */
  model: string
  /** 消息列表 */
  messages: Array<{ role?: ChatRole; content?: string }>
  /** 是否流式输出 */
  stream?: boolean
  /** 采样温度 */
  temperature?: number
  /** 最大生成 token 数 */
  max_tokens?: number
}

/** 流式响应数据块 */
export interface IStreamChunk {
  /** 增量内容 */
  content: string
}
