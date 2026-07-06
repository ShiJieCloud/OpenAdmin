<script setup lang="ts">
import { computed } from 'vue'

import Logo from './logo.vue'
import { LAYOUT } from '@/types/modules/layout'
import MenuItem from '@/components/menu/MenuItem.vue'
import MegaMenu from '@/components/menu/MegaMenu.vue'

import { useLayoutStore, useMenuStore } from '@/store'

const menuStore = useMenuStore()
const layoutStore = useLayoutStore()

// 根据布局匹配对应数据源
const renderMenuList = computed(() => {
  const mode = layoutStore.layoutMode
  switch (mode) {
    case LAYOUT.COLUMN:
      return menuStore.rootMenuList
    case LAYOUT.CLASSIC:
      return menuStore.treeMenuList
    case LAYOUT.MIX:
      return menuStore.currentSubMenu
    default:
      return []
  }
})

</script>

<template>
  <aside class="layout-sidebar">
    <!-- Logo区域 -->
    <div v-show="layoutStore.layoutMode === LAYOUT.CLASSIC || layoutStore.layoutMode === LAYOUT.MEGA"
      class="sidebar-logo">
      <Logo />
    </div>

    <!-- 左侧菜单 -->
    <div class="layout-sidebar-menu">
      <el-scrollbar class="sidebar-scrollbar">
        <el-menu v-if="layoutStore.layoutMode !== LAYOUT.MEGA" 
          class="sidebar-menu"
          :default-active="layoutStore.layoutMode === LAYOUT.COLUMN ? String(menuStore.activeRootMenuId) : String(menuStore.activeSubMenuId)"
          @select="menuStore.handleMenuClick">
          <MenuItem v-for="menu in renderMenuList" :key="menu.id" :item="menu" />
        </el-menu>

        <!-- MegaMenu - 仅在超级菜单布局下显示 -->
        <MegaMenu v-else 
          :treeMenuList="menuStore.treeMenuList" 
          :currentRootMenuId="menuStore.activeRootMenuId"
          :currentSubMenuId="menuStore.activeSubMenuId" 
          @root-click="menuStore.handleMenuClick"
          @item-click="menuStore.handleMenuClick" />
      </el-scrollbar>
    </div>


    <!-- 右侧菜单 - 仅在分栏布局下显示 -->
    <div v-if="layoutStore.layoutMode === LAYOUT.COLUMN" class="layout-sidebar-submenu">
      <el-scrollbar class="sidebar-scrollbar">
        <el-menu class="sidebar-menu" :default-active="String(menuStore.activeSubMenuId)"
          @select="menuStore.handleMenuClick">
          <MenuItem v-for="menu in menuStore.currentSubMenu" :key="menu.id" :item="menu" />
        </el-menu>
      </el-scrollbar>
    </div>

  </aside>
</template>

<style scoped></style>