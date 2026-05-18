<script setup lang="ts">
import { ElMessage } from 'element-plus'

const handleClick = () => {
  ElMessage.success('Element Plus 集成成功！')
}
</script>

<template>
  <h1 class="text-3xl font-bold text-center">Hello World</h1>
  <el-button @click="handleClick"><i-ep-edit />测试按钮</el-button>
</template>

<style scoped>
.demo-card {
  max-width: 500px;
  margin: 20px auto;
}
</style>
