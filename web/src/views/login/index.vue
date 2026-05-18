<script setup lang="ts">
import LoginForm from './components/LoginForm.vue'
</script>

<template>
  <div class="login-page">
    <div class="login-background">
      <div class="login-content">
        <LoginForm />
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-background {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.login-content {
  width: 100%;
  max-width: 1200px;
  display: flex;
  justify-content: flex-end;
}
</style>
