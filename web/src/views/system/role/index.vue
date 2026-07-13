<!--
 * @component RoleManagement
 * @path views/system/role/index
 * @name 角色管理页面
 * @description 实现角色列表的增删改查，提供角色搜索、新增、编辑、删除、批量删除及权限分配功能
 * @example
 * <RoleManagement />
 * @author sjzhao
 * @date 2026-07-13
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useFullscreen } from '@vueuse/core'

import type { IRoleInfo, IRoleListQueryParam, RoleCreateRequest, RoleUpdateRequest } from '@/types/modules/role'
import type { IPageResult } from '@/types/common/api'

import { getRoleList, createRole, updateRole, deleteRole } from '@/api/modules/role'

import PermissionDrawer from './components/PermissionDrawer.vue'

// ===================== 1. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [1, 10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

/** 角色状态选项 */
const ROLE_STATUS_OPTIONS = [
  { label: '启用', value: 1 },
  { label: '禁用', value: 0 },
] as const

// ===================== 2. 响应式状态数据 =====================
/** 角色分页数据 */
const rolePageData = ref<IPageResult<IRoleInfo>>({
  records: [],
  total: 0,
  pages: 0,
  page_size: DEFAULT_PAGE_SIZE,
  page_num: 1,
})

/** 角色列表查询参数 */
const searchRoleParams = reactive<IRoleListQueryParam>({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
  role_name: '',
  role_code: '',
  status: undefined,
})

/** 加载状态管理 */
const loading = ref({
  roleTable: false,
  roleRefreshBtn: false,
  roleEditDrawer: false,
  roleAddBtn: false,
  roleDeleteBtn: false,
  roleBatchDeleteBtn: false,
})

/** 表格已勾选的角色行集合 */
const selectedRows = ref<IRoleInfo[]>([])

/** 权限分配抽屉显隐状态 */
const permissionDrawerVisible = ref(false)

/** 当前操作的角色ID（用于权限分配） */
const currentRoleId = ref<number>(0)

/** 新增角色弹窗显隐状态 */
const addRoleDialogVisible = ref(false)

/** 新增角色表单引用 */
const addRoleFormRef = ref<FormInstance>()

/** 新增角色表单数据 */
const addRoleForm = reactive<RoleCreateRequest>({
  role_name: '',
  role_code: '',
  sort: 0,
  description: '',
  status: 1,
})

/** 新增角色表单校验规则 */
const addRoleRules = reactive<FormRules<RoleCreateRequest>>({
  role_name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' },
  ],
  role_code: [
    { required: true, message: '请输入角色标识', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/,
      message: '只能包含字母、数字和下划线，且以字母或下划线开头',
      trigger: 'blur',
    },
  ],
})

/** 编辑角色弹窗显隐状态 */
const editRoleDialogVisible = ref(false)

/** 编辑角色表单引用 */
const editRoleFormRef = ref<FormInstance>()

/** 编辑角色表单数据 */
const editRoleForm = reactive<RoleUpdateRequest>({
  role_id: 0,
  role_name: '',
  role_code: '',
  sort: 0,
  description: '',
  status: 1,
})

/** 编辑角色表单校验规则 */
const editRoleRules = reactive<FormRules<RoleUpdateRequest>>({
  role_name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' },
  ],
  role_code: [
    { required: true, message: '请输入角色标识', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/,
      message: '只能包含字母、数字和下划线，且以字母或下划线开头',
      trigger: 'blur',
    },
  ],
})

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

// ===================== 3. 接口请求方法 =====================
/**
 * 拉取角色分页列表
 * @description 根据查询参数获取角色列表数据，并按 sort 字段升序排序
 * @returns {Promise<void>}
 */
const fetchRoleList = async () => {
  loading.value.roleTable = true
  try {
    const res: IPageResult<IRoleInfo> = await getRoleList(searchRoleParams)
    rolePageData.value = {
      records: res.records?.sort((a, b) => a.sort - b.sort) || [],
      total: res.total || 0,
      pages: res.pages || 0,
      page_size: res.page_size || DEFAULT_PAGE_SIZE,
      page_num: res.page_num || 1,
    }
  } finally {
    loading.value.roleTable = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 搜索回调
 * @description 重置页码并拉取列表
 */
const handleSearch = () => {
  searchRoleParams.page_num = 1
  fetchRoleList()
}

/**
 * 重置回调
 * @description 清空搜索条件并重新查询
 */
const handleReset = () => {
  searchRoleParams.role_name = ''
  searchRoleParams.role_code = ''
  searchRoleParams.status = undefined
  handleSearch()
}

/**
 * 分页条数变更回调
 * @param val - 新的每页条数
 */
const handleSizeChange = (val: number) => {
  searchRoleParams.page_size = val
  searchRoleParams.page_num = 1
  fetchRoleList()
}

/**
 * 表格勾选变更回调
 * @param val - 已勾选的角色行集合
 */
const handleSelectionChange = (val: IRoleInfo[]) => {
  selectedRows.value = val
}

/**
 * 打开新增角色弹窗
 */
const handleAddRole = () => {
  addRoleDialogVisible.value = true
}

/**
 * 关闭新增角色弹窗并重置表单
 */
const closeAddRoleDialog = () => {
  addRoleDialogVisible.value = false
  addRoleFormRef.value?.resetFields()
}

/**
 * 提交新增角色表单
 * @description 验证表单后调用创建接口，成功后关闭弹窗并刷新列表
 */
const submitAddRole = async () => {
  if (!addRoleFormRef.value) return
  const valid = await addRoleFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.roleAddBtn = true
  try {
    await createRole(addRoleForm)
    ElMessage.success('角色创建成功')
    closeAddRoleDialog()
    fetchRoleList()
  } finally {
    loading.value.roleAddBtn = false
  }
}

/**
 * 打开编辑角色弹窗并回填数据
 * @param row - 目标角色行数据
 */
const handleEditRole = (row: IRoleInfo) => {
  editRoleForm.role_id = row.id
  editRoleForm.role_name = row.role_name
  editRoleForm.role_code = row.role_code
  editRoleForm.sort = row.sort
  editRoleForm.description = row.description
  editRoleForm.status = row.status
  editRoleDialogVisible.value = true
}

/**
 * 关闭编辑角色弹窗并重置表单
 */
const closeEditRoleDialog = () => {
  editRoleDialogVisible.value = false
  editRoleFormRef.value?.resetFields()
}

/**
 * 提交编辑角色表单
 * @description 验证表单后调用更新接口，成功后关闭弹窗并刷新列表
 */
const submitEditRole = async () => {
  if (!editRoleFormRef.value) return
  const valid = await editRoleFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.roleEditDrawer = true
  try {
    await updateRole(editRoleForm)
    ElMessage.success('角色更新成功')
    closeEditRoleDialog()
    fetchRoleList()
  } finally {
    loading.value.roleEditDrawer = false
  }
}

/**
 * 删除单个角色
 * @param row - 目标角色行数据
 * @description 弹出确认框后执行删除操作
 */
const handleDeleteRole = async (row: IRoleInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色【${row.role_name}】吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.roleDeleteBtn = true
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    fetchRoleList()
  } finally {
    loading.value.roleDeleteBtn = false
  }
}

/**
 * 批量删除已勾选角色
 * @description 批量删除选中的角色，支持并发删除
 */
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的角色')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的【${selectedRows.value.length}】个角色吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.roleBatchDeleteBtn = true
    const deletePromises = selectedRows.value.map(role => deleteRole(role.id))
    await Promise.all(deletePromises)

    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchRoleList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value.roleBatchDeleteBtn = false
  }
}

/**
 * 打开权限分配抽屉
 * @param row - 目标角色行数据
 */
const openPermissionDrawer = (row: IRoleInfo) => {
  currentRoleId.value = row.id
  permissionDrawerVisible.value = true
}

const handleRefreshRoleList = async () => {
  try {
    loading.value.roleRefreshBtn = true
    await fetchRoleList()
  } finally {
    loading.value.roleRefreshBtn = false
  }
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取角色列表数据
 */
onMounted(() => fetchRoleList())
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
            <el-form :model="searchRoleParams" label-width="auto">
              <el-row :gutter="20" class="pl-5">
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="角色名称">
                    <el-input v-model="searchRoleParams.role_name" placeholder="请输入角色名称" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="角色标识">
                    <el-input v-model="searchRoleParams.role_code" placeholder="请输入角色标识" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="状态">
                    <el-select v-model="searchRoleParams.status" placeholder="请选择状态" clearable>
                      <el-option
                        v-for="item in ROLE_STATUS_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="24" :lg="6">
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
          <h4 class="layout-toolbar__title">角色列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.roleRefreshBtn" @click="handleRefreshRoleList">
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
            <el-button plain type="primary" @click="handleAddRole">
              <template #icon>
                <i-ep-plus />
              </template>
              新增
            </el-button>
            <el-button plain type="danger" :disabled="selectedRows.length === 0" @click="handleBatchDelete">
              <template #icon>
                <i-ep-delete />
              </template>
              批量删除
            </el-button>
          </el-space>
        </div>

        <el-table
          v-loading="loading.roleTable"
          :data="rolePageData.records"
          stripe
          width="100%"
          class="layout-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="角色 ID" width="100" />
          <el-table-column prop="role_name" label="角色名称" width="150" />
          <el-table-column prop="role_code" label="角色标识" width="150" />
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'danger'">
                {{ row.status === 1 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" />
          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="handleEditRole(row)">
                <template #icon>
                  <i-ep-edit-pen />
                </template>
                编辑
              </el-button>
              <el-button type="primary" size="small" link @click="openPermissionDrawer(row)">
                <template #icon>
                  <i-solar-shield-user-broken />
                </template>
                分配权限
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteRole(row)">
                <template #icon>
                  <i-ep-delete />
                </template>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="layout-pagination">
          <el-pagination
            v-model:current-page="searchRoleParams.page_num"
            v-model:page-size="searchRoleParams.page_size"
            :total="rolePageData.total"
            :page-sizes="PAGE_SIZE_OPTIONS"
            layout="total, sizes, prev, pager, next"
            :teleported="false"
            @size-change="handleSizeChange"
            @current-change="fetchRoleList"
          />
        </div>
      </el-card>
    </div>

      <!-- 新增角色弹窗 -->
  <el-dialog
    v-model="addRoleDialogVisible"
    title="新增角色"
    width="500px"
    @close="closeAddRoleDialog"
  >
    <el-form ref="addRoleFormRef" :model="addRoleForm" :rules="addRoleRules" label-width="80px">
      <el-form-item label="角色名称" prop="role_name">
        <el-input v-model="addRoleForm.role_name" placeholder="请输入角色名称" clearable />
      </el-form-item>
      <el-form-item label="角色标识" prop="role_code">
        <el-input v-model="addRoleForm.role_code" placeholder="请输入角色标识" clearable />
      </el-form-item>
      <el-form-item label="排序" prop="sort">
        <el-input-number v-model="addRoleForm.sort" :min="0" :max="9999" controls-position="right" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="addRoleForm.status">
          <el-radio v-for="item in ROLE_STATUS_OPTIONS" :key="item.value" :value="item.value">
            {{ item.label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="addRoleForm.description"
          type="textarea"
          :rows="3"
          placeholder="请输入角色描述"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-space>
        <el-button @click="closeAddRoleDialog">取消</el-button>
        <el-button plain type="primary" :loading="loading.roleAddBtn" @click="submitAddRole">
          确定
        </el-button>
      </el-space>
    </template>
  </el-dialog>

  <!-- 编辑角色弹窗 -->
  <el-dialog
    v-model="editRoleDialogVisible"
    title="编辑角色"
    width="500px"
    @close="closeEditRoleDialog"
  >
    <el-form ref="editRoleFormRef" :model="editRoleForm" :rules="editRoleRules" label-width="80px">
      <el-form-item label="角色名称" prop="role_name">
        <el-input v-model="editRoleForm.role_name" placeholder="请输入角色名称" clearable />
      </el-form-item>
      <el-form-item label="角色标识" prop="role_code">
        <el-input v-model="editRoleForm.role_code" placeholder="请输入角色标识" clearable />
      </el-form-item>
      <el-form-item label="排序" prop="sort">
        <el-input-number v-model="editRoleForm.sort" :min="0" :max="9999" controls-position="right" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="editRoleForm.status">
          <el-radio v-for="item in ROLE_STATUS_OPTIONS" :key="item.value" :value="item.value">
            {{ item.label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="editRoleForm.description"
          type="textarea"
          :rows="3"
          placeholder="请输入角色描述"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-space>
        <el-button @click="closeEditRoleDialog">取消</el-button>
        <el-button plain type="primary" :loading="loading.roleEditDrawer" @click="submitEditRole">
          确定
        </el-button>
      </el-space>
    </template>
  </el-dialog>

  <!-- 权限分配抽屉 -->
  <PermissionDrawer
    v-model:visible="permissionDrawerVisible"
    :role-id="currentRoleId"
  />
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
