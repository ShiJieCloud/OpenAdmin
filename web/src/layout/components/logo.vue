<script setup lang="ts">
import { ref } from 'vue'

const isCollapsed = ref(false)
</script>
<template>
  <div class="h-full w-full flex items-center justify-center gap-2 cursor-pointer">
    <img src="@/assets/vue.svg" alt="Logo" />
    <span v-show="!isCollapsed" class="text-lg font-text font-bold">OpenAdmin</span>
  </div>
</template>

<style scoped>

</style>
