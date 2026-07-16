<script setup lang="ts">
import { useShiki } from '@/composables/useShiki'

interface Props {
    /** 原始代码字符串 */
    code: string
    /** 代码语言 */
    lang: string
    /** 代码高亮主题 */
    theme?: string,
}
const props = defineProps<Props>()

const { html, loading } = useShiki(props.code, props.lang, props.theme as string)

console.log(props.theme);


</script>

<template>
    <div class="code-wrap" v-if="html || loading">
        <div class="code-content p-3">
            <div v-if="loading" class="code-loading">代码高亮加载中...</div>
            <div v-else v-html="html" />
        </div>
    </div>
</template>

<style scoped>
.code-wrap {
    width: 100%;
    overflow: hidden;
}

.code-loading {
    padding: 20px;
    text-align: center;
    color: #999;
}

/* 穿透shiki原生样式 */
:deep(pre) {
    border-radius: 8px;
    padding: 14px 16px !important;
    overflow: auto;
    max-height: 320px;
}

:deep(code) {
    font-family: inherit;
}

/* 滚动条美化 */
:deep(pre::-webkit-scrollbar) {
    height: 6px;
}

:deep(pre::-webkit-scrollbar-thumb) {
    background: #8884;
    border-radius: 3px;
}

</style>
