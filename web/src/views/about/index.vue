<script setup lang="ts">

/**
 * 打包注入的项目基础信息，全局编译变量
 * 若打包插件未注入则兜底空字符串防止报错
 */
const pkgInfo = {
  name: (__APP_NAME__ as string) || '',
  version: (__APP_VERSION__ as string) || '0.0.0',
  description: (__APP_DESCRIPTION__ as string) || '暂无项目描述',
  author: (__APP_AUTHOR__ as string) || '未知作者',
}

/**
 * 生产环境依赖列表 key:依赖包名 value:版本号
 */
const dependencies: Record<string, string> = (__APP_DEPENDENCIES__ as Record<string, string>) || {}

/**
 * 开发环境依赖列表 key:依赖包名 value:版本号
 */
const devDependencies: Record<string, string> = (__APP_DEV_DEPENDENCIES__ as Record<string, string>) || {}

/**
 * 项目构建打包时间，编译注入变量
 */
const buildTime = (__APP_BUILD_TIME__ as string) || '未知构建时间'

// 当前组件名称定义
defineOptions({ name: 'About' })
</script>

<template>
  <!-- 关于页面根容器 -->
  <div class="about-page">
    <!-- 垂直弹性间距容器，统一卡片间距 -->
    <el-space vertical fill class="pb-3">
      <!-- 模块1：项目简介卡片 -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">关于</div>
        </template>
        <p class="desc-text">{{ pkgInfo.description }}</p>
      </el-card>

      <!-- 模块2：项目核心信息卡片 -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">项目信息</div>
        </template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="项目名">
            {{ pkgInfo.name }}
          </el-descriptions-item>
          <el-descriptions-item label="作者">
            {{ pkgInfo.author }}
          </el-descriptions-item>
          <el-descriptions-item label="版本">
            <el-tag type="success">v{{ pkgInfo.version }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最新构建时间">
            {{ buildTime }}
          </el-descriptions-item>
          <el-descriptions-item label="Github 地址">
            <!-- 新增rel安全属性，防止新页面窃取上下文 -->
            <a
              href="https://github.com/your-org/openadmin"
              target="_blank"
              rel="noopener noreferrer"
              class="github-link"
            >
              https://github.com/your-org/openadmin
            </a>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 模块3：生产依赖清单 -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">生产依赖</div>
        </template>
        <el-descriptions :column="2" border>
          <!-- 遍历生产依赖包 -->
          <template v-for="(version, pkgName) in dependencies" :key="pkgName">
            <el-descriptions-item :label="pkgName">
              {{ version }}
            </el-descriptions-item>
          </template>
          <!-- 无生产依赖时兜底提示 -->
          <el-descriptions-item v-if="Object.keys(dependencies).length === 0" label="-">
            暂无生产依赖
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 模块4：开发依赖清单 -->
      <el-card shadow="never">
        <template #header>
          <div class="card-header">开发依赖</div>
        </template>
        <el-descriptions :column="2" border>
          <!-- 遍历开发依赖包 -->
          <template v-for="(version, pkgName) in devDependencies" :key="pkgName">
            <el-descriptions-item :label="pkgName">
              {{ version }}
            </el-descriptions-item>
          </template>
          <!-- 无开发依赖时兜底提示 -->
          <el-descriptions-item v-if="Object.keys(devDependencies).length === 0" label="-">
            暂无开发依赖
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </el-space>
  </div>
</template>

<style scoped>
/** 页面根容器，占满父级宽高，垂直排列卡片 */
.about-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--page-gap, 16px);
}

/** 深度修改内部卡片样式，全局隔离仅当前页面生效 */
.about-page :deep(.el-card) {
  flex-shrink: 0;
  border-radius: 8px;
}

/** 卡片头部标题样式 */
.card-header {
  font-size: 16px;
  font-weight: 600;
}

/** 项目简介文本间距优化 */
.desc-text {
  margin: 0;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

/** Github链接基础样式 */
.github-link {
  color: #409eff;
  text-decoration: none;
}

/** 鼠标悬浮下划线提示 */
.github-link:hover {
  text-decoration: underline;
}
</style>
