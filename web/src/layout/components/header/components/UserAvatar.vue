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
  <div class="user-avatar-container">
    <el-dropdown trigger="click" class="user-dropdown">
      <div class="user-pill">
        <el-avatar :size="26" class="avatar" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png">
          <el-icon>
            <i-ep-user />
          </el-icon>
        </el-avatar>
        <span class="user-name">
          {{ userName }}
        </span>
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
}

.user-dropdown {
  cursor: pointer;
}

.user-pill {
  display: flex;
  align-items: center;
  height: 36px;
  padding: 4px;
  border: 2px solid var(--el-border-color-lighter);
  border-radius: 99px;
  cursor: pointer;
  transition: padding 0.3s ease, background-color 0.2s ease;

  .avatar {
    flex-shrink: 0;
  }

  .user-name {
    max-width: 0;
    opacity: 0;
    font-size: 13px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: max-width 0.3s ease, opacity 0.3s ease, margin-left 0.3s ease;
  }
}

.user-pill:hover {
  padding: 4px 12px 4px 4px;
  background-color: var(--el-fill-color-light);

  .user-name {
    max-width: 100px;
    margin-left: 8px;
    opacity: 1;
  }
}
</style>
