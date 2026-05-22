<template>
  <div class="app-layout" v-if="route.name !== 'login'">
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
  <router-view v-else />
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import AppSidebar from "@/components/AppSidebar.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

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
});

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
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
.page-title { font-family: var(--font-display); font-size: 18px; font-weight: 600; }
.top-bar-right { display: flex; align-items: center; gap: 16px; }
.user-info { display: flex; align-items: center; gap: 10px; }
.user-avatar {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  color: #fff; font-weight: 700; font-size: 14px;
}
.user-name { font-size: 14px; color: var(--text-secondary); }
.page-container { flex: 1; overflow-y: auto; padding: 28px; }
</style>
