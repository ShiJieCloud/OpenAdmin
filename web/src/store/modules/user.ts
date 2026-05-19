import { defineStore } from 'pinia'
import { ref } from 'vue'
import { passwordLogin, logout as apiLogout } from '@/api'
import type { PasswordLoginRequest, TokenResponse } from '@/api/modules/auth/type'

export const useUserStore = defineStore('user', () => {
  const accessToken = ref<string>('')
  const refreshToken = ref<string>('')
  const username = ref<string>('')
  const expiresIn = ref<number>(0)

  const login = async (req: PasswordLoginRequest): Promise<TokenResponse> => {
    const data = await passwordLogin(req)
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    expiresIn.value = data.expires_in
    return data
  }

  const logout = async (): Promise<void> => {
    await apiLogout()
    accessToken.value = ''
    refreshToken.value = ''
    username.value = ''
    expiresIn.value = 0
  }

  const setToken = (token: string): void => {
    accessToken.value = token
  }

  const isLoggedIn = (): boolean => {
    return !!accessToken.value
  }

  return {
    accessToken,
    refreshToken,
    username,
    expiresIn,
    login,
    logout,
    setToken,
    isLoggedIn
  }
}, {
  persist: {
    key: 'user',
    storage: localStorage
  }
})
