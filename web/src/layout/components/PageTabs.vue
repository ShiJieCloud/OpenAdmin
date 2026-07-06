<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue'
import type { ITabItem } from '@/types/modules/tabs'
import type { DropdownInstance } from 'element-plus'

/**
 * @prop {ITabItem[]} tabList - 标签列表数据
 * @prop {string} activePath - 当前激活标签的路径
 */
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

/** 标签容器的 DOM 引用，用于滚动操作 */
const tabsWrapRef = ref<HTMLElement | null>(null)

/**
 * 右键菜单相关状态
 * 使用 Element Plus 的虚拟触发功能实现右键菜单
 */

/** 下拉菜单组件实例引用 */
const dropdownRef = ref<DropdownInstance>()
/** 当前右键点击的标签路径 */
const contextMenuPath = ref('')
/** 右键菜单弹出位置 */
const position = ref({
  top: 0,
  left: 0,
  bottom: 0,
  right: 0,
} as DOMRect)

/**
 * 虚拟触发引用对象
 * 通过 getBoundingClientRect 返回动态计算的位置，使下拉菜单定位到鼠标点击处
 */
const triggerRef = ref({
  getBoundingClientRect: () => position.value,
})

/**
 * 处理标签右键点击事件
 * @param {MouseEvent} event - 鼠标事件对象
 * @param {string} path - 被点击标签的路径
 */
const handleTabContextmenu = (event: MouseEvent, path: string) => {
  const { clientX, clientY } = event
  position.value = DOMRect.fromRect({
    x: clientX,
    y: clientY,
  })
  contextMenuPath.value = path
  event.preventDefault()
  dropdownRef.value?.handleOpen()
}

/**
 * 点击页面其他区域时关闭右键菜单
 */
const handleClickOutside = () => {
  dropdownRef.value?.handleClose()
}

/**
 * 组件挂载时注册全局点击事件监听
 */
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

/**
 * 组件卸载时移除全局点击事件监听，防止内存泄漏
 */
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

/**
 * 向左滚动标签容器
 */
const scrollLeft = () => {
  if (tabsWrapRef.value) {
    tabsWrapRef.value.scrollBy({ left: -200, behavior: 'smooth' })
  }
}

/**
 * 向右滚动标签容器
 */
const scrollRight = () => {
  if (tabsWrapRef.value) {
    tabsWrapRef.value.scrollBy({ left: 200, behavior: 'smooth' })
  }
}

/**
 * 处理标签容器的鼠标滚轮事件，实现横向滚动
 * @param {WheelEvent} e - 滚轮事件对象
 */
const handleWheel = (e: WheelEvent) => {
  if (!tabsWrapRef.value) return
  e.preventDefault()
  tabsWrapRef.value.scrollBy({ left: e.deltaY, behavior: 'auto' })
}

/**
 * 监听激活路径变化，自动滚动到激活的标签
 */
watch(() => props.activePath, () => {
  nextTick(() => {
    const activeTab = tabsWrapRef.value?.querySelector('.tab-item.active')
    if (activeTab) {
      activeTab.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    }
  })
})

/**
 * 处理标签点击事件
 * @param {string} path - 被点击标签的路径
 */
const handleTabClick = (path: string) => {
  emit('tab-click', path)
}

/**
 * 关闭指定标签
 * @param {string} path - 要关闭的标签路径
 */
const handleClose = (path: string) => {
  emit('tab-close', path)
}

/**
 * 关闭指定标签左侧的所有标签
 * @param {string} path - 参考标签的路径
 */
const handleCloseLeft = (path: string) => {
  emit('tab-close-left', path)
}

/**
 * 关闭指定标签右侧的所有标签
 * @param {string} path - 参考标签的路径
 */
const handleCloseRight = (path: string) => {
  emit('tab-close-right', path)
}

/**
 * 关闭除指定标签外的所有标签
 * @param {string} path - 要保留的标签路径
 */
const handleCloseOther = (path: string) => {
  emit('tab-close-others', path)
}

/**
 * 关闭所有标签
 */
const handleCloseAll = () => {
  emit('tab-close-all')
}

/**
 * 刷新指定标签页
 * @param {string} path - 要刷新的标签路径
 */
const handleRefresh = (path: string) => {
  emit('tab-refresh', path)
}
</script>

<template>
  <div class="tabs-container">
    <!-- 标签滚动容器 -->
    <div class="tabs-scroll-container">
      <!-- 左滚动按钮 -->
      <div class="scroll-btn" @click="scrollLeft">
        <el-icon><i-ep-arrow-left /></el-icon>
      </div>

      <!-- 标签列表容器 -->
      <div ref="tabsWrapRef" class="tabs-wrap" @wheel="handleWheel">
        <!-- 标签项 -->
        <div
          v-for="item in tabList"
          :key="item.path"
          class="tab-item"
          :class="{ active: item.path === activePath }"
          @click="handleTabClick(item.path)"
          @contextmenu="handleTabContextmenu($event, item.path)"
        >
          <div class="flex-center-gap">
            <el-icon><i-ep-setting /></el-icon>
            <span>{{ item.title }}</span>
          </div>

          <!-- 关闭按钮 -->
          <el-icon @click.stop="handleClose(item.path)" class="close-icon">
            <i-ep-close />
          </el-icon>
        </div>
      </div>

      <!-- 右滚动按钮 -->
      <div class="scroll-btn" @click="scrollRight">
        <el-icon><i-ep-arrow-right /></el-icon>
      </div>
    </div>

    <!-- 右键下拉菜单（虚拟触发） -->
    <el-dropdown
      ref="dropdownRef"
      :virtual-ref="triggerRef"
      :show-arrow="false"
      :popper-options="{
        modifiers: [{ name: 'offset', options: { offset: [0, 0] } }],
      }"
      virtual-triggering
      trigger="contextmenu"
      placement="bottom-start"
    >
      <template #dropdown>
        <el-dropdown-menu>
          <!-- 关闭当前标签 -->
          <el-dropdown-item @click="handleClose(contextMenuPath)">
            <div class="flex-center-gap">
              <i-ep-close />
              <span>关闭当前</span>
            </div>
          </el-dropdown-item>

          <!-- 关闭左侧标签 -->
          <el-dropdown-item @click="handleCloseLeft(contextMenuPath)">
            <div class="flex-center-gap">
              <i-ep-d-arrow-left />
              <span>关闭左侧</span>
            </div>
          </el-dropdown-item>

          <!-- 关闭右侧标签 -->
          <el-dropdown-item @click="handleCloseRight(contextMenuPath)">
            <div class="flex-center-gap">
              <i-ep-d-arrow-right />
              <span>关闭右侧</span>
            </div>
          </el-dropdown-item>

          <!-- 关闭其他标签 -->
          <el-dropdown-item @click="handleCloseOther(contextMenuPath)">
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
          <el-dropdown-item divided @click="handleRefresh(contextMenuPath)">
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
