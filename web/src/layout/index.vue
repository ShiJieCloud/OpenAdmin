<script setup lang="ts">
import { onMounted } from 'vue'

import Header from './components/header/index.vue'
import Sidebar from './components/Sidebar.vue'
import Settings from './components/Settings.vue'
import PageTabs from './components/PageTabs.vue'

import { useLayoutStore, useMenuStore, useTabsStore } from '@/store'

const layoutStore = useLayoutStore()
const menuStore = useMenuStore()
const tabsStore = useTabsStore()

onMounted(() => {
  menuStore.loadUserMenu()
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

    <div class="layout-main flex-1">
      <router-view />
    </div>

    <Settings />
  </div>
</template>

<style scoped>
</style>