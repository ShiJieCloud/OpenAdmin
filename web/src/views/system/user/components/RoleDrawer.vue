<!--
 * @component RoleDrawer
 * @path views/system/user/components/RoleDrawer
 * @name 用户角色分配抽屉组件
 * @description 实现用户角色配置，提供角色列表展示、勾选/取消、保存角色功能
 * @props
 *  visible: boolean - 抽屉显示隐藏（v-model绑定）
 *  userId: number - 目标用户唯一ID，必传参数
 * @example
 * <RoleDrawer
 *   v-model:visible="drawerVisible"
 *   :user-id="currentUserId"
 * />
 * @author sjzhao
 * @date 2026-07-28
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ElMessage, ElTable } from 'element-plus'

import type { IRoleInfo } from '@/types/modules/role'
import { getRoleList } from '@/api/modules/role'
import { getUserRoles, assignUserRoles } from '@/api/modules/user'

// ===================== 1. Props / Model 定义 =====================
/** 组件入参：用户ID */
const props = defineProps<{
  userId: number
}>()

/** 抽屉显隐状态（v-model 双向绑定） */
const drawerVisible = defineModel<boolean>('visible', {
  default: false,
})

// ===================== 2. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

// ===================== 3. 响应式状态数据 =====================
/** 加载状态管理 */
const loading = ref({
  saveBtn: false,
  roleList: false,
})

/** 当前页角色列表 */
const roleList = ref<IRoleInfo[]>([])

/** 角色分页查询参数 */
const roleQueryParams = ref({
  role_name: '',
  role_code: '',
  status: undefined,
})

const pagination = ref({
  total: 0,
  pageSize: DEFAULT_PAGE_SIZE,
  pageNum: 1,
})

/** 用户原有角色ID集合（用于变更对比） */
const currentRoleIds = ref<Set<number>>(new Set())

/** 当前已勾选的角色ID集合（跨页保持） */
const selectedRoleIds = ref<Set<number>>(new Set())

/** 表格组件引用 */
const roleTableRef = ref<InstanceType<typeof ElTable>>()

// ===================== 4. 接口请求 method =====================
/** 拉取角色分页列表 */
const fetchRoleList = async () => {
  try {
    loading.value.roleList = true
    const res = await getRoleList({
      page_num: pagination.value.pageNum,
      page_size: pagination.value.pageSize,
      role_name: roleQueryParams.value.role_name || undefined,
      role_code: roleQueryParams.value.role_code || undefined,
      status: roleQueryParams.value.status || undefined,
    })
    roleList.value = res.records || []
    pagination.value.total = res.total || 0
  } finally {
    loading.value.roleList = false
  }
}

/** 拉取用户已绑定角色ID列表 */
const fetchUserRoles = async () => {
  const roleIds = await getUserRoles(props.userId)
  currentRoleIds.value = new Set(roleIds)
  selectedRoleIds.value = new Set(roleIds)
}

// ===================== 5. 业务处理 =====================
/**
 * 抽屉打开回调
 * @description 并行加载数据，等待 DOM 渲染后恢复勾选状态
 */
const handleOpenRoleDrawer = async () => {
  await Promise.all([fetchRoleList(), fetchUserRoles()])
  await nextTick()
  restoreSelection()
}

/** 关闭抽屉 */
const closeRoleDrawer = () => {
  roleQueryParams.value = {
    role_name: '',
    role_code: '',
    status: undefined,
  }
  pagination.value.pageNum = 1
  drawerVisible.value = false
  selectedRoleIds.value.clear()
}

/**
 * 搜索角色
 * @description 重置页码并查询
 */
const handleSearchRole = () => {
  pagination.value.pageNum = 1
  fetchRoleList()
}

/**
 * 重置搜索条件
 */
const handleResetRole = () => {
  roleQueryParams.value = {
    role_name: '',
    role_code: '',
    status: undefined,
  }
  pagination.value.pageNum = 1
  fetchRoleList()
}

/**
 * 单行角色勾选 / 取消
 * @param selection - 当前勾选行列表
 * @param row - 当前操作行
 */
const handleSelectRole = (selection: IRoleInfo[], row: IRoleInfo) => {
  const isChecked = selection.some(item => item.id === row.id)
  isChecked ? selectedRoleIds.value.add(row.id) : selectedRoleIds.value.delete(row.id)
}

/**
 * 全选 / 取消全选当前页角色
 * @description 仅操作当前页可勾选行，不影响其他分页已勾选的角色
 * @param selection - 全选时的勾选行列表，空数组表示取消全选
 */
const handleSelectAllRole = (selection: IRoleInfo[]) => {
  const enabledSelection = selection.filter(row => row.status === 0)
  const isSelectAll = enabledSelection.length > 0;
  
  if (isSelectAll) {
    selection.forEach(row => selectedRoleIds.value.add(row.id))
  } else {
    roleList.value.filter(row => row.status === 0)
    .forEach(row => selectedRoleIds.value.delete(row.id))
  }
}

/**
 * 每页条数变更
 * @param val - 新的每页条数
 */
const handleRoleSizeChange = async (val: number) => {
  pagination.value.pageSize = val
  pagination.value.pageNum = 1
  await fetchRoleList()
  await nextTick()
  restoreSelection()
}

/**
 * 页码变更
 * @param val - 目标页码
 */
const handleRolePageChange = async (val: number) => {
  pagination.value.pageNum = val
  await fetchRoleList()
  await nextTick()
  restoreSelection()
}

/**
 * 恢复表格勾选状态
 * @description 根据 selectedRoleIds 同步表格 UI 勾选
 */
const restoreSelection = () => {
  const table = roleTableRef.value
  if (!table) return
  table.clearSelection()
  roleList.value.forEach(row => {
    if (selectedRoleIds.value.has(row.id)) {
      table.toggleRowSelection(row, true)
    }
  })
}

/**
 * 提交角色分配
 * @description 对比变更后提交
 */
const submitRoleAssign = async () => {
  if (!props.userId) return

  const selectedSet = selectedRoleIds.value
  const originSet = currentRoleIds.value

  // 对比变更
  const isChanged = selectedSet.size !== originSet.size ||
    !Array.from(selectedSet).every(id => originSet.has(id))

  if (!isChanged) {
    ElMessage.warning('角色未发生变更，无需保存')
    return
  }

  const roleIds = Array.from(selectedSet)
  loading.value.saveBtn = true

  try {
    await assignUserRoles(props.userId, roleIds)
    ElMessage.success('角色分配成功')
    closeRoleDrawer()
  } finally {
    loading.value.saveBtn = false
  }
}

// ===================== 6. 监听逻辑 =====================
/** 监听抽屉打开 */
watch(drawerVisible, (val) => {
  if (val) {
    handleOpenRoleDrawer()
  }
})
</script>

<template>
  <!-- 角色配置抽屉 -->
  <el-drawer
    v-model="drawerVisible"
    size="50%"
    resizable
    @close="closeRoleDrawer"
  >
    <!-- 抽屉头部标题 -->
    <template #header>
      <div class="flex items-center gap-2">
        <div class="text-lg font-bold">角色配置</div>
      </div>
    </template>

    <!-- 抽屉主体内容 -->
    <template #default>
      <div class="role-drawer">
        <!-- 搜索筛选区域 -->
        <div class="role-header">
          <el-form :model="roleQueryParams" label-width="auto">
            <el-row :gutter="20">
              <el-col :sm="12">
                <el-form-item label="角色名称">
                  <el-input
                    v-model="roleQueryParams.role_name"
                    placeholder="请输入角色名称"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item label="角色编码">
                  <el-input
                    v-model="roleQueryParams.role_code"
                    placeholder="请输入角色编码"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item label="状态">
                  <el-select
                    v-model="roleQueryParams.status"
                    placeholder="请选择状态"
                    clearable
                  >
                    <el-option label="正常" value="0" />
                    <el-option label="禁用" value="1" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item>
                  <el-space alignment="flex-end" class="justify-end w-full">
                    <el-button plain type="primary" @click="handleSearchRole">
                      <template #icon>
                        <i-ep-search />
                      </template>
                      搜索
                    </el-button>
                    <el-button @click="handleResetRole">
                      <template #icon>
                        <i-ep-refresh-right />
                      </template>
                      重置
                    </el-button>
                  </el-space>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <!-- 角色表格列表 -->
        <div v-loading="loading.roleList" class="role-content">
          <el-table
            ref="roleTableRef"
            :data="roleList"
            border
            stripe
            row-key="id"
            @select="handleSelectRole"
            @select-all="handleSelectAllRole"
          >
            <el-table-column
              type="selection"
              width="55"
              align="center"
              :reserve-selection="true"
              :selectable="(row: IRoleInfo) => row.status === 0"
            />
            <el-table-column prop="role_name" label="角色名称" min-width="120" />
            <el-table-column prop="role_code" label="角色编码" min-width="120" />
            <el-table-column
              prop="description"
              label="描述"
              min-width="180"
              show-overflow-tooltip
            />
          </el-table>
        </div>

        <!-- 分页组件 -->
        <div class="layout-pagination">
          <el-pagination
            v-model:current-page="pagination.pageNum"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="PAGE_SIZE_OPTIONS"
            layout="total, sizes, prev, pager, next"
            :teleported="false"
            @size-change="handleRoleSizeChange"
            @current-change="handleRolePageChange"
          />
        </div>
      </div>
    </template>

    <!-- 底部操作按钮 -->
    <template #footer>
      <el-space>
        <el-button @click="closeRoleDrawer">取消</el-button>
        <el-button
          plain
          type="primary"
          :loading="loading.saveBtn"
          @click="submitRoleAssign"
        >
          确定保存
        </el-button>
      </el-space>
    </template>
  </el-drawer>
</template>

<style scoped>
.role-drawer {
  flex: 1 1 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.role-header {
  flex: 0 0 auto;
  margin-bottom: 16px;
}

.role-content {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.role-content :deep(.el-table) {
  flex: 1 1 auto;
  min-height: 0;
}

.role-content :deep(.el-table__body-wrapper) {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}
</style>
