<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

interface LoginFormData {
  username: string
  password: string
  remember: boolean
}

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive<LoginFormData>({
  username: '',
  password: '',
  remember: false
})

const rules: FormRules<LoginFormData> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20个字符', trigger: 'blur' }
  ]
}

const handleLogin = async (formEl: FormInstance | undefined) => {
  if (!formEl) return

  try {
    await formEl.validate()
    loading.value = true

    setTimeout(() => {
      loading.value = false
      ElMessage.success('登录成功')
      console.log('login form data:', loginForm)
    }, 1500)
  } catch (error) {
    ElMessage.error('请完善登录信息')
    return false
  }
}

const handleReset = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}
</script>

<template>
  <div class="login-form-container">
    <div class="form-header">
      <h2 class="text-2xl font-bold text-gray-800">欢迎登录</h2>
      <p class="text-sm text-gray-500 mt-1">请输入您的账号信息</p>
    </div>

    <el-form
      ref="loginFormRef"
      :model="loginForm"
      :rules="rules"
      class="login-form"
      size="large"
    >
      <el-form-item prop="username" class="form-item">
        <el-input
          v-model="loginForm.username"
          placeholder="用户名"
          clearable
        >
          <template #prefix>
            <i-ep-user />
          </template>
        </el-input>
      </el-form-item>

      <el-form-item prop="password" class="form-item password-item">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="密码"
          show-password
          clearable
        >
          <template #prefix>
            <i-ep-lock />
          </template>
        </el-input>
      </el-form-item>

      <el-form-item class="form-item">
        <div class="remember-row">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <a href="#" class="forgot-link">忘记密码？</a>
        </div>
      </el-form-item>

      <el-form-item class="form-item">
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="submit-btn"
          @click="handleLogin(loginFormRef)"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </el-button>
      </el-form-item>

      <el-form-item class="form-item">
        <el-button class="reset-btn" @click="handleReset(loginFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.login-form-container {
  width: 100%;
  max-width: 380px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item :deep(.el-form-item__error) {
  font-size: 12px;
}

.remember-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.forgot-link {
  font-size: 14px;
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

.forgot-link:hover {
  color: #66b1ff;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
}

.reset-btn {
  width: 100%;
  height: 40px;
  border-radius: 8px;
}

.password-item {
  margin-bottom: 10px;
}
</style>
