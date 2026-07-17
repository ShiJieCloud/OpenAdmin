<!--
 * @component OnlineUserManagement
 * @path views/monitor/online/index
 * @name 在线用户管理页面
 * @description 展示当前在线用户列表，支持查看用户登录信息、强制下线操作
 * @example
 * <OnlineUserManagement />
 * @author sjzhao
 * @date 2026-07-17
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useFullscreen } from '@vueuse/core'
import { ElMessage, ElMessageBox } from 'element-plus'

import type { IOnlineUserInfo, IOnlineUserListQueryParam } from '@/types'
import type { IPageResult } from '@/types/common/api'

import { getOnlineUserList, kickUserOffline } from '@/api/modules/online'

// ===================== 1. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [1, 10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

// ===================== 2. 响应式状态数据 =====================
/** 在线用户分页数据 */
const onlineUserPageData = ref<IPageResult<IOnlineUserInfo>>({
  records: [],
  total: 0,
  pages: 0,
  page_size: DEFAULT_PAGE_SIZE,
  page_num: 1,
})

/** 在线用户列表查询参数 */
const searchOnlineUserParams = reactive<IOnlineUserListQueryParam>({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
})

/** 加载状态管理 */
const loading = ref({
  onlineUserTable: false,
  onlineUserRefreshBtn: false,
})

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

// ===================== 3. 接口请求方法 =====================
/**
 * 拉取在线用户分页列表
 * @description 根据查询参数获取在线用户列表数据
 * @returns {Promise<void>}
 */
const fetchOnlineUserList = async () => {
  loading.value.onlineUserTable = true
  try {
    const res: IPageResult<IOnlineUserInfo> = await getOnlineUserList(searchOnlineUserParams)
    onlineUserPageData.value = {
      records: res.records || [],
      total: res.total || 0,
      pages: res.pages || 0,
      page_size: res.page_size || DEFAULT_PAGE_SIZE,
      page_num: res.page_num || 1,
    }
  } finally {
    loading.value.onlineUserTable = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 分页条数变更回调
 * @param val - 新的每页条数
 */
const handleSizeChange = (val: number) => {
  searchOnlineUserParams.page_size = val
  searchOnlineUserParams.page_num = 1
  fetchOnlineUserList()
}

/**
 * 刷新列表
 */
const handleRefreshOnlineUserList = async () => {
  try {
    loading.value.onlineUserRefreshBtn = true
    await fetchOnlineUserList()
    ElMessage.success('刷新成功')
  } finally {
    loading.value.onlineUserRefreshBtn = false
  }
}

/**
 * 踢出用户下线
 * @param row - 在线用户行数据
 */
const handleKickUser = async (row: IOnlineUserInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要强制踢出用户【${row.nickname || row.username}】下线吗？该用户的所有登录会话将立即失效。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await kickUserOffline(row.id)
    ElMessage.success('用户已强制下线')
    await fetchOnlineUserList()
  } catch (error) {
    // 用户取消操作，不处理
  }
}

/**
 * 格式化登录时间
 * @param loginTime - 登录时间字符串
 * @returns 格式化后的时间文本
 */
const formatLoginTime = (loginTime: string | null) => {
  if (!loginTime) return '-'
  return loginTime
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取在线用户列表数据
 */
onMounted(() => fetchOnlineUserList())
</script>

<template>
  <div ref="layoutPageRef" class="layout-page">
    <!-- 列表区域 -->
    <div class="layout-page__content">
      <el-card shadow="never">
        <div class="layout-toolbar">
          <h4 class="layout-toolbar__title">在线用户列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.onlineUserRefreshBtn" @click="handleRefreshOnlineUserList">
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

        <el-table v-loading="loading.onlineUserTable" :data="onlineUserPageData.records" stripe class="layout-table">
          <!-- 用户ID -->
          <el-table-column prop="id" label="用户ID" width="100" align="center" />

          <!-- 用户名 -->
          <el-table-column prop="username" label="用户名" min-width="120" align="center" />

          <!-- 用户昵称 -->
          <el-table-column prop="nickname" label="用户昵称" min-width="120" align="center">
            <template #default="{ row }">
              {{ row.nickname || '-' }}
            </template>
          </el-table-column>

          <!-- 登录IP -->
          <el-table-column prop="login_ip" label="登录IP" width="120" align="center">
            <template #default="{ row }">
              {{ row.login_ip || '-' }}
            </template>
          </el-table-column>

          <!-- 登录地点 -->
          <el-table-column prop="login_address" label="登录地点" width="180" align="center">
            <template #default="{ row }">
              {{ row.login_address || '-' }}
            </template>
          </el-table-column>

          <!-- 登录设备 -->
          <el-table-column prop="login_device" label="登录设备" width="100" align="center">
            <template #default="{ row }">
              {{ row.login_device || '-' }}
            </template>
          </el-table-column>

          <!-- 登录时间 -->
          <el-table-column label="登录时间" width="180" align="center">
            <template #default="{ row }">
              {{ formatLoginTime(row.login_time) }}
            </template>
          </el-table-column>

          <!-- 在线时长 -->
          <el-table-column prop="online_duration" label="在线时长" width="120" align="center">
            <template #default="{ row }">
              {{ row.online_duration || '-' }}
            </template>
          </el-table-column>

          <!-- 操作 -->
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="danger" link @click="handleKickUser(row)">
                <template #icon>
                  <i-ep-switch-button />
                </template>
                强制下线
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="layout-pagination">
          <el-pagination v-model:current-page="searchOnlineUserParams.page_num"
            v-model:page-size="searchOnlineUserParams.page_size" :total="onlineUserPageData.total"
            :page-sizes="PAGE_SIZE_OPTIONS" layout="total, sizes, prev, pager, next" :teleported="false"
            @size-change="handleSizeChange" @current-change="fetchOnlineUserList" />
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
