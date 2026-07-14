<!--
 * @component LoginLogManagement
 * @path views/monitor/loginLog/index
 * @name 登录日志管理页面
 * @description 展示系统用户登录日志列表，支持按用户名、IP地址、时间范围筛选
 * @example
 * <LoginLogManagement />
 * @author sjzhao
 * @date 2026-07-14
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useFullscreen } from '@vueuse/core'

import type { ILoginLogInfo, ILoginLogListQueryParam } from '@/types'
import type { IPageResult } from '@/types/common/api'

import { getLoginLogList } from '@/api/modules/loginLog'

// ===================== 1. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [1, 10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

// ===================== 2. 响应式状态数据 =====================
/** 登录日志分页数据 */
const loginLogPageData = ref<IPageResult<ILoginLogInfo>>({
  records: [],
  total: 0,
  pages: 0,
  page_size: DEFAULT_PAGE_SIZE,
  page_num: 1,
})

/** 登录日志列表查询参数 */
const searchLoginLogParams = reactive<ILoginLogListQueryParam>({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
  username: '',
  response_code: '',
  client_ip: '',
  os: '',
  browser: '',
  ip_country: '',
  ip_province: '',
  ip_city: '',
  start_time: '',
  end_time: '',
})

/** 加载状态管理 */
const loading = ref({
  loginLogTable: false,
  loginLogRefreshBtn: false,
})

/** 时间范围选择器绑定值 */
const timeRange = ref<[string, string] | null>(null)

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

// ===================== 3. 接口请求方法 =====================
/**
 * 拉取登录日志分页列表
 * @description 根据查询参数获取登录日志列表数据
 * @returns {Promise<void>}
 */
const fetchLoginLogList = async () => {
  loading.value.loginLogTable = true
  try {
    const res: IPageResult<ILoginLogInfo> = await getLoginLogList(searchLoginLogParams)
    loginLogPageData.value = {
      records: res.records || [],
      total: res.total || 0,
      pages: res.pages || 0,
      page_size: res.page_size || DEFAULT_PAGE_SIZE,
      page_num: res.page_num || 1,
    }
  } finally {
    loading.value.loginLogTable = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 搜索回调
 * @description 处理时间范围并重置页码后拉取列表
 */
const handleSearch = () => {
  if (timeRange.value && timeRange.value.length === 2) {
    searchLoginLogParams.start_time = timeRange.value[0]
    searchLoginLogParams.end_time = timeRange.value[1]
  } else {
    searchLoginLogParams.start_time = ''
    searchLoginLogParams.end_time = ''
  }
  searchLoginLogParams.page_num = 1
  fetchLoginLogList()
}

/**
 * 重置回调
 * @description 清空搜索条件并重新查询
 */
const handleReset = () => {
  searchLoginLogParams.username = ''
  searchLoginLogParams.response_code = ''
  searchLoginLogParams.client_ip = ''
  searchLoginLogParams.os = ''
  searchLoginLogParams.browser = ''
  searchLoginLogParams.ip_country = ''
  searchLoginLogParams.ip_province = ''
  searchLoginLogParams.ip_city = ''
  searchLoginLogParams.start_time = ''
  searchLoginLogParams.end_time = ''
  timeRange.value = null
  handleSearch()
}

/**
 * 分页条数变更回调
 * @param val - 新的每页条数
 */
const handleSizeChange = (val: number) => {
  searchLoginLogParams.page_size = val
  searchLoginLogParams.page_num = 1
  fetchLoginLogList()
}

/**
 * 刷新列表
 */
const handleRefreshLoginLogList = async () => {
  try {
    loading.value.loginLogRefreshBtn = true
    await fetchLoginLogList()
  } finally {
    loading.value.loginLogRefreshBtn = false
  }
}

/**
 * 格式化登录结果
 * @param row - 登录日志行数据
 * @returns 登录结果文本
 */
const formatLoginResult = (row: ILoginLogInfo) => {
  if (row.response_code === '0000000' || row.response_code === '0') {
    return '成功'
  }
  return '失败'
}

/**
 * 获取登录结果标签类型
 * @param row - 登录日志行数据
 * @returns 标签类型
 */
const getLoginResultType = (row: ILoginLogInfo) => {
  if (row.response_code === '0000000' || row.response_code === '0') {
    return 'success'
  }
  return 'danger'
}

/**
 * 格式化地理位置
 * @param row - 登录日志行数据
 * @returns 地理位置文本
 */
const formatLocation = (row: ILoginLogInfo) => {
  const parts = [row.ip_country, row.ip_province, row.ip_city].filter(Boolean)
  return parts.length > 0 ? parts.join('-') : '-'
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取登录日志列表数据
 */
onMounted(() => fetchLoginLogList())
</script>

<template>
  <div ref="layoutPageRef" class="layout-page">
    <!-- 搜索区域 -->
    <div class="layout-page__header">
      <el-card shadow="never">
        <el-collapse>
          <el-collapse-item>
            <template #title>
              <div class="font-bold text-base">数据查询</div>
            </template>
            <el-form :model="searchLoginLogParams" label-width="auto">
              <el-row :gutter="20" class="pl-5">
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="用户名">
                    <el-input v-model="searchLoginLogParams.username" placeholder="请输入用户名" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="登录IP">
                    <el-input v-model="searchLoginLogParams.client_ip" placeholder="请输入登录IP" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="响应码">
                    <el-input v-model="searchLoginLogParams.response_code" placeholder="请输入响应码" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="操作系统">
                    <el-input v-model="searchLoginLogParams.os" placeholder="请输入操作系统" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="浏览器">
                    <el-input v-model="searchLoginLogParams.browser" placeholder="请输入浏览器" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="国家">
                    <el-input v-model="searchLoginLogParams.ip_country" placeholder="请输入国家" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="省份">
                    <el-input v-model="searchLoginLogParams.ip_province" placeholder="请输入省份" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="城市">
                    <el-input v-model="searchLoginLogParams.ip_city" placeholder="请输入城市" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="24" :md="16" :lg="12">
                  <el-form-item label="登录时间">
                    <el-date-picker v-model="timeRange" type="datetimerange" range-separator="至"
                      start-placeholder="开始时间" end-placeholder="结束时间" value-format="YYYY-MM-DD HH:mm:ss" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="24" :md="8" :lg="12">
                  <el-space alignment="flex-end" class="justify-end w-full">
                    <el-button plain type="primary" @click="handleSearch">
                      <template #icon>
                        <i-ep-search />
                      </template>
                      搜索
                    </el-button>
                    <el-button @click="handleReset">
                      <template #icon>
                        <i-ep-refresh-right />
                      </template>
                      重置
                    </el-button>
                  </el-space>
                </el-col>
              </el-row>
            </el-form>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </div>

    <!-- 列表区域 -->
    <div class="layout-page__content">
      <el-card shadow="never">
        <div class="layout-toolbar">
          <h4 class="layout-toolbar__title">登录日志列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.loginLogRefreshBtn" @click="handleRefreshLoginLogList">
              <template #icon>
                <i-ep-refresh />
              </template>
              刷新
            </el-button>
            <el-button plain @click="toggleFullscreen">
              <template #icon>
                <i-solar-quit-full-screen-bold-duotone v-if="isFullscreen" />
                <i-solar-full-screen-line-duotone v-else />
              </template>
              {{ isFullscreen ? '退出全屏' : '全屏' }}
            </el-button>
          </el-space>
        </div>

        <el-table v-loading="loading.loginLogTable" :data="loginLogPageData.records" stripe class="layout-table">
          <!-- 展开行 -->
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="pr-20 pl-20">
                <el-descriptions column="2">
                  <el-descriptions-item label="TraceId">
                    {{ row.trace_id || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="操作系统">
                    {{ row.os || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="浏览器">
                    {{ row.browser || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="响应码">
                    <el-tag :type="getLoginResultType(row)">
                      {{ row.response_code || '-' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="提示信息">
                    {{ row.response_msg || '-' }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </template>
          </el-table-column>

          <!-- 追踪ID 第一列 -->
          <el-table-column prop="trace_id" label="追踪ID" width="320" show-overflow-tooltip />

          <!-- 用户名 -->
          <el-table-column prop="username" label="用户名" min-width="120" />

          <!-- 登录结果 -->
          <el-table-column label="登录结果" width="140" align="center">
            <template #default="{ row }">
              <el-tag :type="getLoginResultType(row)">
                {{ formatLoginResult(row) }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 登录IP -->
          <el-table-column prop="client_ip" label="登录IP" width="160" />

          <!-- 登录地点 -->
          <el-table-column prop="location" label="登录地点" width="180">
            <template #default="{ row }">
              {{ formatLocation(row) }}
            </template>
          </el-table-column>

          <!-- 登录时间 -->
          <el-table-column prop="create_time" label="登录时间" width="180" />
        </el-table>

        <div class="layout-pagination">
          <el-pagination v-model:current-page="searchLoginLogParams.page_num"
            v-model:page-size="searchLoginLogParams.page_size" :total="loginLogPageData.total"
            :page-sizes="PAGE_SIZE_OPTIONS" layout="total, sizes, prev, pager, next" :teleported="false"
            @size-change="handleSizeChange" @current-change="fetchLoginLogList" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.layout-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.layout-toolbar__title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.expand-content {
  display: flex;
  justify-content: center;
  padding: 16px 24px;
}
</style>
