<script setup lang="ts">
import type { ITabItem } from '@/types/modules/tabs'

const props = defineProps<{
  tabList: ITabItem[]
  activePath: string
}>()

// 抽离事件类型，便于复用、注释
type TabEmits = {
  /** 点击标签 */
  'tab-click': [path: string]
  /** 关闭当前标签 */
  'tab-close': [path: string]
  /** 关闭左侧标签 */
  'tab-close-left': [path: string]
  /** 关闭右侧标签 */
  'tab-close-right': [path: string]
  /** 关闭其他标签 */
  'tab-close-others': [path: string]
  /** 关闭全部标签 */
  'tab-close-all': []
  /** 刷新当前标签页 */
  'tab-refresh': [path: string]
}

const emit = defineEmits<TabEmits>()

const handleTabClick = (path: string) => {
  emit('tab-click', path)
}

const handleClose = (path: string) => {
  const targetPath = path
  emit('tab-close', targetPath)
}

const handleCloseLeft = (path: string) => {
  const targetPath = path
  emit('tab-close-left', targetPath)
}

const handleCloseRight = (path: string) => {
  const targetPath = path
  emit('tab-close-right', targetPath)
}

const handleCloseOther = (path: string) => {
  const targetPath = path
  emit('tab-close-others', targetPath)
}

const handleCloseAll = () => {
  emit('tab-close-all')
}

const handleRefresh = (path: string) => {
  const targetPath = path
  emit('tab-refresh', targetPath)
}
</script>

<template>
  <div class="tabs-container w-full h-full flex items-center justify-between">
    <div class="tabs-wrap">
      <div v-for="item in tabList" :key="item.path" class="tab-item" :class="{ active: item.path === activePath }"
        @click="handleTabClick(item.path)">
        <div class="flex-center-gap">
          <el-icon><i-ep-setting /></el-icon>
          <span>{{ item.title }}</span>
        </div>

        <el-icon @click.stop="handleClose(item.path)" class="close-icon">
          <i-ep-close />
        </el-icon>
      </div>
    </div>

    <!-- 标签页更多操作下拉菜单 -->
    <el-dropdown placement="bottom-end">
      <span class="w-12 h-12 flex items-center justify-center cursor-pointer outline-none">
        <i-ep-more-filled />
      </span>

      <template #dropdown>
        <el-dropdown-menu>
          <!-- 关闭当前标签 -->
          <el-dropdown-item @click="handleClose(activePath)">
            <div class="flex-center-gap">
              <i-ep-close />
              <span>关闭当前</span>
            </div>
          </el-dropdown-item>

          <!-- 关闭左侧标签 -->
          <el-dropdown-item @click="handleCloseLeft(activePath)">
            <div class="flex-center-gap">
              <i-ep-d-arrow-left />
              <span>关闭左侧</span>
            </div>
          </el-dropdown-item>

          <!-- 关闭右侧标签 -->
          <el-dropdown-item @click="handleCloseRight(activePath)">
            <div class="flex-center-gap">
              <i-ep-d-arrow-right />
              <span>关闭右侧</span>
            </div>
          </el-dropdown-item>

          <!-- 关闭其他标签 -->
          <el-dropdown-item @click="handleCloseOther(activePath)">
            <div class="flex-center-gap">
              <i-ep-minus />
              <span>关闭其他</span>
            </div>
          </el-dropdown-item>

          <!-- 关闭全部标签 -->
          <el-dropdown-item @click="handleCloseAll">
            <div class="flex-center-gap">
              <i-ep-delete />
              <span>关闭全部</span>
            </div>
          </el-dropdown-item>

          <!-- 分割线 -->
          <el-dropdown-item divided @click="handleRefresh(activePath)">
            <div class="flex-center-gap">
              <i-ep-refresh />
              <span>刷新页面</span>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

  </div>
</template>

<style scoped>
.flex-center-gap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.close-icon {
  padding: 2px;
  border-radius: 8px;
  transition: all 0.2s ease-in-out;
  color: #999;
  cursor: pointer;
}

.close-icon:hover {
  color: #fff;
  background-color: var(--el-color-primary);
}
</style>