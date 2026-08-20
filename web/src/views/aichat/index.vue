<!--
 * @component AiChat
 * @path views/aichat/index
 * @name AI 智能对话
 * @description 基于 vue-element-plus-x 实现的 AI 对话页面，支持多轮对话、消息气泡展示、加载状态等功能
 * @example
 * <AiChat />
 * @author sjzhao
 * @date 2026-08-10
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, onMounted, onActivated, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { BubbleList, XSender, Thinking } from 'vue-element-plus-x'
import type {
  BubbleListItemProps
} from 'vue-element-plus-x/types/BubbleList';
import type { ThinkingStatus } from 'vue-element-plus-x/types/Thinking';
import { sendChatMessageStream, getModelList } from '@/api/modules/ai_chat'
import type { SSEEvent } from '@/api/modules/ai_chat'

import { MarkdownRenderer } from 'x-markdown-vue'
import 'x-markdown-vue/style'
import { useThemeStore } from '@/store';

const themeStore = useThemeStore()

const isDark = computed(() => themeStore.isDarkMode)



/** 消息类型定义 */
type ChatMessage = BubbleListItemProps & {
  key: string;
  role: 'user' | 'ai';
  isMarkdown?: boolean;
  loading?: boolean;
  typing?: boolean;
  isFog?: boolean;
  avatarSize?: '24px' | '32px';
  thinkingContent?: string;
  thinkingStatus?: ThinkingStatus;
  thinkingExpanded?: boolean;
}

const senderRef = ref<InstanceType<typeof XSender>>()

/** 可选模型列表 */
const modelOptions = ref<{ label: string; value: string }[]>([])

/** 当前选中的模型 */
const selectedModel = ref('')

/** 加载模型列表 */
const loadModels = async () => {
  try {
    const models = await getModelList()
    modelOptions.value = models.map((m: string) => ({ label: m, value: m }))
    if (models.length > 0 && !selectedModel.value) {
      selectedModel.value = models[0]
    }
  } catch (e) {
    console.error('获取模型列表失败:', e)
    ElMessage.error('获取模型列表失败')
  }
}

onMounted(() => {
  loadModels()
})

/** 页面激活时自动聚焦输入框（KeepAlive 缓存场景） */
onActivated(() => {
  senderRef.value?.focus()
})

/** 消息列表 */
const messageList = ref<ChatMessage[]>([
  {
    key: 'welcome',
    content: '你好，我是 OpenAdmin 的智能助手。',
    role: 'ai',
    placement: 'start',
    variant: 'filled',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    avatarSize: '24px',
    avatarGap: '12px',
    isMarkdown: false,
  }
])

/** 输入框加载状态 */
const senderLoading = ref(false)

/** 当前正在进行的 AI 请求控制器 */
let currentAbortController: AbortController | null = null

/** 消息自增 ID */
let messageId = 0

/**
 * 生成唯一消息 key
 */
const generateKey = (): string => {
  return `msg_${Date.now()}_${++messageId}`
}

/**
 * 添加用户消息
 */
const addUserMessage = (content: string) => {
  messageList.value.push({
    key: generateKey(),
    content,
    role: 'user',
    placement: 'end',
    variant: 'outlined',
    avatar: 'https://avatars.githubusercontent.com/u/76239030?v=4',
    avatarSize: '24px',
    avatarGap: '12px',
    isMarkdown: false,
  })
}

/**
 * 添加 AI 消息（含加载态）
 * 注意：流式场景下不使用 typing，因为 SSE 逐 chunk 到达本身就是打字机效果
 * typing 会缓冲完整内容后逐字播放，与流式增量冲突
 */
const addAiMessage = (content: string, loading = false): string => {
  const key = generateKey()
  messageList.value.push({
    key,
    content,
    role: 'ai',
    placement: 'start',
    variant: 'filled',
    loading,
    isMarkdown: true, // 使用 Markdown 渲染
    thinkingContent: '', // 初始化思考内容
    thinkingStatus: 'start', // 初始化思考状态
    thinkingExpanded: true, // 默认展开
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    avatarSize: '24px',
    avatarGap: '12px',
  })
  return key
}

/**
 * 更新 AI 消息内容
 */
const updateAiMessage = (key: string, content: string, loading = false) => {
  const message = messageList.value.find(msg => msg.key === key)
  if (message) {
    message.content = content
    message.loading = loading
  }
}

/**
 * 删除指定消息
 */
const removeMessage = (key: string) => {
  const index = messageList.value.findIndex(msg => msg.key === key)
  if (index > -1) {
    messageList.value.splice(index, 1)
  }
}

/**
 * 处理发送消息
 * @param value 输入框提交的数据
 */
const handleSend = async () => {
  // 提取文本内容
  const content = senderRef.value?.getModelValue()?.text?.trim()

  if (!content) {
    ElMessage.warning('请输入消息内容')
    return
  }
  senderRef.value?.clear()

  // 创建 AbortController 用于取消请求
  currentAbortController = new AbortController()

  // 添加用户消息
  addUserMessage(content)

  // 设置加载状态
  senderLoading.value = true

  // 添加 AI 加载消息
  const aiMessageKey = addAiMessage('', true)

  // 构建消息历史（过滤掉空内容和欢迎消息）
  const messages = messageList.value
    .filter(msg => (msg.role === 'user' || msg.role === 'ai') && msg.content?.trim())
    .map(msg => ({
      role: msg.role === 'user' ? 'user' as const : 'assistant' as const,
      content: msg.content!.trim()
    }))

  try {
    // 调用流式接口
    await sendChatMessageStream(
      {
        model: selectedModel.value || 'qwen3.7-plus',
        messages,
        stream: true
      },
      (event: SSEEvent) => {
        const message = messageList.value.find(msg => msg.key === aiMessageKey)
        if (!message) return

        // 根据事件类型处理
        switch (event.type) {
          case 'reasoning':
            // 推理内容 - 累积到 thinkingContent
            // 后端发送的是 reasoning 字段，不是 content
            // console.log('[SSE] reasoning event:', event.reasoning?.substring(0, 50))
            if (event.reasoning) {
              message.thinkingContent = (message.thinkingContent || '') + event.reasoning
              message.thinkingStatus = 'thinking'
            }
            break

          case 'content':
            // 实际内容 - 累积到 message.content，过滤空白内容
            // JSON.parse 已自动还原 \n 等转义，无需手动处理
            console.log('[SSE] content event:', event.content?.substring(0, 50))
            if (event.content && event.content.trim()) {
              message.content += event.content
              message.loading = false
              // 标记思考完成并自动收起
              message.thinkingStatus = 'end'
              message.thinkingExpanded = false
            }
            break

          case 'error':
            // 错误处理
            message.content = `错误: ${event.message || '未知错误'}`
            message.loading = false
            message.thinkingStatus = 'error'
            break
        }
      },
      currentAbortController.signal
    )

  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      updateAiMessage(aiMessageKey, '消息已取消', false)
      ElMessage.info('已取消发送')
    } else {
      console.error('发送消息失败:', error)
      updateAiMessage(aiMessageKey, '抱歉，消息发送失败，请稍后重试。', false)
      ElMessage.error('消息发送失败')
    }
  } finally {
    senderLoading.value = false
    currentAbortController = null
  }
}

/**
 * 处理取消请求
 */
const handleCancel = () => {
  if (currentAbortController) {
    currentAbortController.abort()
    currentAbortController = null
  }
  senderLoading.value = false
}

/**
 * 清空对话
 */
const handleClear = async () => {
  console.log(messageList);

  // try {
  //   await ElMessageBox.confirm(
  //     '确定要清空所有对话记录吗？此操作不可恢复。',
  //     '提示',
  //     {
  //       confirmButtonText: '确定',
  //       cancelButtonText: '取消',
  //       type: 'warning',
  //     }
  //   )

  //   // 如果有正在进行的请求，先取消
  //   if (currentAbortController) {
  //     currentAbortController.abort()
  //     currentAbortController = null
  //   }

  //   // 清空所有消息
  //   messageList.value = []

  //   // 重置加载状态
  //   senderLoading.value = false

  //   ElMessage.success('对话已清空')
  // } catch {
  //   // 用户取消操作
  // }
}
</script>

<template>
  <div class="ai-chat-page">
    <div class="ai-chat-header">
      <h2>AI 智能对话</h2>
      <p class="ai-chat-desc">基于大语言模型的智能助手，支持多轮对话</p>
      <el-button type="danger" size="small" @click="handleClear">
        清空对话
      </el-button>
    </div>

    <div class="ai-chat-container">
      <div class="message-area">
        <BubbleList :list="messageList" :auto-scroll="true" class="bubble-list">
          <template #avatar="{ item }">
            <el-avatar :src="item.avatar" :size="28" />
          </template>

          <template #header="{ item }">
            <div class="message-header">
              <span class="message-header-name">{{ item.role === 'user' ? '用户' : 'AI 助手' }}</span>
              <el-button v-if="item.key !== 'welcome'" type="danger" size="small" link @click="removeMessage(item.key)">
                删除
              </el-button>
            </div>
          </template>

          <template #content="{ item }">
            <!-- AI 消息：先展示思考过程，再展示内容 -->
            <div v-if="item.role === 'ai'">
              <!-- 思考过程展示 -->
              <Thinking
                v-if="item.thinkingContent || item.thinkingStatus === 'thinking'"
                v-model="item.thinkingExpanded"
                :content="item.thinkingContent"
                :status="item.thinkingStatus || 'start'"
                max-width="100%"
                class="thinking-block"
              >
                <template #content="{ content }">
                  <MarkdownRenderer v-if="content" :is-dark="isDark"
                :shiki-theme="['github-light', 'github-dark']"
                :markdown="content"
                :enable-animate="true"
                :enable-gfm="true" :enable-breaks="true" :allow-html="true"
                  :enable-shiki="true" :enable-code-line-number="true"
                  :enable-code-block="true"
                  :enable-code-block-number="true"
                  class="prose-xmd-renderer"/>
                <span v-else>{{ content }}</span>
                </template>
              </Thinking>
              <!-- 内容展示（Markdown 或纯文本） -->
              <div v-if="item.content" :class="item.isMarkdown ? 'prose prose-sm dark:prose-invert max-w-none' : ''">
                <MarkdownRenderer v-if="item.isMarkdown" :is-dark="isDark"
                :shiki-theme="['github-light', 'github-dark']"
                :markdown="item.content"
                :enable-animate="true"
                :enable-gfm="true" :enable-breaks="true" :allow-html="true"
                  :enable-shiki="true" :enable-code-line-number="true"
                  :enable-code-block="true"
                  :enable-code-block-number="true"
                  class="prose-xmd-renderer"/>
                <span v-else>{{ item.content }}</span>
              </div>
              <!-- 加载状态 -->
              <div v-if="item.loading && !item.content && !item.thinkingContent" class="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
            <!-- 用户消息纯文本显示 -->
            <div v-else class="user-content">
              {{ item.content }}
            </div>
          </template>
        </BubbleList>
      </div>

      <div class="input-area">
        <XSender ref="senderRef" 
        :loading="senderLoading" 
        variant="updown" 
        placeholder="输入消息，Enter 发送，Shift+Enter 换行"
          @submit="handleSend" 
          @cancel="handleCancel" 
          auto-focus 
          clearable 
          submit-type="enter">
          <template #prefix>
            <div>
              <el-select v-model="selectedModel" placeholder="选择模型" style="width: 160px">
                <el-option v-for="model in modelOptions" :key="model.value" :label="model.label" :value="model.value" />
              </el-select>
            </div>
          </template>
        </XSender>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-chat-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: calc(100vh - 120px);
}

.ai-chat-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.ai-chat-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.ai-chat-desc {
  margin: 0;
  color: #606266;
  font-size: 14px;
  flex: 1;
}

.ai-chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-area {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}

.bubble-list {
  height: 100%;
}

.input-area {
  border-top: 1px solid var(--el-border-color);
  padding: 16px;
  background: var(--el-fill-color-lighter);
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-header-name {
  font-weight: 500;
  font-size: 14px;
}

:deep(.elx-bubble-list__list) {
  scrollbar-gutter: stable;
}

:deep(.elx-bubble__content-wrapper .elx-bubble__content) {
  max-width: 80%;
}

:deep(.elx-x-sender) {
  background-color: var(--el-fill-color-blank);
}

:deep(.chat-rich-text) {
  color: var(--el-text-color);
}

:deep(.prose-xmd-renderer) {
  padding: 0px !important;
  background-color: var(--el-fill-color) !important;
}

:deep(.elx-bubble__content-wrapper .elx-bubble__content--outlined) {
  border: none;
  background-color: var(--el-fill-color);
}

:deep(.prose pre) {
  background-color: transparent;
}

/* Thinking 思考组件样式 */
.thinking-block {
  margin-bottom: 12px;
}

:deep(.thinking-block .elx-thinking) {
  --elx-thinking-trigger-bg: var(--el-fill-color-light);
  --elx-thinking-trigger-bg-hover: var(--el-fill-color);
  --elx-thinking-content-wrapper-background-color: var(--el-fill-color-lighter);
}

/* 加载动画 */
.loading-dots {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  animation: loading-bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
