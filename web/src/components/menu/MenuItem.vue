<script setup lang="ts">
import { Icon } from '@iconify/vue';
import { defineAsyncComponent } from 'vue'
import type { IMenuItem } from '@/types/modules/menu'

// 递归引入自身组件
const MenuItem = defineAsyncComponent(() => import('./MenuItem.vue'))

// Props强类型约束，替换any
const props = defineProps<{
  item: IMenuItem
}>()

// 定义派发事件，参数为当前菜单对象
const emit = defineEmits<{
  'menu-click': [menuItem: IMenuItem]
}>()

// 封装点击函数（便于后续扩展埋点、权限拦截）
const handleMenuClick = () => {
  emit('menu-click', props.item)
}
</script>

<template>
  <!-- 有子菜单：折叠子菜单容器，自身不可点击 -->
  <el-sub-menu v-if="item.children && item.children.length > 0" :index="String(item.id)">
    <template #title>
      <el-icon v-if="item.icon">
        <Icon :icon="item.icon" />
      </el-icon>
      <span>{{ item.label }}</span>
    </template>
    <!-- 递归子项：子项点击时把子item向上抛出 -->
    <MenuItem
      v-for="child in item.children"
      :key="child.id"
      :item="child"
      @menu-click="emit('menu-click', $event)"
    />
  </el-sub-menu>

  <!-- 无子女菜单：绑定点击事件 -->
  <el-menu-item
    v-else
    :index="String(item.id)"
    @click="handleMenuClick"
  >
    <el-icon v-if="item.icon">
      <Icon :icon="item.icon" />
    </el-icon>
    <span>{{ item.label }}</span>
  </el-menu-item>
</template>

<style lang="css"></style>