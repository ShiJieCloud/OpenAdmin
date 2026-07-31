import type { Plugin, ResolvedConfig } from 'vite'
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'

// ====================== 类型定义 ======================
/**
 * 插件配置参数类型
 */
export interface VersionPluginOptions {
  /**
   * 自定义版本号
   * @description 默认值为 0.0.0，适合CI流水线动态注入版本
   */
  version?: string
  /**
   * changelog 更新日志文件相对路径
   * @default CHANGELOG.md
   */
  changelogFile?: string
  /**
   * 开发环境是否生成 public/version.json
   * @description 开启后 npm run dev 启动时生成版本文件，用于本地调试更新弹窗
   * @default false
   */
  enableDevGenerate?: boolean
}

export interface VersionInfo {
  version: string
  buildTs: number
  publishTime: string
  changelog: string
}

// ====================== 常量抽取 ======================
const PLUGIN_NAME = 'vite-plugin-version'
const DEFAULT_CHANGELOG_NAME = 'CHANGELOG.md'
const DEFAULT_FALLBACK_CHANGELOG = (v: string) => `## ${v}\n\n- 系统更新`
const NO_CHANGELOG_TIP = '# 暂无更新日志'
const MKDIR_RECURSIVE_OPT = { recursive: true }
const DEFAULT_VERSION = '0.0.0'

// 匹配格式：## [1.0.0] - 2026-07-30 或 ## [1.0.0] - 2026-07-30 12:00:00
const VERSION_HEADER_REG = /## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2})?([\s\S]*?)(?=\n## \[\d+\.\d+\.\d+\]|$)/

// ====================== 工具函数 ======================
/** 从 changelog 文本截取最新版本更新内容 */
function extractLatestChangelog(mdContent: string): string {
  const match = mdContent.match(VERSION_HEADER_REG)
  if (!match) return NO_CHANGELOG_TIP
  return match[2].trim()
}

/** 安全创建目录，不存在则递归创建 */
function ensureDirExists(filePath: string): void {
  const targetDir = dirname(filePath)
  if (!existsSync(targetDir)) {
    mkdirSync(targetDir, MKDIR_RECURSIVE_OPT)
  }
}

/**
 * 时间戳转 YYYY-MM-DD HH:mm:ss
 * @param timestamp 毫秒时间戳
 */
function formatDateTime(timestamp: number): string {
  const d = new Date(timestamp)
  const pad = (n: number) => n.toString().padStart(2, '0')
  const y = d.getFullYear()
  const m = pad(d.getMonth() + 1)
  const day = pad(d.getDate())
  const h = pad(d.getHours())
  const min = pad(d.getMinutes())
  const s = pad(d.getSeconds())
  return `${y}-${m}-${day} ${h}:${min}:${s}`
}

// ====================== 插件主入口 ======================
export function versionPlugin(options: VersionPluginOptions = {}): Plugin {
  // 配置默认值解构
  const {
    version: customVersion,
    changelogFile = DEFAULT_CHANGELOG_NAME,
    enableDevGenerate = false
  } = options

  let root = ''
  let outDir = 'dist'
  let isDev = false

  /** 生成 version.json 主逻辑 */
  function generateVersionFile(targetPath: string): void {
    try {
      // 1. 获取最终版本号：自定义参数 > package.json > 默认值
      let finalVersion = customVersion || DEFAULT_VERSION

      // 2. 读取并解析 changelog
      const changelogAbsPath = resolve(root, changelogFile)
      let changelogContent = ''
      if (existsSync(changelogAbsPath)) {
        const mdRaw = readFileSync(changelogAbsPath, 'utf-8')
        changelogContent = extractLatestChangelog(mdRaw)
      } else {
        changelogContent = DEFAULT_FALLBACK_CHANGELOG(finalVersion)
      }

      // 3. 组装版本信息
      const nowTs = Date.now()
      const versionInfo: VersionInfo = {
        version: finalVersion,
        buildTs: nowTs,
        publishTime: formatDateTime(nowTs),
        changelog: changelogContent
      }

      // 4. 写入文件
      ensureDirExists(targetPath)
      writeFileSync(targetPath, JSON.stringify(versionInfo, null, 2), 'utf-8')
      console.log(`[${PLUGIN_NAME}] ✅ v${finalVersion} 已生成 → ${targetPath}`)
    } catch (err) {
      console.error(`[${PLUGIN_NAME}] ❌ 生成 version.json 失败`, err)
    }
  }

  return {
    // Vite 插件名称
    name: 'vite-plugin-version',

    /**
     * Vite钩子：configResolved
     * 在Vite解析完成全部配置后触发
     * @param config Vite最终合并后的完整配置对象
     */
    configResolved(config) {
      root = config.root                 // 项目根目录绝对路径
      outDir = config.build.outDir || 'dist' // 打包输出目录，默认dist
      isDev = config.mode === 'development'  // 判断当前是否开发环境
    },

    /**
     * Vite钩子：configureServer
     * 仅【开发模式 npm run dev】触发，启动dev服务时执行
     */
    // 仅在开发环境且配置允许时执行
    configureServer() {
      if (!isDev || !enableDevGenerate) return
      // 拼接路径：项目根目录/public/version.json
      const publicPath = resolve(root, 'public/version.json')
      // 生成version.json到public目录
      generateVersionFile(publicPath)
    },

    /**
     * Vite钩子：closeBundle
     * 仅【生产打包 npm run build】触发
     * 打包完成、资源写入dist之后执行
     */
    closeBundle() {
      // 开发环境直接跳过，避免重复执行
      if (isDev) return
      // 拼接输出路径：项目根目录/dist/version.json
      const outputPath = resolve(root, outDir, 'version.json')
      generateVersionFile(outputPath)
    },
  }
}
