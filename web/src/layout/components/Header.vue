<script setup lang="ts">
import Logo from './logo.vue'
import { useLayoutStore, useMenuStore } from '@/store'
import { LAYOUT } from '@/types/modules/layout'
import MenuItem from '@/components/menu/MenuItem.vue'

const layoutStore = useLayoutStore()
const menuStore = useMenuStore()

</script>

<template>
  <header class="layout-header">
    <!-- Logo区域 -->
    <div v-show="layoutStore.layoutMode === LAYOUT.COLUMN || layoutStore.layoutMode === LAYOUT.MIX" class="header-logo">
      <Logo />
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
}

.header-logo {
  display: flex;
  align-items: center;
  height: var(--header-height);
  width: var(--logo-width);
}
</style>
