import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginByPassword, loginByFace, refreshTokenApi } from '@/api'
import type { PasswordLoginRequest, TokenResponse, RefreshTokenRequest } from '@/types'

export const useUserStore = defineStore(
  'user',
  () => {
    const accessToken = ref<string>('')
    const refreshToken = ref<string>('')

    const passwordLogin = async (req: PasswordLoginRequest): Promise<TokenResponse> => {
      const data = await loginByPassword(req)
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
      return data
    }

    const faceLogin = async (blob: Blob): Promise<TokenResponse> => {
      const data = await loginByFace(blob)
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
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
      return data
    }

    const logout = (): void => {
      accessToken.value = ''
      refreshToken.value = ''
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
      passwordLogin,
      faceLogin,
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
