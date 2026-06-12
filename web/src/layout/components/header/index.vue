<script setup lang="ts">
import Logo from '@/layout/components/logo.vue'
import { useLayoutStore, useMenuStore, useThemeStore } from '@/store'
import { LAYOUT } from '@/types/modules/layout'
import MenuItem from '@/components/menu/MenuItem.vue'
import { useRoute } from 'vue-router'
import { ref, watch } from 'vue'
import UserAvatar from './components/UserAvatar.vue'

import type { RouteLocationMatched } from 'vue-router'
import Breadcrumb from '@/layout/components/Breadcrumb.vue'
import FullScreen from '@/components/common/FullScreen.vue'

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
      :default-active="String(menuStore.activeRootMenuId)" v-if="layoutStore.layoutMode === LAYOUT.MIX"
      @select="menuStore.handleMenuClick">
      <MenuItem v-for="menu in menuStore.rootMenuList" :key="menu.id" :item="menu" />
    </el-menu>

    <!-- 全屏按钮 -->
    <div class="header-settings-btn">
      <FullScreen />
    </div>

    <!-- 设置面板按钮 -->
    <div >
      <el-tooltip content="主题设置" placement="bottom-end">
        <el-icon class="header-settings-btn" @click="themeStore.toggleSettingsPanel">
          <i-solar-palette-broken />
        </el-icon>
      </el-tooltip>
    </div>

    <!-- 用户头像区域 -->
    <UserAvatar />
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
  margin-right: 8px;
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
