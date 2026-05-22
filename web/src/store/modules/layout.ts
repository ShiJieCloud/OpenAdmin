import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLayoutStore = defineStore(
    'layout',
    () => {
        const layoutMode = ref('default')

        function setLayoutMode(newLayoutMode: 'default' | 'mobile') {
            layoutMode.value = newLayoutMode
        }

        return {
            layoutMode,
            setLayoutMode
        }
    }, {
    persist: true
    }
)
