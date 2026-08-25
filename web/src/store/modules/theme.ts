/**
 * @desc 主题全局状态仓库
 * @module store/theme
 * @author sjzhao
 * @createDate 2026-07-04
 * @business 主题色配置、暗黑模式切换、系统主题同步、Element Plus CSS变量生成
 * @remark 数据持久化pinia-plugin-persistedstate，刷新保留主题设置
 */
import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'
import { tint, shade, mix } from '@/utils/color'
import type { ThemeMode, FontType, ThemeConfig, CodeThemeMode, CodeThemeLabel } from '@/types/modules/theme'
import { THEME_MODE, FONT_TYPE, CODE_THEME_MODE, CODE_THEME_LABEL } from '@/types/modules/theme'

/**
 * @constant DEFAULT_THEME
 * @desc 默认主题配置
 */
export const DEFAULT_THEME: ThemeConfig = {
  primaryColor: '#409EFF',
  themeMode: THEME_MODE.Light,
  showTags: true,
  showBreadcrumb: true,
  showFooter: true,
  showSettingsPanel: false,
  fontType: FONT_TYPE.Default,
  codeTheme: CODE_THEME_MODE['github-light'],
}

/**
 * @constant darkModeMedia
 * @desc 系统暗黑模式媒体查询
 */
const darkModeMedia = window.matchMedia('(prefers-color-scheme: dark)')

/**
 * @constant fontMap
 * @desc 字体类型与自定义字体名字符串映射表
 */
const fontMap: Record<FontType, string> = {
  [FONT_TYPE.Default]: '',
  [FONT_TYPE.JetBrainsMono]: 'JetBrains Mono',
  [FONT_TYPE.HuiWenMingChao]: 'HuiWenMingChao',
  [FONT_TYPE.SlideXiaxing]: 'Slide Xiaxing',
  [FONT_TYPE.OPPOSans]: 'OPPO Sans',
  [FONT_TYPE.HarmonyOSSansSC]: 'HarmonyOS Sans',
  [FONT_TYPE.AlibabaPuHuiTi]: 'Alibaba PuHuiTi'
}

/**
 * @function generateElementTheme
 * @desc 批量生成 Element Plus 主题色并一次性设置 CSS 变量
 * @param {string} color 主色值
 * @param {boolean} isDark 是否暗黑模式
 */
const generateElementTheme = (color: string, isDark: boolean) => {
  const cssLines: string[] = []

  cssLines.push(`--el-color-primary: ${color};`)

  const levels = [10, 20, 30, 40, 50, 60, 70, 80, 90]
  levels.forEach((level, index) => {
    const i = index + 1
    const lightColor = isDark
      ? mix(color, '#141414', level)
      : tint(color, level)
    cssLines.push(`--el-color-primary-light-${i}: ${lightColor};`)
  })

  const dark2Color = isDark
    ? mix(color, '#ffffff', 20)
    : shade(color, 20)
  cssLines.push(`--el-color-primary-dark-2: ${dark2Color};`)

  document.documentElement.style.cssText += cssLines.join('')
}

export const useThemeStore = defineStore(
  'theme',
  () => {
    // #region State
    /**
     * @var primaryColor
     * @desc 当前主题主色值
     */
    const primaryColor = ref(DEFAULT_THEME.primaryColor)

    /**
     * @var themeMode
     * @desc 主题模式：Light/Dark/Gray/System
     */
    const themeMode = ref<ThemeMode>(DEFAULT_THEME.themeMode)

    /**
     * @var showTags
     * @desc 是否显示标签页
     */
    const showTags = ref(DEFAULT_THEME.showTags)

    /**
     * @var switchBreadcrumb
     * @desc 是否显示面包屑导航
     */
    const switchBreadcrumb = ref(DEFAULT_THEME.showBreadcrumb)

    /**
     * @var switchFooter
     * @desc 是否显示页脚
     */
    const switchFooter = ref(DEFAULT_THEME.showFooter)

    /**
     * @var switchSettingsPanel
     * @desc 设置面板展开/收起状态
     */
    const switchSettingsPanel = ref(DEFAULT_THEME.showSettingsPanel)

    /**
     * @var isDarkMode
     * @desc 当前是否为暗黑模式（实际生效的模式）
     */
    const isDarkMode = ref(darkModeMedia.matches)

    /**
     * @var fontType
     * @desc 当前字体类型
     */
    const fontType = ref<FontType>(DEFAULT_THEME.fontType)

    /**
     * @var codeTheme
     * @desc 代码高亮主题
     */
    const codeTheme = ref<CodeThemeLabel>(DEFAULT_THEME.codeTheme)
    // #endregion

    // #region Action
    /**
     * @method setPrimaryColor
     * @desc 设置主题主色值
     * @param {string} color 主色值
     */
    const setPrimaryColor = (color: string) => {
      primaryColor.value = color
    }

    /**
     * @method setThemeMode
     * @desc 设置主题模式
     * @param {ThemeMode} mode 主题模式枚举值
     */
    const setThemeMode = (mode: ThemeMode) => {
      themeMode.value = mode
    }

    /**
     * @method setSwitchBreadcrumb
     * @desc 设置面包屑显示/隐藏
     * @param {boolean} show 是否显示面包屑
     */
    const setSwitchBreadcrumb = (show: boolean) => {
      switchBreadcrumb.value = show
    }

    /**
     * @method setFontType
     * @desc 设置字体类型
     * @param {FontType} type 字体类型
     */
    const setFontType = (type: FontType) => {
      fontType.value = type
    }

    /**
     * @method setCodeTheme
     * @desc 设置代码高亮主题
     * @param {CodeThemeMode} theme 代码高亮主题枚举值
     */
    const applyCodeTheme = computed((): CodeThemeMode => {

      const SYSTEM_FLAG = CODE_THEME_LABEL['跟随系统']

      // 1. 非跟随系统，直接映射
      if (codeTheme.value !== SYSTEM_FLAG) {
        return codeTheme.value as CodeThemeMode
      }
      // 2. 跟随系统：读取全局暗黑状态自动切换
      return isDarkMode.value ? CODE_THEME_MODE['github-dark'] : CODE_THEME_MODE['github-light']
    })

    /**
     * @method applyFont
     * @desc 应用字体样式到根元素
     */
    const applyFont = () => {
      const root = document.documentElement
      const fontFamily = fontMap[fontType.value]
      if (fontFamily) {
        root.style.setProperty('--font-family', fontFamily)
      } else {
        root.style.removeProperty('--font-family')
      }
    }

    /**
     * @method resetPrimaryColor
     * @desc 重置主题主色为默认值
     */
    const resetPrimaryColor = () => {
      primaryColor.value = DEFAULT_THEME.primaryColor
    }

    /**
     * @method resetTheme
     * @desc 恢复所有主题配置为默认值
     */
    const resetTheme = () => {
      primaryColor.value = DEFAULT_THEME.primaryColor
      themeMode.value = DEFAULT_THEME.themeMode
      showTags.value = DEFAULT_THEME.showTags
      switchBreadcrumb.value = DEFAULT_THEME.showBreadcrumb
      switchFooter.value = DEFAULT_THEME.showFooter
      switchSettingsPanel.value = DEFAULT_THEME.showSettingsPanel
      fontType.value = DEFAULT_THEME.fontType
    }

    /**
     * @method toggleSettingsPanel
     * @desc 切换设置面板显示状态
     */
    const toggleSettingsPanel = () => {
      switchSettingsPanel.value = !switchSettingsPanel.value
    }

    /**
     * @method applyThemeClass
     * @desc 应用主题样式类到根元素
     */
    const applyThemeClass = () => {
      const root = document.documentElement
      root.classList.remove(THEME_MODE.Light, THEME_MODE.Dark, THEME_MODE.Gray)

      if (themeMode.value === THEME_MODE.Gray) {
        root.classList.add(THEME_MODE.Gray)
        return
      }

      root.classList.add(isDarkMode.value ? THEME_MODE.Dark : THEME_MODE.Light)
    }

    /**
     * @method handleSystemThemeChange
     * @desc 监听系统主题变化回调
     * @param {MediaQueryListEvent} e 媒体查询事件
     */
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      isDarkMode.value = e.matches
      applyThemeClass()
      console.log('System theme mode changed:', e.matches)
    }
    // #endregion

    /**
     * @watch themeMode
     * @desc 监听主题模式变化，处理系统模式切换与暗黑状态更新
     */
    watch(themeMode, (newMode, oldMode) => {
      if (oldMode === THEME_MODE.System) {
        darkModeMedia.removeEventListener('change', handleSystemThemeChange)
      }

      if (newMode === THEME_MODE.System) {
        isDarkMode.value = darkModeMedia.matches
        darkModeMedia.addEventListener('change', handleSystemThemeChange)
        applyThemeClass()
        return
      }

      isDarkMode.value = newMode === THEME_MODE.Dark
      applyThemeClass()
    }, { immediate: true })

    /**
     * @watch [primaryColor, isDarkMode]
     * @desc 监听主色或暗黑模式变化，重新生成 Element Plus 主题变量
     */
    watch([primaryColor, isDarkMode], ([color, isDark]) => {
      generateElementTheme(color, isDark)
    }, { immediate: true })

    /**
     * @watch fontType
     * @desc 监听字体类型变化，应用字体样式
     */
    watch(fontType, () => {
      applyFont()
    }, { immediate: true })

    return {
      // State
      primaryColor,
      themeMode,
      showTags,
      switchBreadcrumb,
      switchFooter,
      switchSettingsPanel,
      isDarkMode,
      fontType,
      codeTheme,
      // Action
      setPrimaryColor,
      setThemeMode,
      setSwitchBreadcrumb,
      setFontType,
      applyCodeTheme,
      resetPrimaryColor,
      resetTheme,
      toggleSettingsPanel,
    }
  },
  {
    /**
     * @config persist
     * @desc 开启pinia持久化，localStorage缓存主题设置状态
     * @omit isDarkMode 派生状态，由themeMode watcher计算，无需持久化
     */
    persist: {
      omit: ['isDarkMode'],
    },
  }
)
