<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue'

import Header from './components/header/index.vue'
import Sidebar from './components/Sidebar.vue'
import Settings from './components/Settings.vue'
import PageTabs from './components/PageTabs.vue'
import MainContent from './components/MainContent.vue'
import AppUpdateDialog from '@/components/AppUpdateDialog/index.vue'

import { useLayoutStore, useMenuStore, useTabsStore } from '@/store'
import { initVersionChecker } from '@/utils/version-check'

const layoutStore = useLayoutStore()
const menuStore = useMenuStore()
const tabsStore = useTabsStore()

const updateDialogRef = ref<InstanceType<typeof AppUpdateDialog> | null>(null)

// 初始化版本检查器
const checker = initVersionChecker({
  interval: 10 * 60 * 1000, // 10分钟检查一次
  autoCheck: true,
})

// 浏览器切回窗口主动检测
const onVisibilityChange = async () => {
  if (!document.hidden) {
    await checker.checkNow()
  }
}

onMounted(() => {
  menuStore.loadUserMenu()

  // 启动自动检查，检测到更新时打开弹窗
  checker.start((newVersion) => {
    updateDialogRef.value?.open(newVersion)
  })

  document.addEventListener('visibilitychange', onVisibilityChange)
})

onUnmounted(() => {
  checker.destroy()
  document.removeEventListener('visibilitychange', onVisibilityChange)
})

</script>

<template>
  <div class="layout-container" :class="layoutStore.layoutMode">
    <div class="layout-sidebar">
      <Sidebar />
    </div>

    <div class="layout-header">
      <Header />
    </div>

    <div class="layout-tagsview">
      <PageTabs
        :tab-list="tabsStore.visitedTabs"
        :active-path="tabsStore.activePath"
        @tab-click="tabsStore.clickTab"
        @tab-close="tabsStore.removeTab"
        @tab-close-left="tabsStore.removeLeftTabs"
        @tab-close-right="tabsStore.removeRightTabs"
        @tab-close-others="tabsStore.removeOtherTabs"
        @tab-close-all="tabsStore.removeAllTabs"
        @tab-refresh="tabsStore.refreshTab"
      />
    </div>

    <div class="layout-main">
      <MainContent />
    </div>

    <Settings />

    <!-- 版本更新弹窗 -->
    <AppUpdateDialog ref="updateDialogRef" />
  </div>
</template>

<style scoped>
</style>