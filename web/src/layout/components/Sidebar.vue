<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isCollapsed = ref(false)

const menuItems = ref([
  {
    name: 'dashboard',
    label: '首页',
    icon: 'i-ep-home',
    path: '/dashboard',
    children: []
  },
  {
    name: 'system',
    label: '系统管理',
    icon: 'i-ep-setting',
    children: [
      { name: 'user', label: '用户管理', path: '/system/user' },
      { name: 'role', label: '角色管理', path: '/system/role' },
      { name: 'menu', label: '菜单管理', path: '/system/menu' },
      { name: 'dept', label: '部门管理', path: '/system/dept' }
    ]
  },
  {
    name: 'content',
    label: '内容管理',
    icon: 'i-ep-document',
    children: [
      { name: 'article', label: '文章管理', path: '/content/article' },
      { name: 'category', label: '分类管理', path: '/content/category' },
      { name: 'comment', label: '评论管理', path: '/content/comment' }
    ]
  },
  {
    name: 'data',
    label: '数据统计',
    icon: 'i-ep-bar-chart',
    path: '/data',
    children: []
  },
  {
    name: 'tools',
    label: '工具管理',
    icon: 'i-ep-tools',
    children: [
      { name: 'log', label: '操作日志', path: '/tools/log' },
      { name: 'config', label: '系统配置', path: '/tools/config' }
    ]
  }
])

</script>

<template>
  <aside class="layout-sidebar" :class="{ collapsed: isCollapsed }">
    Sidebar
  </aside>
</template>

<style scoped>

</style>
