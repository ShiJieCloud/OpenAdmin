<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElDrawer, ElSwitch, ElSelect, ElOption, ElButton, ElColorPicker } from 'element-plus'
import { LayoutMode } from '@/types/modules/layout'

const isOpen = ref(false)

const themeMode = ref('light')
const showTags = ref(true)
const showBreadcrumb = ref(false)
const fontType = ref('default')

const toggleSettings = () => {
    isOpen.value = !isOpen.value
}

const handleReset = () => {
    themeMode.value = 'light'
    showTags.value = true
    showBreadcrumb.value = false
    fontType.value = 'default'
    layoutMode.value = LayoutMode.Classic
    primaryColor.value = '#409EFF'
}

const handleSave = () => {
    isOpen.value = false
}

const layoutMode = ref(LayoutMode.Classic)

const layouts = [
    { key: 'classic', label: '经典布局', desc: '侧边固定导航' },
    { key: 'mix', label: '混合布局', desc: '顶部+侧边双导航' },
    { key: 'column', label: '分栏布局', desc: '双栏联动导航' },
    { key: 'mega', label: '超级布局', desc: '聚合式菜单' },
]

/**
 * @description 将颜色字符串转换为 RGB 对象
 * @param {string} color 颜色字符串，支持格式：
 *   - 十六进制: #fff, #ffffff
 *   - RGB: rgb(255, 255, 255)
 *   - RGBA: rgba(255, 255, 255, 1)
 * @returns {{r: number, g: number, b: number}} 返回 RGB 对象
 */
function hexToRgb(color: string): { r: number; g: number; b: number } {
    // 移除首尾空格
    color = color.trim()

    // 处理 RGB/RGBA 格式
    const rgbMatch = color.match(/^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i)
    if (rgbMatch) {
        return {
            r: parseInt(rgbMatch[1], 10),
            g: parseInt(rgbMatch[2], 10),
            b: parseInt(rgbMatch[3], 10),
        }
    }

    // 处理十六进制格式
    let hexStr = color.replace('#', '')
    let r: number, g: number, b: number

    if (hexStr.length === 3) {
        r = parseInt(hexStr[0] + hexStr[0], 16)
        g = parseInt(hexStr[1] + hexStr[1], 16)
        b = parseInt(hexStr[2] + hexStr[2], 16)
    } else if (hexStr.length === 6) {
        r = parseInt(hexStr.slice(0, 2), 16)
        g = parseInt(hexStr.slice(2, 4), 16)
        b = parseInt(hexStr.slice(4, 6), 16)
    } else {
        // 默认返回灰色
        return { r: 128, g: 128, b: 128 }
    }

    return { r, g, b }
}

/**
 * @description 将 RGB 值转换为十六进制颜色字符串
 * @param {number} r 红色通道值 (0-255)
 * @param {number} g 绿色通道值 (0-255)
 * @param {number} b 蓝色通道值 (0-255)
 * @returns {string} 返回 #RRGGBB 格式的十六进制颜色字符串
 */
function rgbToHex(r: number, g: number, b: number): string {
    const hex = [r, g, b].map(v => {
        const h = Math.round(v).toString(16)
        return h.length === 1 ? '0' + h : h
    })
    return `#${hex.join('')}`
}

/**
 * @description Tint 混合模式（与 Sass 的 tint() 函数一致）
 * 将颜色与白色混合，percentage 表示白色占比
 * @param {string} color 源颜色
 * @param {number} percentage 白色百分比 (0-100)
 * @returns {string} 混合后的颜色
 * 
 * 示例：
 *   tint('#409EFF', 90) → 90%白色 + 10%原色 → 接近原色
 *   tint('#409EFF', 10) → 10%白色 + 90%原色 → 接近白色
 */
function tint(color: string, percentage: number): string {
    const rgb = hexToRgb(color)
    const ratio = percentage / 100
    const r = Math.round(rgb.r * (1 - ratio) + 255 * ratio)
    const g = Math.round(rgb.g * (1 - ratio) + 255 * ratio)
    const b = Math.round(rgb.b * (1 - ratio) + 255 * ratio)
    return rgbToHex(r, g, b)
}

/**
 * @description Shade 混合模式（与 Sass 的 shade() 函数一致）
 * 将颜色与黑色混合，percentage 表示黑色占比
 * @param {string} color 源颜色
 * @param {number} percentage 黑色百分比 (0-100)
 * @returns {string} 混合后的颜色
 */
function shade(color: string, percentage: number): string {
    const rgb = hexToRgb(color)
    const ratio = percentage / 100
    const r = Math.round(rgb.r * (1 - ratio))
    const g = Math.round(rgb.g * (1 - ratio))
    const b = Math.round(rgb.b * (1 - ratio))
    return rgbToHex(r, g, b)
}

// 用户只需要选：主色调
const primaryColor = ref('#409EFF')

/**
 * @description 生成 Element Plus 主题色阶（使用 Tint 混合模式）
 * @param {string} color 主色调十六进制值
 * 
 * Tint 混合模式算法（与 Sass/PostCSS 的 tint() 函数一致）：
 * - light-1: tint(90%) → 90%白色 + 10%原色 → 最接近原色
 * - light-2: tint(80%) → 80%白色 + 20%原色
 * - ...
 * - light-9: tint(10%) → 10%白色 + 90%原色 → 最接近白色
 * 
 * 对于主色 #409EFF，生成的色阶应为：
 * --el-color-primary: #409eff
 * --el-color-primary-light-1: #53a8ff
 * --el-color-primary-light-2: #66b1ff
 * --el-color-primary-light-3: #79bbff
 * --el-color-primary-light-4: #8cc5ff
 * --el-color-primary-light-5: #a0cfff
 * --el-color-primary-light-6: #b3d8ff
 * --el-color-primary-light-7: #c6e2ff
 * --el-color-primary-light-8: #d9ecff
 * --el-color-primary-light-9: #ecf5ff
 * --el-color-primary-dark-2: #337ecc
 */
const generateElementTheme = (color: string) => {
    const root = document.documentElement

    // 设置主色调
    root.style.setProperty('--el-color-primary', color)

    // 使用 Tint 混合模式生成 light 系列
    // tint(percentage): percentage 表示白色占比，数字越大颜色越浅
    const tintLevels = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for (let i = 1; i <= 9; i++) {
        const lightColor = tint(color, tintLevels[i - 1])
        root.style.setProperty(`--el-color-primary-light-${i}`, lightColor)
    }

    // 使用 Shade 混合模式生成 dark-2：比主色深一级
    root.style.setProperty('--el-color-primary-dark-2', shade(color, 20))
}

// 监听变化
watch(primaryColor, (val) => {
    generateElementTheme(val)
    localStorage.setItem('primaryColor', val)
})

// 初始化
onMounted(() => {
    const cache = '#409EFF'
    if (cache) {
        primaryColor.value = cache
    }
    generateElementTheme(primaryColor.value)
})
</script>

<template>
    <!-- 悬浮设置按钮 -->
    <button @click="toggleSettings" class="fixed bottom-8 right-8 z-50 flex h-12 w-12 items-center 
           justify-center rounded-full border border-gray-200 bg-white 
           shadow-md transition-all hover:-translate-y-1 hover:bg-gray-50 
           hover:scale-105">
        <i-ep-setting class="text-2xl text-gray-600 hover:animate-spin hover:text-blue-500" />
    </button>

    <!-- Element Plus 抽屉组件 -->
    <div class="settings-drawer">
        <ElDrawer v-model="isOpen" direction="rtl" size="320px">
            <template #header>
                <span class="text-lg font-medium">系统设置</span>
            </template>

            <template #default>
                <!-- 设置内容区域 -->
                <div class="space-y-6">
                    <!-- 布局模式：经典 / 简洁 / 混合 / 超级 -->
                    <div class="space-y-3">
                        <h3 class="text-sm font-semibold text-gray-700">布局模式</h3>
                        <div class="grid grid-cols-2 gap-3">
                            <div v-for="layout in layouts" :key="layout.key" class="flex flex-col items-center">
                                <button @click="layoutMode = layout.key"
                                    class="group relative flex flex-col items-center rounded-lg border-4 p-2 transition-all hover:shadow-md w-full"
                                    :class="layoutMode === layout.key ? 'border-[var(--el-color-primary)] bg-[var(--el-color-primary-light-9)]' 
                                    : 'border-gray-200 bg-white hover:border-gray-300'">
                                    <!-- 选中指示器 -->
                                    <div v-if="layoutMode === layout.key"
                                        class="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-[var(--el-color-primary)]">
                                        <i-ep-check class="text-xs text-white h-4 w-4" />
                                    </div>

                                    <!-- 布局缩略图 -->
                                    <div class="relative h-16 w-full overflow-hidden rounded bg-[var(--el-color-primary-light-9)]">
                                        <!-- 经典布局：侧边栏 + 顶部 + 内容 -->
                                        <template v-if="layout.key === 'classic'">
                                            <div class="flex flex-row h-full w-full">
                                                <div class="w-6 h-full rounded-sm bg-[var(--el-color-primary-dark-2)]"></div>
                                                
                                                <div class="flex-1 flex flex-col gap-1 ml-1">
                                                    <div class="h-3 w-full rounded-sm bg-[var(--el-color-primary-light-5)]"></div>
                                                    <div class="flex-1 rounded-sm bg-[var(--el-color-primary-light-7)]"></div>
                                                </div>
                                            </div>
                                        </template>

                                        <!-- 混合布局：可折叠侧边栏 + 顶部 + 内容 -->
                                        <template v-else-if="layout.key === 'mix'">
                                            <div class="flex flex-col h-full w-full">
                                                <div class="h-3 w-full rounded-sm bg-[var(--el-color-primary-light-5)]"></div>
                                                <div class="flex-1 flex flex-row mt-1 gap-1">
                                                    <div class="w-6 h-full rounded-sm bg-[var(--el-color-primary-dark-2)]"></div>
                                                    <div class="flex-1 rounded-sm bg-[var(--el-color-primary-light-7)]"></div>
                                                </div>
                                            </div>
                                        </template>

                                        <!-- 分栏布局 -->
                                        <template v-else-if="layout.key === 'column'">
                                            <div class="flex flex-col h-full w-full">
                                                <div class="h-3 w-full rounded-sm bg-[var(--el-color-primary-light-5)]"></div>
                                                <div class="flex-1 flex flex-row mt-1 gap-1">
                                                    <div class="w-1/6 rounded-sm bg-[var(--el-color-primary-dark-2)]"></div>
                                                    <div class="w-1/7 rounded-sm bg-[var(--el-color-primary-light-3)]"></div>
                                                    <div class="flex-1 rounded-sm bg-[var(--el-color-primary-light-7)]"></div>
                                                </div>
                                            </div>
                                        </template>

                                        <!-- 超级布局：完整功能 -->
                                        <template v-else-if="layout.key === 'mega'">
                                            <div class="flex flex-row h-full w-full">
                                                <div class="h-full w-6 rounded-sm flex flex-col pt-2 items-center gap-1 px-1 bg-[var(--el-color-primary-dark-2)]">
                                                    <div class="w-3 h-1 rounded-sm bg-[var(--el-color-primary-light-3)]"></div>
                                                    <div class="w-2 h-1 rounded-sm bg-[var(--el-color-primary-light-3)]"></div>
                                                    <div class="w-2 h-1 rounded-sm bg-[var(--el-color-primary-light-3)]"></div>
                                                    <div class="w-3 h-1 rounded-sm bg-[var(--el-color-primary-light-3)]"></div>
                                                </div>
                                                <div class="flex-1 bg-white border rounded-sm p-1 grid grid-cols-3 gap-0.5 border-[var(--el-color-primary-light-8)]">
                                                    <div class="flex flex-col gap-0.5" v-for="i in 3" :key="i">
                                                        <div class="h-1 rounded-sm bg-[var(--el-color-primary-light-5)]"></div>
                                                        <div class="h-0.5 rounded-sm bg-[var(--el-color-primary-light-7)]"></div>
                                                        <div class="h-0.5 rounded-sm bg-[var(--el-color-primary-light-7)]"></div>
                                                    </div>
                                                </div>
                                                
                                            </div>
                                        </template>
                                    </div>
                                </button>
                                
                                <!-- 布局名称（在卡片外部） -->
                                <span class="text-xs font-medium mt-2" :class="layoutMode === layout.key ? 'text-[var(--el-color-primary)]' : 'text-gray-700'">
                                    {{ layout.label }}
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- 主题设置 -->
                    <div class="space-y-4">
                        <h3 class="text-sm font-semibold text-gray-700">主题设置</h3>

                        <!-- 主题模式：左右布局 -->
                        <div class="flex items-center justify-between">
                            <p class="text-sm text-gray-600">主题模式</p>
                            <div class="w-40">
                                <ElSelect v-model="themeMode" placeholder="请选择主题">
                                <ElOption label="浅色模式" value="light" />
                                <ElOption label="深色模式" value="dark" />
                                <ElOption label="跟随系统" value="system" />
                                <ElOption label="灰色悼念模式" value="gray" />
                            </ElSelect>
                            </div>
                        </div>

                        <!-- 主题色：左右布局 -->
                        <div class="flex items-center justify-between">
                            <p class="text-sm text-gray-600">主题色</p>
                            <ElColorPicker v-model="primaryColor" show-alpha class="w-[160px]" />
                        </div>

                    </div>

                    <!-- 显示设置 -->
                    <div class="space-y-3">
                        <h3 class="text-sm font-semibold text-gray-700">显示设置</h3>
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600">显示标签</span>
                            <ElSwitch v-model="showTags" />
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-600">显示面包屑</span>
                            <ElSwitch v-model="showBreadcrumb" />
                        </div>
                    </div>

                    <!-- 字体设置 -->
                    <div class="space-y-3">
                        <h3 class="text-sm font-semibold text-gray-700">字体设置</h3>
                        <ElSelect v-model="fontType" placeholder="请选择字体">
                            <ElOption label="默认字体" value="default" />
                            <ElOption label="微软雅黑" value="microsoft" />
                            <ElOption label="宋体" value="songti" />
                            <ElOption label="黑体" value="heiti" />
                        </ElSelect>
                    </div>
                </div>
            </template>

            <template #footer>
                <!-- 操作按钮区域 -->
                <div class="flex gap-3">
                    <ElButton type="danger" plain class="flex-1" @click="handleReset">
                        恢复默认设置
                    </ElButton>
                    <ElButton type="primary" plain class="flex-1" @click="handleSave">
                        保存设置
                    </ElButton>
                </div>
            </template>
        </ElDrawer>
    </div>
</template>

<style scoped>
.settings-drawer:deep(.el-drawer__header) {
    margin-bottom: 0 !important;
}
</style>
