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