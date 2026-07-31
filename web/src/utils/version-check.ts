/**
 * 版本检测工具
 * 用于检测前端应用是否有新版本发布，配套version.json方案
 * 交互规则：稍后提醒仅关闭弹窗，不会屏蔽当前版本；依靠冷却机制防止频繁弹窗
 */
import type { VersionInfo } from '@/components/AppUpdateDialog/index.vue'

// 本地存储key
const STORAGE_KEY = 'app_version_build_ts'
// 默认弹窗冷却时长 10分钟
const MODAL_COOLING_MS = 10 * 60 * 1000

interface VersionCheckOptions {
  /** 检查间隔（毫秒），默认 5 分钟 */
  interval?: number
  /** 是否启用自动轮询，默认 true */
  autoCheck?: boolean
  /** version.json 路径，默认 /version.json */
  versionFileUrl?: string
}

class VersionChecker {
  private timer: ReturnType<typeof setInterval> | null = null
  private options: Required<VersionCheckOptions>
  // 冷却时间戳，防止短时间重复弹窗
  private coolingUntil = 0

  constructor(options: VersionCheckOptions = {}) {
    this.options = {
      interval: options.interval ?? 5 * 60 * 1000,
      autoCheck: options.autoCheck ?? true,
      versionFileUrl: options.versionFileUrl ?? '/version.json',
    }
  }

  /**
   * 获取本地持久化构建时间戳
   */
  private getLocalBuildTs(): number | null {
    const str = localStorage.getItem(STORAGE_KEY)
    if (!str) return null
    return Number(str)
  }

  /**
   * 保存最新版本到本地存储
   */
  public saveLocalBuildTs(ts: number): void {
    localStorage.setItem(STORAGE_KEY, String(ts))
  }

  /**
   * 获取远程版本信息
   */
  private async fetchVersion(): Promise<VersionInfo | null> {
    try {
      // 拼接时间戳强效防缓存
      const url = `${this.options.versionFileUrl}?t=${Date.now()}`
      const response = await fetch(url, { cache: 'no-store' })
      if (!response.ok) throw new Error(`Http ${response.status}`)
      return await response.json()
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn('[VersionChecker] Failed to fetch version:', error)
      }
      return null
    }
  }

  /**
   * 检查版本更新
   * @returns 如果有新版本返回版本信息，否则返回 null
   */
  async check(): Promise<VersionInfo | null> {
    const remoteVersion = await this.fetchVersion()
    if (!remoteVersion) return null

    const localTs = this.getLocalBuildTs()
    const remoteTs = remoteVersion.buildTs

    // 首次访问，初始化本地版本
    if (localTs === null) {
      this.saveLocalBuildTs(remoteTs)
      return null
    }

    // 版本一致，无需更新
    if (remoteTs === localTs) return null

    // 冷却中，暂时不触发弹窗
    const now = Date.now()
    if (now < this.coolingUntil) return null

    // 设置冷却时间，10分钟内不再弹出
    this.coolingUntil = now + MODAL_COOLING_MS
    return remoteVersion
  }

  /**
   * 启动自动轮询检查
   * @param onUpdate 检测到更新回调
   */
  start(onUpdate: (version: VersionInfo) => void): void {
    if (this.timer) return

    // 首次立即检测
    this.check()
      .then((newVersion) => {
        if (newVersion) {
          // 页面刷新后重新初始化，拉到新版本代表已加载新资源，更新本地版本标识
          this.saveLocalBuildTs(newVersion.buildTs)
          onUpdate(newVersion)
        }
      })
      .catch((err) => import.meta.env.DEV && console.warn('首次版本检测异常', err))

    if (!this.options.autoCheck) return

    // 启动轮询
    this.timer = setInterval(async () => {
      const newVersion = await this.check()
      if (newVersion) onUpdate(newVersion)
    }, this.options.interval)
  }

  /**
   * 停止自动轮询
   */
  stop(): void {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
  }

  /**
   * 销毁实例，清理资源
   */
  destroy(): void {
    this.stop()
  }

  /**
   * 手动触发一次版本检查
   */
  async checkNow(): Promise<VersionInfo | null> {
    return this.check()
  }
}

// 全局单例
let instance: VersionChecker | null = null

/**
 * 初始化版本检查器（全局只初始化一次）
 */
export function initVersionChecker(options: VersionCheckOptions = {}): VersionChecker {
  if (!instance) {
    instance = new VersionChecker(options)
  }
  return instance
}

/**
 * 获取版本检查器实例
 */
export function getVersionChecker(): VersionChecker | null {
  return instance
}

/**
 * 手动检查版本更新（快捷方法）
 */
export async function checkVersion(): Promise<VersionInfo | null> {
  if (!instance) {
    instance = new VersionChecker()
  }
  return instance.checkNow()
}
