/**
 * @desc 标签页全局状态仓库
 * @module store/tabs
 * @author sjzhao
 * @createDate 2026-06-11
 * @business 标签页增删、激活态切换、标签刷新、多标签管理
 * @remark 数据持久化pinia-plugin-persistedstate，刷新保留已打开标签
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RouteLocationNormalized } from 'vue-router'
import router from '@/router'
import type { ITabItem } from '@/types/modules/tabs'

export const useTabsStore = defineStore(
  'tabs',
  () => {
    // #region State
    /**
     * @var visitedTabs
     * @desc 已访问标签页列表
     */
    const visitedTabs = ref<ITabItem[]>([])

    /**
     * @var activePath
     * @desc 当前激活标签页的路由路径
     */
    const activePath = ref<string>('')
    // #endregion

    // #region Action
    /**
     * @method addTab
     * @desc 添加路由标签页并更新激活状态
     * @param {RouteLocationNormalized} route 路由标准对象
     */
    const addTab = (route: RouteLocationNormalized) => {
      const tabs = visitedTabs.value
      const { path, name, meta } = route

      const title = meta?.title ?? ''
      const icon = meta?.icon ?? ''
      const affix = meta?.affix ?? false
      const routeName = name ?? ''

      // 校验标签是否已存在，避免重复添加相同路由
      const tabExists = tabs.some(item => item.path === path)

      // 如果标签不存在，添加到列表
      if (!tabExists) {
        tabs.push({
          id: meta?.id as number,
          path,
          name: routeName as string,
          title: title as string,
          icon: icon as string,
          affix: affix as boolean
        })
      }

      // 更新激活标签页
      activePath.value = path
    }

    /**
     * 关闭指定标签页
     * @param path 待关闭标签的路由路径
     * @description
     * 1. 标签不存在或为固定标签则直接拦截，禁止关闭
     * 2. 删除目标标签后，若关闭的是当前激活页
     * 3. 优先跳转右侧相邻标签，无则跳转左侧，标签全部清空时兜底跳转首页
     */
    const removeTab = (path: string) => {
      // 缓存标签列表，减少响应式对象重复读取
      const tabs = visitedTabs.value
      // 查找目标标签在列表中的索引
      const index = tabs.findIndex(item => item.path === path)

      // 未匹配到对应标签，直接终止执行
      if (index === -1) return
      // 固定标签不允许关闭，终止执行
      if (tabs[index].affix) return

      // 从标签列表中移除当前项
      tabs.splice(index, 1)

      // 关闭的非当前激活标签，无需切换路由，直接返回
      if (activePath.value !== path) return

      // 优先取右侧标签，不存在则取左侧标签
      const targetTab = tabs[index] ?? tabs[index - 1]
      // 跳转到目标标签，无可用标签则兜底访问首页
      router.push(targetTab?.path ?? '/')
    }

    /**
     * @method removeLeftTabs
     * @desc 移除当前标签左侧所有标签页
     * @param {string} currentPath 当前路由路径，以此为分割点
     */
    const removeLeftTabs = (currentPath: string) => {
      const tabs = visitedTabs.value
      const index = tabs.findIndex(item => item.path === currentPath)

      if (index > -1) {
        visitedTabs.value = tabs.slice(index)
      }
    }

    /**
     * @method removeRightTabs
     * @desc 移除当前标签右侧所有标签页
     * @param {string} currentPath 当前路由路径，以此为分割点
     */
    const removeRightTabs = (currentPath: string) => {
      const tabs = visitedTabs.value
      const index = tabs.findIndex(item => item.path === currentPath)

      if (index > -1) {
        visitedTabs.value = tabs.slice(0, index + 1)
      }
    }

    /**
     * @method removeOtherTabs
     * @desc 关闭除当前标签外的所有其他标签页
     * @param {string} currentPath 当前路由路径，保留该路径对应的标签
     */
    const removeOtherTabs = (currentPath: string) => {
      visitedTabs.value = visitedTabs.value.filter(item => item.path === currentPath)
    }

    /**
     * @method removeAllTabs
     * @desc 关闭所有标签页
     */
    const removeAllTabs = () => {
      visitedTabs.value = []
      router.push('/')
    }

    /**
     * @method refreshTab
     * @desc 刷新指定标签页
     * @param {string} path 目标标签路由路径
     */
    const refreshTab = (path: string) => {
      router.replace({
        path,
        query: {
          ...router.currentRoute.value.query,
          _t: Date.now()
        }
      })
    }

    /**
     * @method clickTab
     * @desc 点击路由标签页
     * @param {string} path 待点击的路由路径
     */
    const clickTab = (path: string) => {
      if (path === activePath.value) return
      router.push(path)
    }
    // #endregion

    return {
      // State
      visitedTabs,
      activePath,
      // Action
      addTab,
      removeTab,
      removeLeftTabs,
      removeRightTabs,
      removeOtherTabs,
      removeAllTabs,
      refreshTab,
      clickTab,
    }
  },
  {
    /**
     * @config persist
     * @desc 开启pinia持久化，localStorage缓存标签页状态
     */
    persist: true
  }
)
