<template>
  <!-- Loading screen while auth state resolves -->
  <div v-if="!ready" class="app-loading">
    <div class="loading-spinner"></div>
  </div>

  <!-- Login page: no layout wrapper -->
  <router-view v-else-if="route.name === 'login'" />

  <!-- Authenticated pages: layout with sidebar -->
  <div v-else class="app-layout">
    <AppSidebar />
    <main class="main-content">
      <header class="top-bar glass">
        <div class="top-bar-left">
          <h2 class="page-title">{{ pageTitle }}</h2>
        </div>
        <div class="top-bar-right">
          <div class="user-info" v-if="auth.user">
            <span class="user-avatar">{{ auth.user.username?.charAt(0).toUpperCase() }}</span>
            <span class="user-name">{{ auth.user.username }}</span>
          </div>
          <button class="btn btn-sm" @click="handleLogout">退出</button>
        </div>
      </header>
      <div class="page-container">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import AppSidebar from "@/components/AppSidebar.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const ready = ref(false);

const pageTitles: Record<string, string> = {
  dashboard: "工作台",
  workflows: "工作流",
  "workflow-editor": "工作流编辑器",
  agents: "智能体",
  "agent-detail": "智能体配置",
  tasks: "任务调度",
  executions: "执行监控",
};
const pageTitle = computed(() => pageTitles[route.name as string] || "FlowMind");

onMounted(async () => {
  if (auth.token) {
    await auth.fetchUser();
  }
  ready.value = true;
});

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.app-loading {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
}
.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border-subtle);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.app-layout { display: flex; height: 100vh; overflow: hidden; }
.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.top-bar {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.page-title { font-family: var(--font-display); font-size: 20px; font-weight: 400; font-style: italic; color: var(--text-primary); }
.top-bar-right { display: flex; align-items: center; gap: 16px; }
.user-info { display: flex; align-items: center; gap: 10px; }
.user-avatar {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  background: var(--accent);
  color: #fff; font-size: 14px; font-weight: 600;
}
.user-name { font-size: 14px; font-weight: 500; color: var(--text-secondary); }
.page-container { flex: 1; overflow-y: auto; padding: 28px; }
</style>
