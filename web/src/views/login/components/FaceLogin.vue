<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Avatar } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'

const emit = defineEmits(['success'])
const router = useRouter()
const userStore = useUserStore()

// idle | scanning | success
const status = ref<'idle' | 'scanning' | 'success'>('idle')
const loading = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
let stream: MediaStream | null = null

const statusText = computed(() => {
  if (status.value === 'scanning') return '正在识别，请保持面部在框内…'
  if (status.value === 'success') return '识别成功'
  return '请点击下方按钮开始人脸识别'
})

// 停止摄像头流
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop())
    stream = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

// 从摄像头画面抓拍一帧并返回 Blob
function captureFrame(): Promise<Blob | null> {
  return new Promise((resolve) => {
    const video = videoRef.value
    if (!video || !video.videoWidth) {
      resolve(null)
      return
    }
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      resolve(null)
      return
    }
    // 镜像绘制，与前置摄像头显示效果一致
    ctx.translate(canvas.width, 0)
    ctx.scale(-1, 1)
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.9)
  })
}

async function startScan() {
  if (status.value === 'scanning') return
  loading.value = true
  // 1. 申请摄像头权限
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 320, height: 320 },
      audio: false,
    })
  } catch (e) {
    loading.value = false
    ElMessage.error('无法访问摄像头，请检查浏览器权限设置')
    return
  }
  // 2. 播放摄像头画面
  if (videoRef.value) {
    videoRef.value.srcObject = stream
    await videoRef.value.play().catch(() => {})
  }
  status.value = 'scanning'
  // 3. 等待画面稳定后抓拍
  await new Promise((resolve) => setTimeout(resolve, 1500))
  const blob = await captureFrame()
  if (!blob) {
    stopCamera()
    status.value = 'idle'
    loading.value = false
    ElMessage.error('抓拍失败，请重试')
    return
  }
  // 4. 调用人脸识别登录接口
  try {
    await userStore.faceLogin(blob)
    status.value = 'success'
    ElNotification({
      title: '登录成功',
      message: '人脸识别通过，欢迎回来',
      type: 'success',
    })
    emit('success', { method: 'face' })
    router.push('/')
  } catch (e) {
    // 请求层已统一弹出错误信息
    status.value = 'idle'
  } finally {
    stopCamera()
    loading.value = false
  }
}

// 组件卸载时释放摄像头
onUnmounted(() => {
  stopCamera()
})
</script>

<template>
  <div class="face-login">
    <div class="face-scanner" :class="status">
      <div class="face-frame">
        <video
          v-show="status === 'scanning'"
          ref="videoRef"
          class="face-video"
          autoplay
          playsinline
          muted
        ></video>
        <el-icon v-if="status !== 'scanning'" class="face-icon"><Avatar /></el-icon>
        <div class="scan-line"></div>
        <!-- 四角装饰 -->
        <span class="corner top-left"></span>
        <span class="corner top-right"></span>
        <span class="corner bottom-left"></span>
        <span class="corner bottom-right"></span>
      </div>
    </div>
    <p class="face-status" :class="status">{{ statusText }}</p>
    <el-button
      type="primary"
      class="submit-btn"
      :loading="loading"
      :disabled="status === 'scanning'"
      @click="startScan"
    >
      {{ status === 'success' ? '重新识别' : '开始人脸识别' }}
    </el-button>
    <p class="face-tip">请将面部置于识别框中央，保持光线充足</p>
  </div>
</template>

<style scoped>
.face-login {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0 4px;
}

/* 扫描区域 */
.face-scanner {
  width: 200px;
  height: 200px;
  border-radius: 16px;
  background: var(--el-fill-color);
  border: 2px solid var(--el-border-color);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}
.face-scanner.scanning {
  border-color: #4f6ef7;
  box-shadow: 0 0 24px rgba(79, 110, 247, 0.35);
}
.face-scanner.success {
  border-color: #22c55e;
  box-shadow: 0 0 24px rgba(34, 197, 94, 0.4);
}
.face-frame {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 摄像头画面 */
.face-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); /* 前置摄像头镜像，符合直觉 */
  z-index: 1;
}

.face-icon {
  font-size: 84px;
  color: #c0c6d4;
  transition: color 0.3s;
  z-index: 1;
}
.face-scanner.scanning .face-icon {
  color: #4f6ef7;
}
.face-scanner.success .face-icon {
  color: #22c55e;
}

/* 扫描线 */
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 10px;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(79, 110, 247, 0.15),
    rgba(79, 110, 247, 0.9) 45%,
    #4f6ef7 50%,
    rgba(79, 110, 247, 0.9) 55%,
    rgba(79, 110, 247, 0.15),
    transparent
  );
  top: 0;
  opacity: 0;
  will-change: transform, opacity;
  pointer-events: none;
  z-index: 2;
}
.face-scanner.scanning .scan-line {
  animation: scanMove 2s linear infinite;
}
@keyframes scanMove {
  0% {
    transform: translateY(0);
    opacity: 0;
  }
  12% {
    opacity: 1;
  }
  88% {
    opacity: 1;
  }
  100% {
    transform: translateY(190px);
    opacity: 0;
  }
}

/* 四角装饰 */
.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid #4f6ef7;
  opacity: 0.65;
  z-index: 3;
}
.corner.top-left {
  top: 10px;
  left: 10px;
  border-right: none;
  border-bottom: none;
  border-radius: 6px 0 0 0;
}
.corner.top-right {
  top: 10px;
  right: 10px;
  border-left: none;
  border-bottom: none;
  border-radius: 0 6px 0 0;
}
.corner.bottom-left {
  bottom: 10px;
  left: 10px;
  border-right: none;
  border-top: none;
  border-radius: 0 0 0 6px;
}
.corner.bottom-right {
  bottom: 10px;
  right: 10px;
  border-left: none;
  border-top: none;
  border-radius: 0 0 6px 0;
}

/* 状态文字 */
.face-status {
  margin: 18px 0 4px;
  font-size: 14px;
  color: #64748b;
  transition: color 0.3s;
}
.face-status.scanning {
  color: #4f6ef7;
}
.face-status.success {
  color: #22c55e;
}

.submit-btn {
  width: 100%;
  margin-top: 14px;
  padding: 12px 0;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
  border-radius: 8px;
}
.face-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}
</style>
