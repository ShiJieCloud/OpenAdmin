<!--
 * @component PermissionDrawer
 * @path views/system/role/components/PermissionDrawer
 * @name 角色权限分配抽屉组件
 * @description 实现角色权限配置，提供权限树搜索、菜单分类筛选、批量勾选/取消、保存权限功能
 * @props
 *  visible: boolean - 抽屉显示隐藏（v-model绑定）
 *  roleId: string|number - 目标角色唯一ID，必传参数
 * @example
 * <PermissionDrawer
 *   v-model:visible="drawerVisible"
 *   :role-id="currentRoleId"
 * />
 * @author sjzhao
 * @date 2026-07-13
 * @version 1.0.0
 * @internal 内部业务组件，不对外通用导出
-->

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElTable } from 'element-plus'

import type { IPermissionInfo } from '@/types/modules/permission'
import type { IMenuItem } from '@/types/modules/menu'

import { getSystemMenuTree } from '@/api/modules/menu'
import { fetchSystemPermissionList } from '@/api/modules/permission'
import { assignRolePermissions, getRolePermissions } from '@/api/modules/role'

// ===================== 1. Props / Model 定义 =====================
/** 组件入参：角色ID */
const props = defineProps<{
  roleId: number
}>()

/** 抽屉显隐状态（v-model 双向绑定） */
const drawerVisible = defineModel<boolean>('visible', {
  default: false,
})

// ===================== 2. 全局静态常量 =====================
/** 权限搜索字段选项 */
const PERMISSION_SEARCH_OPTIONS = [
  { label: '权限名称', value: 'name' },
  { label: 'API', value: 'api' },
]

/** 菜单树节点字段映射 */
const TREE_DEFAULT_PROPS = {
  children: 'children',
  label: 'label',
}

// ===================== 3. 响应式状态数据 =====================
/** 加载状态管理 */
const loading = ref({
  savePermissionBtn: false,
  menuTree: false,
  permTable: false,
})

/** 系统菜单树数据 */
const systemMenuTree = ref<IMenuItem[]>([])

/** 全量权限列表 */
const allPermissionList = ref<IPermissionInfo[]>([])

/** 当前选中的菜单ID（0 表示全部） */
const selectedMenu = ref<number>(0)

/** 角色原有权限ID集合（用于变更对比） */
const currentRolePermissionIdSet = ref<Set<number>>(new Set())

/** 搜索表单 */
const permissionSearchForm = ref({
  searchKey: '',
  searchType: 'name',
})

/** 当前已勾选的权限ID集合 */
const selectedPermissionSet = ref<Set<number>>(new Set())

/** 表格组件引用 */
const permissionTableRef = ref<InstanceType<typeof ElTable>>()

// ===================== 4. 计算属性 =====================
/**
 * 按菜单ID分组权限
 * @description 将全量权限数据按照菜单ID进行分组存储
 * @returns Record<菜单ID, 对应权限列表>，key=0 为全部权限集合
 */
const menuPermissionMap = computed(() => {
  const permissionMap = Object.create(null) as Record<number, IPermissionInfo[]>
  const list = allPermissionList.value

  for (const perm of list) {
    const menuId = perm.menu_id
    const targetArr = permissionMap[menuId] ?? (permissionMap[menuId] = [])
    targetArr.push(perm)
  }

  permissionMap[0] = [...list]

  return permissionMap
})

/**
 * 过滤后的权限列表
 * @description 根据当前选中菜单、搜索关键词、搜索字段过滤权限数据
 * @returns 匹配筛选条件的权限数组
 */
const filterPermissionData = computed(() => {
  const map = menuPermissionMap.value
  const currentMenuId = selectedMenu.value
  const searchForm = permissionSearchForm.value

  // 根据当前选中菜单ID取出对应分组权限集合，无匹配菜单权限则赋值空数组兜底
  const targetPermissionList = map[currentMenuId] ?? []
  const searchKey = searchForm.searchKey.trim()
  if (!searchKey) return targetPermissionList

  const searchField = searchForm.searchType === 'name' ? 'name' : 'code'

  // 遍历权限列表过滤匹配项
  return targetPermissionList.filter(item => {
    const fieldValue = item[searchField]
    return fieldValue?.includes(searchKey)
  })
})

// ===================== 5. 通用工具函数 =====================
/**
 * 判断两个 Set 是否相等（O(N)）
 * @param setA - 集合A
 * @param setB - 集合B
 * @returns 元素完全一致返回 true，否则 false
 */
function isSetEqual(setA: Set<number>, setB: Set<number>): boolean {
  // 长度不等直接不相等
  if (setA.size !== setB.size) return false

  for (const id of setA) {
    // 存在缺失元素直接中断循环，提前返回
    if (!setB.has(id)) return false
  }

  // 长度相同且A所有元素都在B中，集合完全相等
  return true
}

/**
 * 恢复表格勾选状态
 * @description 根据 selectedPermissionSet 同步表格 UI 勾选
 */
const restoreSelection = () => {
  const table = permissionTableRef.value
  if (!table) return
  table.clearSelection()
  filterPermissionData.value.forEach(row => {
    if (selectedPermissionSet.value.has(row.id)) {
      table.toggleRowSelection(row, true)
    }
  })
}

// ===================== 6. 接口请求方法 =====================
/** 拉取全量权限列表 */
const fetchAllPermissionList = async () => {
  try {
    loading.value.permTable = true
    const perms = await fetchSystemPermissionList()
    allPermissionList.value = perms
  } finally {
    loading.value.permTable = false
  }
}

/** 拉取系统菜单树 */
const fetchMenuTree = async () => {
  try {
    loading.value.menuTree = true
    const menuTree = await getSystemMenuTree()
    systemMenuTree.value = [
      { id: 0, name: 'all', label: '全部' },
      ...menuTree,
    ]
  } finally {
    loading.value.menuTree = false
  }
}

/** 拉取角色已有权限 */
const fetchRolePerms = async () => {
  const rolePerms = await getRolePermissions(props.roleId)
  if (!rolePerms) return
  currentRolePermissionIdSet.value = new Set(rolePerms.map(p => p.id))
  selectedPermissionSet.value = new Set(currentRolePermissionIdSet.value)
}

// ===================== 7. 业务处理 =====================
/**
 * 抽屉打开回调
 * @description 并行加载数据，等待 DOM 渲染后恢复勾选状态
 */
const handleOpenPermissionDrawer = async () => {
  await Promise.all([fetchMenuTree(), fetchAllPermissionList(), fetchRolePerms()])

  // 等待 DOM 渲染完成，确保表格数据更新，再恢复勾选状态
  await nextTick()
  restoreSelection()
}

/** 关闭抽屉 */
const closePermissionDrawer = () => {
  drawerVisible.value = false
  selectedPermissionSet.value.clear()
}

/**
 * 单行权限勾选/取消
 * @param selection - 当前勾选行列表
 * @param row - 当前操作行
 */
const handleSelectPermission = (selection: IPermissionInfo[], row: IPermissionInfo) => {
  const permissionId = row.id
  const isChecked = selection.some(item => item.id === permissionId)

  if (isChecked) {
    selectedPermissionSet.value.add(permissionId)
  } else {
    selectedPermissionSet.value.delete(permissionId)
  }
}

/**
 * 全选/取消全选当前菜单权限
 * @param rows - 全选时的勾选行列表，空数组表示取消全选
 */
const handleSelectAllPermission = (rows: IPermissionInfo[]) => {
  const currentMenuId = selectedMenu.value
  const allMenuPerms = menuPermissionMap.value[currentMenuId!] ?? []

  if (rows.length === 0) {
    const removeIds = new Set(allMenuPerms.map(p => p.id))
    selectedPermissionSet.value = new Set(
      Array.from(selectedPermissionSet.value).filter(id => !removeIds.has(id))
    )
  } else {
    const addIds = rows.map(row => row.id)
    selectedPermissionSet.value = new Set([
      ...selectedPermissionSet.value,
      ...addIds
    ])
  }
}

/**
 * 提交权限分配
 * @description 对比变更后提交，成功后同步最新状态
 */
const submitPermissionAssign = async () => {
  const { roleId } = props
  if (!roleId) return

  const selectedSet = selectedPermissionSet.value
  const originSet = currentRolePermissionIdSet.value

  if (isSetEqual(selectedSet, originSet)) {
    ElMessage.warning('权限未发生变更，无需保存')
    return
  }

  const perm_ids = [...selectedSet]
  loading.value.savePermissionBtn = true

  try {
    await assignRolePermissions(roleId, { perm_ids })
    ElMessage.success('权限分配成功')
  } finally {
    loading.value.savePermissionBtn = false
  }
}

/** 菜单节点点击 */
const handleClickMenu = (menuId: number) => {
  selectedMenu.value = menuId
  restoreSelection()
}

// ===================== 8. 监听逻辑 =====================
/** 监听过滤数据变化，自动恢复勾选状态 */
watch(filterPermissionData, restoreSelection, { flush: 'post' })
</script>

<template>
  <el-drawer
    v-model="drawerVisible"
    title="开通权限"
    size="50%"
    resizable
    @close="closePermissionDrawer"
    @open="handleOpenPermissionDrawer"
  >

    <template #default>
      <div class="permission-header">
        <el-input
          v-model="permissionSearchForm.searchKey"
          placeholder="例如：获取群组信息、im:chat:readonly"
        >
          <template #prefix>
            <el-icon>
              <i-ep-search />
            </el-icon>
          </template>
          <template #append>
            <el-select
              v-model="permissionSearchForm.searchType"
              placeholder="Select"
              style="width: 115px"
            >
              <el-option
                v-for="option in PERMISSION_SEARCH_OPTIONS"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </template>
        </el-input>
      </div>

      <div class="permission-content">
        <div
          v-loading="loading.menuTree"
          class="permission-content__tree"
        >
          <el-tree
            :data="systemMenuTree"
            :props="TREE_DEFAULT_PROPS"
            node-key="id"
            default-expand-all
            highlight-current
            :current-node-key="selectedMenu"
            @node-click="handleClickMenu($event.id)"
          />
        </div>

        <div
          v-loading="loading.permTable"
          class="permission-content__table"
        >
          <el-table
            ref="permissionTableRef"
            border
            :data="filterPermissionData"
            stripe
            row-key="id"
            @select="handleSelectPermission"
            @select-all="handleSelectAllPermission"
          >
            <el-table-column
              type="selection"
              width="55"
              align="center"
              :reserve-selection="true"
            />

            <el-table-column
              prop="name"
              label="权限名称"
              min-width="140"
              align="center"
            >
              <template #default="{ row }">
                <el-tooltip
                  v-if="row.description"
                  :content="row.description"
                  placement="top"
                >
                  <el-link>{{ row.name }}</el-link>
                </el-tooltip>
                <el-link v-else>{{ row.name }}</el-link>
              </template>
            </el-table-column>

            <el-table-column
              prop="code"
              label="API"
              min-width="160"
              align="center"
            >
              <template #default="{ row }">
                <el-tag type="info">{{ row.code }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </template>

    <template #footer>
      <el-space>
        <el-button @click="closePermissionDrawer">取消</el-button>
        <el-button
          plain
          type="primary"
          :loading="loading.savePermissionBtn"
          @click="submitPermissionAssign"
        >
          确定开通权限
        </el-button>
      </el-space>
    </template>
  </el-drawer>
</template>

<style scoped>
:deep(.el-drawer__body) {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 16px;
  overflow: hidden;
}

.permission-header {
  flex: 0 0 auto;
  margin-bottom: 16px;
}

.permission-content {
  flex: 1 1 auto;
  height: calc(100% - 40px);
  display: flex;
  gap: 12px;
}

.permission-content__tree {
  flex: 0 0 200px;
  height: 100%;
  overflow-y: auto;
  padding: 8px;
}

.permission-content__table {
  flex: 1 1 auto;
  min-width: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.permission-content__table :deep(.el-table) {
  width: 100%;
  height: 100%;
}

.permission-content__table :deep(.el-table__body-wrapper) {
  flex: 1 1 auto;
  min-height: 0;
}

.permission-content__table :deep(.el-empty) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>
