<!--
 * @component MenuManagement
 * @path views/system/menu/index
 * @name 菜单管理页面
 * @description 实现菜单树的增删改查，提供菜单新增、编辑、删除、状态修改功能
 * @example
 * <MenuManagement />
 * @author sjzhao
 * @date 2026-08-06
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useFullscreen } from '@vueuse/core'

import type { IMenuItem, IMenuCreateRequest, IMenuUpdateRequest } from '@/types/modules/menu'
import {
  getSystemMenuTree,
  createMenu,
  updateMenu,
  updateMenuStatus,
  deleteMenu,
  batchDeleteMenus,
} from '@/api/modules/menu'

// ===================== 1. 全局静态常量 =====================
/** 菜单类型选项 */
const MENU_TYPE_OPTIONS = [
  { label: '目录', value: 0 },
  { label: '菜单', value: 1 },
] as const

/** 菜单状态选项 */
const MENU_STATUS_OPTIONS = [
  { label: '启用', value: 0 },
  { label: '禁用', value: 1 },
] as const

/** 是否隐藏选项 */
const HIDDEN_OPTIONS = [
  { label: '显示', value: 0 },
  { label: '隐藏', value: 1 },
] as const

/** 是否内嵌选项 */
const FRAME_OPTIONS = [
  { label: '否', value: 0 },
  { label: '是', value: 1 },
] as const

// ===================== 2. 响应式状态数据 =====================
/** 菜单树形数据 */
const menuTreeData = ref<IMenuItem[]>([])

/** 加载状态管理 */
const loading = ref({
  menuTable: false,
  menuRefreshBtn: false,
  menuAddBtn: false,
  menuEditBtn: false,
  menuDeleteBtn: false,
})

/** 新增菜单弹窗显隐状态 */
const addMenuDialogVisible = ref(false)

/** 新增菜单表单引用 */
const addMenuFormRef = ref<FormInstance>()

/** 新增菜单表单数据 */
const addMenuForm = reactive<IMenuCreateRequest>({
  name: '',
  label: '',
  parent_id: undefined as unknown as number,
  sort: 0,
  path: '',
  component: '',
  type: 0,
  description: '',
  icon: '',
  is_hidden: 0,
  is_frame: 0,
  status: 0,
})

/** 新增菜单表单校验规则 */
const addMenuRules = reactive<FormRules<IMenuCreateRequest>>({
  name: [
    { required: true, message: '请输入菜单标识', trigger: 'blur' },
    { max: 128, message: '长度不超过 128 个字符', trigger: 'blur' },
  ],
  label: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { max: 128, message: '长度不超过 128 个字符', trigger: 'blur' },
  ],
  type: [
    { required: true, message: '请选择菜单类型', trigger: 'change' },
  ],
  path: [
    { max: 255, message: '长度不超过 255 个字符', trigger: 'blur' },
  ],
})

/** 编辑菜单弹窗显隐状态 */
const editMenuDialogVisible = ref(false)

/** 编辑菜单表单引用 */
const editMenuFormRef = ref<FormInstance>()

/** 编辑菜单表单数据 */
const editMenuForm = reactive<IMenuUpdateRequest>({
  name: '',
  label: '',
  parent_id: undefined,
  sort: 0,
  path: '',
  component: '',
  type: 0,
  description: '',
  icon: '',
  is_hidden: 0,
  is_frame: 0,
  status: 0,
})

/** 编辑菜单表单校验规则 */
const editMenuRules = reactive<FormRules<IMenuUpdateRequest>>({
  name: [
    { max: 128, message: '长度不超过 128 个字符', trigger: 'blur' },
  ],
  label: [
    { max: 128, message: '长度不超过 128 个字符', trigger: 'blur' },
  ],
  path: [
    { max: 255, message: '长度不超过 255 个字符', trigger: 'blur' },
  ],
})

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

/** 当前编辑的菜单ID */
const currentMenuId = ref(0)

/** 表格已勾选的菜单行集合 */
const selectedRows = ref<IMenuItem[]>([])

// ===================== 3. 接口请求 method =====================
/**
 * 拉取菜单树形列表
 * @description 获取所有菜单的树形结构数据
 */
const fetchMenuTree = async () => {
  loading.value.menuTable = true
  try {
    const res = await getSystemMenuTree()
    menuTreeData.value = res || []
  } finally {
    loading.value.menuTable = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 打开新增菜单弹窗
 * @param parentId 父菜单ID，默认为0（顶级菜单）
 */
const handleAddMenu = (parentId: number = 0) => {
  // 将 0 转换为 undefined，使上级菜单显示为空
  addMenuForm.parent_id = parentId === 0 ? undefined : parentId
  addMenuDialogVisible.value = true
}

/**
 * 关闭新增菜单弹窗并重置表单
 */
const closeAddMenuDialog = () => {
  addMenuDialogVisible.value = false
  addMenuFormRef.value?.resetFields()
}

/**
 * 提交新增菜单表单
 * @description 验证表单后调用创建接口，成功后关闭弹窗并刷新列表
 */
const submitAddMenu = async () => {
  if (!addMenuFormRef.value) return
  const valid = await addMenuFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.menuAddBtn = true
  try {
    await createMenu(addMenuForm)
    ElMessage.success('菜单创建成功')
    closeAddMenuDialog()
    fetchMenuTree()
  } finally {
    loading.value.menuAddBtn = false
  }
}

/**
 * 打开编辑菜单弹窗并回填数据
 * @param row - 目标菜单行数据
 */
const handleEditMenu = (row: IMenuItem) => {
  currentMenuId.value = row.id
  // 将 parent_id 为 0 转换为 undefined，使上级菜单显示为空
  Object.assign(editMenuForm, {
    name: row.name,
    label: row.label,
    parent_id: (row.parent_id || 0) === 0 ? undefined : row.parent_id,
    sort: row.sort,
    path: row.path || '',
    component: row.component || '',
    type: row.type,
    description: row.description || '',
    icon: row.icon || '',
    is_hidden: row.is_hidden,
    is_frame: row.is_frame,
    status: row.status,
  })
  editMenuDialogVisible.value = true
}

/**
 * 关闭编辑菜单弹窗并重置表单
 */
const closeEditMenuDialog = () => {
  editMenuDialogVisible.value = false
  editMenuFormRef.value?.resetFields()
}

/**
 * 提交编辑菜单表单
 * @description 验证表单后调用更新接口，成功后关闭弹窗并刷新列表
 */
const submitEditMenu = async () => {
  if (!editMenuFormRef.value) return
  const valid = await editMenuFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.menuEditBtn = true
  try {
    await updateMenu(currentMenuId.value, editMenuForm)
    ElMessage.success('菜单更新成功')
    closeEditMenuDialog()
    fetchMenuTree()
  } finally {
    loading.value.menuEditBtn = false
  }
}

/**
 * 删除菜单
 * @param row - 目标菜单行数据
 */
const handleDeleteMenu = async (row: IMenuItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除菜单【${row.label}】吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.menuDeleteBtn = true
    await deleteMenu(row.id)
    ElMessage.success('删除成功')
    fetchMenuTree()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    loading.value.menuDeleteBtn = false
  }
}

/**
 * 修改菜单状态
 * @param row - 目标菜单行数据
 * @param status - 目标状态
 */
const handleChangeStatus = async (row: IMenuItem, status: number) => {
  try {
    await updateMenuStatus(row.id, status)
    ElMessage.success('状态修改成功')
    fetchMenuTree()
  } catch {
    ElMessage.error('状态修改失败')
  }
}

/**
 * 表格勾选变更回调
 * @param val - 已勾选的菜单行集合
 */
const handleSelectionChange = (val: IMenuItem[]) => {
  selectedRows.value = val
}

/**
 * 批量删除已勾选菜单
 */
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的菜单')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的【${selectedRows.value.length}】个菜单吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.menuDeleteBtn = true
    const menuIds = selectedRows.value.map(menu => menu.id)
    await batchDeleteMenus(menuIds)
    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchMenuTree()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value.menuDeleteBtn = false
  }
}

/**
 * 刷新菜单列表
 */
const handleRefreshMenuList = async () => {
  try {
    loading.value.menuRefreshBtn = true
    await fetchMenuTree()
  } finally {
    loading.value.menuRefreshBtn = false
  }
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取菜单树数据
 */
onMounted(() => {
  fetchMenuTree()
})
</script>

<template>
  <div ref="layoutPageRef" class="layout-page">
    <!-- 列表区域 -->
    <div class="layout-page__content">
      <el-card shadow="never">
        <div class="layout-toolbar">
          <h4 class="layout-toolbar__title">菜单列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.menuRefreshBtn" @click="handleRefreshMenuList">
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
            <el-button plain type="primary" @click="handleAddMenu(0)">
              <template #icon>
                <i-ep-plus />
              </template>
              新增顶级菜单
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
          v-loading="loading.menuTable"
          :data="menuTreeData"
          stripe
          row-key="id"
          :tree-props="{ children: 'children' }"
          class="layout-table"
          table-layout="auto"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="label" label="菜单名称" width="200" align="left" />
          <el-table-column prop="icon" label="图标" width="80" align="center">
            <template #default="{ row }">
              <i v-if="row.icon" :class="row.icon" class="text-lg" />
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="path" label="路由地址" align="left" show-overflow-tooltip />
          <el-table-column prop="is_hidden" label="是否隐藏" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_hidden === 0 ? 'success' : 'info'">
                {{ HIDDEN_OPTIONS.find(item => item.value === row.is_hidden)?.label || '未知' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-dropdown @command="(status: number) => handleChangeStatus(row, status)">
                <el-tag
                  :type="row.status === 0 ? 'success' : 'danger'"
                  class="cursor-pointer"
                >
                  {{ MENU_STATUS_OPTIONS.find(item => item.value === row.status)?.label || '未知' }}
                </el-tag>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-for="item in MENU_STATUS_OPTIONS"
                      :key="item.value"
                      :command="item.value"
                      :disabled="item.value === row.status"
                    >
                      {{ item.label }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="200" align="center" />
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="handleAddMenu(row.id)">
                <template #icon>
                  <i-ep-plus />
                </template>
                新增
              </el-button>
              <el-button type="primary" size="small" link @click="handleEditMenu(row)">
                <template #icon>
                <i-ep-edit-pen />
                </template>
                编辑
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteMenu(row)">
                <template #icon>
                  <i-ep-delete />
                </template>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 新增菜单弹窗 -->
    <el-dialog
      v-model="addMenuDialogVisible"
      title="新增菜单"
      width="700px"
      @close="closeAddMenuDialog"
    >
      <el-form ref="addMenuFormRef" :model="addMenuForm" :rules="addMenuRules" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="上级菜单">
              <el-tree-select
                v-model="addMenuForm.parent_id"
                :data="menuTreeData"
                :props="{ label: 'label', value: 'id', children: 'children' }"
                placeholder="请选择上级菜单（留空为顶级）"
                clearable
                check-strictly
                filterable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单类型" prop="type">
              <el-radio-group v-model="addMenuForm.type">
                <el-radio v-for="item in MENU_TYPE_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="addMenuForm.status">
                <el-radio v-for="item in MENU_STATUS_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单标识" prop="name">
              <el-input v-model="addMenuForm.name" placeholder="请输入菜单唯一标识" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单名称" prop="label">
              <el-input v-model="addMenuForm.label" placeholder="请输入菜单显示名称" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="路由地址" prop="path">
              <el-input v-model="addMenuForm.path" placeholder="请输入路由地址" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="组件路径" prop="component">
              <el-input v-model="addMenuForm.component" placeholder="请输入组件路径" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单图标" prop="icon">
              <el-input v-model="addMenuForm.icon" placeholder="请输入图标名称" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="sort">
              <el-input-number v-model="addMenuForm.sort" :min="0" :max="9999" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否隐藏" prop="is_hidden">
              <el-radio-group v-model="addMenuForm.is_hidden">
                <el-radio v-for="item in HIDDEN_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否内嵌" prop="is_frame">
              <el-radio-group v-model="addMenuForm.is_frame">
                <el-radio v-for="item in FRAME_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="描述" prop="description">
              <el-input
                v-model="addMenuForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入菜单描述"
                maxlength="255"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeAddMenuDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.menuAddBtn" @click="submitAddMenu">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 编辑菜单弹窗 -->
    <el-dialog
      v-model="editMenuDialogVisible"
      title="编辑菜单"
      width="700px"
      @close="closeEditMenuDialog"
    >
      <el-form ref="editMenuFormRef" :model="editMenuForm" :rules="editMenuRules" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="上级菜单">
              <el-tree-select
                v-model="editMenuForm.parent_id"
                :data="menuTreeData"
                :props="{ label: 'label', value: 'id', children: 'children' }"
                placeholder="请选择上级菜单（留空为顶级）"
                clearable
                check-strictly
                filterable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单类型" prop="type">
              <el-radio-group v-model="editMenuForm.type">
                <el-radio v-for="item in MENU_TYPE_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="editMenuForm.status">
                <el-radio v-for="item in MENU_STATUS_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单标识" prop="name">
              <el-input v-model="editMenuForm.name" placeholder="请输入菜单唯一标识" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单名称" prop="label">
              <el-input v-model="editMenuForm.label" placeholder="请输入菜单显示名称" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="路由地址" prop="path">
              <el-input v-model="editMenuForm.path" placeholder="请输入路由地址" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="组件路径" prop="component">
              <el-input v-model="editMenuForm.component" placeholder="请输入组件路径" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单图标" prop="icon">
              <el-input v-model="editMenuForm.icon" placeholder="请输入图标名称" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="sort">
              <el-input-number v-model="editMenuForm.sort" :min="0" :max="9999" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否隐藏" prop="is_hidden">
              <el-radio-group v-model="editMenuForm.is_hidden">
                <el-radio v-for="item in HIDDEN_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否内嵌" prop="is_frame">
              <el-radio-group v-model="editMenuForm.is_frame">
                <el-radio v-for="item in FRAME_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="描述" prop="description">
              <el-input
                v-model="editMenuForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入菜单描述"
                maxlength="255"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeEditMenuDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.menuEditBtn" @click="submitEditMenu">
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

.cursor-pointer {
  cursor: pointer;
}
</style>
