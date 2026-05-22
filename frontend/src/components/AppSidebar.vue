<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-icon">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <rect width="28" height="28" rx="8" fill="url(#g1)" />
          <path d="M8 14h4l2-4 2 8 2-4h4" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          <defs><linearGradient id="g1" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#06b6d4" /><stop offset="1" stop-color="#8b5cf6" /></linearGradient></defs>
        </svg>
      </div>
      <div class="brand-text">
        <span class="brand-name">FlowMind</span>
        <span class="brand-sub">AI Workflow</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" :class="{ active: route.name === 'dashboard' }">
        <span class="nav-icon">📊</span><span class="nav-label">工作台</span>
      </router-link>
      <router-link to="/workflows" class="nav-item" :class="{ active: route.name === 'workflows' || route.name === 'workflow-editor' }">
        <span class="nav-icon">⚡</span><span class="nav-label">工作流</span>
      </router-link>
      <router-link to="/agents" class="nav-item" :class="{ active: route.name === 'agents' || route.name === 'agent-detail' }">
        <span class="nav-icon">🤖</span><span class="nav-label">智能体</span>
      </router-link>
      <router-link to="/tasks" class="nav-item" :class="{ active: route.name === 'tasks' }">
        <span class="nav-icon">📋</span><span class="nav-label">任务调度</span>
      </router-link>
      <router-link to="/executions" class="nav-item" :class="{ active: route.name === 'executions' }">
        <span class="nav-icon">🔍</span><span class="nav-label">执行监控</span>
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <div class="version-info">
        <span class="dot"></span>
        <span>v1.0.0</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
const route = useRoute();
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  border-right: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 20px 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}
.brand-text { display: flex; flex-direction: column; }
.brand-name { font-family: var(--font-display); font-size: 20px; font-weight: 800; background: linear-gradient(135deg, var(--accent), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.brand-sub { font-size: 11px; color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; }
.sidebar-nav { flex: 1; padding: 16px 12px; display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px; font-weight: 500;
  transition: all 0.2s ease;
  text-decoration: none;
}
.nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.nav-item.active {
  background: var(--accent-glow);
  color: var(--accent);
  border: 1px solid var(--border-accent);
}
.nav-icon { font-size: 18px; width: 24px; text-align: center; }
.sidebar-footer { padding: 16px 20px; border-top: 1px solid var(--border-subtle); }
.version-info { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-muted); }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); }

@media (max-width: 1024px) {
  .sidebar { width: 72px; }
  .brand-text, .nav-label, .sidebar-footer { display: none; }
  .sidebar-brand { justify-content: center; padding: 16px; }
  .nav-item { justify-content: center; padding: 12px; }
  .nav-icon { margin: 0; }
}
</style>
