<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Logo from './logo.vue'
import { useLayoutStore } from '@/store/modules/layout'
import { LAYOUT } from '@/types/modules/layout'
import MenuItem from '@/components/menu/MenuItem.vue'
import { useMenuStore } from '@/store/modules/menu'
import type { IMenuItem } from '@/types/modules/menu'

const menuStore = useMenuStore()
const layoutStore = useLayoutStore()

const menuList = ref<IMenuItem[]>([
  { id: 1, parent_id: 0, name: 'dashboard', label: '首页', icon: 'iconamoon:home', path: '/dashboard', component: 'dashboard/index.vue' },
  { id: 2, parent_id: 0, name: 'system', label: '系统管理', icon: 'ep:setting', path: '/system', component: '' },
  { id: 21, parent_id: 2, name: 'user', label: '用户管理', path: '/system/user', icon: 'iconamoon:user', component: '' },
  { id: 211, parent_id: 21, name: 'user-online', label: '在线用户', path: '/system/user/online', icon: 'iconamoon:user-online', component: 'system/user/OnlineUser.vue' },
  { id: 212, parent_id: 21, name: 'user-detail', label: '用户详情', path: '/system/user/detail', icon: 'iconamoon:user-detail', component: 'dashboard/index.vue' },
  { id: 213, parent_id: 21, name: 'user-roles', label: '角色分配', path: '/system/user/roles', icon: 'iconamoon:user-roles', component: 'dashboard/index.vue' },
  { id: 22, parent_id: 2, name: 'role', label: '角色管理', path: '/system/role', icon: 'iconamoon:role', component: 'dashboard/index.vue' },
  { id: 23, parent_id: 2, name: 'menu', label: '菜单管理', path: '/system/menu', icon: 'iconamoon:menu', component: 'dashboard/index.vue' },
  { id: 24, parent_id: 2, name: 'dept', label: '部门管理', path: '/system/dept', icon: 'iconamoon:dept', component: 'dashboard/index.vue' },
  { id: 3, parent_id: 0, name: 'content', label: '内容管理', icon: 'ep:document', path: '/content', component: '' },
  { id: 31, parent_id: 3, name: 'article', label: '文章管理', path: '/content/article', icon: 'iconamoon:article', component: 'dashboard/index.vue' },
  { id: 32, parent_id: 3, name: 'category', label: '分类管理', path: '/content/category', icon: 'iconamoon:category', component: 'dashboard/index.vue' },
  { id: 33, parent_id: 3, name: 'comment', label: '评论管理', path: '/content/comment', icon: 'iconamoon:comment', component: 'dashboard/index.vue' },
  { id: 4, parent_id: 0, name: 'data', label: '数据统计', icon: 'ep:data-line', path: '/data', component: 'dashboard/index.vue' },
  { id: 5, parent_id: 0, name: 'tools', label: '工具管理', icon: 'ep:tools', path: '/tools', component: '' },
  { id: 51, parent_id: 5, name: 'log', label: '操作日志', path: '/tools/log', icon: 'iconamoon:log', component: 'dashboard/index.vue' },
  { id: 52, parent_id: 5, name: 'config', label: '系统配置', path: '/tools/config', icon: 'iconamoon:config', component: 'dashboard/index.vue' },
])


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

onMounted(() => {
  menuStore.setRawMenuList(menuList.value)
  console.log('动态路由配置...', menuStore.dynamicRoutes)
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

      <el-menu class="sidebar-menu" :default-active="
        layoutStore.layoutMode === LAYOUT.COLUMN ? String(menuStore.activeRootMenuId):String(menuStore.activeSubMenuId)" @select="menuStore.handleMenuClick">
        <MenuItem v-for="menu in renderMenuList" :key="menu.id" :item="menu"/>
      </el-menu>

      <div v-show="layoutStore.layoutMode === LAYOUT.MEGA">
        自定义菜单
      </div>
    </div>

    <!-- 右侧菜单 - 仅在分栏布局下显示 -->
    <div v-if="layoutStore.layoutMode === LAYOUT.COLUMN" class="layout-sidebar-submenu">
      <el-menu router class="sidebar-menu" :default-active="String(menuStore.activeSubMenuId)" @select="menuStore.handleMenuClick">
        <MenuItem v-for="menu in menuStore.currentSubMenu" :key="menu.id" :item="menu"/>
      </el-menu>
    </div>

  </aside>
</template>

<style scoped></style>