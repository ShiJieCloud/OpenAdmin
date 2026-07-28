<!--
 * @component PostManagement
 * @path views/system/post/index
 * @name 岗位管理页面
 * @description 实现岗位列表的增删改查，提供部门树筛选、岗位搜索、新增、编辑、删除、批量删除功能
 * @example
 * <PostManagement />
 * @author sjzhao
 * @date 2026-07-22
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useFullscreen } from '@vueuse/core'

import type { IPostInfo, IPostQueryParams, IPostCreateRequest, IPostUpdateRequest } from '@/types/modules/post'
import type { IDeptInfo } from '@/types/modules/dept'
import type { IPageResult } from '@/types/common/api'


import { getPostList, createPost, updatePost, deletePost, batchDeletePost, getPostInfo } from '@/api/modules/post'
import { getDeptList } from '@/api/modules/dept'
import RoleDrawer from './components/RoleDrawer.vue'

// ===================== 1. 全局静态常量 =====================
/** 岗位状态选项 */
const POST_STATUS_OPTIONS = [
  { label: '启用', value: 0 },
  { label: '禁用', value: 1 },
] as const

// ===================== 2. 响应式状态数据 =====================
/** 部门树形数据 */
const deptTreeData = ref<IDeptInfo[]>([])

/** 岗位列表查询参数 */
const searchPostParams = reactive<IPostQueryParams>({
  page_num: 1,
  page_size: 10,
  post_name: '',
  status: undefined,
  dept_ids: undefined,
})

/** 岗位列表数据 */
const postPageData = ref<IPageResult<IPostInfo>>({
  records: [],
  total: 0,
  pages: 0,
  page_size: 10,
  page_num: 1,
})

/** 加载状态管理 */
const loading = ref({
  postTable: false,
  postRefreshBtn: false,
  postAddBtn: false,
  postEditBtn: false,
  postDeleteBtn: false,
  postBatchDeleteBtn: false,
})

/** 表格已勾选的岗位行集合 */
const selectedRows = ref<IPostInfo[]>([])

/** 新增岗位弹窗显隐状态 */
const addPostDialogVisible = ref(false)

/** 新增岗位表单引用 */
const addPostFormRef = ref<FormInstance>()

/** 新增岗位表单数据 */
const addPostForm = reactive<IPostCreateRequest>({
  post_name: '',
  dept_id: undefined,
  sort: 999,
  status: 0,
  remark: '',
})

/** 新增岗位表单校验规则 */
const addPostRules = reactive<FormRules<IPostCreateRequest>>({
  dept_id: [
    { required: true, message: '请选择所属部门', trigger: 'change' },
  ],
  post_name: [
    { required: true, message: '请输入岗位名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
  ],
})

/** 编辑岗位弹窗显隐状态 */
const editPostDialogVisible = ref(false)

/** 编辑岗位表单引用 */
const editPostFormRef = ref<FormInstance>()

/** 编辑岗位表单数据 */
const editPostForm = reactive<IPostUpdateRequest>({
  post_id: 0,
  post_name: '',
  dept_id: undefined,
  sort: 999,
  status: 0,
  remark: '',
})

/** 编辑岗位表单校验规则 */
const editPostRules = reactive<FormRules<IPostUpdateRequest>>({
  dept_id: [
    { required: true, message: '请选择所属部门', trigger: 'change' },
  ],
  post_name: [
    { required: true, message: '请输入岗位名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
  ],
})

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

/** 角色分配抽屉显隐状态 */
const roleDrawerVisible = ref(false)

/** 当前操作岗位ID */
const currentPostId = ref<number>(0)

// ===================== 3. 接口请求方法 =====================
/**
 * 拉取部门树形列表
 * @description 获取所有部门的树形结构数据
 * @returns {Promise<void>}
 */
const fetchDeptTree = async () => {
  try {
    const res = await getDeptList()
    deptTreeData.value = buildDeptTree(res)
  } catch {
    // ignore
  }
}

/**
 * 拉取岗位列表
 * @description 根据查询参数获取岗位列表数据（分页）
 * @returns {Promise<void>}
 */
const fetchPostList = async () => {
  loading.value.postTable = true
  try {
    const res = await getPostList(searchPostParams)
    postPageData.value = res
  } finally {
    loading.value.postTable = false
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

  deptList.forEach(dept => {
    deptMap.set(dept.id, { ...dept, children: [] })
  })

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
 * 搜索岗位列表
 * @description 根据搜索条件重新加载列表，重置到第一页
 */
const handleSearchPost = () => {
  searchPostParams.page_num = 1
  fetchPostList()
}

/**
 * 重置搜索条件
 * @description 清空搜索条件并重新加载列表，重置到第一页
 */
const handleResetSearch = () => {
  searchPostParams.post_name = ''
  searchPostParams.status = undefined
  searchPostParams.dept_ids = undefined
  searchPostParams.page_num = 1
  fetchPostList()
}

/**
 * 分页页码变更回调
 * @param page - 当前页码
 */
const handlePageChange = (page: number) => {
  searchPostParams.page_num = page
  fetchPostList()
}

/**
 * 分页每页条数变更回调
 * @param size - 每页条数
 */
const handleSizeChange = (size: number) => {
  searchPostParams.page_size = size
  searchPostParams.page_num = 1
  fetchPostList()
}

/**
 * 打开新增岗位弹窗
 */
const handleAddPost = () => {
  addPostDialogVisible.value = true
}

/**
 * 关闭新增岗位弹窗并重置表单
 */
const closeAddPostDialog = () => {
  addPostDialogVisible.value = false
  addPostFormRef.value?.resetFields()
}

/**
 * 提交新增岗位表单
 * @description 验证表单后调用创建接口，成功后关闭弹窗并刷新列表
 */
const submitAddPost = async () => {
  if (!addPostFormRef.value) return
  const valid = await addPostFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.postAddBtn = true
  try {
    await createPost(addPostForm)
    ElMessage.success('岗位创建成功')
    closeAddPostDialog()
    fetchPostList()
  } finally {
    loading.value.postAddBtn = false
  }
}

/**
 * 打开编辑岗位弹窗并回填数据
 * @param row - 目标岗位行数据
 */
const handleEditPost = async (row: IPostInfo) => {
  // 调用接口获取岗位详情
  const res = await getPostInfo(row.id)
  editPostForm.post_id = res.id
  editPostForm.post_name = res.post_name
  editPostForm.dept_id = res.dept_id
  editPostForm.sort = res.sort
  editPostForm.status = res.status
  editPostForm.remark = res.remark
  editPostDialogVisible.value = true
}

/**
 * 关闭编辑岗位弹窗并重置表单
 */
const closeEditPostDialog = () => {
  editPostDialogVisible.value = false
  editPostFormRef.value?.resetFields()
}

/**
 * 提交编辑岗位表单
 * @description 验证表单后调用更新接口，成功后关闭弹窗并刷新列表
 */
const submitEditPost = async () => {
  if (!editPostFormRef.value) return
  const valid = await editPostFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.postEditBtn = true
  try {
    await updatePost(editPostForm)
    ElMessage.success('岗位更新成功')
    closeEditPostDialog()
    fetchPostList()
  } finally {
    loading.value.postEditBtn = false
  }
}

/**
 * 删除单个岗位
 * @param row - 目标岗位行数据
 * @description 弹出确认框后执行删除操作
 */
const handleDeletePost = async (row: IPostInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除岗位【${row.post_name}】吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.postDeleteBtn = true
    await deletePost(row.id)
    ElMessage.success('删除成功')
    fetchPostList()
  } finally {
    loading.value.postDeleteBtn = false
  }
}

/**
 * 刷新岗位列表
 */
const handleRefreshPostList = async () => {
  try {
    loading.value.postRefreshBtn = true
    await Promise.all([fetchDeptTree(), fetchPostList()])
  } finally {
    loading.value.postRefreshBtn = false
  }
}

/**
 * 表格勾选变更回调
 * @param val - 已勾选的岗位行集合
 */
const handleSelectionChange = (val: IPostInfo[]) => {
  selectedRows.value = val
}

/**
 * 批量删除已勾选岗位
 * @description 批量删除选中的岗位
 */
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的岗位')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的【${selectedRows.value.length}】个岗位吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.postBatchDeleteBtn = true
    const postIds = selectedRows.value.map(post => post.id)
    await batchDeletePost(postIds)

    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchPostList()
  } finally {
    loading.value.postBatchDeleteBtn = false
  }
}

/**
 * 打开角色分配抽屉
 * @param row - 目标岗位行数据
 */
const handleAssignRoles = (row: IPostInfo) => {
  currentPostId.value = row.id
  roleDrawerVisible.value = true
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取部门树和岗位列表数据
 */
onMounted(() => {
  fetchDeptTree()
  fetchPostList()
})
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
            <el-form :model="searchPostParams" label-width="auto">
              <el-row :gutter="20" class="pl-5">
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="岗位名称">
                    <el-input v-model="searchPostParams.post_name" placeholder="请输入岗位名称" clearable
                      @keyup.enter="handleSearchPost" />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="所属部门">
                    <el-tree-select v-model="searchPostParams.dept_ids" :data="deptTreeData"
                      :props="{ label: 'dept_name', value: 'id', children: 'children' }" placeholder="请选择部门" clearable
                      check-strictly multiple collapse-tags collapse-tags-tooltip />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="状态">
                    <el-select v-model="searchPostParams.status" multiple placeholder="请选择状态" clearable>
                      <el-option v-for="item in POST_STATUS_OPTIONS" :key="item.value" :label="item.label"
                        :value="item.value" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="24" :lg="6">
                  <el-space alignment="flex-end" class="justify-end w-full">
                    <el-button plain type="primary" @click="handleSearchPost">
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
                </el-col>
              </el-row>
            </el-form>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </div>

    <!-- 主体区域 -->
    <div class="layout-page__content">
      <!-- 岗位列表 -->
      <el-card shadow="never">
        <div class="layout-toolbar">
          <h4 class="layout-toolbar__title">岗位列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.postRefreshBtn" @click="handleRefreshPostList">
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
            <el-button plain type="primary" @click="handleAddPost">
              <template #icon>
                <i-ep-plus />
              </template>
              新增岗位
            </el-button>
            <el-button plain type="danger" :disabled="selectedRows.length === 0" @click="handleBatchDelete">
              <template #icon>
                <i-ep-delete />
              </template>
              批量删除
            </el-button>
          </el-space>
        </div>

        <el-table v-loading="loading.postTable" :data="postPageData.records" stripe width="100%" class="layout-table"
          row-key="id" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55" />
          <el-table-column prop="post_name" label="岗位名称" min-width="150" />
          <el-table-column prop="dept_name" label="所属部门" min-width="150">
            <template #default="{ row }">
              <span>{{ row.dept_name || '-' }}</span>
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
          <el-table-column prop="remark" label="备注" min-width="200" show-overflow-tooltip />
          <el-table-column prop="create_time" label="创建时间" width="180" />
          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="handleEditPost(row)">
                <template #icon>
                  <i-ep-edit-pen />
                </template>
                编辑
              </el-button>
              <el-button type="success" size="small" link @click="handleAssignRoles(row)">
                <template #icon>
                  <i-ep-user />
                </template>
                角色配置
              </el-button>
              <el-button type="danger" size="small" link @click="handleDeletePost(row)">
                <template #icon>
                  <i-ep-delete />
                </template>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
        <div class="layout-pagination">
          <el-pagination v-model:current-page="searchPostParams.page_num" v-model:page-size="searchPostParams.page_size"
            :total="postPageData.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next"
            :teleported="false" @size-change="handleSizeChange" @current-change="fetchPostList" />
        </div>
      </el-card>
    </div>

    <!-- 新增岗位弹窗 -->
    <el-dialog v-model="addPostDialogVisible" title="新增岗位" width="500px" @close="closeAddPostDialog">
      <el-form ref="addPostFormRef" :model="addPostForm" :rules="addPostRules" label-width="100px">
        <el-form-item label="所属部门" prop="dept_id">
          <el-tree-select v-model="addPostForm.dept_id" :data="deptTreeData"
            :props="{ label: 'dept_name', value: 'id', children: 'children' }" placeholder="请选择所属部门" clearable
            check-strictly filterable style="width: 100%" />
        </el-form-item>
        <el-form-item label="岗位名称" prop="post_name">
          <el-input v-model="addPostForm.post_name" placeholder="请输入岗位名称" clearable />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="addPostForm.sort" :min="0" :max="9999" controls-position="right" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="addPostForm.status">
            <el-radio v-for="item in POST_STATUS_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="addPostForm.remark" type="textarea" :rows="3" placeholder="请输入备注" maxlength="200"
            show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeAddPostDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.postAddBtn" @click="submitAddPost">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 编辑岗位弹窗 -->
    <el-dialog v-model="editPostDialogVisible" title="编辑岗位" width="500px" @close="closeEditPostDialog">
      <el-form ref="editPostFormRef" :model="editPostForm" :rules="editPostRules" label-width="100px">
        <el-form-item label="所属部门" prop="dept_id">
          <el-tree-select v-model="editPostForm.dept_id" :data="deptTreeData"
            :props="{ label: 'dept_name', value: 'id', children: 'children' }" placeholder="请选择所属部门" clearable
            check-strictly filterable style="width: 100%" />
        </el-form-item>
        <el-form-item label="岗位名称" prop="post_name">
          <el-input v-model="editPostForm.post_name" placeholder="请输入岗位名称" clearable />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="editPostForm.sort" :min="0" :max="9999" controls-position="right" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="editPostForm.status">
            <el-radio v-for="item in POST_STATUS_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="editPostForm.remark" type="textarea" :rows="3" placeholder="请输入备注" maxlength="200"
            show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeEditPostDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.postEditBtn" @click="submitEditPost">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 权限分配抽屉 -->
    <RoleDrawer v-model:visible="roleDrawerVisible" :post-id="currentPostId" />
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
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
