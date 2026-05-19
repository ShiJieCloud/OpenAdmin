import { defineStore } from 'pinia'

import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {

  // username
  const username = ref<string>('')

  return {
    username
  }
}, {
  // 持久化配置
  persist: true,
})
