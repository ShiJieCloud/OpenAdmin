<!--
 * @component DeptManagement
 * @path views/system/dept/index
 * @name 部门管理页面
 * @description 实现部门树形列表的增删改查，提供部门搜索、新增、编辑、删除功能
 * @example
 * <DeptManagement />
 * @author sjzhao
 * @date 2026-07-20
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useFullscreen } from '@vueuse/core'

import type { IDeptInfo, IDeptCreateRequest, IDeptUpdateRequest } from '@/types/modules/dept'

import { getDeptList, createDept, updateDept, deleteDept } from '@/api/modules/dept'

// ===================== 1. 全局静态常量 =====================
/** 部门状态选项 */
const DEPT_STATUS_OPTIONS = [
  { label: '启用', value: 0 },
  { label: '禁用', value: 1 },
] as const

// ===================== 2. 响应式状态数据 =====================
/** 部门树形数据 */
const deptTreeData = ref<IDeptInfo[]>([])

const deptTreeProps = reactive({
  checkStrictly: true,
  children: 'children',
  hasChildren: 'hasChildren',
})

/** 加载状态管理 */
const loading = ref({
  deptTable: false,
  deptRefreshBtn: false,
  deptAddBtn: false,
  deptEditBtn: false,
  deptDeleteBtn: false,
  deptBatchDeleteBtn: false,
})

/** 表格已勾选的部门行集合 */
const selectedRows = ref<IDeptInfo[]>([])

/** 新增部门弹窗显隐状态 */
const addDeptDialogVisible = ref(false)

/** 新增部门表单引用 */
const addDeptFormRef = ref<FormInstance>()

/** 新增部门表单数据 */
const addDeptForm = reactive<IDeptCreateRequest>({
  parent_id: 0,
  dept_name: '',
  sort: 999,
  status: 0,
})

/** 新增部门表单校验规则 */
const addDeptRules = reactive<FormRules<IDeptCreateRequest>>({
  dept_name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
  ],
})

/** 编辑部门弹窗显隐状态 */
const editDeptDialogVisible = ref(false)

/** 编辑部门表单引用 */
const editDeptFormRef = ref<FormInstance>()

/** 编辑部门表单数据 */
const editDeptForm = reactive<IDeptUpdateRequest>({
  dept_id: 0,
  parent_id: 0,
  dept_name: '',
  sort: 999,
  status: 0,
})

/** 编辑部门表单校验规则 */
const editDeptRules = reactive<FormRules<IDeptUpdateRequest>>({
  dept_name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
  ],
})

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

// ===================== 3. 接口请求方法 =====================
/**
 * 拉取部门树形列表
 * @description 获取所有部门的树形结构数据
 * @returns {Promise<void>}
 */
const fetchDeptTree = async () => {
  loading.value.deptTable = true
  try {
    const res = await getDeptList()
    deptTreeData.value = buildDeptTree(res)
  } finally {
    loading.value.deptTable = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 构建树形结构
 * @param deptList - 扁平部门列表
 * @returns 树形部门列表
 */
const buildDeptTree = (deptList: IDeptInfo[]): IDeptInfo[] => {
  const deptMap = new Map<number, IDeptInfo>()
  const rootList: IDeptInfo[] = []

  // 创建映射
  deptList.forEach(dept => {
    deptMap.set(dept.id, { ...dept, children: [] })
  })

  // 构建树形结构
  deptList.forEach(dept => {
    const node = deptMap.get(dept.id)!
    if (dept.parent_id === 0) {
      rootList.push(node)
    } else {
      const parent = deptMap.get(dept.parent_id)
      if (parent) {
        parent.children!.push(node)
      }
    }
  })

  // 排序并清理空 children
  const sortTree = (list: IDeptInfo[]) => {
    list.sort((a, b) => a.sort - b.sort)
    list.forEach(item => {
      if (item.children && item.children.length === 0) {
        delete item.children
      } else if (item.children) {
        sortTree(item.children)
      }
    })
  }

  sortTree(rootList)
  return rootList
}

/**
 * 打开新增部门弹窗
 * @param parentId - 父级部门ID（可选）
 */
const handleAddDept = (parentId: number = 0) => {
  addDeptForm.parent_id = parentId
  addDeptDialogVisible.value = true
}

/**
 * 关闭新增部门弹窗并重置表单
 */
const closeAddDeptDialog = () => {
  addDeptDialogVisible.value = false
  addDeptFormRef.value?.resetFields()
}

/**
 * 提交新增部门表单
 * @description 验证表单后调用创建接口，成功后关闭弹窗并刷新列表
 */
const submitAddDept = async () => {
  if (!addDeptFormRef.value) return
  const valid = await addDeptFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.deptAddBtn = true
  try {
    await createDept(addDeptForm)
    ElMessage.success('部门创建成功')
    closeAddDeptDialog()
    fetchDeptTree()
  } finally {
    loading.value.deptAddBtn = false
  }
}

/**
 * 打开编辑部门弹窗并回填数据
 * @param row - 目标部门行数据
 */
const handleEditDept = (row: IDeptInfo) => {
  editDeptForm.dept_id = row.id
  editDeptForm.parent_id = row.parent_id
  editDeptForm.dept_name = row.dept_name
  editDeptForm.sort = row.sort
  editDeptForm.status = row.status
  editDeptDialogVisible.value = true
}

/**
 * 关闭编辑部门弹窗并重置表单
 */
const closeEditDeptDialog = () => {
  editDeptDialogVisible.value = false
  editDeptFormRef.value?.resetFields()
}

/**
 * 提交编辑部门表单
 * @description 验证表单后调用更新接口，成功后关闭弹窗并刷新列表
 */
const submitEditDept = async () => {
  if (!editDeptFormRef.value) return
  const valid = await editDeptFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.deptEditBtn = true
  try {
    await updateDept(editDeptForm)
    ElMessage.success('部门更新成功')
    closeEditDeptDialog()
    fetchDeptTree()
  } finally {
    loading.value.deptEditBtn = false
  }
}

/**
 * 删除单个部门
 * @param row - 目标部门行数据
 * @description 弹出确认框后执行删除操作
 */
const handleDeleteDept = async (row: IDeptInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除部门【${row.dept_name}】吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.deptDeleteBtn = true
    await deleteDept(row.id)
    ElMessage.success('删除成功')
    fetchDeptTree()
  } finally {
    loading.value.deptDeleteBtn = false
  }
}

/**
 * 刷新部门列表
 */
const handleRefreshDeptList = async () => {
  try {
    loading.value.deptRefreshBtn = true
    await fetchDeptTree()
  } finally {
    loading.value.deptRefreshBtn = false
  }
}

/**
 * 表格勾选变更回调
 * @param val - 已勾选的部门行集合
 */
const handleSelectionChange = (val: IDeptInfo[]) => {
  selectedRows.value = val
}

/**
 * 批量删除已勾选部门
 * @description 批量删除选中的部门，支持并发删除
 */
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的部门')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的【${selectedRows.value.length}】个部门吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.deptBatchDeleteBtn = true
    const deletePromises = selectedRows.value.map(dept => deleteDept(dept.id))
    await Promise.all(deletePromises)

    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchDeptTree()
  } finally {
    loading.value.deptBatchDeleteBtn = false
  }
}

/**
 * 根据部门ID获取部门名称
 * @param deptId - 部门ID
 * @returns 部门名称
 */
const getDeptNameById = (deptId: number): string => {
  const findDept = (list: IDeptInfo[]): IDeptInfo | null => {
    for (const dept of list) {
      if (dept.id === deptId) return dept
      if (dept.children) {
        const found = findDept(dept.children)
        if (found) return found
      }
    }
    return null
  }
  const dept = findDept(deptTreeData.value)
  return dept?.dept_name || ''
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取部门树形数据
 */
onMounted(() => fetchDeptTree())
</script>

<template>
  <div ref="layoutPageRef" class="layout-page">
    <!-- 列表区域 -->
    <div class="layout-page__content">
      <el-card shadow="never">
        <div class="layout-toolbar">
          <h4 class="layout-toolbar__title">部门列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.deptRefreshBtn" @click="handleRefreshDeptList">
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
            <el-button plain type="primary" @click="handleAddDept(0)">
              <template #icon>
                <i-ep-plus />
              </template>
              新增顶级部门
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
          v-loading="loading.deptTable"
          :data="deptTreeData"
          :tree-props="deptTreeProps"
          stripe
          width="100%"
          class="layout-table"
          row-key="id"
          default-expand-all
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="dept_name" label="部门名称" min-width="200">
            <template #default="{ row }">
              {{ row.dept_name }}
              <el-tag v-if="row.children && row.children.length > 0" size="small" type="info" class="ml-2">
                {{ row.children.length }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sort" label="排序" width="100" align="center" />
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 0 ? 'success' : 'danger'">
                {{ row.status === 0 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="180" />
          <el-table-column label="操作" width="240" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="handleAddDept(row.id)">
                <template #icon>
                  <i-ep-plus />
                </template>
                新增子部门
              </el-button>
              <el-button type="primary" size="small" link @click="handleEditDept(row)">
                <template #icon>
                  <i-ep-edit-pen />
                </template>
                编辑
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteDept(row)">
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

    <!-- 新增部门弹窗 -->
    <el-dialog
      v-model="addDeptDialogVisible"
      title="新增部门"
      width="500px"
      @close="closeAddDeptDialog"
    >
      <el-form ref="addDeptFormRef" :model="addDeptForm" :rules="addDeptRules" label-width="100px">
        <el-form-item label="父级部门" v-if="addDeptForm.parent_id !== undefined && addDeptForm.parent_id > 0">
          <el-tag>{{ getDeptNameById(addDeptForm.parent_id || 0) }}</el-tag>
        </el-form-item>
        <el-form-item label="部门名称" prop="dept_name">
          <el-input v-model="addDeptForm.dept_name" placeholder="请输入部门名称" clearable />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="addDeptForm.sort" :min="0" :max="9999" controls-position="right" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="addDeptForm.status">
            <el-radio v-for="item in DEPT_STATUS_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeAddDeptDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.deptAddBtn" @click="submitAddDept">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 编辑部门弹窗 -->
    <el-dialog
      v-model="editDeptDialogVisible"
      title="编辑部门"
      width="500px"
      @close="closeEditDeptDialog"
    >
      <el-form ref="editDeptFormRef" :model="editDeptForm" :rules="editDeptRules" label-width="100px">
        <el-form-item label="部门名称" prop="dept_name">
          <el-input v-model="editDeptForm.dept_name" placeholder="请输入部门名称" clearable />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="editDeptForm.sort" :min="0" :max="9999" controls-position="right" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="editDeptForm.status">
            <el-radio v-for="item in DEPT_STATUS_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeEditDeptDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.deptEditBtn" @click="submitEditDept">
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
