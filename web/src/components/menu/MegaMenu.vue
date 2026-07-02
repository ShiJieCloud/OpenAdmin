<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { MegaMenuProps, MegaMenuEmits } from '@/types/modules/menu'
import { computed, readonly } from 'vue'

// 定义 props，支持外部自定义配置（优化默认值写法）
const props = withDefaults(defineProps<MegaMenuProps>(), {
  treeMenuList: () => [],
  currentRootMenuId: 0,
  currentSubMenuId: 0,
})

const emit = defineEmits<MegaMenuEmits>()

// 只读菜单列表（优化命名，语义更清晰）
const menuList = computed(() => readonly(props.treeMenuList))

</script>

<template>
  <!-- 根容器 - BEM 块级命名 -->
  <div class="mega-menu">
    <!-- 左侧一级菜单容器 - BEM 元素 -->
    <div class="mega-menu__root-bar">
      <!-- 一级菜单项 - BEM 元素 + 循环 -->
      <el-popover v-for="menu in menuList" :key="menu.id" placement="right-start"
        :trigger="menu.children?.length ? 'hover' : 'manual'" :open-delay="150" :close-delay="150" width="auto"
        teleported="false">
        <!-- 触发源：一级菜单项 -->
        <template #reference>
          <div class="mega-menu__root-item"
            :class="{ 'mega-menu__root-item--active': menu.id === props.currentRootMenuId }"
            @click="emit('root-click', String(menu.id))">
            <div class="mega-menu__root-icon">
              <el-icon>
                <Icon :icon="menu.icon || 'lucide:layout-grid'" />
              </el-icon>
            </div>
            <div class="mega-menu__root-label">{{ menu.label }}</div>
          </div>
        </template>

        <!-- 弹窗内容：二级菜单面板 -->
        <template v-if="menu.children?.length" #default>
          <div class="mega-menu__popover">
            <div class="mega-menu__group-wrap">
              <!-- 二级菜单分组 - BEM 元素 -->
              <div v-for="group in menu.children" :key="group.id" class="mega-menu__group">
                <div class="mega-menu__group-title">{{ group.label }}</div>
                <div class="mega-menu__group-items">
                  <!-- 三级菜单项 - BEM 元素 -->
                  <div v-for="child in group.children" :key="child.id" class="mega-menu__item"
                    @click="emit('item-click', String(child.id))">
                    <div class="mega-menu__item-content">
                      <div class="mega-menu__item-label"
                        :class="{ 'mega-menu__item-label--active': child.id === props.currentSubMenuId }">
                        {{ child.label }}
                      </div>
                      <div v-if="child.desc" class="mega-menu__item-desc">
                        {{ child.desc }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </el-popover>
    </div>
  </div>
</template>

<style scoped>
.mega-menu {
  /* 尺寸变量 */
  --mega-root-item-size: 56px;
  --mega-root-bar-width: 60px;

  position: relative;
  height: 100%;
}

/* 左侧一级菜单容器 */
.mega-menu__root-bar {
  width: var(--mega-root-bar-width);
  height: 100%;
  background: var(--el-bg-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 8px;
  gap: 4px;
  overflow-y: auto;
  overflow-x: hidden;
  flex-shrink: 0;
  z-index: 10;
  justify-content: center;
}

/* 滚动条隐藏 */
.mega-menu__root-bar::-webkit-scrollbar {
  width: 0;
}

/* 一级菜单项 */
.mega-menu__root-item {
  width: var(--mega-root-item-size);
  height: var(--mega-root-item-size);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  flex-shrink: 0;
}

/* 一级菜单项 hover 状态 */
.mega-menu__root-item:hover {
  background: var(--el-color-primary-light-9);
}

/* 一级菜单项激活状态 - BEM 修饰符 */
.mega-menu__root-item--active {
  background: var(--el-color-primary-light-8);
}

/* 激活状态左侧指示条 */
.mega-menu__root-item--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: var(--el-color-primary);
  border-radius: 0 2px 2px 0;
}

/* 一级菜单图标 */
.mega-menu__root-icon {
  font-size: 18px;
  color: var(--el-text-color-regular);
}

/* 激活状态图标颜色 */
.mega-menu__root-item--active .mega-menu__root-icon {
  color: var(--el-color-primary);
}

/* 一级菜单文字 */
.mega-menu__root-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: center;
  line-height: 1.2;
  word-break: break-all;
}

/* 激活状态文字颜色 */
.mega-menu__root-item--active .mega-menu__root-label {
  color: var(--el-text-color-primary);
}

/* 弹窗容器 */
.mega-menu__popover {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 3px;
}

/* 分组容器 */
.mega-menu__group-wrap {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 18px;
  min-width: 140px;
  max-width: min(720px, calc(100vw - 140px));
  max-height: 400px;
  overflow-y: auto;
}

/* 分组项 */
.mega-menu__group {
  min-width: 140px;
  max-width: 140px;
}

/* 分组标题 */
.mega-menu__group-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

/* 分组内菜单项容器 */
.mega-menu__group-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 子菜单项 */
.mega-menu__item {
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* 子菜单项内容容器 */
.mega-menu__item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

/* 子菜单项文字 */
.mega-menu__item-label {
  font-size: 14px;
  color: var(--el-text-color-primary);
  line-height: 1.4;
  transition: color 0.2s ease;
}

/* 子菜单项激活状态 - BEM 修饰符 */
.mega-menu__item-label--active {
  color: var(--el-color-primary-light-3);
}

/* 子菜单项 hover 状态 */
.mega-menu__item-label:hover {
  color: var(--el-color-primary);
}

/* 子菜单项描述 */
.mega-menu__item-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>