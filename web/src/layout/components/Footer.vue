<script setup lang="ts">
import { computed } from 'vue'

interface FooterItem {
  key: string
  type: 'text' | 'link'
  text?: string
  href?: string
  isLink?: boolean
}

const env = import.meta.env

const items = computed<FooterItem[]>(() => {
  const list: FooterItem[] = []

  list.push({ key: 'agreement', type: 'text', text: '用户协议', isLink: true })
  list.push({ key: 'privacy', type: 'text', text: '隐私政策', isLink: true })

  if (env.VITE_APP_ICP_NUMBER) {
    list.push({ key: 'icp', type: 'text', text: env.VITE_APP_ICP_NUMBER })
  }
  if (env.VITE_APP_SECURITY_RECORD) {
    list.push({ key: 'security', type: 'text', text: env.VITE_APP_SECURITY_RECORD })
  }
  if (env.VITE_APP_COPYRIGHT_TEXT) {
    list.push({ key: 'copyright', type: 'text', text: env.VITE_APP_COPYRIGHT_TEXT })
  }
  if (env.VITE_APP_PROJECT_LINK) {
    list.push({
      key: 'project',
      type: 'link',
      text: '开源地址',
      href: env.VITE_APP_PROJECT_LINK
    })
  }
  if (env.VITE_APP_BUSINESS_EMAIL) {
    list.push({
      key: 'business',
      type: 'text',
      text: `商务合作：${env.VITE_APP_BUSINESS_EMAIL}`
    })
  }

  return list
})

const isLast = (index: number) => index === items.value.length - 1
</script>

<template>
  <div class="footer-inner">
    <div class="footer-content">
      <template v-if="items.length === 0">
        <span>&nbsp;</span>
      </template>
      <template v-else>
        <template v-for="(item, index) in items" :key="item.key">
          <a
            v-if="item.type === 'link'"
            class="footer-link"
            :href="item.href"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ item.text }}
          </a>
          <span
            v-else-if="item.isLink"
            class="footer-link"
          >
            {{ item.text }}
          </span>
          <span v-else>{{ item.text }}</span>
          <span v-if="!isLast(index)" class="footer-divider">·</span>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.footer-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  display: flex;
  align-items: center;
  gap: 0;
  font-size: 12px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
}

.footer-link {
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: color 0.2s;
  text-decoration: none;

  &:hover {
    color: var(--el-color-primary);
  }
}

.footer-divider {
  margin: 0 6px;
  color: var(--el-border-color);
}
</style>
