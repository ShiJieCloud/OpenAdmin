<!--
 * @component UserManagement
 * @path views/system/user/index
 * @name 用户管理页面
 * @description 实现用户列表的增删改查，提供用户搜索、新增、编辑、删除、批量删除、重置密码、状态修改及角色分配功能
 * @example
 * <UserManagement />
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

import type { IUserInfo, IUserCreateRequest, IUserUpdateRequest } from '@/types/modules/user'
import type { IDeptInfo } from '@/types/modules/dept'
import { getUserInfo } from '@/api/modules/user'

import {
  getUserList,
  createUser,
  updateUser,
  updateUserStatus,
  resetUserPassword,
} from '@/api/modules/user'
import { getDeptList, listPostsByDeptId } from '@/api/modules/dept'
import type { IPostInfo } from '@/types/modules/post'
import RoleDrawer from './components/RoleDrawer.vue'

// ===================== 1. 全局静态常量 =====================
/** 分页每页条数可选项 */
const PAGE_SIZE_OPTIONS = [1, 10, 20, 50]

/** 默认分页条数 */
const DEFAULT_PAGE_SIZE = 10

/** 用户状态选项 */
const USER_STATUS_OPTIONS = [
  { label: '正常', value: 0 },
  { label: '禁用', value: 1 },
  { label: '锁定', value: 2 },
  { label: '注销', value: 3 },
  { label: '冻结', value: 4 },
] as const

/** 性别选项 */
const SEX_OPTIONS = [
  { label: '未知', value: 0 },
  { label: '男', value: 1 },
  { label: '女', value: 2 },
] as const

// ===================== 2. 响应式状态数据 =====================
/** 部门树形数据 */
const deptTreeData = ref<IDeptInfo[]>([])

/** 岗位列表数据 */
const postListData = ref<IPostInfo[]>([])

/** 用户分页数据 */
const userPageData = ref({
  records: [] as IUserInfo[],
  total: 0,
  pages: 0,
  page_size: DEFAULT_PAGE_SIZE,
  page_num: 1,
})

/** 用户列表查询参数 */
const searchUserParams = reactive({
  page_num: 1,
  page_size: DEFAULT_PAGE_SIZE,
  username: '',
  nickname: '',
  email: '',
  phone: '',
  status: undefined as number | undefined,
  dept_id: undefined as number | undefined,
})

/** 加载状态管理 */
const loading = ref({
  userTable: false,
  userRefreshBtn: false,
  userAddBtn: false,
  userEditBtn: false,
  userDeleteBtn: false,
  userBatchDeleteBtn: false,
  userResetPwdBtn: false,
})

/** 表格已勾选的用户行集合 */
const selectedRows = ref<IUserInfo[]>([])

/** 新增用户弹窗显隐状态 */
const addUserDialogVisible = ref(false)

/** 新增用户表单引用 */
const addUserFormRef = ref<FormInstance>()

/** 新增用户表单数据 */
const addUserForm = reactive<IUserCreateRequest>({
  username: '',
  password: '',
  nickname: '',
  email: '',
  phone: '',
  sex: 0,
  dept_id: undefined,
  post_ids: [],
  remark: '',
})

/** 新增用户表单校验规则 */
const addUserRules = reactive<FormRules<IUserCreateRequest>>({
  username: [
    { required: true, message: '请输入登录账号', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' },
    { min: 6, max: 50, message: '长度在 6 到 50 个字符', trigger: 'blur' },
  ],
  nickname: [
    { max: 50, message: '长度不超过 50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
})

/** 编辑用户弹窗显隐状态 */
const editUserDialogVisible = ref(false)

/** 编辑用户表单引用 */
const editUserFormRef = ref<FormInstance>()

/** 编辑用户表单数据 */
const editUserForm = reactive<IUserUpdateRequest>({
  user_id: 0,
  nickname: '',
  email: '',
  phone: '',
  sex: 0,
  dept_id: undefined,
  post_ids: [],
  remark: '',
})

/** 编辑用户表单校验规则 */
const editUserRules = reactive<FormRules<IUserUpdateRequest>>({
  nickname: [
    { max: 50, message: '长度不超过 50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
})

/** 重置密码弹窗显隐状态 */
const resetPwdDialogVisible = ref(false)

/** 重置密码表单引用 */
const resetPwdFormRef = ref<FormInstance>()

/** 重置密码表单数据 */
const resetPwdForm = reactive({
  user_id: 0,
  new_password: '',
  confirm_password: '',
})

/** 重置密码表单校验规则 */
const resetPwdRules = reactive({
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '长度在 6 到 50 个字符', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== resetPwdForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
})

/** 页面容器 DOM 引用 */
const layoutPageRef = ref<HTMLElement | null>(null)

/** 全屏状态及切换方法 */
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(layoutPageRef)

/** 角色配置抽屉显隐状态 */
const roleDrawerVisible = ref(false)

/** 当前选中的用户ID（用于角色配置） */
const currentUserId = ref(0)

/** 岗位请求取消控制器 */
let postAbort: AbortController | null = null

/** 岗位缓存：key=部门ID，value=该部门下的岗位列表，弹窗关闭时清空 */
const postCache = new Map<number, IPostInfo[]>()

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
    // 忽略主动取消的异常
    if (err.name !== 'AbortError') {
      postListData.value = []
    }
    return []
  }
}

// ===================== 3. 接口请求 method =====================
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
 * 拉取用户分页列表
 * @description 根据查询参数获取用户列表数据
 */
const fetchUserList = async () => {
  loading.value.userTable = true
  try {
    const res = await getUserList(searchUserParams)
    userPageData.value = {
      records: res.records || [],
      total: res.total || 0,
      pages: res.pages || 0,
      page_size: res.page_size || DEFAULT_PAGE_SIZE,
      page_num: res.page_num || 1,
    }
  } finally {
    loading.value.userTable = false
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
 * 搜索回调
 * @description 重置页码并拉取列表
 */
const handleSearch = () => {
  searchUserParams.page_num = 1
  fetchUserList()
}

/**
 * 重置回调
 * @description 清空搜索条件并重新查询
 */
const handleReset = () => {
  searchUserParams.username = ''
  searchUserParams.nickname = ''
  searchUserParams.email = ''
  searchUserParams.phone = ''
  searchUserParams.status = undefined
  searchUserParams.dept_id = undefined
  handleSearch()
}

/**
 * 分页条数变更回调
 * @param val - 新的每页条数
 */
const handleSizeChange = (val: number) => {
  searchUserParams.page_size = val
  searchUserParams.page_num = 1
  fetchUserList()
}

/**
 * 表格勾选变更回调
 * @param val - 已勾选的用户行集合
 */
const handleSelectionChange = (val: IUserInfo[]) => {
  selectedRows.value = val
}

/**
 * 新增表单：部门变更时清空已选岗位并查询新部门的岗位列表
 */
const handleAddDeptChange = async (deptId: number | undefined) => {
  addUserForm.post_ids = []
  await fetchPostsByDept(deptId)
}

/**
 * 编辑表单：部门变更时清空已选岗位并查询新部门的岗位列表
 */
const handleEditDeptChange = async (deptId: number | undefined) => {
  editUserForm.post_ids = []
  await fetchPostsByDept(deptId)
}

/**
 * 打开新增用户弹窗
 */
const handleAddUser = () => {
  addUserDialogVisible.value = true
}

/**
 * 关闭新增用户弹窗并重置表单
 */
const closeAddUserDialog = () => {
  addUserDialogVisible.value = false
  addUserFormRef.value?.resetFields()
  postCache.clear()
}

/**
 * 提交新增用户表单
 * @description 验证表单后调用创建接口，成功后关闭弹窗并刷新列表
 */
const submitAddUser = async () => {
  if (!addUserFormRef.value) return
  const valid = await addUserFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.userAddBtn = true
  try {
    await createUser(addUserForm)
    ElMessage.success('用户创建成功')
    closeAddUserDialog()
    fetchUserList()
  } finally {
    loading.value.userAddBtn = false
  }
}

/**
 * 打开编辑用户弹窗并回填数据
 * @param row - 目标用户行数据
 */
const handleEditUser = async (row: IUserInfo) => {
  // 1. 查询用户详细信息
  const userInfo = await getUserInfo(row.id)
  
  // 2. 先查询该用户部门的岗位列表（等待完成）
  await fetchPostsByDept(userInfo.dept_id ?? undefined)
  
  // 3. 使用 Object.assign 一次性更新所有字段，避免中间状态触发 watch
  Object.assign(editUserForm, {
    user_id: userInfo.id,
    nickname: userInfo.nickname,
    email: userInfo.email,
    phone: userInfo.phone,
    sex: userInfo.sex,
    dept_id: userInfo.dept_id,
    post_ids: userInfo.post_ids || [],
    remark: userInfo.remark,
  })
  
  // 4. 打开弹窗
  editUserDialogVisible.value = true
}

/**
 * 关闭编辑用户弹窗并重置表单
 */
const closeEditUserDialog = () => {
  editUserDialogVisible.value = false
  editUserFormRef.value?.resetFields()
  postCache.clear()
}

/**
 * 提交编辑用户表单
 * @description 验证表单后调用更新接口，成功后关闭弹窗并刷新列表
 */
const submitEditUser = async () => {
  if (!editUserFormRef.value) return
  const valid = await editUserFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.userEditBtn = true
  try {
    await updateUser(editUserForm)
    ElMessage.success('用户更新成功')
    closeEditUserDialog()
    fetchUserList()
  } finally {
    loading.value.userEditBtn = false
  }
}

/**
 * 删除单个用户
 * @param row - 目标用户行数据
 */
const handleDeleteUser = async (row: IUserInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户【${row.nickname || row.username}】吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.userDeleteBtn = true
    // TODO: 调用删除接口（后端暂未提供批量删除接口，此处暂用状态修改代替）
    await updateUserStatus({ user_id: row.id, status: 3 }) // 3=注销
    ElMessage.success('删除成功')
    fetchUserList()
  } finally {
    loading.value.userDeleteBtn = false
  }
}

/**
 * 批量删除已勾选用户
 * @description 批量注销选中的用户
 */
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的用户')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的【${selectedRows.value.length}】个用户吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value.userBatchDeleteBtn = true
    // TODO: 后端暂未提供批量删除接口，此处暂用批量状态修改代替
    const promises = selectedRows.value.map(user =>
      updateUserStatus({ user_id: user.id, status: 3 })
    )
    await Promise.all(promises)

    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value.userBatchDeleteBtn = false
  }
}

/**
 * 打开重置密码弹窗
 * @param row - 目标用户行数据
 */
const handleResetPassword = (row: IUserInfo) => {
  resetPwdForm.user_id = row.id
  resetPwdForm.new_password = ''
  resetPwdForm.confirm_password = ''
  resetPwdDialogVisible.value = true
}

/**
 * 关闭重置密码弹窗
 */
const closeResetPwdDialog = () => {
  resetPwdDialogVisible.value = false
  resetPwdFormRef.value?.resetFields()
}

/**
 * 提交重置密码表单
 */
const submitResetPassword = async () => {
  if (!resetPwdFormRef.value) return
  const valid = await resetPwdFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value.userResetPwdBtn = true
  try {
    await resetUserPassword({
      user_id: resetPwdForm.user_id,
      new_password: resetPwdForm.new_password,
    })
    ElMessage.success('密码重置成功')
    closeResetPwdDialog()
  } finally {
    loading.value.userResetPwdBtn = false
  }
}

/**
 * 修改用户状态
 * @param row - 目标用户行数据
 * @param status - 目标状态
 */
const handleChangeStatus = async (row: IUserInfo, status: number) => {
  await updateUserStatus({ user_id: row.id, status })
  ElMessage.success('状态修改成功')
  fetchUserList()
}

/**
 * 打开角色配置抽屉
 * @param row - 目标用户行数据
 */
const handleAssignRole = (row: IUserInfo) => {
  currentUserId.value = row.id
  roleDrawerVisible.value = true
}

/**
 * 刷新用户列表
 */
const handleRefreshUserList = async () => {
  try {
    loading.value.userRefreshBtn = true
    await Promise.all([fetchDeptTree(), fetchUserList()])
  } finally {
    loading.value.userRefreshBtn = false
  }
}

// ===================== 5. 生命周期 =====================
/**
 * 组件挂载时初始化
 * @description 首次加载时拉取部门树、岗位列表和用户列表数据
 */
onMounted(() => {
  fetchUserList()
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
            <el-form :model="searchUserParams" label-width="auto">
              <el-row :gutter="20" class="pl-5">
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="登录账号">
                    <el-input v-model="searchUserParams.username" placeholder="请输入登录账号" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="用户昵称">
                    <el-input v-model="searchUserParams.nickname" placeholder="请输入用户昵称" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="邮箱">
                    <el-input v-model="searchUserParams.email" placeholder="请输入邮箱" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="手机号">
                    <el-input v-model="searchUserParams.phone" placeholder="请输入手机号" clearable />
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="状态">
                    <el-select v-model="searchUserParams.status" placeholder="请选择状态" clearable>
                      <el-option
                        v-for="item in USER_STATUS_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :sm="12" :md="8" :lg="6">
                  <el-form-item label="所属部门">
                    <el-tree-select
                      v-model="searchUserParams.dept_id"
                      :data="deptTreeData"
                      :props="{ label: 'dept_name', value: 'id', children: 'children' }"
                      placeholder="请选择部门"
                      clearable
                      check-strictly
                      style="width: 100%"
                    />
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
          <h4 class="layout-toolbar__title">用户列表</h4>
          <el-space alignment="flex-end">
            <el-button plain :loading="loading.userRefreshBtn" @click="handleRefreshUserList">
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
            <el-button plain type="primary" @click="handleAddUser">
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
          v-loading="loading.userTable"
          :data="userPageData.records"
          stripe
          width="100%"
          class="layout-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="用户 ID" width="80" align="center" />
          <el-table-column prop="username" label="登录账号" width="120" align="center" />
          <el-table-column prop="nickname" label="用户昵称" align="center" />
          <el-table-column prop="sex" label="性别" width="80" align="center">
            <template #default="{ row }">
              {{ SEX_OPTIONS.find(item => item.value === row.sex)?.label || '未知' }}
            </template>
          </el-table-column>
          <el-table-column prop="dept_name" label="所属部门" width="120" align="center" />
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-dropdown @command="(status: number) => handleChangeStatus(row, status)">
                <el-tag
                  :type="row.status === 0 ? 'success' : row.status === 3 ? 'info' : 'danger'"
                  class="cursor-pointer"
                >
                  {{ USER_STATUS_OPTIONS.find(item => item.value === row.status)?.label || '未知' }}
                </el-tag>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-for="item in USER_STATUS_OPTIONS"
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
          <el-table-column prop="create_time" label="创建时间" width="180" align="center" />
          <el-table-column label="操作" width="320" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="handleEditUser(row)">
                <template #icon>
                  <i-ep-edit-pen />
                </template>
                编辑
              </el-button>
              <el-button type="warning" size="small" link @click="handleResetPassword(row)">
                <template #icon>
                  <i-ep-key />
                </template>
                重置密码
              </el-button>
              <el-button type="success" size="small" link @click="handleAssignRole(row)">
                <template #icon>
                  <i-ep-user />
                </template>
                角色配置
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteUser(row)">
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
            v-model:current-page="searchUserParams.page_num"
            v-model:page-size="searchUserParams.page_size"
            :total="userPageData.total"
            :page-sizes="PAGE_SIZE_OPTIONS"
            layout="total, sizes, prev, pager, next"
            :teleported="false"
            @size-change="handleSizeChange"
            @current-change="fetchUserList"
          />
        </div>
      </el-card>
    </div>

    <!-- 新增用户弹窗 -->
    <el-dialog
      v-model="addUserDialogVisible"
      title="新增用户"
      width="600px"
      @close="closeAddUserDialog"
    >
      <el-form ref="addUserFormRef" :model="addUserForm" :rules="addUserRules" label-width="100px">
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="addUserForm.username" placeholder="请输入登录账号" clearable />
        </el-form-item>
        <el-form-item label="登录密码" prop="password">
          <el-input v-model="addUserForm.password" type="password" placeholder="请输入登录密码" show-password />
        </el-form-item>
        <el-form-item label="用户昵称" prop="nickname">
          <el-input v-model="addUserForm.nickname" placeholder="请输入用户昵称" clearable />
        </el-form-item>
        <el-form-item label="所属部门" prop="dept_id">
          <el-tree-select
            v-model="addUserForm.dept_id"
            :data="deptTreeData"
            :props="{ label: 'dept_name', value: 'id', children: 'children' }"
            placeholder="请选择所属部门"
            clearable
            check-strictly
            filterable
            style="width: 100%"
            @change="handleAddDeptChange"
          />
        </el-form-item>
        <el-form-item label="所属岗位" prop="post_ids">
          <el-select
            v-model="addUserForm.post_ids"
            multiple
            filterable
            placeholder="请先选择部门，再选择岗位"
            style="width: 100%"
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
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="addUserForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="addUserForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="性别" prop="sex">
          <el-radio-group v-model="addUserForm.sex">
            <el-radio v-for="item in SEX_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="addUserForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeAddUserDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.userAddBtn" @click="submitAddUser">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 编辑用户弹窗 -->
    <el-dialog
      v-model="editUserDialogVisible"
      title="编辑用户"
      width="600px"
      @close="closeEditUserDialog"
    >
      <el-form ref="editUserFormRef" :model="editUserForm" :rules="editUserRules" label-width="100px">
        <el-form-item label="用户昵称" prop="nickname">
          <el-input v-model="editUserForm.nickname" placeholder="请输入用户昵称" clearable />
        </el-form-item>
        <el-form-item label="所属部门" prop="dept_id">
          <el-tree-select
            v-model="editUserForm.dept_id"
            :data="deptTreeData"
            :props="{ label: 'dept_name', value: 'id', children: 'children' }"
            placeholder="请选择所属部门"
            clearable
            check-strictly
            filterable
            style="width: 100%"
            @change="handleEditDeptChange"
          />
        </el-form-item>
        <el-form-item label="所属岗位" prop="post_ids">
          <el-select
            v-model="editUserForm.post_ids"
            multiple
            filterable
            placeholder="请先选择部门，再选择岗位"
            style="width: 100%"
            :disabled="!editUserForm.dept_id"
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
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editUserForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editUserForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="性别" prop="sex">
          <el-radio-group v-model="editUserForm.sex">
            <el-radio v-for="item in SEX_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="editUserForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeEditUserDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.userEditBtn" @click="submitEditUser">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog
      v-model="resetPwdDialogVisible"
      title="重置密码"
      width="500px"
      @close="closeResetPwdDialog"
    >
      <el-form ref="resetPwdFormRef" :model="resetPwdForm" :rules="resetPwdRules" label-width="100px">
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="resetPwdForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="resetPwdForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-space>
          <el-button @click="closeResetPwdDialog">取消</el-button>
          <el-button plain type="primary" :loading="loading.userResetPwdBtn" @click="submitResetPassword">
            确定
          </el-button>
        </el-space>
      </template>
    </el-dialog>

    <RoleDrawer v-model:visible="roleDrawerVisible" :user-id="currentUserId" />
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
