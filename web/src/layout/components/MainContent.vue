<script setup lang="ts">
</script>

<template>
  <div class="main-container">
    <router-view v-slot="{ Component }">
      <KeepAlive>
        <component :is="Component" />
      </KeepAlive>
    </router-view>
  </div>
</template>

<style scoped>
.main-container {
  width: 100%;
  height: 100%;
  padding: 12px;
}
</style>
