import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

/**
 * @description Markdown 渲染组合式函数
 * @example
 * ```ts
 * const { renderMarkdown } = useMarkdown()
 * const html = renderMarkdown('# Hello World')
 * ```
 * @since 2026-07-31
 */
export function useMarkdown() {

  let md: MarkdownIt = new MarkdownIt({
      html: false, // 禁用 HTML 标签，防止 XSS
      linkify: true, // 自动识别链接
      typographer: true, // 启用排版优化
      breaks: true, // 启用换行符转换
    })

  // 渲染 markdown 文本
  const renderMarkdown = (text: string): string => {
    if (!text || !md) return ''
    const rawHtml = md.render(text)
    // DOMPurify 过滤恶意标签，防止 XSS 攻击
    return DOMPurify.sanitize(rawHtml)
  }

  return {
    renderMarkdown
  }
}
