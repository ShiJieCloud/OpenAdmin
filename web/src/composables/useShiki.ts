import { ref, watch, unref } from 'vue'
import { createHighlighter } from 'shiki/bundle/web'
import { transformerColorizedBrackets } from '@shikijs/colorized-brackets'
import { CODE_THEME_MODE, CODE_LANGS } from '@/types/modules/theme'


// 全局单例锁（全局唯一，所有组件共享）
let highlighterInstance: Awaited<ReturnType<typeof createHighlighter>> | null = null
let initPromise: ReturnType<typeof createHighlighter> | null = null

async function initHighlighter() {
  if (highlighterInstance) return highlighterInstance
  if (initPromise) return await initPromise

  try {
    initPromise = createHighlighter({
      themes: [...Object.values(CODE_THEME_MODE)],
      langs: [...CODE_LANGS],
    })
    highlighterInstance = await initPromise
    return highlighterInstance
  } catch (err){
    return null
  } finally {
    initPromise = null
  }
}

/**
 * 代码预处理：兼容对象/数组、自动格式化JSON
 */
function formatRawCode(rawCode: unknown, lang: string): string {
  if (rawCode === null || rawCode === undefined) return ''

  let codeStr: string
  if (typeof rawCode === 'object') {
    codeStr = JSON.stringify(rawCode, null, 2)
  } else {
    codeStr = String(rawCode).trim()
  }

  // json 容错，处理转义字符串
  if (lang === 'json') {
    try {
      const parsed = JSON.parse(codeStr)
      codeStr = JSON.stringify(parsed, null, 2)
    } catch {}
  }
  return codeStr
}

/**
 * Vue 组合式 Shiki 高亮
 * @param rawCode 原始代码（支持对象/字符串/null）
 * @param lang 语言标识
 * @param theme 代码高亮主题
 */
export function useShiki(
  rawCode: unknown,
  lang: string,
  theme: string,
) {
  const html = ref('')
  const loading = ref(false)

  // 渲染函数
  const render = async () => {
    const codeVal = unref(rawCode)
    const langVal = unref(lang)
    const themeVal = unref(theme)

    const code = formatRawCode(codeVal, langVal)
    if (!code) {
      html.value = ''
      return
    }

    loading.value = true
    const hl = await initHighlighter()
    loading.value = false

    if (!hl) {
      html.value = `<pre>${code}</pre>`
      return
    }

    try {
      html.value = hl.codeToHtml(code, {
        lang: langVal,
        theme: themeVal,
        transformers: [transformerColorizedBrackets()],
      })
    } catch (err) {
      console.error('[useShiki] 渲染异常', err)
      html.value = `<pre>${code}</pre>`
    }
  }

  // 监听所有依赖自动重渲染
  watch(
    [() => unref(rawCode), () => unref(lang), () => unref(theme)],
    () => render(),
    { flush: 'post', immediate: true }
  )

  return {
    html,
    loading,
    refresh: render,
  }
}
