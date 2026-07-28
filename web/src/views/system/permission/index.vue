<!--
 * @component PermissionManagement
 * @path views/system/permission/index
 * @name 权限管理页面
 * @description 实现权限列表的增删改查，提供权限搜索、新增、编辑、删除、批量删除功能
 * @example
 * <PermissionManagement />
 * @author sjzhao
 * @date 2026-07-28
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useFullscreen } from '@vueuse/core'

import type {
  IPermissionInfo,
  PermissionCreateRequest,
  PermissionUpdateRequest
} from '@/types/modules/permission'
import type { IMenuItem } from '@/types/modules/menu'
import type { IPageResult } from '@/types/common/api'

import {
  getPermissionList,
  createPermission,
  updatePermission,
  deletePermission
} from '@/api/modules/permission'
import { getSystemMenuTree } from '@/api/modules/menu'

// ===================== 1. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [1, 10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

/** 权限状态选项 */
const PERM_STATUS_OPTIONS = [
  { label: '正常', value: 0 },
  { label: '停用', value: 1 },
] as const

// ===================== 2. 响应式状态数据 =====================
/** 权限列表数据 */
const permissionTableData = ref<IPermissionInfo[]>([])

/** 权限列表查询参数 */
const searchPermissionParams = reactive({
  name: '',
  code: '',
  status: undefined,
  menu_ids: [],
})

/** 权限分页数据 */
const pagination = reactive({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
  total: 0,
})

/** 加载状态管理 */
const loading = ref({
  permTable: false,
  permRefreshBtn: false,
  permEditBtn: false,
  permAddBtn: false,
  permDeleteBtn: false,
  permBatchDeleteBtn: false,
  menuTree: false,
})

/** 表格已勾选的权限行集合 */
const selectedRows = ref<IPermissionInfo[]>([])

/** 菜单树数据 */
const menuTreeData = ref<IMenuItem[]>([])

/** 新增权限弹窗显隐状态 */
const addPermDialogVisible = ref(false)

/** 新增权限表单引用 */
const addPermFormRef = ref<FormInstance>()

/** 新增权限表单数据 */
const addPermForm = reactive<PermissionCreateRequest>({
  menu_id: undefined as unknown as number,
  name: '',
  code: '',
  sort: 0,
  status: 0,
  description: '',
})

/** 新增权限表单校验规则 */
const addPermRules = reactive<FormRules<PermissionCreateRequest>>({
  menu_id: [
    { required: true, message: '请选择所属菜单', trigger: 'change' },
  ],
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 64, message: '长度在 2 到 64 个字符', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z_][a-zA-Z0-9_:]*$/,
      message: '只能包含字母、数字、下划线和冒号，且以字母或下划线开头',
      trigger: 'blur',
    },
  ],
})

/** 编辑权限弹窗显隐状态 */
const editPermDialogVisible = ref(false)

/** 编辑权限表单引用 */
const editPermFormRef = ref<FormInstance>()

/** 编辑权限表单数据 */
const editPermForm = reactive<PermissionUpdateRequest>({
  perm_id: 0,
  menu_id: undefined,
  name: '',
  code: '',
  sort: 0,
  status: 0,
  description: '',
})

/** 编辑权限表单校验规则 */
const editPermRules = reactive<FormRules<PermissionUpdateRequest>>({
  menu_id: [
    { required: true, message: '请选择所属菜单', trigger: 'change' },
  ],
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 64, message: '长度在 2 到 64 个字符', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z_][a-zA-Z0-9_:]*$/,
      message: '只能包含字母、数字、下划线和冒号，且以字母或下划线开头',
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
 * 拉取权限分页列表
 * @description 根据查询参数获取权限列表数据，并按 sort 字段升序排序
 * @returns {Promise<void>}
 */
const fetchPermissionList = async () => {
  loading.value.permTable = true
  try {
    const res: IPageResult<IPermissionInfo> = await getPermissionList({
      ...searchPermissionParams,
      page_num: pagination.page_num,
      page_size: pagination.page_size,
    })
    permissionTableData.value = res.records?.sort((a, b) => a.sort - b.sort) || [],
    pagination.total = res.total || 0
  } finally {
    loading.value.permTable = false
  }
}

/**
 * 拉取系统菜单树
 * @description 获取所有菜单的树形结构数据
 * @returns {Promise<void>}
 */
const fetchMenuTree = async () => {
  loading.value.menuTree = true
  try {
    const menuTree = await getSystemMenuTree()
    menuTreeData.value = menuTree
  } finally {
    loading.value.menuTree = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 搜索回调
 * @description 重置页码并拉取列表
 */
const handleSearch = () => {
  pagination.page_num = 1
  fetchPermissionList()
}

/**
 * 重置回调
 * @description 清空搜索条件并重新查询
 */
const handleReset = () => {
  searchPermissionParams.name = ''
  searchPermissionParams.code = ''
  searchPermissionParams.status = undefined
  searchPermissionParams.menu_ids = []
  handleSearch()
}

/**
 * 分页条数变更回调
 * @param val - 新的每页条数
 */
const handleSizeChange = (val: number) => {
  pagination.page_size = val
  pagination.page_num = 1
  fetchPermissionList()
}

/**
 * 表格勾选变更回调
 * @param val - 已勾选的权限行集合
 */
const handleSelectionChange = (val: IPermissionInfo[]) => {
  selectedRows.value = val
}

/**
 * 打开新增权限弹窗
 */
const handleAddPerm = () => {
  addPermDialogVisible.value = true
}

/**
 * 关闭新增权限弹窗并重置表单
 */
const closeAddPermDialog = () => {
  addPermDialogVisible.value = false
  addPermFormRef.value?.resetFields()
}

/**
 * 提交新增权限表单
 * @description 验证表单后调用创建接口，成功后关闭弹窗并刷新列表
 */
const submitAddPerm = async () => {
  if (!addPermFormRef.value) return
  const valid = await addPermFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.permAddBtn = true
  try {
    await createPermission(addPermForm)
    ElMessage.success('权限创建成功')
    closeAddPermDialog()
    fetchPermissionList()
  } finally {
    loading.value.permAddBtn = false
  }
}

/**
 * 打开编辑权限弹窗并回填数据
 * @param row - 目标权限行数据
 */
const handleEditPerm = (row: IPermissionInfo) => {
  editPermForm.perm_id = row.id
  editPermForm.menu_id = row.menu_id
  editPermForm.name = row.name
  editPermForm.code = row.code
  editPermForm.sort = row.sort
  editPermForm.status = row.status
  editPermForm.description = row.description
  editPermDialogVisible.value = true
}

/**
 * 关闭编辑权限弹窗并重置表单
 */
const closeEditPermDialog = () => {
  editPermDialogVisible.value = false
  editPermFormRef.value?.resetFields()
}

/**
 * 提交编辑权限表单
 * @description 验证表单后调用更新接口，成功后关闭弹窗并刷新列表
 */
const submitEditPerm = async () => {
  if (!editPermFormRef.value) return
  const valid = await editPermFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.permEditBtn = true
  try {
    await updatePermission(editPermForm)
    ElMessage.success('权限更新成功')
    closeEditPermDialog()
    fetchPermissionList()
  } finally {
    loading.value.permEditBtn = false
  }
}

/**
 * 删除单个权限
 * @param row - 目标权限行数据
 * @description 弹出确认框后执行删除操作
 */
const handleDeletePerm = async (row: IPermissionInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除权限【${row.name}】吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.permDeleteBtn = true
    await deletePermission(row.id)
    ElMessage.success('删除成功')
    fetchPermissionList()
  } finally {
    loading.value.permDeleteBtn = false
  }
}

/**
 * 批量删除已勾选权限
 * @description 批量删除选中的权限，支持并发删除
 */
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的权限')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的【${selectedRows.value.length}】个权限吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.permBatchDeleteBtn = true
    const deletePromises = selectedRows.value.map(perm => deletePermission(perm.id))
    await Promise.all(deletePromises)

    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchPermissionList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value.permBatchDeleteBtn = false
  }
}

/**
 * 刷新权限列表
 */
const handleRefreshPermList = async () => {
  try {
    loading.value.permRefreshBtn = true
    await Promise.all([fetchMenuTree(), fetchPermissionList()])
  } finally {
    loading.value.permRefreshBtn = false
  }
}

/**
 * 根据菜单ID获取菜单名称
 * @param menuId - 菜单ID
 * @returns 菜单名称
 */
const getMenuName = (menuId: number): string => {
  const findMenu = (menus: IMenuItem[]): string | null => {
    for (const menu of menus) {
      if (menu.id === menuId) return menu.label
      if (menu.children) {
        const found = findMenu(menu.children)
        if (found) return found
      }
    }
    return null
  }
  return findMenu(menuTreeData.value) || '未知菜单'
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取菜单树和权限列表数据
 */
onMounted(() => {
  fetchMenuTree()
  fetchPermissionList()
})
</script>

<template>
  <div ref="layoutPageRef" class="layout-page">
    <!-- 搜索筛选区域 -->
    <div class="layout-page__header">
      <el-card shadow="never">
        <el-collapse>
          <el-collapse-item>
            <template #title>
              <div class="font-bold text-base">数据查询</div>
            </template>
            <el-form :model="searchPermissionParams" label-width="auto">
              <el-row :gutter="20" class="pl-5">
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="权限名称">
                    <el-input
                      v-model="searchPermissionParams.name"
                      placeholder="请输入权限名称"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="权限标识">
                    <el-input
                      v-model="searchPermissionParams.code"
                      placeholder="请输入权限标识"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="状态">
                    <el-select
                      v-model="searchPermissionParams.status"
                      placeholder="请选择状态"
                      clearable
                    >
                      <el-option
                        v-for="item in PERM_STATUS_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="所属菜单">
                    <el-tree-select
                      v-model="searchPermissionParams.menu_ids"
                      :data="menuTreeData"
                      :props="{ label: 'label', value: 'id', children: 'children' }"
                      placeholder="请选择菜单"
                      clearable
                      check-strictly
                      filterable
                      multiple
                      collapse-tags
                      collapse-tags-tooltip
                    />
                  </el-form-item>
                </el-col>
                <el-col :sm="24" :md="16" :lg="24">
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

    <!-- 列表表格区域 -->
    <div class="layout-page__content">
      <el-card shadow="never">
        <div class="layout-toolbar">
          <h4 class="layout-toolbar__title">权限列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.permRefreshBtn" @click="handleRefreshPermList">
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
            <el-button plain type="primary" @click="handleAddPerm">
              <template #icon>
                <i-ep-plus />
              </template>
              新增
            </el-button>
            <el-button
              plain
              type="danger"
              :disabled="selectedRows.length === 0"
              @click="handleBatchDelete"
            >
              <template #icon>
                <i-ep-delete />
              </template>
              批量删除
            </el-button>
          </el-space>
        </div>

        <el-table
          v-loading="loading.permTable"
          :data="permissionTableData"
          stripe
          width="100%"
          class="layout-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="权限 ID" width="80" align="center" />
          <el-table-column
            prop="name"
            label="权限名称"
            width="150"
            align="center"
            show-overflow-tooltip
          />
          <el-table-column
            prop="code"
            label="权限标识"
            width="200"
            align="center"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <el-tag type="info">{{ row.code }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="所属菜单" width="150" align="center">
            <template #default="{ row }">
              <span>{{ getMenuName(row.menu_id) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 0 ? 'success' : 'danger'">
                {{ row.status === 0 ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="description"
            label="描述"
            min-width="200"
            show-overflow-tooltip
            align="center"
          />
          <el-table-column label="操作" width="140" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="handleEditPerm(row)">
                <template #icon>
                  <i-ep-edit-pen />
                </template>
                编辑
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeletePerm(row)">
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
            v-model:current-page="pagination.page_num"
            v-model:page-size="pagination.page_size"
            :total="pagination.total"
            :page-sizes="PAGE_SIZE_OPTIONS"
            layout="total, sizes, prev, pager, next"
            :teleported="false"
            @size-change="handleSizeChange"
            @current-change="fetchPermissionList"
          />
        </div>
      </el-card>
    </div>

    <!-- 新增权限弹窗 -->
    <el-dialog
      v-model="addPermDialogVisible"
      title="新增权限"
      width="500px"
      @close="closeAddPermDialog"
    >
      <el-form
        ref="addPermFormRef"
        :model="addPermForm"
        :rules="addPermRules"
        label-width="100px"
      >
        <el-form-item label="所属菜单" prop="menu_id">
          <el-tree-select
            v-model="addPermForm.menu_id"
            :data="menuTreeData"
            :props="{ label: 'label', value: 'id', children: 'children' }"
            placeholder="请选择所属菜单"
            check-strictly
            filterable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="addPermForm.name" placeholder="请输入权限名称" clearable />
        </el-form-item>
        <el-form-item label="权限标识" prop="code">
          <el-input v-model="addPermForm.code" placeholder="例如：system:user:read" clearable />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="addPermForm.status"
            :active-value="0"
            :inactive-value="1"
            inline-prompt
          >
            <template #active>
              <i-ep-check />
            </template>
            <template #inactive>
              <i-ep-close />
            </template>
          </el-switch>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number
            v-model="addPermForm.sort"
            :min="0"
            :max="9999"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="addPermForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入权限描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeAddPermDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.permAddBtn" @click="submitAddPerm">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 编辑权限弹窗 -->
    <el-dialog
      v-model="editPermDialogVisible"
      title="编辑权限"
      width="500px"
      @close="closeEditPermDialog"
    >
      <el-form
        ref="editPermFormRef"
        :model="editPermForm"
        :rules="editPermRules"
        label-width="100px"
      >
        <el-form-item label="所属菜单" prop="menu_id">
          <el-tree-select
            v-model="editPermForm.menu_id"
            :data="menuTreeData"
            :props="{ label: 'label', value: 'id', children: 'children' }"
            placeholder="请选择所属菜单"
            check-strictly
            filterable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="editPermForm.name" placeholder="请输入权限名称" clearable />
        </el-form-item>
        <el-form-item label="权限标识" prop="code">
          <el-input v-model="editPermForm.code" placeholder="例如：system:user:read" clearable />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="editPermForm.status"
            :active-value="0"
            :inactive-value="1"
            inline-prompt
          >
            <template #active>
              <i-ep-check />
            </template>
            <template #inactive>
              <i-ep-close />
            </template>
          </el-switch>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number
            v-model="editPermForm.sort"
            :min="0"
            :max="9999"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editPermForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入权限描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeEditPermDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.permEditBtn" @click="submitEditPerm">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>
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
