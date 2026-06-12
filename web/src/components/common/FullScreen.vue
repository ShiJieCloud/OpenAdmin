<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { MaybeElementRef } from '@vueuse/core'
import { useFullscreen } from '@vueuse/core'

const props = defineProps<{
  target?: MaybeElementRef
}>()

const targetRef = ref<MaybeElementRef>(undefined)

watch(
  () => props.target,
  (newTarget) => {
    if (newTarget) {
      targetRef.value = newTarget
    }
  },
  { immediate: true }
)

const { isFullscreen, toggle } = useFullscreen(targetRef)

const tipText = computed(() => (isFullscreen.value ? '退出全屏' : '全屏显示'))
</script>

<template>
  <el-tooltip :content="tipText" placement="bottom">
    <span class="fullscreen-btn" @click="toggle">
      <el-icon>
        <i-ep-full-screen />
      </el-icon>
    </span>
  </el-tooltip>
</template>

<style scoped>
.fullscreen-btn {
  display: inline-flex;
  align-items: center;
  padding: 0 10px;
  height: 100%;
  cursor: pointer;
}
</style>