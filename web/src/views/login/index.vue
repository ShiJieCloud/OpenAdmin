
<script setup lang="ts">
import { ref, nextTick } from 'vue'
import {
  Platform,
  Lock,
  Lightning,
  Aim,
  Key,
  Avatar,
} from '@element-plus/icons-vue'
import PasswordLogin from './components/PasswordLogin.vue'
import FaceLogin from './components/FaceLogin.vue'
import RegisterForm from './components/RegisterForm.vue'
import { useThemeStore } from '@/store'
import { THEME_MODE } from '@/types/modules/theme'

// ==================== 响应式数据 ====================
const activeTab = ref<string>('login')
const loginMethod = ref<string>('password') // password | face
const prefillUsername = ref<string>('') // 注册成功后填充到密码登录

// ==================== 主题模式 ====================
const themeStore = useThemeStore()

interface LoginSuccessPayload {
  username?: string
  phone?: string
  method?: string
}

function toggleTheme(event: MouseEvent) {
  const doc = document as Document & {
    startViewTransition?: (cb: () => Promise<void>) => {
      ready: Promise<void>
      finished: Promise<void>
    }
  }
  // 是否切换到暗色（false 为切换到亮色）
  const isSwitchingToDark = !themeStore.isDarkMode
  const targetMode = isSwitchingToDark ? THEME_MODE.Dark : THEME_MODE.Light

  // 不支持 View Transition API 时直接切换
  if (typeof doc.startViewTransition !== 'function') {
    themeStore.setThemeMode(targetMode)
    return
  }

  const root = document.documentElement
  // 圆形扩散起点 = 点击位置；endRadius 为扩散至视口最远角的距离
  const { clientX: x, clientY: y } = event
  const endRadius = Math.hypot(
    Math.max(x, innerWidth - x),
    Math.max(y, innerHeight - y)
  )
  const circle = (r: number) => `circle(${r}px at ${x}px ${y}px)`

  // 在 startViewTransition 之前设置 z-index，伪元素创建时就确定层级：
  // 切暗色旧（亮）快照在上层缩小消失，切亮色新（亮）快照在上层向外扩散
  root.style.setProperty('--vt-old-z', isSwitchingToDark ? '9999' : '1')
  root.style.setProperty('--vt-new-z', isSwitchingToDark ? '1' : '9999')

  const transition = doc.startViewTransition(() => {
    themeStore.setThemeMode(targetMode)
    return nextTick()
  })

  // 切暗色动画作用于旧快照（满屏圆 → 点击点），切亮色作用于新快照（点击点 → 满屏圆）
  const [fromRadius, toRadius] = isSwitchingToDark
    ? [endRadius, 0]
    : [0, endRadius]

  transition.ready
    .then(() => {
      root.animate(
        { clipPath: [circle(fromRadius), circle(toRadius)] },
        {
          duration: 500,
          easing: 'ease-in-out',
          // fill: 'both'：首帧绘制前即应用起始裁剪；动画结束后保持末帧（切暗色时
          // 旧快照保持 circle(0)），避免伪元素移除前 clip-path 回弹导致亮色闪回
          fill: 'both',
          pseudoElement: `::view-transition-${isSwitchingToDark ? 'old' : 'new'}(root)`,
        }
      )
    })
    .catch(() => {
      // 快速连续切换时过渡被跳过，ready 会 reject，无需处理
    })

  // 过渡结束后清理临时 z-index 变量，避免污染根元素
  transition.finished
    .catch(() => {})
    .then(() => {
      root.style.removeProperty('--vt-old-z')
      root.style.removeProperty('--vt-new-z')
    })
}

// ==================== 登录/注册回调 ====================
function onLoginSuccess(payload: LoginSuccessPayload) {
  // 登录成功后的后续处理（如路由跳转）可在此扩展
  console.log('登录成功', payload)
}

function onRegisterSuccess({ username }: { username: string }) {
  // 注册成功：填充密码登录用户名并切回登录页
  prefillUsername.value = username
  loginMethod.value = 'password'
  activeTab.value = 'login'
}
</script>

<template>
  <div class="auth-page">
    <!-- 主卡片容器 -->
    <div class="auth-card">
      <!-- 主题模式开关 -->
      <div class="theme-toggle">
        <el-tooltip
          :content="themeStore.isDarkMode ? '切换为明亮模式' : '切换为暗黑模式'"
          placement="left"
        >
          <el-button circle class="theme-toggle-btn" @click="toggleTheme">
            <i-solar-sun-2-line-duotone v-if="themeStore.isDarkMode" />
            <i-solar-moon-stars-line-duotone v-else />
          </el-button>
        </el-tooltip>
      </div>
      <!-- 左侧品牌区 -->
      <div class="auth-brand">
        <div class="brand-logo">
          <el-icon :size="28" color="#fff"><Platform /></el-icon>
          <span class="brand-name">OpenAdmin</span>
        </div>
        <div class="brand-content">
          <h2>现代化后台管理<br />从登录开始</h2>
          <p>OpenAdmin 为您提供高效、安全、美观的管理体验。</p>
          <ul class="brand-features">
            <li><el-icon><Lock /></el-icon> 企业级安全防护</li>
            <li><el-icon><Lightning /></el-icon> 极速响应式设计</li>
            <li><el-icon><Aim /></el-icon> 灵活可配置组件</li>
          </ul>
        </div>
        <div class="brand-footer">© 2025 OpenAdmin · v2.4.1</div>
      </div>

      <!-- 右侧表单区 -->
      <div class="auth-form-panel">
        <el-tabs v-model="activeTab" class="auth-tabs" stretch>
          <el-tab-pane label="登录" name="login">
            <PasswordLogin
              v-if="loginMethod === 'password'"
              :prefill-username="prefillUsername"
              @success="onLoginSuccess"
            />
            <FaceLogin v-else @success="onLoginSuccess" />

            <!-- 登录方式切换 -->
            <div class="login-method-switch">
              <el-tooltip content="密码登录" placement="top">
                <el-button
                  circle
                  class="method-btn"
                  :type="loginMethod === 'password' ? 'primary' : 'default'"
                  @click="loginMethod = 'password'"
                >
                  <el-icon><Key /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="人脸识别" placement="top">
                <el-button
                  circle
                  class="method-btn"
                  :type="loginMethod === 'face' ? 'primary' : 'default'"
                  @click="loginMethod = 'face'"
                >
                  <el-icon><Avatar /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <RegisterForm @success="onRegisterSuccess" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== 页面整体 ==================== */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: var(--el-bg-color-page);
  position: relative;
  overflow: hidden;
}

/* 主卡片 */
.auth-card {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 960px;
  min-height: 580px;
  background: var(--el-bg-color);
  border-radius: 20px;
  box-shadow: var(--el-box-shadow);
  overflow: hidden;
  animation: cardEnter 0.6s ease-out;
}
@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 左侧品牌区 */
.auth-brand {
  flex: 1;
  background: linear-gradient(135deg, var(--el-color-primary) 0%, color-mix(in srgb, var(--el-color-primary), black 15%) 50%, color-mix(in srgb, var(--el-color-primary), black 30%) 100%);
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: var(--el-color-white);
  position: relative;
  overflow: hidden;
}
.auth-brand::before {
  content: '';
  position: absolute;
  top: -100px;
  right: -100px;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
}
.auth-brand::after {
  content: '';
  position: absolute;
  bottom: -80px;
  left: -60px;
  width: 250px;
  height: 250px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
}
.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}
.brand-name {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
}
.brand-content {
  position: relative;
  z-index: 1;
  margin: 40px 0;
}
.brand-content h2 {
  font-size: 30px;
  font-weight: 700;
  line-height: 1.35;
  margin-bottom: 14px;
}
.brand-content p {
  font-size: 15px;
  line-height: 1.7;
  opacity: 0.85;
  max-width: 320px;
}
.brand-features {
  list-style: none;
  padding: 0;
  margin: 24px 0 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.brand-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  opacity: 0.9;
}
.brand-features .el-icon {
  font-size: 18px;
}
.brand-footer {
  position: relative;
  z-index: 1;
  font-size: 12.5px;
  opacity: 0.7;
}

/* 右侧表单面板 */
.auth-form-panel {
  flex: 1;
  padding: 32px 64px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: var(--el-bg-color);
}
.auth-tabs {
  margin-bottom: 10px;
}

/* 登录方式切换 */
.login-method-switch {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
}
.method-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  font-size: 18px;
  border: 1px solid var(--el-border-color);
  background: var(--el-bg-color);
  color: var(--el-text-color-regular);
  transition: all 0.3s;
}
.method-btn:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  transform: translateY(-2px);
}

/* 主题模式开关 */
.theme-toggle {
  position: absolute;
  top: 16px;
  right: 20px;
  z-index: 10;
}
.theme-toggle-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  font-size: 18px;
  border: 2px solid var(--el-border-color);
  background: linear-gradient(180deg, var(--el-bg-color) 0%, var(--el-fill-color-light) 100%);
  color: var(--el-text-color-regular);
  box-shadow: var(--el-box-shadow-light);
  transition: all 0.3s ease;
}
.theme-toggle-btn:hover {
  color: var(--el-color-primary);
  border-color: var(--el-color-primary);
  border-width: 2px;
  background: linear-gradient(180deg, var(--el-bg-color) 0%, var(--el-color-primary-light-9) 100%);
  transform: rotate(20deg) scale(1.08);
  box-shadow: 0 6px 14px color-mix(in srgb, var(--el-color-primary), transparent 80%);
}

/* 暗黑模式适配：背景/文本/边框/阴影随 Element Plus 变量自动切换，仅保留品牌区与主题开关的特殊处理 */
html.dark .auth-brand {
  background: linear-gradient(135deg, color-mix(in srgb, var(--el-color-primary), black 35%) 0%, color-mix(in srgb, var(--el-color-primary), black 55%) 100%);
}
html.dark .theme-toggle-btn:hover {
  color: var(--el-color-warning);
  border-color: var(--el-color-warning);
  box-shadow: 0 6px 14px color-mix(in srgb, var(--el-color-warning), transparent 75%);
}

/* 响应式 */
@media (max-width: 768px) {
  .auth-card {
    flex-direction: column;
    max-width: 440px;
  }
  .auth-brand {
    padding: 28px 24px;
  }
  .brand-content {
    display: none;
  }
  .brand-features {
    display: none;
  }
  .auth-form-panel {
    padding: 28px 56px;
  }
}
</style>

<style>
/* 主题切换：圆形扩散动画（View Transition API，仿 Element Plus 官网） */
::view-transition-old(root),
::view-transition-new(root) {
  animation: none;
  mix-blend-mode: normal;
}
::view-transition-old(root) {
  z-index: var(--vt-old-z, 1);
}
::view-transition-new(root) {
  z-index: var(--vt-new-z, 9999);
}
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(root),
  ::view-transition-new(root) {
    animation: none !important;
  }
}
</style>
