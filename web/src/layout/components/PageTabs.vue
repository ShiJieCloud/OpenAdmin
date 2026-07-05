<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import type { ITabItem } from '@/types/modules/tabs'

const props = defineProps<{
  tabList: ITabItem[]
  activePath: string
}>()

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

const tabsWrapRef = ref<HTMLElement | null>(null)

const scrollLeft = () => {
  if (tabsWrapRef.value) {
    tabsWrapRef.value.scrollBy({ left: -200, behavior: 'smooth' })
  }
}

const scrollRight = () => {
  if (tabsWrapRef.value) {
    tabsWrapRef.value.scrollBy({ left: 200, behavior: 'smooth' })
  }
}

const handleWheel = (e: WheelEvent) => {
  if (!tabsWrapRef.value) return
  e.preventDefault()
  tabsWrapRef.value.scrollBy({ left: e.deltaY, behavior: 'auto' })
}

watch(() => props.activePath, () => {
  nextTick(() => {
    const activeTab = tabsWrapRef.value?.querySelector('.tab-item.active')
    if (activeTab) {
      activeTab.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    }
  })
})

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
  <div class="tabs-container">
    <div class="tabs-scroll-container">
      <div class="scroll-btn" @click="scrollLeft">
        <el-icon><i-ep-arrow-left /></el-icon>
      </div>

      <div ref="tabsWrapRef" class="tabs-wrap" @wheel="handleWheel">
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

      <div class="scroll-btn" @click="scrollRight">
        <el-icon><i-ep-arrow-right /></el-icon>
      </div>
    </div>

    <el-dropdown class="tabs-dropdown" placement="bottom-end">
      <span class="w-10 h-10 flex items-center justify-center cursor-pointer outline-none">
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
  white-space: nowrap;
  /* 文字不自动换行 */
  overflow: hidden;
  /* 超出部分隐藏 */
  text-overflow: ellipsis;
  /* 超出显示省略号 ... */
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