<script setup lang="ts">
import { ref } from 'vue'
import Logo from '@/layout/components/logo.vue'
import { useLayoutStore, useMenuStore, useThemeStore } from '@/store'
import { LAYOUT } from '@/types/modules/layout'
import MenuItem from '@/components/menu/MenuItem.vue'
import UserAvatar from './components/UserAvatar.vue'

import Breadcrumb from '@/layout/components/Breadcrumb.vue'
import FullScreen from '@/components/common/FullScreen.vue'
import SearchDialog from '@/components/SearchDialog/index.vue'

const layoutStore = useLayoutStore()
const menuStore = useMenuStore()
const themeStore = useThemeStore()

const searchDialogRef = ref<InstanceType<typeof SearchDialog>>()

</script>

<template>
  <header class="layout-header flex items-center justify-between">
    <!-- 左侧区域 -->
    <div class="flex items-center header-left">
      <!-- Logo区域 -->
      <div v-show="layoutStore.layoutMode === LAYOUT.COLUMN || layoutStore.layoutMode === LAYOUT.MIX" class="header-logo">
        <Logo />
      </div>

      <!-- 面包屑区域 -->
      <div v-if="layoutStore.layoutMode !== LAYOUT.MIX && themeStore.switchBreadcrumb" class="header-breadcrumb">
        <Breadcrumb />
      </div>

      <el-menu class="header-menu" mode="horizontal" :ellipsis="false" :active="String(menuStore.activeRootMenuId)"
        :default-active="String(menuStore.activeRootMenuId)" v-if="layoutStore.layoutMode === LAYOUT.MIX"
        @select="menuStore.handleMenuClick">
        <MenuItem v-for="menu in menuStore.rootMenuList" :key="menu.id" :item="menu" />
      </el-menu>
    </div>

    <!-- 右侧按钮 -->
    <div class="flex items-center gap-2">

      <!-- 搜索按钮 -->
      <el-tooltip content="搜索 (Ctrl+K)" placement="bottom">
        <div class="header-settings-btn" @click="searchDialogRef?.open()">
          <el-icon>
            <i-ep-search />
          </el-icon>
        </div>
      </el-tooltip>

      <!-- 全屏按钮 -->
      <div class="header-settings-btn">
        <FullScreen />
      </div>

      <el-tooltip content="主题设置" placement="bottom-end">
        <el-icon class="header-settings-btn" @click="themeStore.toggleSettingsPanel">
          <i-solar-palette-broken />
        </el-icon>
      </el-tooltip>

      <!-- 用户头像区域 -->
      <UserAvatar />
    </div>

    <!-- 搜索弹窗 -->
    <SearchDialog ref="searchDialogRef" />

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

.header-settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
}
</style>
