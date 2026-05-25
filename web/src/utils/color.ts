// src/utils/color.ts
/**
 * 十六进制/ rgb 颜色转 rgb 对象
 * @param color 颜色值（#fff / #ffffff / rgb(r,g,b)）
 * @returns { r: number; g: number; b: number }
 */
export function hexToRgb(color: string): { r: number; g: number; b: number } {
    color = color.trim()

    const rgbMatch = color.match(/^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i)
    if (rgbMatch) {
        return {
            r: parseInt(rgbMatch[1], 10),
            g: parseInt(rgbMatch[2], 10),
            b: parseInt(rgbMatch[3], 10),
        }
    }

    let hexStr = color.replace('#', '')
    let r: number, g: number, b: number

    if (hexStr.length === 3) {
        r = parseInt(hexStr[0] + hexStr[0], 16)
        g = parseInt(hexStr[1] + hexStr[1], 16)
        b = parseInt(hexStr[2] + hexStr[2], 16)
    } else if (hexStr.length === 6) {
        r = parseInt(hexStr.slice(0, 2), 16)
        g = parseInt(hexStr.slice(2, 4), 16)
        b = parseInt(hexStr.slice(4, 6), 16)
    } else {
        return { r: 128, g: 128, b: 128 }
    }

    return { r, g, b }
}

/**
 * rgb 对象转十六进制颜色
 * @param r 红色值 (0-255)
 * @param g 绿色值 (0-255)
 * @param b 蓝色值 (0-255)
 * @returns 十六进制颜色字符串（#ffffff）
 */
export function rgbToHex(r: number, g: number, b: number): string {
    const hex = [r, g, b].map(v => {
        const h = Math.round(v).toString(16)
        return h.length === 1 ? '0' + h : h
    })
    return `#${hex.join('')}`
}

/**
 * 颜色提亮（混合白色）
 * @param color 基础颜色
 * @param percentage 提亮百分比 (0-100)
 * @returns 提亮后的十六进制颜色
 */
export function tint(color: string, percentage: number): string {
    const rgb = hexToRgb(color)
    const ratio = percentage / 100
    const r = Math.round(rgb.r * (1 - ratio) + 255 * ratio)
    const g = Math.round(rgb.g * (1 - ratio) + 255 * ratio)
    const b = Math.round(rgb.b * (1 - ratio) + 255 * ratio)
    return rgbToHex(r, g, b)
}

/**
 * 颜色加深（混合黑色）
 * @param color 基础颜色
 * @param percentage 加深百分比 (0-100)
 * @returns 加深后的十六进制颜色
 */
export function shade(color: string, percentage: number): string {
    const rgb = hexToRgb(color)
    const ratio = percentage / 100
    const r = Math.round(rgb.r * (1 - ratio))
    const g = Math.round(rgb.g * (1 - ratio))
    const b = Math.round(rgb.b * (1 - ratio))
    return rgbToHex(r, g, b)
}