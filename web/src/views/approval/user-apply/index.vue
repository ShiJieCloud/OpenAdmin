<!--
 * @component UserApplyManagement
 * @path views/approval/user-apply/index
 * @name 用户注册申请审批页面
 * @description 展示用户注册申请列表，支持按用户名、手机号、审核状态筛选，提供审批通过（绑定部门/岗位）和拒绝（填写原因）功能
 * @example
 * <UserApplyManagement />
 * @author sjzhao
 * @date 2026-09-29
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useFullscreen } from '@vueuse/core'

import type { IUserApplyInfo, IUserApplyListQueryParam, IUserApplyPassRequest } from '@/types'
import type { IPageResult } from '@/types/common/api'
import type { IDeptInfo } from '@/types/modules/dept'
import type { IPostInfo } from '@/types/modules/post'

import { getUserApplyList, passUserApply, rejectUserApply } from '@/api/modules/userApply'
import { getDeptList, listPostsByDeptId } from '@/api/modules/dept'

// ===================== 1. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [1, 10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

/** 审核状态选项 */
const APPLY_STATUS_OPTIONS = [
  { label: '待审核', value: 0, type: 'warning' },
  { label: '已通过', value: 1, type: 'success' },
  { label: '已拒绝', value: 2, type: 'danger' },
  { label: '撤销', value: 3, type: 'info' },
] as const

/** 拒绝原因快捷预设（点击直接填充到输入框，展示文本取逗号前的简短描述） */
const REJECT_REASON_PRESETS = [
  '信息填写不完整，请补充姓名与手机号后重新提交',
  '申请部门与岗位不匹配，请确认后重新提交',
  '该账号已存在，请勿重复注册',
  '非本公司人员，暂不通过',
] as const

// ===================== 2. 响应式状态数据 =====================
/** 部门树形数据 */
const deptTreeData = ref<IDeptInfo[]>([])

/** 岗位列表数据 */
const postListData = ref<IPostInfo[]>([])

/** 注册申请分页数据 */
const applyPageData = ref<IPageResult<IUserApplyInfo>>({
  records: [],
  total: 0,
  pages: 0,
  page_size: DEFAULT_PAGE_SIZE,
  page_num: 1,
})

/** 列表查询参数 */
const searchApplyParams = reactive<IUserApplyListQueryParam>({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
  username: '',
  phone: '',
  status: undefined,
})

/** 加载状态管理 */
const loading = ref({
  applyTable: false,
  applyRefreshBtn: false,
  applyPassBtn: false,
  applyRejectBtn: false,
})

/** 审批通过弹窗显隐状态 */
const passDialogVisible = ref(false)

/** 审批通过表单引用 */
const passFormRef = ref<FormInstance>()

/** 当前操作的申请记录 */
const currentApply = ref<IUserApplyInfo | null>(null)

/** 审批通过表单数据 */
const passForm = reactive<IUserApplyPassRequest>({
  dept_id: undefined,
  post_ids: [],
})

/** 审批通过表单校验规则 */
const passRules = reactive<FormRules<IUserApplyPassRequest>>({
  dept_id: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
  post_ids: [{ required: true, type: 'array', min: 1, message: '请至少选择一个岗位', trigger: 'change' }],
})

/** 拒绝弹窗显隐状态 */
const rejectDialogVisible = ref(false)

/** 详情弹窗显隐状态 */
const detailDialogVisible = ref(false)

/** 拒绝表单引用 */
const rejectFormRef = ref<FormInstance>()

/** 拒绝表单数据 */
const rejectForm = reactive({
  apply_id: 0,
  reason: '',
})

/** 拒绝表单校验规则 */
const rejectRules = reactive({
  reason: [
    { required: true, message: '请输入拒绝原因', trigger: 'blur' },
    { min: 1, max: 500, message: '长度不超过 500 个字符', trigger: 'blur' },
  ],
})

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

/** 岗位请求取消控制器 */
let postAbort: AbortController | null = null

/** 岗位缓存：key=部门ID，value=该部门下的岗位列表，弹窗关闭时清空 */
const postCache = new Map<number, IPostInfo[]>()

// ===================== 3. 接口请求方法 =====================
/**
 * 拉取部门树形列表
 * @description 获取所有部门的树形结构数据
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
 * 拉取注册申请分页列表
 * @description 根据查询参数获取申请列表数据
 */
const fetchApplyList = async () => {
  loading.value.applyTable = true
  try {
    const res = await getUserApplyList(searchApplyParams)
    applyPageData.value = {
      records: res.records || [],
      total: res.total || 0,
      pages: res.pages || 0,
      page_size: res.page_size || DEFAULT_PAGE_SIZE,
      page_num: res.page_num || 1,
    }
  } finally {
    loading.value.applyTable = false
  }
}

// ===================== 4. 业务处理 =====================
/**
 * 构建部门树形结构
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
 * 根据部门ID查询岗位列表（带缓存）
 * @param deptId - 部门ID
 * @returns 岗位列表
 */
const fetchPostsByDept = async (deptId: number | undefined): Promise<IPostInfo[]> => {
  if (!deptId) {
    postListData.value = []
    return []
  }

  // 命中缓存直接返回
  if (postCache.has(deptId)) {
    postListData.value = postCache.get(deptId)!
    return postListData.value
  }

  // 取消上一次未完成请求，防止竞态
  postAbort?.abort()
  postAbort = new AbortController()

  try {
    const res = await listPostsByDeptId(deptId, { signal: postAbort.signal })
    const list = res ?? []
    postCache.set(deptId, list)
    postListData.value = list
    return list
  } catch (err: any) {
    if (err.name !== 'AbortError') {
      postListData.value = []
    }
    return []
  }
}

/**
 * 搜索回调
 * @description 重置页码并拉取列表
 */
const handleSearch = () => {
  searchApplyParams.page_num = 1
  fetchApplyList()
}

/**
 * 重置回调
 * @description 清空搜索条件并重新查询
 */
const handleReset = () => {
  searchApplyParams.username = ''
  searchApplyParams.phone = ''
  searchApplyParams.status = undefined
  handleSearch()
}

/**
 * 分页条数变更回调
 * @param val - 新的每页条数
 */
const handleSizeChange = (val: number) => {
  searchApplyParams.page_size = val
  searchApplyParams.page_num = 1
  fetchApplyList()
}

/**
 * 打开审批通过弹窗
 * @param row - 目标申请行数据
 */
const handlePass = (row: IUserApplyInfo) => {
  currentApply.value = row
  passForm.dept_id = undefined
  passForm.post_ids = []
  postListData.value = []
  passDialogVisible.value = true
}

/**
 * 审批通过弹窗：部门变更时清空已选岗位并查询新部门的岗位列表
 */
const handleDeptChange = async (deptId: number | undefined) => {
  passForm.post_ids = []
  await fetchPostsByDept(deptId)
}

/**
 * 关闭审批通过弹窗并重置表单
 */
const closePassDialog = () => {
  passDialogVisible.value = false
  passFormRef.value?.resetFields()
  postCache.clear()
}

/**
 * 提交审批通过
 * @description 验证表单后调用通过接口，成功后关闭弹窗并刷新列表
 */
const submitPass = async () => {
  if (!passFormRef.value || !currentApply.value) return
  const valid = await passFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.applyPassBtn = true
  try {
    await passUserApply(currentApply.value.id, { ...passForm })
    ElMessage.success('审批通过成功')
    closePassDialog()
    fetchApplyList()
  } finally {
    loading.value.applyPassBtn = false
  }
}

/**
 * 打开拒绝弹窗
 * @param row - 目标申请行数据
 */
const handleReject = (row: IUserApplyInfo) => {
  currentApply.value = row
  rejectForm.apply_id = row.id
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

/**
 * 快捷填充拒绝原因
 * @description 点击预设标签时，将完整原因文本填入输入框
 * @param reason - 预设原因完整文本
 */
const fillReason = (reason: string) => {
  rejectForm.reason = reason
}

/**
 * 打开详情弹窗
 * @description 展示申请完整信息，待审核状态额外提供通过/拒绝入口
 * @param row - 目标申请行数据
 */
const handleDetail = (row: IUserApplyInfo) => {
  currentApply.value = row
  detailDialogVisible.value = true
}

/**
 * 详情弹窗：审批通过
 * @description 关闭详情弹窗后复用 handlePass 打开通过弹窗
 */
const handleDetailPass = () => {
  detailDialogVisible.value = false
  if (currentApply.value) handlePass(currentApply.value)
}

/**
 * 详情弹窗：审批拒绝
 * @description 关闭详情弹窗后复用 handleReject 打开拒绝弹窗
 */
const handleDetailReject = () => {
  detailDialogVisible.value = false
  if (currentApply.value) handleReject(currentApply.value)
}

/**
 * 关闭拒绝弹窗并重置表单
 */
const closeRejectDialog = () => {
  rejectDialogVisible.value = false
  rejectFormRef.value?.resetFields()
}

/**
 * 提交拒绝
 * @description 验证表单后调用拒绝接口，成功后关闭弹窗并刷新列表
 */
const submitReject = async () => {
  if (!rejectFormRef.value || !currentApply.value) return
  const valid = await rejectFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.applyRejectBtn = true
  try {
    await rejectUserApply(currentApply.value.id, { reason: rejectForm.reason })
    ElMessage.success('审批拒绝成功')
    closeRejectDialog()
    fetchApplyList()
  } finally {
    loading.value.applyRejectBtn = false
  }
}

/**
 * 刷新申请列表
 */
const handleRefreshApplyList = async () => {
  try {
    loading.value.applyRefreshBtn = true
    await Promise.all([fetchDeptTree(), fetchApplyList()])
  } finally {
    loading.value.applyRefreshBtn = false
  }
}

/**
 * 获取状态标签类型
 * @param status - 审核状态
 * @returns 标签类型
 */
const getStatusType = (status: number) => {
  return APPLY_STATUS_OPTIONS.find(item => item.value === status)?.type ?? 'info'
}

/**
 * 获取状态文本
 * @param status - 审核状态
 * @returns 状态文本
 */
const getStatusLabel = (status: number) => {
  return APPLY_STATUS_OPTIONS.find(item => item.value === status)?.label ?? '未知'
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取部门树和申请列表数据
 */
onMounted(() => {
  fetchApplyList()
  fetchDeptTree()
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
            <el-form :model="searchApplyParams" label-width="auto">
              <el-row :gutter="20" class="pl-5">
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="登录账号">
                    <el-input v-model="searchApplyParams.username" placeholder="请输入登录账号" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="手机号">
                    <el-input v-model="searchApplyParams.phone" placeholder="请输入手机号" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="审核状态">
                    <el-select v-model="searchApplyParams.status" placeholder="请选择审核状态" clearable>
                      <el-option
                        v-for="item in APPLY_STATUS_OPTIONS"
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
          <h4 class="layout-toolbar__title">申请列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.applyRefreshBtn" @click="handleRefreshApplyList">
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

        <el-table
          v-loading="loading.applyTable"
          :data="applyPageData.records"
          stripe
          class="layout-table"
        >
          <el-table-column prop="id" label="申请ID" width="80" align="center" />
          <el-table-column prop="username" label="登录账号" width="140" align="center" />
          <el-table-column prop="phone" label="手机号" width="140" align="center">
            <template #default="{ row }">
              {{ row.phone || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="审核状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="申请时间" align="center" />
          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <template v-if="row.status === 0">
                <el-button type="success" size="small" link @click="handlePass(row)">
                  <template #icon>
                    <i-ep-check />
                  </template>
                  通过
                </el-button>
                <el-button type="danger" size="small" link @click="handleReject(row)">
                  <template #icon>
                    <i-ep-close />
                  </template>
                  拒绝
                </el-button>
              </template>
              <el-button type="primary" size="small" link @click="handleDetail(row)">
                <template #icon>
                  <i-ep-view />
                </template>
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="layout-pagination">
          <el-pagination
            v-model:current-page="searchApplyParams.page_num"
            v-model:page-size="searchApplyParams.page_size"
            :total="applyPageData.total"
            :page-sizes="PAGE_SIZE_OPTIONS"
            layout="total, sizes, prev, pager, next"
            :teleported="false"
            @size-change="handleSizeChange"
            @current-change="fetchApplyList"
          />
        </div>
      </el-card>
    </div>

    <!-- 审批通过弹窗 -->
    <el-dialog
      v-model="passDialogVisible"
      title="审批通过"
      width="480px"
      @close="closePassDialog"
    >
      <el-form ref="passFormRef" :model="passForm" :rules="passRules" label-width="100px">
        <el-form-item label="登录账号">
          <el-input :model-value="currentApply?.username" disabled />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input :model-value="currentApply?.phone || '-'" disabled />
        </el-form-item>
        <el-form-item label="所属部门" prop="dept_id">
          <el-tree-select
            v-model="passForm.dept_id"
            :data="deptTreeData"
            :props="{ label: 'dept_name', value: 'id', children: 'children' }"
            placeholder="请选择所属部门"
            clearable
            check-strictly
            filterable
            style="width: 100%"
            @change="handleDeptChange"
          />
        </el-form-item>
        <el-form-item label="所属岗位" prop="post_ids">
          <el-select
            v-model="passForm.post_ids"
            multiple
            filterable
            placeholder="请先选择部门，再选择岗位"
            style="width: 100%"
            :disabled="!passForm.dept_id"
          >
            <el-option
              v-for="post in postListData"
              :key="post.id"
              :label="post.post_name"
              :value="post.id"
              :disabled="post.status === 1"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closePassDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.applyPassBtn" @click="submitPass">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 拒绝弹窗 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝注册申请"
      width="500px"
      @close="closeRejectDialog"
    >
      <el-form ref="rejectFormRef" :model="rejectForm" :rules="rejectRules" label-width="100px">
        <el-form-item label="登录账号">
          <el-input :model-value="currentApply?.username" disabled />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input :model-value="currentApply?.phone || '-'" disabled />
        </el-form-item>
        <el-form-item label="拒绝原因" prop="reason">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请填写拒绝原因，该内容将通知用户…"
            maxlength="500"
            show-word-limit
          />
          <!-- 快捷原因 -->
          <div class="reject-chips">
            <el-tag
              v-for="item in REJECT_REASON_PRESETS"
              :key="item"
              class="reject-chip"
              effect="plain"
              type="info"
              @click="fillReason(item)"
            >
              {{ item.split('，')[0] }}
            </el-tag>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-space>
          <el-button @click="closeRejectDialog">取消</el-button>
          <el-button type="danger" :loading="loading.applyRejectBtn" @click="submitReject">
            确认拒绝
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="申请详情"
      width="640px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="登录账号">
          {{ currentApply?.username }}
        </el-descriptions-item>
        <el-descriptions-item label="手机号码">
          {{ currentApply?.phone || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="审核状态">
          <el-tag :type="getStatusType(currentApply?.status ?? 0)">
            {{ getStatusLabel(currentApply?.status ?? 0) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ currentApply?.create_time }}
        </el-descriptions-item>
        <el-descriptions-item label="审批时间">
          {{ currentApply?.audit_time ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="拒绝原因">
          {{ currentApply?.audit_reason ?? '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-space>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <template v-if="currentApply?.status === 0">
            <el-button plain type="danger" @click="handleDetailReject">
              拒绝
            </el-button>
            <el-button type="primary" @click="handleDetailPass">
              通过
            </el-button>
          </template>
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

/* 拒绝原因快捷标签 */
.reject-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.reject-chip {
  cursor: pointer;
  transition: all 0.2s ease;
}

.reject-chip:hover {
  opacity: 0.8;
}
</style>
