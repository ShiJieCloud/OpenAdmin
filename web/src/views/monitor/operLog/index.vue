<!--
 * @component OperLogManagement
 * @path views/monitor/operLog/index
 * @name 操作日志管理页面
 * @description 展示系统操作日志列表，支持按追踪ID、请求方法、API路径、模块、操作员、IP、响应码、时间范围筛选
 * @example
 * <OperLogManagement />
 * @author sjzhao
 * @date 2026-07-15
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useFullscreen } from '@vueuse/core'

import type { IOperLogInfo, IOperLogListQueryParam } from '@/types'
import type { IPageResult } from '@/types/common/api'

import { getOperLogList } from '@/api/modules/operLog'

// ===================== 1. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [1, 10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

/** HTTP请求方法选项 */
const REQUEST_METHOD_OPTIONS = [
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'DELETE', value: 'DELETE' },
  { label: 'PATCH', value: 'PATCH' },
]

// ===================== 2. 响应式状态数据 =====================
/** 操作日志分页数据 */
const operLogPageData = ref<IPageResult<IOperLogInfo>>({
  records: [],
  total: 0,
  pages: 0,
  page_size: DEFAULT_PAGE_SIZE,
  page_num: 1,
})

/** 操作日志列表查询参数 */
const searchOperLogParams = reactive<IOperLogListQueryParam>({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
  trace_id: '',
  request_method: [],
  api_path: '',
  api_name: '',
  module: '',
  operator_id: '',
  client_ip: '',
  response_code: '',
  start_time: '',
  end_time: '',
})

/** 加载状态管理 */
const loading = ref({
  operLogTable: false,
  operLogRefreshBtn: false,
})

/** 时间范围选择器绑定值 */
const timeRange = ref<[string, string] | null>(null)

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

// ===================== 3. 接口请求方法 =====================
/**
 * 拉取操作日志分页列表
 * @description 根据查询参数获取操作日志列表数据
 * @returns {Promise<void>}
 */
const fetchOperLogList = async () => {
  loading.value.operLogTable = true
  try {
    const res: IPageResult<IOperLogInfo> = await getOperLogList(searchOperLogParams)
    operLogPageData.value = {
      records: res.records || [],
      total: res.total || 0,
      pages: res.pages || 0,
      page_size: res.page_size || DEFAULT_PAGE_SIZE,
      page_num: res.page_num || 1,
    }
  } finally {
    loading.value.operLogTable = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 搜索回调
 * @description 处理时间范围并重置页码后拉取列表
 */
const handleSearch = () => {
  if (timeRange.value && timeRange.value.length === 2) {
    searchOperLogParams.start_time = timeRange.value[0]
    searchOperLogParams.end_time = timeRange.value[1]
  } else {
    searchOperLogParams.start_time = ''
    searchOperLogParams.end_time = ''
  }
  searchOperLogParams.page_num = 1
  fetchOperLogList()
}

/**
 * 重置回调
 * @description 清空搜索条件并重新查询
 */
const handleReset = () => {
  searchOperLogParams.trace_id = ''
  searchOperLogParams.request_method = []
  searchOperLogParams.api_path = ''
  searchOperLogParams.api_name = ''
  searchOperLogParams.module = ''
  searchOperLogParams.operator_id = ''
  searchOperLogParams.client_ip = ''
  searchOperLogParams.response_code = ''
  searchOperLogParams.start_time = ''
  searchOperLogParams.end_time = ''
  timeRange.value = null
  handleSearch()
}

/**
 * 分页条数变更回调
 * @param val - 新的每页条数
 */
const handleSizeChange = (val: number) => {
  searchOperLogParams.page_size = val
  searchOperLogParams.page_num = 1
  fetchOperLogList()
}

/**
 * 刷新列表
 */
const handleRefreshOperLogList = async () => {
  try {
    loading.value.operLogRefreshBtn = true
    await fetchOperLogList()
  } finally {
    loading.value.operLogRefreshBtn = false
  }
}

/**
 * 获取请求方法标签类型
 * @param method - HTTP请求方法
 * @returns 标签类型
 */
const getRequestMethodType = (method: string) => {
  const typeMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info',
  }
  return typeMap[method] || 'info'
}

/**
 * 获取响应结果标签类型
 * @param row - 操作日志行数据
 * @returns 标签类型
 */
const getResponseResultType = (row: IOperLogInfo) => {
  if (row.response_code === '0000000' || row.response_code === '0' || !row.response_code) {
    return 'success'
  }
  return 'danger'
}

/**
 * 格式化响应结果
 * @param row - 操作日志行数据
 * @returns 响应结果文本
 */
const formatResponseResult = (row: IOperLogInfo) => {
  if (row.response_code === '0000000' || row.response_code === '0' || !row.response_code) {
    return '成功'
  }
  return '失败'
}

/**
 * 格式化地理位置
 * @param row - 操作日志行数据
 * @returns 地理位置文本
 */
const formatLocation = (row: IOperLogInfo) => {
  const parts = [row.ip_country, row.ip_province, row.ip_city].filter(Boolean)
  return parts.length > 0 ? parts.join('-') : '-'
}

/**
 * 格式化耗时
 * @param costTime - 耗时（毫秒）
 * @returns 格式化后的耗时文本
 */
const formatCostTime = (costTime: number) => {
  if (costTime < 1000) {
    return `${costTime}ms`
  }
  return `${(costTime / 1000).toFixed(2)}s`
}

/**
 * 获取耗时标签类型
 * @param costTime - 耗时（毫秒）
 * @returns 标签类型
 */
const getCostTimeType = (costTime: number) => {
  if (costTime < 500) {
    return 'success'
  } else if (costTime < 2000) {
    return 'warning'
  }
  return 'danger'
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取操作日志列表数据
 */
onMounted(() => fetchOperLogList())
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
            <el-form :model="searchOperLogParams" label-width="auto">
              <el-row :gutter="20" class="pl-5">
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="追踪ID">
                    <el-input v-model="searchOperLogParams.trace_id" placeholder="请输入追踪ID" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="请求方法">
                    <el-select v-model="searchOperLogParams.request_method"
                    multiple
      collapse-tags
      collapse-tags-tooltip placeholder="请选择请求方法" clearable>
                      <el-option
                        v-for="item in REQUEST_METHOD_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="API路径">
                    <el-input v-model="searchOperLogParams.api_path" placeholder="请输入API路径" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="API名称">
                    <el-input v-model="searchOperLogParams.api_name" placeholder="请输入API名称" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="业务模块">
                    <el-input v-model="searchOperLogParams.module" placeholder="请输入业务模块" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="操作员ID">
                    <el-input v-model="searchOperLogParams.operator_id" placeholder="请输入操作员ID" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="客户端IP">
                    <el-input v-model="searchOperLogParams.client_ip" placeholder="请输入客户端IP" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="响应码">
                    <el-input v-model="searchOperLogParams.response_code" placeholder="请输入响应码" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="24" :md="16" :lg="12">
                  <el-form-item label="操作时间">
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
          <h4 class="layout-toolbar__title">操作日志列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.operLogRefreshBtn" @click="handleRefreshOperLogList">
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

        <el-table v-loading="loading.operLogTable" :data="operLogPageData.records" stripe class="layout-table">
          <!-- 展开行 -->
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="pr-20 pl-20">
                <el-descriptions column="2">
                  <el-descriptions-item label="追踪ID">
                    {{ row.trace_id || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="API名称">
                    {{ row.api_name || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="业务模块">
                    {{ row.module || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="操作员ID">
                    {{ row.operator_id || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="响应码">
                    <el-tag :type="getResponseResultType(row)">
                      {{ row.response_code || '-' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="响应信息">
                    {{ row.response_msg || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="请求耗时">
                    <el-tag :type="getCostTimeType(row.cost_time)">
                      {{ formatCostTime(row.cost_time) }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="IP归属地">
                    {{ row.ip_location || formatLocation(row) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="请求数据">
                    <code>{{ row.request_body || '-' }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item label="响应数据">
                    {{ row.response_data || '-' }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </template>
          </el-table-column>

          <!-- 追踪ID -->
          <el-table-column prop="trace_id" label="追踪ID" width="280" show-overflow-tooltip />

          <!-- 请求方法 -->
          <el-table-column label="请求方法" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getRequestMethodType(row.request_method)">
                {{ row.request_method }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- API路径 -->
          <el-table-column prop="api_path" label="API路径" min-width="200" show-overflow-tooltip />

          <!-- 响应结果 -->
          <el-table-column label="响应结果" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getResponseResultType(row)">
                {{ formatResponseResult(row) }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 客户端IP -->
          <el-table-column prop="client_ip" label="客户端IP" width="100" />

          <!-- 请求耗时 -->
          <el-table-column label="请求耗时" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getCostTimeType(row.cost_time)">
                {{ formatCostTime(row.cost_time) }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 操作时间 -->
          <el-table-column prop="create_time" label="操作时间" width="180" />
        </el-table>

        <div class="layout-pagination">
          <el-pagination v-model:current-page="searchOperLogParams.page_num"
            v-model:page-size="searchOperLogParams.page_size" :total="operLogPageData.total"
            :page-sizes="PAGE_SIZE_OPTIONS" layout="total, sizes, prev, pager, next" :teleported="false"
            @size-change="handleSizeChange" @current-change="fetchOperLogList" />
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
</style>
