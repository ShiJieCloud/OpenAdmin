import { resolve } from 'path'
import { readFileSync } from 'node:fs'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import tailwindcss from '@tailwindcss/vite'

import dayjs from 'dayjs'

import { versionPlugin } from './scripts/vite-plugin-version'

// 读取 package.json 依赖信息
const pkg = JSON.parse(readFileSync(resolve(__dirname, 'package.json'), 'utf-8'))
const dependencies = pkg.dependencies || {}
const devDependencies = pkg.devDependencies || {}
const buildTs = Date.now()

// 格式化构建时间
const buildTime = dayjs(buildTs).format('YYYY-MM-DD HH:mm:ss')

export default defineConfig({
  plugins: [
    vue(),

    // 配置 Tailwind CSS 插件
    tailwindcss(),

    // 自动导入 API
    AutoImport({
      resolvers: [
        // ElementPlus 自动导入
        ElementPlusResolver(),
      ],
    }),

    // 自动注册组件
    Components({
      resolvers: [
        // ElementPlus 组件
        ElementPlusResolver(),
        // 图标组件注册
        IconsResolver({
          prefix: 'i', // 图标组件前缀，例如：i-ep-edit
          // 加载指定的图标集合：element-plus/icons-vue
          enabledCollections: ['ep','mdi','mi','meteor-icons','iconamoon', 'solar'],
        }),
      ],
    }),

    // 图标配置
    Icons({
      autoInstall: true, // 自动下载图标组件
      compiler: 'vue3',
      scale: 1, // 图标缩放比例
    }),

    // 版本信息插件
    versionPlugin({
      changelogFile: 'CHANGELOG.md',
      enableDevGenerate: false,
      version: pkg.version || '',
      buildTs,
    }),
  ],

  // 配置路径别名
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  // 注入全局常量
  define: {
    __APP_NAME__: JSON.stringify(pkg.name),
    __APP_DESCRIPTION__: JSON.stringify(pkg.description || ''),
    __APP_AUTHOR__: JSON.stringify(pkg.author || ''),
    __APP_LICENSE__: JSON.stringify(pkg.license || ''),
    __APP_VERSION__: JSON.stringify(pkg.version || ''),
    __APP_BUILD_TIME__: JSON.stringify(buildTime),
    __APP_DEPENDENCIES__: JSON.stringify(dependencies),
    __APP_DEV_DEPENDENCIES__: JSON.stringify(devDependencies),
  },
})
