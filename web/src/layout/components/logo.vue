<script setup lang="ts">
import { ref } from 'vue'

const isCollapsed = ref(false)
</script>
<template>
  <div class="h-full w-full flex items-center justify-center gap-1 cursor-pointer">
    <img src="@/assets/vue.svg" alt="Logo" />
    <el-badge v-show="!isCollapsed" size="small" :value="'v1.0.0'">
      <span class="text-lg font-text font-bold">
        OpenAdmin
      </span>
    </el-badge>
  </div>
</template>

<style scoped>

</style>
