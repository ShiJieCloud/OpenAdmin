/**
 * @file vite-plugin-version.ts
 * @desc Vite 版本信息生成插件
 * @feature 构建/开发时自动生成 version.json，包含版本号、构建时间、更新日志
 * @usage 用于前端检测版本更新弹窗、关于页面展示构建信息
 */
import type { Plugin, ResolvedConfig } from 'vite'
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import dayjs from 'dayjs'

// ====================== 类型定义 ======================
/** 插件入参配置项 */
export interface VersionPluginOptions {
  /** 自定义版本号，优先级高于默认兜底 */
  version?: string
  /** 更新日志 MD 文件相对路径 */
  changelogFile?: string
  /** 开发环境是否生成 public/version.json */
  enableDevGenerate?: boolean
  /** 构建时间戳，用于格式化发布时间 */
  buildTs?: number
}

/** 输出 version.json 完整结构 */
export interface VersionInfo {
  version: string
  buildTs: number
  publishTime: string
  changelog: string
}

// ====================== 全局常量（统一维护默认值/正则） ======================
/** 插件唯一标识名称，日志打印使用 */
const PLUGIN_NAME = 'vite-plugin-version'
/** 默认更新日志文件名 */
const DEFAULT_CHANGELOG_NAME = 'CHANGELOG.md'
/** 目录创建配置：递归创建多级目录 */
const MKDIR_OPT = { recursive: true }
/** 兜底默认版本号 */
const DEFAULT_VERSION = '0.0.0'
/** 无日志时占位文案 */
const NO_CHANGELOG_TEXT = '# 暂无更新日志'

/**
 * 日志缺失时默认模板
 * @param version 当前版本号
 * @returns 填充版本的默认更新内容
 */
const getDefaultChangelog = (version: string) => `## ${version}\n\n- 系统更新`

/**
 * 正则匹配 CHANGELOG 首个版本块
 * 匹配格式：## [1.0.0] - 2026-07-30 或 ## [1.0.0] - 2026-07-30 12:00:00
 */
const VERSION_BLOCK_REG = /## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2})?([\s\S]*?)(?=\n## \[\d+\.\d+\.\d+\]|$)/

// ====================== 工具函数 ======================
/**
 * 从 changelog 文本中提取最新版本的更新内容
 * @param mdContent CHANGELOG.md 完整文本
 * @returns 最新版本更新描述文本
 */
function extractLatestChangelog(mdContent: string): string {
  const matchResult = mdContent.match(VERSION_BLOCK_REG)
  if (!matchResult) return NO_CHANGELOG_TEXT
  return matchResult[2].trim()
}

/**
 * 校验目录是否存在，不存在则递归创建
 * @param filePath 完整文件路径
 */
function ensureDirectoryExist(filePath: string): void {
  const targetDir = dirname(filePath)
  if (!existsSync(targetDir)) {
    mkdirSync(targetDir, MKDIR_OPT)
  }
}

// ====================== 插件主函数 ======================
/**
 * Vite 版本信息插件工厂函数
 * @param options 插件自定义配置
 * @returns Vite Plugin 实例
 */
export function versionPlugin(options: VersionPluginOptions = {}): Plugin {
  // 解构配置并赋予默认值
  const {
    version = DEFAULT_VERSION,
    changelogFile = DEFAULT_CHANGELOG_NAME,
    enableDevGenerate = false,
    buildTs = Date.now()
  } = options

  // 运行时缓存变量（Vite 配置解析后赋值）
  let projectRoot = ''
  let buildOutDir = 'dist'
  let isDevelopmentEnv = false

  /**
   * 核心逻辑：读取日志、组装版本对象、写入 version.json
   * @param targetJsonPath json 文件输出绝对路径
   */
  function generateVersionJsonFile(targetJsonPath: string): void {
    try {
      // 1. 拼接 changelog 绝对路径并读取内容
      const changelogAbsolutePath = resolve(projectRoot, changelogFile)
      let latestLogContent = ''

      if (existsSync(changelogAbsolutePath)) {
        const mdRawText = readFileSync(changelogAbsolutePath, 'utf-8')
        latestLogContent = extractLatestChangelog(mdRawText)
      } else {
        // 日志文件不存在，使用默认模板
        latestLogContent = getDefaultChangelog(version)
      }

      // 2. 组装标准版本信息对象
      const versionExportData: VersionInfo = {
        version,
        buildTs,
        publishTime: dayjs(buildTs).format('YYYY-MM-DD HH:mm:ss'),
        changelog: latestLogContent
      }

      // 3. 确保目录存在并写入 JSON 文件
      ensureDirectoryExist(targetJsonPath)
      writeFileSync(targetJsonPath, JSON.stringify(versionExportData, null, 2), 'utf-8')
      console.log(`[${PLUGIN_NAME}] ✅ v${version} 版本文件已生成 → ${targetJsonPath}`)
    } catch (error) {
      console.error(`[${PLUGIN_NAME}] ❌ 生成 version.json 异常`, error)
    }
  }

  return {
    name: PLUGIN_NAME,

    /**
     * Vite 钩子：配置完全解析完成后触发
     * @param config Vite 合并后的完整配置对象
     */
    configResolved(config: ResolvedConfig) {
      projectRoot = config.root
      buildOutDir = config.build.outDir || 'dist'
      isDevelopmentEnv = config.mode === 'development'
    },

    /**
     * Vite 钩子：开发服务启动时执行（仅 dev 模式）
     */
    configureServer() {
      // 非开发环境 / 未开启开发生成配置则直接跳过
      if (!isDevelopmentEnv || !enableDevGenerate) return
      const publicJsonPath = resolve(projectRoot, 'public/version.json')
      generateVersionJsonFile(publicJsonPath)
    },

    /**
     * Vite 钩子：打包完成后触发（仅 build 生产模式）
     */
    closeBundle() {
      if (isDevelopmentEnv) return
      const distJsonPath = resolve(projectRoot, buildOutDir, 'version.json')
      generateVersionJsonFile(distJsonPath)
    }
  }
}
