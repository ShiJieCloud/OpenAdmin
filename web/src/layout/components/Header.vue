<script setup lang="ts">
import Logo from './logo.vue'
import { useLayoutStore, useMenuStore, useThemeStore } from '@/store'
import { LAYOUT } from '@/types/modules/layout'
import MenuItem from '@/components/menu/MenuItem.vue'
import { useRoute } from 'vue-router'
import { ref, watch } from 'vue'

import type { RouteLocationMatched } from 'vue-router'
import Breadcrumb from './Breadcrumb.vue'

const layoutStore = useLayoutStore()
const menuStore = useMenuStore()
const themeStore = useThemeStore()

const route = useRoute()
// 面包屑数组
const breadcrumbList = ref<RouteLocationMatched[]>([])

// 监听路由变化，更新面包屑
watch(
  () => route.path,
  () => {
    // 过滤掉布局壳等不需要展示的路由，根据 meta 控制显隐
    breadcrumbList.value = route.matched.filter(
      item => item.meta?.title && !item.meta?.hidden
    )
    console.log(breadcrumbList.value)
  },
  { immediate: true }
)

</script>

<template>
  <header class="layout-header">
    <!-- Logo区域 -->
    <div v-show="layoutStore.layoutMode === LAYOUT.COLUMN || layoutStore.layoutMode === LAYOUT.MIX" class="header-logo">
      <Logo />
    </div>

    <!-- 面包屑区域 -->
    <div v-if="layoutStore.layoutMode !== LAYOUT.MIX && themeStore.switchBreadcrumb" class="header-breadcrumb">
      <Breadcrumb />
    </div>

    <el-menu class="header-menu" mode="horizontal" :active="String(menuStore.activeRootMenuId)"
      :default-active="String(menuStore.activeRootMenuId)"
      v-if="layoutStore.layoutMode === LAYOUT.MIX"
      @select="menuStore.handleMenuClick"
      >
      <MenuItem v-for="menu in menuStore.rootMenuList" :key="menu.id" :item="menu" />
    </el-menu>
  </header>
</template>

<style scoped>
.layout-header {
  display: flex;
  align-items: center;

  .header-menu {
    height: var(--header-height);
  }

  .header-breadcrumb {
    margin: 0 16px;
  }
}

.header-logo {
  display: flex;
  align-items: center;
  height: var(--header-height);
  width: var(--logo-width);
}
</style>
