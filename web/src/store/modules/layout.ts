import { defineStore } from 'pinia'
import { ref } from 'vue'
import { LAYOUT, type LayoutMode } from '@/types/modules/layout'


export const useLayoutStore = defineStore(
    'layout',
    () => {
        const layoutMode = ref<LayoutMode>(LAYOUT.CLASSIC)

        function setLayoutMode(mode: LayoutMode) {
            layoutMode.value = mode
        }

        return {
            layoutMode,
            setLayoutMode
        }
    }, {
    persist: true
})
