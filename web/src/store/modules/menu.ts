/**
 * @desc 菜单全局状态仓库
 * @module store/menu
 * @author sjzhao
 * @createDate 2026-06-01
 * @business 侧边菜单栏、菜单激活态、菜单树构建、动态路由生成、菜单点击路由跳转
 * @remark 数据持久化pinia-plugin-persistedstate，刷新保留菜单选中状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'
import type { IMenuItem } from '@/types/modules/menu'
import { getCurrentUserMenuList } from '@/api'

export const useMenuStore = defineStore(
  'menu',
  () => {
    // #region State
    /**
     * @var rawMenuList
     * @desc 后端返回扁平化原始菜单数组（平级结构，依靠parent_id关联父子）
     */
    const rawMenuList = ref<IMenuItem[]>([])

    /**
     * @var activeRootMenuId
     * @desc 当前选中顶级一级菜单ID
     */
    const activeRootMenuId = ref<number>(0)

    /**
     * @var activeSubMenuId
     * @desc 当前选中子级菜单ID
     */
    const activeSubMenuId = ref<number>(0)

    /**
     * @var isRouteLoaded
     * @desc 路由是否已加载，避免重复加载
     */
    const isRouteLoaded = ref<boolean>(false)
    // #endregion

    // #region Getter
    /**
     * @computed rootMenuList
     * @desc 筛选parent_id=0的一级根菜单
     */
    const rootMenuList = computed(() => {
      return rawMenuList.value.filter(item => item.parent_id === 0)
    })

    /**
     * @computed menuIdMap
     * @desc 菜单ID-Map索引，key=菜单id，value=菜单对象，统一补全children空数组
     * @return Map<number, IMenuItem>
     */
    const menuIdMap = computed(() => {
      const map = new Map<number, IMenuItem>()
      rawMenuList.value.forEach(item => {
        map.set(item.id, { ...item, component: `/src/views/${item.component}.vue`, children: item.children ?? [] })
      })
      return map
    })

    /**
     * @computed treeMenuList
     * @desc 平级数组转嵌套树形菜单结构
     */
    const treeMenuList = computed(() => {
      const idMap = menuIdMap.value
      const rootArr: IMenuItem[] = []
      idMap.forEach(node => {
        const parent = idMap.get(node.parent_id ?? 0)
        parent ? parent.children!.push(node) : rootArr.push(node)
      })
      return rootArr
    })

    /**
     * @computed rootMenuIdMap
     * @desc Map<一级菜单ID, 下级子菜单数组>，快速根据根ID获取子菜单
     */
    const rootMenuIdMap = computed(() => {
      const map = new Map<number, IMenuItem[]>()
      treeMenuList.value.forEach(root => map.set(root.id, root.children ?? []))
      return map
    })

    /**
     * @computed currentSubMenu
     * @desc 当前激活一级菜单对应的子菜单列表
     */
    const currentSubMenu = computed(() => {
      return rootMenuIdMap.value.get(activeRootMenuId.value) || []
    })

    /**
     * @computed rootIdTraceMap
     * @desc 懒加载缓存Map<菜单ID,所属顶级根ID>，用到再计算
     */
    const rootIdTraceMap = computed(() => {
      const cache = new Map<number, number>()
      const idMap = menuIdMap.value

      /**
       * @inner findRoot
       * @desc 递归溯源根ID + 懒缓存，首次查询计算，后续直接命中缓存
       * @param mid 菜单ID
       * @returns 顶级根菜单ID
       */
      const findRoot = (mid: number): number => {
        if (cache.has(mid)) return cache.get(mid)!

        const node = idMap.get(mid)
        if (!node) {
          cache.set(mid, 0)
          return 0
        }
        if (node.parent_id === 0) {
          cache.set(mid, node.id)
          return node.id
        }
        const rootId = findRoot(node.parent_id!)
        cache.set(mid, rootId)
        return rootId
      }

      return { cache, findRoot }
    })
    // #endregion

    // #region Action
    /**
     * @method setRawMenuList
     * @desc 赋值后端原始菜单数据源
     * @param {IMenuItem[]} list 后端菜单数组
     */
    const setRawMenuList = (list: IMenuItem[]) => {
      rawMenuList.value = Array.isArray(list) ? list : []
    }

    /**
     * @method setActiveRootMenuId
     * @desc 更新选中根菜单ID
     * @param {number} id 一级菜单id
     */
    const setActiveRootMenuId = (id: number) => {
      activeRootMenuId.value = id
    }

    /**
     * @method setActiveSubMenuId
     * @desc 更新选中子菜单ID
     * @param {number} id 子菜单id
     */
    const setActiveSubMenuId = (id: number) => {
      activeSubMenuId.value = id
    }

    /**
     * @method setIsRouteLoaded
     * @desc 更新路由是否加载状态
     * @param {boolean} loaded 是否加载完成
     */
    const setIsRouteLoaded = (loaded: boolean) => {
      isRouteLoaded.value = loaded
    }

    /**
     * @method traceRootId
     * @desc 外部快捷方法：根据菜单ID查顶级根ID（懒加载入口）
     * @param menuId 目标菜单ID
     * @returns 根ID，无匹配返回0
     */
    const traceRootId = (menuId: number): number => {
      const { findRoot } = rootIdTraceMap.value
      return findRoot(menuId)
    }

    /**
     * @method handleMenuClick
     * @desc 菜单栏点击统一入口：更新选中ID + 自动页面跳转
     * @param {string} id dom绑定字符串格式菜单ID
     */
    const handleMenuClick = (id: string) => {
      const menuId = Number(id)
      if (Number.isNaN(menuId)) return

      setActiveSubMenuId(menuId)
      const menuItem = menuIdMap.value.get(menuId)
      if (!menuItem || !menuItem.path) return

      const rootId = traceRootId(menuItem.id)
      setActiveRootMenuId(rootId)

      if (rootMenuIdMap.value.has(menuItem.id)) {
        !currentSubMenu.value.length && router.push(menuItem.path)
      } else {
        router.push(menuItem.path)
      }
    }

    /**
     * @method loadUserMenu
     * @desc 加载当前用户菜单列表
     */
    const loadUserMenu = async () => {
      const currentUserMenuList = await getCurrentUserMenuList()
      setRawMenuList(currentUserMenuList)
    }
    // #endregion

    return {
      // State
      rawMenuList,
      activeRootMenuId,
      activeSubMenuId,
      isRouteLoaded,
      // Getter
      rootMenuList,
      menuIdMap,
      treeMenuList,
      rootMenuIdMap,
      currentSubMenu,
      rootIdTraceMap,
      // Action
      setRawMenuList,
      setActiveRootMenuId,
      setActiveSubMenuId,
      setIsRouteLoaded,
      traceRootId,
      handleMenuClick,
      loadUserMenu,
    }
  },
  {
    /**
     * @config persist
     * @desc 开启pinia持久化，localStorage缓存菜单选中状态
     */
    persist: {
      omit: ['isRouteLoaded'],
    },
  }
)