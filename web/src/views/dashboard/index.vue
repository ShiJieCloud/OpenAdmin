<!--
 * @component Dashboard
 * @path views/dashboard/index
 * @name 首页仪表盘
 * @description 展示系统核心数据概览卡片，包括用户总数、角色数量、菜单数量、部门数量，以及最近登录日志和操作日志
 * @example
 * <Dashboard />
 * @author sjzhao
 * @date 2026-08-07
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { User, UserFilled, Menu as MenuIcon, OfficeBuilding } from '@element-plus/icons-vue'
import { getSystemOverview } from '@/api/modules/dashboard'
import type { ISystemOverview, ILoginLogInfo, IOperLogInfo  } from '@/types'

import { getRecentLoginLogs, getRecentOperLogs } from '@/api/modules/dashboard'

/** 统计数据 */
const systemOverview = ref<ISystemOverview>({
  user_count: 0,
  role_count: 0,
  menu_count: 0,
  dept_count: 0,
})

/** 日志数据 */
const recent_login_logs = ref<ILoginLogInfo[]>([])
const recent_oper_logs = ref<IOperLogInfo[]>([])

/** 加载状态 */
const loading = ref(false)
const logsLoading = ref(false)

/** 卡片配置 */
const cards = [
  { key: 'user_count' as const, label: '用户总数', icon: UserFilled, color: '#409EFF', bg: '#ECF5FF' },
  { key: 'role_count' as const, label: '角色数量', icon: User, color: '#67C23A', bg: '#F0F9EB' },
  { key: 'menu_count' as const, label: '菜单数量', icon: MenuIcon, color: '#E6A23C', bg: '#FDF6EC' },
  { key: 'dept_count' as const, label: '部门数量', icon: OfficeBuilding, color: '#F56C6C', bg: '#FEF0F0' },
]

/** 加载统计数据 */
const loadStats = async () => {
  loading.value = true
  try {
    systemOverview.value = await getSystemOverview()
  } finally {
    loading.value = false
  }
}

/** 加载日志数据 */
const loadLogs = async () => {
  logsLoading.value = true
  try {
    recent_login_logs.value = await getRecentLoginLogs()
    recent_oper_logs.value = await getRecentOperLogs()
  } finally {
    logsLoading.value = false
  }
}

/** 拼接IP属地 */
const formatIpLocation = (log: any): string => {
  const parts = [log.ip_country, log.ip_province, log.ip_city].filter(Boolean)
  return parts.length > 0 ? parts.join(' ') : '-'
}

/** 判断登录结果 */
const getLoginResult = (log: any): { text: string; type: 'success' | 'danger' } => {
  // response_code 为 '0000000' 表示成功
  const isSuccess = log.response_code === '0000000'
  return {
    text: isSuccess ? '成功' : '失败',
    type: isSuccess ? 'success' : 'danger'
  }
}

/** 判断响应码是否成功 */
const getResponseCodeType = (responseCode: string): 'success' | 'danger' => {
  return responseCode === '0000000' ? 'success' : 'danger'
}

onMounted(() => {
  loadStats()
  loadLogs()
})
</script>

<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <h2>欢迎使用 OpenAdmin</h2>
      <p class="dashboard-desc">系统数据概览</p>
    </div>

    <div class="overview-cards">
      <el-card
        v-for="card in cards"
        :key="card.key"
        shadow="never"
        class="overview-card"
      >
        <div class="overview-card__content">
          <div class="overview-card__info">
            <div class="overview-card__label">{{ card.label }}</div>
            <div class="overview-card__value" :style="{ color: card.color }">
              {{ systemOverview[card.key] }}
            </div>
          </div>
          <div
            class="overview-card__icon"
            :style="{ backgroundColor: card.bg, color: card.color }"
          >
            <el-icon :size="28">
              <component :is="card.icon" />
            </el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <div class="log-section">
      <el-card shadow="never" class="log-card">
        <template #header>
          <div class="card-header">
            <span>最近登录日志</span>
          </div>
        </template>
        <el-table
          :data="recent_login_logs"
          v-loading="logsLoading"
          style="width: 100%"
          size="small"
        >
          <el-table-column prop="username" label="账号名称" min-width="100" />
          <el-table-column prop="create_time" label="登录时间" min-width="160" />
          <el-table-column label="IP 属地" min-width="140">
            <template #default="{ row }">{{ formatIpLocation(row) }}</template>
          </el-table-column>
          <el-table-column label="登录结果" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getLoginResult(row).type" size="small">
                {{ getLoginResult(row).text }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card shadow="never" class="log-card">
        <template #header>
          <div class="card-header">
            <span>最近操作日志</span>
          </div>
        </template>
        <el-table
          :data="recent_oper_logs"
          v-loading="logsLoading"
          style="width: 100%"
          size="small"
        >
          <el-table-column prop="operator_id" label="操作员" min-width="100" />
          <el-table-column prop="create_time" label="操作时间" min-width="160" />
          <el-table-column prop="api_name" label="接口名称" min-width="150" />
          <el-table-column label="响应码" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getResponseCodeType(row.response_code)" size="small">
                {{ row.response_code }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dashboard-header {
  line-height: 1.5;
}
.dashboard-header h2 {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
}
.dashboard-desc {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.overview-card {
  border-radius: 8px;
}

.overview-card__content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.overview-card__info {
  flex: 1;
}

.overview-card__label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.overview-card__value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.overview-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  flex-shrink: 0;
}

.log-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 12px;
}

.log-card {
  border-radius: 8px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
</style>
