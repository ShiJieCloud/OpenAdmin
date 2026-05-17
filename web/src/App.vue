<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const inputValue = ref('')
const handleClick = () => {
  ElMessage.success('Element Plus 集成成功！')
}
</script>

<template>
  <HelloWorld />
  <el-card class="demo-card">
    <template #header>
      <span>Element Plus 组件示例</span>
    </template>
    <el-space direction="vertical" :size="20">
      <el-input v-model="inputValue" placeholder="请输入内容" style="width: 300px" />
      <el-button type="primary" @click="handleClick">
        <i-ep-edit />
        点击测试
      </el-button>
      <el-tag type="success">标签一</el-tag>
      <el-tag type="warning">标签二</el-tag>
    </el-space>
  </el-card>
</template>

<style scoped>
.demo-card {
  max-width: 500px;
  margin: 20px auto;
}
</style>
