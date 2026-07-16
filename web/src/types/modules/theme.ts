/**
 * @desc 主题模式枚举
 * @module types/theme
 */
export const THEME_MODE = {
  /** 明亮模式 */
  Light: 'light',
  /** 暗黑模式 */
  Dark: 'dark',
  /** 跟随系统主题 */
  System: 'system',
  /** 灰度模式 */
  Gray: 'gray'
} as const

/**
 * @type ThemeMode
 * @desc 主题模式联合类型，从 THEME_MODE 枚举值推导
 */
export type ThemeMode = typeof THEME_MODE[keyof typeof THEME_MODE]

export const FONT_TYPE = {
  Default: 'default',
  JetBrainsMono: 'jetbrainsmono',
  HuiWenMingChao: 'huiwenmingchao',
  SlideXiaxing: 'slidxiaxing',
  OPPOSans: 'opposans',
  HarmonyOSSansSC: 'harmonyossanssc',
  AlibabaPuHuiTi: 'alibabapuhuiti'
} as const

export type FontType = typeof FONT_TYPE[keyof typeof FONT_TYPE]

export const FONT_LABEL: Record<FontType, string> = {
  [FONT_TYPE.Default]: '默认字体',
  [FONT_TYPE.JetBrainsMono]: 'JetBrains Mono',
  [FONT_TYPE.HuiWenMingChao]: '汇文明潮',
  [FONT_TYPE.SlideXiaxing]: '夏行楷',
  [FONT_TYPE.OPPOSans]: 'OPPO Sans',
  [FONT_TYPE.HarmonyOSSansSC]: 'HarmonyOS Sans SC',
  [FONT_TYPE.AlibabaPuHuiTi]: '阿里巴巴普惠体'
}

export const THEME_MODE_LABEL: Record<ThemeMode, string> = {
  [THEME_MODE.Light]: '明亮模式',
  [THEME_MODE.Dark]: '暗黑模式',
  [THEME_MODE.System]: '跟随系统',
  [THEME_MODE.Gray]: '灰度模式'
}

export const CODE_THEME_MODE = {
  'github-light':'github-light',
  'github-dark':'github-dark',
  'solarized-light':'solarized-light',
  'houston':'houston',
} as const

// 自动生成联合类型
export type CodeThemeMode = typeof CODE_THEME_MODE[keyof typeof CODE_THEME_MODE]

export const CODE_THEME_LABEL = {
  '跟随系统':'system',
  'github-light':'github-light',
  'github-dark':'github-dark',
  'solarized-light':'solarized-light',
  'houston':'houston',
} as const

export type CodeThemeLabel = typeof CODE_THEME_LABEL[keyof typeof CODE_THEME_LABEL]

export const CODE_LANGS = [
  'javascript',
  'typescript',
  'vue',
  'json',
  'html',
  'css',
] as const

export type CodeLang = typeof CODE_LANGS[number]

export interface ThemeConfig {
  primaryColor: string
  themeMode: ThemeMode
  showBreadcrumb: boolean
  showSettingsPanel: boolean
  fontType: FontType
  codeTheme: CodeThemeMode
}