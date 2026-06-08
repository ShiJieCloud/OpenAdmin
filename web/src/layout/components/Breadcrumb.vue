<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { RouteLocationMatched } from 'vue-router'
import { Icon } from '@iconify/vue'

const route = useRoute()
const router = useRouter()

const breadcrumbList = computed((): RouteLocationMatched[] => {
  return route.matched.filter(item => item.meta?.title && !item.meta?.hidden)
})

const handleNavigate = (path: string) => {
  router.push(path)
}
</script>

<template>
  <div class="breadcrumb-container">
    <el-breadcrumb class="breadcrumb">
      <el-breadcrumb-item
        v-for="(item, index) in breadcrumbList"
        :key="item.name"
        :to="item.path"
      >
        <div class="breadcrumb-item">
          <el-icon v-if="item.meta?.icon">
            <Icon :icon="item.meta.icon as string" />
          </el-icon>
          <span>{{ item.meta?.title }}</span>
        </div>
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<style scoped>
.breadcrumb-container {
  display: flex;
  align-items: center;
}

.breadcrumb-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
</style>
