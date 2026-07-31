import { createVNode, render } from 'vue'
import AppUpdateDialog from './index.vue'
import type { VersionInfo } from './index.vue'

// 全局单例，防止同时弹出多个更新弹窗
let container: HTMLDivElement | null = null

export function showAppUpdateDialog(versionInfo: VersionInfo) {
  // 如果实例已存在直接返回，避免重复弹窗
  if (container) return

  container = document.createElement('div')
  const vnode = createVNode(AppUpdateDialog)
  render(vnode, container)
  document.body.appendChild(container)

  // 调用组件open方法
  vnode.component?.exposed?.open(versionInfo)
}

// 导出类型方便外部使用
export type { VersionInfo }
