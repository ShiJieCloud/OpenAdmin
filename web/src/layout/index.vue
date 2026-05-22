<script setup lang="ts">
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
import Footer from './components/Footer.vue'
import Settings from './components/Settings.vue'
</script>

<template>
  <div class="layout-container">
    <Sidebar />

    <div class="layout-main">
      <Header />

      <main class="main-content">
        <router-view />
      </main>

      <Footer />
    </div>

    <Settings />
  </div>
</template>

<style scoped>
.layout-container {
  min-height: 100vh;
  display: flex;
  background: #f5f7fa;
}

.layout-main {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.layout-sidebar.collapsed + .layout-main {
  margin-left: 64px;
}

.main-content {
  flex: 1;
  padding: 24px;
  margin-top: 60px;
  margin-bottom: 60px;
}

.layout-footer {
  position: fixed;
  bottom: 0;
  left: 220px;
  right: 0;
  height: 60px;
  background: #ffffff;
  border-top: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: left 0.3s ease;
}

.layout-sidebar.collapsed + .layout-main .layout-footer {
  left: 64px;
}

.footer-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.copyright {
  font-size: 13px;
  color: #8f959e;
}

.version {
  font-size: 13px;
  color: #8f959e;
  padding-left: 24px;
  border-left: 1px solid #e8e8e8;
}

@media screen and (max-width: 768px) {
  .layout-sidebar {
    transform: translateX(-100%);
  }

  .layout-sidebar.collapsed {
    transform: translateX(0);
  }

  .layout-main {
    margin-left: 0;
  }

  .layout-footer {
    left: 0;
  }
}
</style>
