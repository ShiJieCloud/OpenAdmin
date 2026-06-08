<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElDrawer, ElButton, ElColorPicker, ElSwitch, ElSelect, ElOption } from 'element-plus'
import { LAYOUT, layoutList } from '@/types/modules/layout'

import { useLayoutStore, useThemeStore } from '@/store'

const layoutStore = useLayoutStore()
const themeStore = useThemeStore()

const settingsDrawerVisible = ref(false)
const themeMode = ref('light')
const fontType = ref('')
const showTags = ref(true)

const toggleSettings = () => {
    settingsDrawerVisible.value = !settingsDrawerVisible.value
}

const handleReset = () => {
    themeStore.resetPrimaryColor()
    layoutStore.setLayoutMode(LAYOUT.CLASSIC)
}

onMounted(() => {
    themeStore.initTheme()
})
</script>

<template>
    <!-- 悬浮设置按钮 -->
    <button @click="toggleSettings" class="fixed bottom-8 right-8 z-50 flex h-12 w-12 items-center 
           justify-center rounded-full border border-gray-200 bg-white 
           shadow-md transition-all hover:-translate-y-1 hover:bg-gray-50 
           hover:scale-105">
        <i-ep-setting class="text-2xl text-gray-600 hover:animate-spin hover:text-(--el-color-primary)" />
    </button>

    <!-- Element Plus 抽屉组件 -->
    <div class="settings-drawer">
        <ElDrawer v-model="settingsDrawerVisible" direction="rtl" size="320px">
            <template #header>
                <span class="text-lg font-medium">系统设置</span>
            </template>

            <template #default>
                <!-- 设置内容区域 -->
                <div class="space-y-6">
                    
                    <!-- 布局模式：经典 / 混合 / 超级 / 分栏 -->
                    <div class="space-y-3">
                        <h3 class="text-sm font-semibold text-gray-700">布局模式</h3>
                        <div class="grid grid-cols-2 gap-3">
                            <div v-for="layout in layoutList" :key="layout.value" class="flex flex-col items-center">
                                <el-tooltip :content="layout.desc" placement="top">
                                    <button @click="layoutStore.setLayoutMode(layout.value)"
                                        class="group relative flex flex-col items-center rounded-lg border-2 p-2 transition-all hover:shadow-md w-full"
                                        :class="layout.value === layoutStore.layoutMode ? 'border-(--el-color-primary)'
                                            : 'border-gray-200 bg-white hover:border-gray-300'">

                                        <!-- 选中指示器 -->
                                        <div v-if="layout.value === layoutStore.layoutMode"
                                            class="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-(--el-color-primary)">
                                            <i-ep-check class="text-xs text-white h-4 w-4" />
                                        </div>

                                        <!-- 布局缩略图 -->
                                        <div class="relative h-16 w-full overflow-hidden rounded bg-(--el-color-primary-light-9)">
                                            
                                            <!-- 经典布局-->
                                            <template v-if="layout.value === LAYOUT.CLASSIC">
                                                <div class="flex flex-row h-full w-full">
                                                    <div class="w-6 h-full rounded-sm bg-(--el-color-primary-dark-2)">
                                                    </div>
                                                    <div class="flex-1 flex flex-col gap-1 ml-1">
                                                        <div class="h-3 w-full rounded-sm bg-(--el-color-primary-light-5)">
                                                        </div>
                                                        <div class="flex-1 rounded-sm bg-(--el-color-primary-light-7)">
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>

                                            <!-- 混合布局 -->
                                            <template v-else-if="layout.value === LAYOUT.MIX">
                                                <div class="flex flex-col h-full w-full">
                                                    <div class="h-3 w-full rounded-sm bg-(--el-color-primary-light-5)">
                                                    </div>
                                                    <div class="flex-1 flex flex-row mt-1 gap-1">
                                                        <div class="w-6 h-full rounded-sm bg-(--el-color-primary-dark-2)">
                                                        </div>
                                                        <div class="flex-1 rounded-sm bg-(--el-color-primary-light-7)">
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>

                                            <!-- 分栏布局 -->
                                            <template v-else-if="layout.value === LAYOUT.COLUMN">
                                                <div class="flex flex-col h-full w-full">
                                                    <div class="h-3 w-full rounded-sm bg-(--el-color-primary-light-5)">
                                                    </div>
                                                    <div class="flex-1 flex flex-row mt-1 gap-1">
                                                        <div class="w-1/6 rounded-sm bg-(--el-color-primary-dark-2)">
                                                        </div>
                                                        <div class="w-1/7 rounded-sm bg-(--el-color-primary-light-3)">
                                                        </div>
                                                        <div class="flex-1 rounded-sm bg-(--el-color-primary-light-7)">
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>

                                            <!-- 超级菜单布局 -->
                                            <template v-else-if="layout.value === LAYOUT.MEGA">
                                                <div class="flex flex-row h-full w-full">
                                                    <div class="h-full w-6 rounded-sm flex flex-col pt-2 items-center gap-1 px-1 bg-(--el-color-primary-dark-2)">
                                                        <div class="w-3 h-1 rounded-sm bg-(--el-color-primary-light-3)">
                                                        </div>
                                                        <div class="w-2 h-1 rounded-sm bg-(--el-color-primary-light-3)">
                                                        </div>
                                                        <div class="w-3 h-1 rounded-sm bg-(--el-color-primary-light-3)">
                                                        </div>
                                                    </div>
                                                    <div class="flex-1 bg-white border rounded-sm p-1 grid grid-cols-3 gap-0.5 border-(--el-color-primary-light-8)">
                                                        <div class="flex flex-col gap-0.5" v-for="i in 3" :key="i">
                                                            <div class="h-1 rounded-sm bg-(--el-color-primary-light-5)">
                                                            </div>
                                                            <div class="h-0.5 rounded-sm bg-(--el-color-primary-light-7)">
                                                            </div>
                                                            <div class="h-0.5 rounded-sm bg-(--el-color-primary-light-7)">
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>
                                        </div>
                                    </button>
                                </el-tooltip>

                                <!-- 布局名称 -->
                                <span class="text-xs font-medium mt-2"
                                    :class="layout.value === layoutStore.layoutMode ? 'text-(--el-color-primary)' : 'text-gray-700'">
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
                            <ElColorPicker v-model="themeStore.primaryColor" class="w-[160px]" />
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
                            <ElSwitch v-model="themeStore.switchBreadcrumb" />
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
                <div class="flex">
                    <ElButton type="danger" plain class="flex-1" @click="handleReset">
                        恢复默认设置
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