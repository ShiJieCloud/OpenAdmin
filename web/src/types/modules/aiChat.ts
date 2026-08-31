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
  /** 本轮新消息（历史由后端按 session_id 自动加载，无需重传） */
  message: { content: string }
  /** 会话 ID（首轮通过 createChatSession 获取，后续轮回传） */
  session_id: string
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

/** 会话元数据 */
export interface ISessionMeta {
  /** 会话 ID */
  session_id: string
  /** 会话标题 */
  title: string
  /** 模型标识 */
  model_id: string
  /** 创建时间戳 */
  created_at: number
  /** 更新时间戳 */
  updated_at: number
}

/** 会话消息 */
export interface ISessionMessage {
  /** 消息角色 */
  role: ChatRole
  /** 消息内容 */
  content: string
  /** 推理内容 */
  reasoning_content?: string
  /** 模型标识 */
  model_id: string
  /** 时间戳 */
  timestamp: number
}

/** 创建会话响应 */
export interface ICreateSessionResponse {
  /** 会话 ID */
  session_id: string
}
