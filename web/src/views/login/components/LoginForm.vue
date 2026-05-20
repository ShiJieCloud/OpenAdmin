<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import { getCaptcha } from '@/api/modules/auth'
import type { PasswordLoginRequest } from '@/types'



const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const userStore = useUserStore()
const captchaUrl = ref('')
const captchaId = ref('')

const loginForm = reactive<PasswordLoginRequest>({
  username: '',
  password: '',
  captcha_id: '',
  captcha_code: ''
})

const rules: FormRules<PasswordLoginRequest> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20个字符', trigger: 'blur' }
  ],
  captcha_code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 6, max: 6, message: '验证码长度为 6 位', trigger: 'blur' }
  ]
}

const refreshCaptcha = async () => {
  try {
    const data = await getCaptcha()
    captchaUrl.value = data.captcha_image
    captchaId.value = data.captcha_id
    loginForm.captcha_code = ''
  } catch (error) {

  }
}

const handleLogin = async (formEl: FormInstance | undefined) => {
  // 1. 触发全量表单校验（修复你原来的异步问题）
  if (!formEl) return
  const valid = await formEl.validate()
  if (!valid) return

  try {
    loading.value = true

    // 2. 发起登录请求
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
      captcha_id: captchaId.value,
      captcha_code: loginForm.captcha_code
    })

    // 3. 登录成功
    ElMessage.success('登录成功')
    setTimeout(() => {
      window.location.href = '/'
    }, 800)

  } catch (error) {
    // 4. 登录失败：提示 + 清空验证码
    const err = error as Error
    loginForm.captcha_code = '' // 清空验证码输入框

    return false

  } finally {
    // 5. 无论成功失败，关闭 loading
    loading.value = false
  }
}

const handleReset = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
  refreshCaptcha()
}

onMounted(() => {
  refreshCaptcha()
})
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

      <el-form-item prop="password" class="form-item">
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

      <el-form-item prop="captcha_code" class="form-item">
        <div class="captcha-row">
          <el-input
            v-model="loginForm.captcha_code"
            placeholder="验证码"
            clearable
            class="captcha-input"
          >
            <template #prefix>
              <i-mdi-shield-outline />
            </template>
          </el-input>
          <img
            v-if="captchaUrl"
            :src="captchaUrl"
            alt="验证码"
            class="captcha-img"
            @click="refreshCaptcha"
          />
        </div>
      </el-form-item>

      <el-form-item class="form-item">
        <div class="forgot-row">
          <a href="#" class="forgot-link">忘记密码？</a>
        </div>
      </el-form-item>

      <el-form-item class="form-item">
        <el-button
          type="primary"
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

.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-img {
  width: 120px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  background: #f5f5f5;
}

.forgot-row {
  display: flex;
  justify-content: flex-end;
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
</style>