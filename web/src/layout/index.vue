<script setup lang="ts">

import { onMounted } from 'vue'

import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
import Settings from './components/Settings.vue'

import { useLayoutStore, useMenuStore } from '@/store'

// 实例化 Store
const layoutStore = useLayoutStore()
const menuStore = useMenuStore()

onMounted(() => {
  // 页面挂载完成，加载用户菜单数据
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

    <div class="layout-tagsview">TAGS View</div>

    <div class="layout-main flex-1">
      <router-view />
    </div>

    <Settings />
  </div>
</template>
<style scoped>

</style>