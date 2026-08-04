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
