<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { refDebounced } from '@vueuse/core'
import { useMenuStore } from '@/store'

/**
 * 搜索结果项
 */
interface SearchResult {
  id: number
  label: string
  desc: string
  path: string
  groupLabel: string
}

/** 弹窗显示状态 */
const visible = ref(false)

/** 搜索关键词 */
const keyword = ref('')

/** 防抖关键词（300ms），避免频繁触发搜索计算 */
const debouncedKeyword = refDebounced(keyword, 300)

/** 当前高亮的结果索引 */
const activeIndex = ref(-1)

/** 搜索结果列表容器引用 */
const resultListRef = ref<HTMLElement>()

/** 输入框引用 */
const inputRef = ref<any>()

const menuStore = useMenuStore()

/** 扁平化菜单列表（仅含有效路径的叶子节点） */
const flatMenuList = computed(() => {
  return menuStore.rawMenuList.filter(item => !!item.path)
})

/** 搜索结果（基于防抖关键词，filter + map 合并为单次遍历） */
const searchResults = computed(() => {
  const kw = debouncedKeyword.value.trim().toLowerCase()
  if (!kw) return []

  return flatMenuList.value.reduce<SearchResult[]>((list, item) => {
    const label = item.label ?? ''
    const desc = item.description ?? ''
    if (`${label}${desc}`.toLowerCase().includes(kw)) {
      list.push({ id: item.id, label, desc, path: item.path!, groupLabel: '菜单' })
    }
    return list
  }, [])
})

/** 结果 id → 索引映射，O(1) 查找高亮位置（替代模板中 indexOf 的 O(n) 扫描） */
const resultIndexMap = computed(() => {
  const map = new Map<number, number>()
  searchResults.value.forEach((r, i) => map.set(r.id, i))
  return map
})

/** 按分组归类搜索结果 */
const groupedResults = computed(() => {
  const groups = new Map<string, SearchResult[]>()
  for (const r of searchResults.value) {
    const key = r.groupLabel || '其他'
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(r)
  }
  return Array.from(groups.entries())
})

/** 打开搜索弹窗 */
const open = () => {
  visible.value = true
  keyword.value = ''
  activeIndex.value = -1
  nextTick(() => {
    inputRef.value?.focus()
  })
}

/** 关闭弹窗 */
const close = () => {
  visible.value = false
  keyword.value = ''
  activeIndex.value = -1
}

/** 选中某条结果并跳转 */
const selectResult = (result: SearchResult) => {
  close()
  menuStore.handleMenuClick(String(result.id))
}

/** 键盘导航 - 上移 */
const moveUp = () => {
  if (searchResults.value.length === 0) return
  activeIndex.value = activeIndex.value <= 0 ? searchResults.value.length - 1 : activeIndex.value - 1
  scrollToActive()
}

/** 键盘导航 - 下移 */
const moveDown = () => {
  if (searchResults.value.length === 0) return
  activeIndex.value = activeIndex.value >= searchResults.value.length - 1 ? 0 : activeIndex.value + 1
  scrollToActive()
}

/** 键盘导航 - 确认选择 */
const confirmSelect = () => {
  if (activeIndex.value >= 0 && activeIndex.value < searchResults.value.length) {
    selectResult(searchResults.value[activeIndex.value])
  }
}

/** 滚动使高亮项可见（通过 data-index 精准查询，避免 querySelectorAll 全量扫描） */
const scrollToActive = () => {
  nextTick(() => {
    resultListRef.value
      ?.querySelector(`.search-result-item[data-index="${activeIndex.value}"]`)
      ?.scrollIntoView({ block: 'nearest' })
  })
}

/** 全局键盘快捷键 */
const handleKeydown = (e: KeyboardEvent) => {
  // Ctrl/Cmd + K 打开搜索
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    if (!visible.value) open()
  }
  // Esc 关闭
  if (e.key === 'Escape' && visible.value) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

defineExpose({ open })
</script>

<template>
  <el-dialog
    v-model="visible"
    :show-close="false"
    width="680px"
    :close-on-click-modal="true"
    :close-on-press-escape="false"
    append-to-body
    class="search-dialog"
    @closed="close"
  >
    <!-- 搜索输入区 -->
    <div class="search-input-wrapper">
      <el-icon class="search-icon">
        <i-ep-search />
      </el-icon>
      <el-input
        ref="inputRef"
        class="search-dialog-input"
        v-model="keyword"
        placeholder="全局搜索"
        clearable
        @keydown.up.prevent="moveUp"
        @keydown.down.prevent="moveDown"
        @keydown.enter.prevent="confirmSelect"
      />
    </div>

    <!-- 搜索结果区（基于防抖关键词显示，避免输入期间闪烁） -->
    <div v-if="debouncedKeyword" class="search-result-area" ref="resultListRef">
      <!-- 有结果 -->
      <template v-if="searchResults.length > 0">
        <div v-for="[group, items] in groupedResults" :key="group" class="search-group">
          <div class="search-group-title">{{ group }}</div>
          <div
            v-for="result in items"
            :key="result.id"
            class="search-result-item"
            :data-index="resultIndexMap.get(result.id)"
            :class="{ active: resultIndexMap.get(result.id) === activeIndex }"
            @click="selectResult(result)"
            @mouseenter="activeIndex = resultIndexMap.get(result.id)!"
          >
            <el-icon class="result-icon">
              <i-ep-document />
            </el-icon>
            <div class="result-content">
              <div class="result-label">{{ result.label }}</div>
              <div class="result-desc">{{ result.desc }}</div>
            </div>
            <el-icon class="result-enter-icon">
              <i-mi-enter />
            </el-icon>
          </div>
        </div>
      </template>

      <!-- 无结果 -->
      <div v-else class="search-empty">
        <el-icon class="empty-icon">
          <i-ep-search />
        </el-icon>
        <p class="empty-text">无法找到相关结果 "{{ keyword }}"</p>
      </div>
    </div>

    <!-- 底部快捷键提示 -->
    <div class="search-footer">
      <div class="footer-shortcuts">
        <div class="shortcut-group">
          <span class="key-box">
            <el-icon><i-mi-arrow-down /></el-icon>
          </span>
          <span class="key-box">
            <el-icon><i-mi-arrow-up /></el-icon>
          </span>
          <span class="key-label">切换</span>
        </div>
        <div class="shortcut-group">
          <span class="key-box">
            <el-icon><i-mi-enter /></el-icon>
          </span>
          <span class="key-label">选择</span>
        </div>
        <div class="shortcut-group">
          <span class="key-box">
            <el-icon><i-mdi-keyboard-esc /></el-icon>
          </span>
          <span class="key-label">关闭</span>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
/* 搜索输入区 */
.search-input-wrapper {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  gap: 12px;
}

.search-icon {
  font-size: 20px;
  color: var(--el-color-primary);
  flex-shrink: 0;
}

:deep(.search-dialog-input .el-input__wrapper) {
  box-shadow: none;
  padding: 0;
}

:deep(.search-dialog-input .el-input__inner) {
  font-size: 16px;
}

/* 搜索结果区 */
.search-result-area {
  max-height: 420px;
  overflow-y: auto;
  padding: 8px 0;
  background-color: var(--el-bg-color-page);
}

.search-group-title {
  padding: 8px 20px 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  cursor: pointer;
  gap: 12px;
  height: 64px;
  border-radius: 8px;
  margin: 4px 8px;
  transition: background-color 0.15s;
  border: 2px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color);

  &:hover,
  &.active {
    background-color: var(--el-color-primary-light-9);
  }

  &.active {
    background-color: var(--el-color-primary-light-8);
  }
}

.result-icon {
  font-size: 18px;
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
}

.result-label {
  flex: 1;
  font-size: 14px;
  color: var(--el-text-color-primary);

  :deep(mark) {
    background-color: var(--el-color-warning-light-3);
    color: inherit;
    padding: 0 2px;
    border-radius: 2px;
  }
}

.result-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.result-content {
  flex: 1;
}

.result-enter-icon {
  font-size: 16px;
  color: var(--el-text-color-placeholder);
  opacity: 0;
  transition: opacity 0.15s;

  .search-result-item:hover &,
  .search-result-item.active & {
    opacity: 1;
  }
}

/* 无结果 */
.search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

.empty-icon {
  font-size: 48px;
  color: var(--el-text-color-placeholder);
  margin-bottom: 16px;
}

.empty-text {
  font-size: 15px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

/* 底部快捷键提示 */
.search-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* 快捷键容器组 */
.footer-shortcuts {
  display: flex;
  gap: 16px;
  align-items: center;
}

.shortcut-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 快捷键盒子：统一固定尺寸、居中，图标/文字共用 */
.key-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  font-size: 12px;
  border-radius: 4px;
  box-shadow:
    inset 0 -2px #cdcde6,
    inset 0 0 1px 1px #fff,
    0 1px 2px 1px rgba(30, 35, 90, 0.4);

  .el-icon {
    font-size: 18px;
  }
}

.key-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

</style>
