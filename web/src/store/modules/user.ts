import { defineStore } from 'pinia'
import { ref } from 'vue'
import { passwordLogin, refreshTokenApi } from '@/api'
import type { PasswordLoginRequest, TokenResponse, RefreshTokenRequest } from '@/types'

export const useUserStore = defineStore(
  'user',
  () => {
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

    const renewToken = async (): Promise<TokenResponse> => {
      if (!refreshToken.value) {
        throw new Error('没有可用的刷新令牌')
      }
      const refreshTokenReq: RefreshTokenRequest = {
        refresh_token: refreshToken.value,
      }
      const data = await refreshTokenApi(refreshTokenReq)
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
      expiresIn.value = data.expires_in
      return data
    }

    const logout = (): void => {
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
      renewToken,
      logout,
      setToken,
      isLoggedIn,
    }
  },
  {
    persist: true,
  }
)
