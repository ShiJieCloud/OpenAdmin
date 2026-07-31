<script setup lang="ts">
import { ref } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { getVersionChecker } from '@/utils/version-check'

/**
 * 版本信息结构
 */
export interface VersionInfo {
  /** 构建时间戳 */
  buildTs: number
  /** 语义化版本号 */
  version: string
  /** 发布时间 格式化字符串 */
  publishTime: string
  /** 更新日志 markdown 原文 */
  changelog: string
}

/** 弹窗显示状态 */
const visible = ref(false)

/** 当前弹窗展示的版本数据 */
const data = ref<VersionInfo>({
  buildTs: 0,
  version: '',
  publishTime: '',
  changelog: ''
})

/**
 * Markdown 转换 + XSS防御净化
 * @param mdText 原始markdown文本
 * @returns 安全HTML字符串
 */
const md = new MarkdownIt()

/**
 * Markdown 转换 + XSS防御净化
 * @param mdText 原始markdown文本
 * @returns 安全HTML字符串
 */
const renderMarkdown = (mdText: string): string => {
  if (!mdText) return ''
  // markdown转html
  const rawHtml = md.render(mdText)
  // DOMPurify 过滤恶意标签，防止XSS攻击
  return DOMPurify.sanitize(rawHtml)
}

/**
 * 外部调用：打开弹窗，传入版本信息
 * @param info 新版本数据
 */
const open = (info: VersionInfo) => {
  // 浅拷贝隔离外部对象，防止污染源数据
  data.value = { ...info }
  visible.value = true
}

/**
 * 关闭弹窗（稍后提醒）
 * 仅关闭弹窗，不修改本地版本标记，冷却到期后继续提醒
 */
const handleClose = () => {
  visible.value = false
}

/**
 * 立即刷新页面
 * 1. 标记本地版本为最新，避免刷新立刻重复弹窗
 * 2. 执行页面重载加载新版本资源
 */
const handleRefresh = () => {
  // 保存当前版本到本地，避免刷新后重复提示
const checker = getVersionChecker ()
  if (checker) {
    checker.saveLocalBuildTs (data.value.buildTs)
  }
  location.reload()
}

/**
 * 对外暴露组件方法，父组件可调用 open()
 */
defineExpose({ open })
</script>

<template>
  <el-dialog
    v-model="visible"
    title="🎉 系统新版本已发布"
    width="720px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <!-- 版本基础信息 -->
    <div class="version-meta">
      <span><strong>版本号：</strong><el-tag>{{ data.version }}</el-tag></span>
      <span><strong>发布时间：</strong>{{ data.publishTime }}</span>
    </div>

    <el-divider />

    <!-- Markdown 更新日志渲染区域 -->
    <div
      class="markdown-container prose prose-sm max-w-none overflow-auto max-h-[50vh] px-1"
      v-html="renderMarkdown(data.changelog)"
    />

    <template #footer>
      <div class="footer-wrap">
        <el-button @click="handleClose">稍后提醒</el-button>
        <el-button type="primary" @click="handleRefresh">立即刷新</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.version-meta {
  display: flex;
  gap: 32px;
  color: #606266;
  font-size: 14px;
}
</style>
