<script setup lang="ts">
import { ref } from 'vue'

const tagsViewHeight = ref('40px')

</script>

<template>
  <div class="layout-tagsview" :style="{ height: tagsViewHeight }">
    TAGS View
  </div>
</template>

<style scoped>

</style>
