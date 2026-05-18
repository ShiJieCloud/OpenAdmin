import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import AutoImport from 'unplugin-auto-import/vite'
import Icons from 'unplugin-icons/vite'
import Components from 'unplugin-vue-components/vite'
import IconsResolver from 'unplugin-icons/resolver'
import tailwindcss from '@tailwindcss/vite'

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
          enabledCollections: ['ep'],
        }),
      ],
    }),

    // 图标配置
    Icons({
      autoInstall: true, // 自动下载图标组件
      compiler: 'vue3',
      scale: 1, // 图标缩放比例
    }),
  ],
})
