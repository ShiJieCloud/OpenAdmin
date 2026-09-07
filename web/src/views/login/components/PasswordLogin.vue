<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Lock, Key, User, Refresh } from '@element-plus/icons-vue'
import { getCaptcha } from '@/api'
import { useUserStore } from '@/store'
import type { FormInstance } from 'element-plus'

const props = defineProps({
  prefillUsername: { type: String, default: '' },
})
const emit = defineEmits(['success'])

const router = useRouter()
const userStore = useUserStore()

const passwordLoginFormRef = ref<FormInstance>()
const loading = ref(false)
const captchaId = ref('')
const captchaImage = ref('')

const form = reactive({
  username: props.prefillUsername || '',
  password: '',
  captcha: '',
})

// 注册成功后由父组件传入用户名，自动填充
watch(
  () => props.prefillUsername,
  (val) => {
    if (val) form.username = val
  }
)

// ==================== 图形验证码（后端） ====================
async function loadCaptcha() {
  try {
    const data = await getCaptcha()
    captchaId.value = data.captcha_id
    captchaImage.value = data.captcha_image
  } catch (e) {
    // 请求层已统一弹出错误提示
    captchaImage.value = ''
  }
}

onMounted(() => {
  loadCaptcha()
})

// ==================== 表单校验规则 ====================
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 4, message: '请输入完整的验证码', trigger: 'blur' },
  ],
}

// ==================== 登录逻辑 ====================
async function handleSubmit() {
  if (loading.value) return
  await passwordLoginFormRef.value?.validate(async (valid) => {
    if (!valid) return
    if (!captchaId.value) {
      ElMessage.warning('验证码未加载，请点击验证码图片刷新')
      return
    }
    loading.value = true
    try {
      await userStore.passwordLogin({
        username: form.username,
        password: form.password,
        captcha_id: captchaId.value,
        captcha_code: form.captcha,
      })
      ElNotification({
        title: '登录成功',
        message: `欢迎回来，${form.username}`,
        type: 'success',
      })
      emit('success', { username: form.username })
      // 跳转首页，路由守卫会处理动态路由加载与重定向
      router.push('/')
    } catch (e) {
      // 请求层已统一弹出错误信息，此处仅刷新验证码
      loadCaptcha()
      form.captcha = ''
    } finally {
      loading.value = false
    }
  })
}

function handleForgot() {
  if (form.username) {
    ElMessage.success(`已向账号 ${form.username} 发送重置指引`)
  } else {
    ElMessage.warning('请先输入用户名')
  }
}
</script>

<template>
  <el-form
    ref="passwordLoginFormRef"
    :model="form"
    :rules="rules"
    size="large"
    label-position="top"
    @submit.prevent="handleSubmit"
  >
    <el-form-item prop="username">
      <el-input
        v-model="form.username"
        placeholder="请输入用户名"
        :prefix-icon="User"
        clearable
      />
    </el-form-item>
    <el-form-item prop="password">
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        :prefix-icon="Lock"
        show-password
        @keyup.enter="handleSubmit"
      />
    </el-form-item>
    <el-form-item prop="captcha">
      <div class="captcha-row">
        <el-input
          v-model="form.captcha"
          placeholder="请输入验证码"
          :prefix-icon="Key"
          clearable
          @keyup.enter="handleSubmit"
        />
        <img
          v-if="captchaImage"
          class="captcha-img"
          :src="captchaImage"
          title="点击刷新验证码"
          alt="验证码"
          @click="loadCaptcha"
        />
        <div v-else class="captcha-placeholder" @click="loadCaptcha">
          <el-icon><Refresh /></el-icon>
        </div>
      </div>
    </el-form-item>
    <div class="form-options">
      <el-link type="primary" :underline="false" @click="handleForgot">忘记密码？</el-link>
    </div>
    <el-button
      type="primary"
      class="submit-btn"
      :loading="loading"
      @click="handleSubmit"
      native-type="submit"
    >
      登录
    </el-button>
  </el-form>
</template>

<style scoped>
.form-options {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin: 4px 0 16px;
}
.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
}
.captcha-row .el-input {
  flex: 1;
}
.captcha-img {
  width: 120px;
  height: 40px;
  border-radius: 6px;
  border: 1px solid var(--el-border-color);
  cursor: pointer;
  flex-shrink: 0;
  transition: border-color 0.3s;
}
.captcha-img:hover {
  border-color: var(--el-color-primary);
}
.captcha-placeholder {
  width: 120px;
  height: 40px;
  border-radius: 6px;
  border: 1px dashed var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.submit-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
  border-radius: 8px;
}
</style>
