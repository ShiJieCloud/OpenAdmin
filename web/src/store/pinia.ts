import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'

// 创建 pinia 实例
export const pinia = createPinia()

// 注册持久化插件
pinia.use(
  createPersistedState({
    // 存储位置：localStorage
    storage: localStorage,
    // 存储 key 前缀（企业规范：项目名_模块名）
    key: (id) => `openadmin_${id}`,
  })
)