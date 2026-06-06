<script setup lang="ts">
import Settings from './components/Settings.vue'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import { useLayoutStore } from '@/store'

const layoutStore = useLayoutStore()

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