/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_ICP_NUMBER: string
  readonly VITE_APP_SECURITY_RECORD: string
  readonly VITE_APP_COPYRIGHT_TEXT: string
  readonly VITE_APP_PROJECT_LINK: string
  readonly VITE_APP_BUSINESS_EMAIL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare global {
  const __APP_VERSION__: string
  const __APP_NAME__: string
  const __APP_AUTHOR__: string
  const __APP_BUILD_TIME__: string
  const __APP_DESCRIPTION__: string
  const __APP_DEPENDENCIES__: Record<string, string>
  const __APP_DEV_DEPENDENCIES__: Record<string, string>
}

export {}
