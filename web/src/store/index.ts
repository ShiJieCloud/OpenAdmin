import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate'

// 创建 Pinia 实例
const pinia = createPinia()

// 使用持久化插件
pinia.use(
  createPersistedState({
    storage: localStorage,
    key: (id) => `openadmin_${id}`,
  })
)

export default pinia
