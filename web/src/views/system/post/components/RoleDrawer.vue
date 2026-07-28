<!--
 * @component RoleDrawer
 * @path views/system/post/components/RoleDrawer
 * @name 岗位角色分配抽屉组件
 * @description 为指定岗位配置绑定角色，支持角色分页筛选、跨页多选、变更对比保存
 * @props
 *  postId: number - 目标岗位唯一ID（必传）
 * @v-model
 *  visible: boolean - 抽屉显示隐藏
 * @example
 * <RoleDrawer
 *   v-model:visible="drawerVisible"
 *   :post-id="currentPostId"
 * />
 * @author sjzhao
 * @date 2026-07-24
 * @version 1.0.0
 * @internal 内部业务组件，仅岗位页面使用，不对外导出
-->
<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElTable } from 'element-plus'

import type { IRoleInfo, IPostInfo } from '@/types'
import { getRoleList, getPostRoles, assignPostRoles, getPostInfo } from '@/api'

const router = useRouter()

// ===================== Props / Model =====================

/** 组件入参：目标岗位 ID */
const props = defineProps<{ postId: number }>()

/** 抽屉显隐状态，支持 v-model:visible 双向绑定 */
const drawerVisible = defineModel<boolean>('visible', { default: false })

// ===================== 静态常量 =====================

/** 分页每页条数选项 */
const PAGE_SIZE_OPTIONS = [20, 50, 100]

/** 默认每页条数 */
const DEFAULT_PAGE_SIZE = 10

/** 角色状态下拉选项 */
const ROLE_STATUS_OPTIONS = [
  { label: '启用', value: 0 },
  { label: '禁用', value: 1 },
] as const

// ===================== 响应式状态 =====================

/** 按钮 / 表格加载状态 */
const loading = ref({
  saveRoleBtn: false,
  roleTable: false,
})

/** 角色表格数据 */
const roleTableData = ref<IRoleInfo[]>([])

/** 岗位已绑定的角色 ID 集合（原始快照，用于变更对比） */
const currentPostRoleIdSet = ref<Set<number>>(new Set())

/** 当前已勾选的角色 ID 集合 —— 跨页多选唯一数据源 */
const selectedRoleSet = ref<Set<number>>(new Set())

/** 表格 DOM 引用 */
const roleTableRef = ref<InstanceType<typeof ElTable>>()

/** 搜索表单 */
const searchForm = reactive({
  role_name: '',
  role_code: '',
  status: undefined as number | undefined,
})

/** 分页参数 */
const pagination = reactive({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
  total: 0,
})

/** 当前岗位详情 */
const currentPostInfo = ref<IPostInfo>()

// ===================== 工具函数 =====================

/**
 * 判断两个 Set 是否相等
 * @param setA - 集合 A
 * @param setB - 集合 B
 * @returns 两个集合元素完全一致时返回 true
 */
function isSetEqual(setA: Set<number>, setB: Set<number>): boolean {
  if (setA.size !== setB.size) return false
  for (const id of setA) {
    if (!setB.has(id)) return false
  }
  return true
}

/**
 * 恢复表格勾选状态
 * @description 根据 selectedRoleSet 同步当前页表格行的勾选 UI
 */
const restoreSelection = () => {
  const table = roleTableRef.value
  if (!table) return
  table.clearSelection()
  roleTableData.value.forEach(row => {
    if (selectedRoleSet.value.has(row.id)) {
      table.toggleRowSelection(row, true)
    }
  })
}

// ===================== 事件处理 =====================

/** 搜索角色 —— 重置到第一页后查询 */
const handleSearch = () => {
  pagination.page_num = 1
  fetchRoleList()
}

/** 重置搜索条件并重新查询 */
const handleResetSearch = () => {
  searchForm.role_name = ''
  searchForm.role_code = ''
  searchForm.status = undefined
  pagination.page_num = 1
  fetchRoleList()
}

/**
 * 点击角色名称，跳转至角色管理页并自动打开权限分配抽屉
 * @param row - 目标角色行数据
 */
const handleJumpToRole = (row: IRoleInfo) => {
  router.push({
    path: '/system/role',
    query: { openPermission: String(row.id) },
  })
}

/**
 * 单行角色勾选 / 取消
 * @param selection - 当前勾选行列表
 * @param row - 当前操作行
 */
const handleSelectRole = (selection: IRoleInfo[], row: IRoleInfo) => {
  const isChecked = selection.some(item => item.id === row.id)
  isChecked ? selectedRoleSet.value.add(row.id) : selectedRoleSet.value.delete(row.id)
}

/**
 * 全选 / 取消全选当前页角色
 * @description 仅操作当前页可勾选行，不影响其他分页已勾选的角色
 * @param selection - 全选时的勾选行列表，空数组表示取消全选
 */
const handleSelectAllRole = (selection: IRoleInfo[]) => {
  if (selection.length === 0) {
    // 取消全选：移除当前页所有启用状态角色的 ID
    roleTableData.value
      .filter(row => row.status === 0)
      .forEach(row => selectedRoleSet.value.delete(row.id))
  } else {
    // 全选：selection 已包含当前页所有可勾选行
    selection.forEach(row => selectedRoleSet.value.add(row.id))
  }
}

/**
 * 分页 —— 页码切换
 * @param val - 目标页码
 */
const handleCurrentChange = async (val: number) => {
  pagination.page_num = val
  await fetchRoleList()
  await nextTick()
  restoreSelection()
}

/**
 * 分页 —— 每页条数切换
 * @param val - 新的每页条数
 */
const handleSizeChange = async (val: number) => {
  pagination.page_size = val
  pagination.page_num = 1
  await fetchRoleList()
  await nextTick()
  restoreSelection()
}

// ===================== 接口请求 =====================

/** 拉取角色列表（带搜索 & 分页） */
const fetchRoleList = async () => {
  try {
    loading.value.roleTable = true
    const res = await getRoleList({
      ...searchForm,
      page_num: pagination.page_num,
      page_size: pagination.page_size,
    })
    roleTableData.value = res.records
    pagination.total = res.total
  } finally {
    loading.value.roleTable = false
  }
}

/** 拉取岗位已绑定的角色 ID 列表，并初始化勾选集合 */
const fetchPostRoles = async () => {
  const postRoles = await getPostRoles(props.postId)
  if (!postRoles) return
  currentPostRoleIdSet.value = new Set(postRoles)
  selectedRoleSet.value = new Set(currentPostRoleIdSet.value)
}

/** 拉取岗位详情 */
const fetchPostInfo = async () => {
  const postInfo = await getPostInfo(props.postId)
  if (!postInfo) return
  currentPostInfo.value = postInfo
}

// ===================== 业务逻辑 =====================

/**
 * 抽屉打开回调
 * @description 并行加载角色列表、已绑定角色、岗位详情，DOM 就绪后恢复勾选状态
 */
const handleOpenRoleDrawer = async () => {
  await Promise.all([fetchRoleList(), fetchPostRoles(), fetchPostInfo()])
  await nextTick()
  restoreSelection()
}

/** 关闭抽屉并重置所有状态 */
const closeRoleDrawer = () => {
  drawerVisible.value = false
  selectedRoleSet.value.clear()
  searchForm.role_name = ''
  searchForm.role_code = ''
  searchForm.status = undefined
}

/**
 * 提交角色分配
 * @description 对比变更后再提交，无变更时给出提示
 */
const submitRoleAssign = async () => {
  const { postId } = props
  if (!postId) return

  const selectedSet = selectedRoleSet.value
  const originSet = currentPostRoleIdSet.value

  if (isSetEqual(selectedSet, originSet)) {
    ElMessage.warning('角色未发生变更，无需保存')
    return
  }

  loading.value.saveRoleBtn = true
  try {
    await assignPostRoles(postId, [...selectedSet])
    ElMessage.success('角色分配成功')
    closeRoleDrawer()
  } finally {
    loading.value.saveRoleBtn = false
  }
}
</script>

<template>
  <el-drawer
    v-model="drawerVisible"
    size="50%"
    resizable
    @close="closeRoleDrawer"
    @open="handleOpenRoleDrawer"
  >
    <!-- 抽屉头部标题区域 -->
    <template #header>
      <div class="flex items-center gap-2">
        <div class="text-lg font-bold">角色配置</div>
        <el-tag type="primary" effect="light" size="small">
          {{ currentPostInfo?.post_name || '未知岗位' }}
        </el-tag>
      </div>
    </template>

    <!-- 抽屉主体内容 -->
    <template #default>
      <div class="role-drawer">
        <!-- 搜索筛选栏 -->
        <div class="role-drawer__header">
          <el-form :model="searchForm" label-width="auto">
            <el-row :gutter="20">
              <el-col :sm="12">
                <el-form-item label="角色名称">
                  <el-input
                    v-model="searchForm.role_name"
                    placeholder="请输入角色名称"
                    clearable
                    @keyup.enter="handleSearch"
                  />
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item label="角色编码">
                  <el-input
                    v-model="searchForm.role_code"
                    placeholder="请输入角色编码"
                    clearable
                    @keyup.enter="handleSearch"
                  />
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item label="状态">
                  <el-select
                    v-model="searchForm.status"
                    placeholder="请选择状态"
                    clearable
                  >
                    <el-option
                      v-for="item in ROLE_STATUS_OPTIONS"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :sm="12">
                <el-form-item>
                  <el-space alignment="flex-end" class="justify-end w-full">
                    <el-button type="primary" @click="handleSearch">
                      <template #icon>
                        <i-ep-search />
                      </template>
                      搜索
                    </el-button>
                    <el-button @click="handleResetSearch">
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

        <!-- 角色表格+分页容器 -->
        <div v-loading="loading.roleTable" class="role-drawer__content">
          <el-table
            ref="roleTableRef"
            border
            stripe
            :data="roleTableData"
            row-key="id"
            @select="handleSelectRole"
            @select-all="handleSelectAllRole"
          >
            <!-- 多选框：仅启用角色可勾选 -->
            <el-table-column
              type="selection"
              width="55"
              align="center"
              :reserve-selection="true"
              :selectable="(row: IRoleInfo) => row.status === 0"
            />
            <!-- 角色名称（可跳转角色管理） -->
            <el-table-column prop="role_name" label="角色名称" min-width="140" align="center">
              <template #default="{ row }">
                <el-link type="primary" underline="hover" @click="handleJumpToRole(row)">
                  {{ row.role_name }}
                </el-link>
              </template>
            </el-table-column>
            <!-- 角色编码 -->
            <el-table-column prop="role_code" label="角色编码" min-width="160" align="center">
              <template #default="{ row }">
                <el-tag type="info">{{ row.role_code }}</el-tag>
              </template>
            </el-table-column>
            <!-- 角色状态 -->
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 0 ? 'success' : 'danger'">
                  {{ row.status === 0 ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <!-- 角色描述，超长悬浮提示 -->
            <el-table-column
              prop="description"
              label="描述"
              min-width="200"
              align="center"
              show-overflow-tooltip
            />
          </el-table>

          <!-- 分页组件 -->
          <div class="layout-pagination">
            <el-pagination
              v-model:current-page="pagination.page_num"
              v-model:page-size="pagination.page_size"
              :total="pagination.total"
              :page-sizes="PAGE_SIZE_OPTIONS"
              layout="total, sizes, prev, pager, next"
              @current-change="handleCurrentChange"
              @size-change="handleSizeChange"
            />
          </div>
        </div>
      </div>
    </template>

    <!-- 抽屉底部操作按钮 -->
    <template #footer>
      <el-space>
        <el-button @click="closeRoleDrawer">取消</el-button>
        <el-button
          plain
          type="primary"
          :loading="loading.saveRoleBtn"
          @click="submitRoleAssign"
        >
          确定分配
        </el-button>
      </el-space>
    </template>
  </el-drawer>
</template>

<style scoped>
/* 抽屉整体弹性容器，自适应高度 */
.role-drawer {
  flex: 1 1 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 搜索栏固定高度不压缩 */
.role-drawer__header {
  flex: 0 0 auto;
}

/* 表格区域自适应剩余高度，溢出滚动 */
.role-drawer__content {
  flex: 1 1 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 表格撑满容器高度 */
.role-drawer__content :deep(.el-table) {
  width: 100%;
  height: 100%;
}

/* 表格主体区域自适应，出现滚动条 */
.role-drawer__content :deep(.el-table__body-wrapper) {
  flex: 1 1 auto;
  min-height: 0;
}

/* 空数据居中 */
.role-drawer__content :deep(.el-empty) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>