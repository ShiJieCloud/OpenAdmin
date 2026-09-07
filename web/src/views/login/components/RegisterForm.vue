<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { Lock, User, Iphone, Key } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { register } from '@/api'
import TermsDialog from './TermsDialog.vue'

const emit = defineEmits(['success'])

const formRef = ref<FormInstance>()
const loading = ref(false)
const counting = ref(0)
const termsVisible = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const form = reactive({
  name: '',
  phone: '',
  smsCode: '',
  password: '',
  confirmPassword: '',
  agree: false,
})

// ==================== 校验规则 ====================
const rules = {
  name: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (!value) {
          callback(new Error('请输入手机号'))
        } else if (!/^1[3-9]\d{9}$/.test(value)) {
          callback(new Error('请输入正确的手机号'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  smsCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码（至少8位，包含字母和数字）', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (!/[a-zA-Z]/.test(value) || !/\d/.test(value)) {
          callback(new Error('密码必须包含字母和数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change'],
    },
  ],
}

// ==================== 发送短信验证码 ====================
function sendSms() {
  formRef.value?.validateField('phone', (valid) => {
    if (!valid) return
    // 模拟发送短信验证码
    ElMessage.success(`验证码已发送至 ${form.phone}`)
    counting.value = 60
    timer = setInterval(() => {
      counting.value--
      if (counting.value <= 0) {
        clearInterval(timer as number)
        timer = null
      }
    }, 1000)
  })
}

// ==================== 密码强度 ====================
const strengthLevel = ref(0) // 0-3

function checkPasswordStrength() {
  const pwd = form.password
  if (!pwd) {
    strengthLevel.value = 0
    return
  }
  let score = 0
  if (pwd.length >= 8) score++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++
  if (/\d/.test(pwd)) score++
  if (/[^a-zA-Z0-9]/.test(pwd)) score++
  strengthLevel.value = Math.min(score, 3)
}

const strengthClass = (index: number) => {
  if (strengthLevel.value === 0) return ''
  if (index <= strengthLevel.value) {
    if (strengthLevel.value === 1) return 'weak'
    if (strengthLevel.value === 2) return 'medium'
    return 'strong'
  }
  return ''
}

// ==================== 注册逻辑 ====================
function handleSubmit() {
  if (loading.value) return
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return
    if (!form.agree) {
      ElMessage.warning('请先同意服务条款')
      return
    }
    loading.value = true
    try {
      await register({
        username: form.name,
        phone: form.phone,
        password: form.password,
        sms_code: form.smsCode,
      })
      ElNotification({
        title: '注册成功',
        message: '请使用新账号登录',
        type: 'success',
      })
      // 通知父组件：填充密码登录并切回登录页
      emit('success', { username: form.name })
    } catch {
      // 请求层已统一弹出错误信息
    } finally {
      loading.value = false
    }
  })
}

function showTerms() {
  termsVisible.value = true
}

onUnmounted(() => {
  if (timer) {
    clearInterval(timer as number)
    timer = null
  }
})
</script>

<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    size="large"
    @submit.prevent="handleSubmit"
  >
    <el-form-item prop="name">
      <el-input
        v-model="form.name"
        placeholder="请输入用户名"
        :prefix-icon="User"
        clearable
      />
    </el-form-item>
    <el-form-item prop="phone">
      <el-input
        v-model="form.phone"
        placeholder="请输入手机号"
        :prefix-icon="Iphone"
        :maxlength="11"
        clearable
      />
    </el-form-item>
    <el-form-item prop="smsCode">
      <div class="sms-row">
        <el-input
          v-model="form.smsCode"
          placeholder="请输入验证码"
          :prefix-icon="Key"
          :maxlength="6"
          clearable
        />
        <el-button
          class="sms-btn"
          :disabled="counting > 0"
          @click="sendSms"
        >
          {{ counting > 0 ? `${counting}s 后重发` : '获取验证码' }}
        </el-button>
      </div>
    </el-form-item>
    <el-form-item prop="password">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        :prefix-icon="Lock"
        show-password
        @input="checkPasswordStrength"
      />
      <div class="password-strength">
        <div
          v-for="i in 3"
          :key="i"
          class="strength-bar"
          :class="strengthClass(i)"
        ></div>
      </div>
    </el-form-item>
    <el-form-item prop="confirmPassword">
      <el-input
        v-model="form.confirmPassword"
        type="password"
        placeholder="请再次输入密码"
        :prefix-icon="Lock"
        show-password
      />
    </el-form-item>
    <el-form-item>
      <el-checkbox v-model="form.agree">
        <span class="flex gap-1">
      我已阅读并同意
      <el-link type="primary" :underline="false" @click="showTerms">《OpenAdmin 服务条款》</el-link>
    </span>
      </el-checkbox>
    </el-form-item>
    <el-button
      type="primary"
      class="submit-btn"
      :loading="loading"
      :disabled="!form.agree"
      native-type="submit"
    >
      注册
    </el-button>
    <p class="register-tip">注册即表示您同意我们的服务条款</p>

    <!-- 注册用户条款弹窗 -->
    <TermsDialog
      v-model="termsVisible"
      v-model:agreed="form.agree"
    />
  </el-form>
</template>

<style scoped>
.sms-row {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
}
.sms-row .el-input {
  flex: 1;
}
.sms-btn {
  flex-shrink: 0;
  width: 120px;
  border-radius: 8px;
}
.submit-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
  border-radius: 8px;
}

/* 密码强度 */
.password-strength {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  width: 100%;
  flex: 0 0 100%;
}
.strength-bar {
  flex: 1;
  height: 4px;
  border-radius: 999px;
  background: var(--el-fill-color);
  transition: all 0.35s ease;
}
.strength-bar.weak {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.45);
}
.strength-bar.medium {
  background: #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.45);
}
.strength-bar.strong {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.45);
}

.register-tip {
  text-align: center;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}
</style>
