import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { tint, shade } from '@/utils/color'

// 生成 Element Plus 主题变量的逻辑（仍属于主题管理，无需拆分）
const generateElementTheme = (color: string) => {
    const root = document.documentElement

    root.style.setProperty('--el-color-primary', color)

    const tintLevels = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for (let i = 1; i <= 9; i++) {
        const lightColor = tint(color, tintLevels[i - 1])
        root.style.setProperty(`--el-color-primary-light-${i}`, lightColor)
    }

    root.style.setProperty('--el-color-primary-dark-2', shade(color, 20))
}

export const useThemeStore = defineStore(
    'theme',
    () => {
        const primaryColor = ref('#409EFF')

        // 是否显示面包屑
        const switchBreadcrumb = ref(true)

        const setPrimaryColor = (color: string) => {
            primaryColor.value = color
        }

        // 设置是否显示面包屑
        const setSwitchBreadcrumb = (show: boolean) => {
            switchBreadcrumb.value = show
        }

        const resetPrimaryColor = () => {
            primaryColor.value = '#409EFF'
        }

        const initTheme = () => {
            generateElementTheme(primaryColor.value)
        }

        watch(primaryColor, (val) => {
            generateElementTheme(val)
        })

        return {
            primaryColor,
            switchBreadcrumb,
            setPrimaryColor,
            setSwitchBreadcrumb,
            resetPrimaryColor,
            initTheme,
        }
    },
    {
        persist: true,
    }
)