<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { ElDropdown, ElDropdownItem, ElDropdownMenu } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const userName = computed(() => {
  return '用户'
})

const handlePersonalCenter = () => {
  router.push('/profile')
}

const handleChangePassword = () => {
  router.push('/profile/change-password')
}

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="user-avatar-container w-14 h-full">
    <el-dropdown trigger="click" class="user-dropdown">
      <div>
        <el-avatar :size="32" class="avatar">
          <el-icon>
            <i-ep-user />
          </el-icon>
        </el-avatar>
      </div>

      <template #dropdown>

        <el-dropdown-menu class="user-dropdown-menu">

          <el-dropdown-item class="dropdown-item" @click="handlePersonalCenter">
            <el-icon>
              <i-solar-user-line-duotone />
            </el-icon>
            <span>个人中心</span>
          </el-dropdown-item>
          <el-dropdown-item class="dropdown-item" @click="handleChangePassword">
            <el-icon>
              <i-solar-key-broken />
            </el-icon>
            <span>修改密码</span>
          </el-dropdown-item>
          <el-dropdown-item class="dropdown-item logout" @click="handleLogout">
            <el-icon>
              <i-solar-logout-2-line-duotone />
            </el-icon>
            <span>退出登录</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<style scoped>
.user-avatar-container {
  display: flex;
  align-items: center;
  padding: 0 8px;
}

.user-dropdown {
  cursor: pointer;
}
</style>
