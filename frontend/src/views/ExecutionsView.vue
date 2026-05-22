<template>
  <div class="executions-page">
    <div class="page-header">
      <h1>执行监控</h1>
    </div>

    <div class="exec-list" v-if="store.executions.length">
      <div class="exec-card card" v-for="ex in store.executions" :key="ex.id">
        <div class="exec-row">
          <span class="exec-status-icon" :class="ex.status">
            {{ ex.status === 'completed' ? '✓' : ex.status === 'running' ? '⟳' : '✕' }}
          </span>
          <div class="exec-main">
            <span class="exec-title">执行 #{{ ex.id }}</span>
            <span class="exec-time">{{ formatTime(ex.started_at) }}</span>
          </div>
          <span class="badge" :class="`badge-${ex.status}`">{{ ex.status }}</span>
          <span class="exec-duration" v-if="ex.duration_ms">{{ ex.duration_ms }}ms</span>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">🔍</div>
      <h3>暂无执行记录</h3>
      <p>运行工作流或任务后，执行记录将显示在这里</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useTaskStore } from "@/stores/task";

const store = useTaskStore();

function formatTime(t: string | undefined) {
  if (!t) return "";
  return new Date(t).toLocaleString("zh-CN");
}

onMounted(() => store.fetchExecutions());
</script>

<style scoped>
.executions-page { max-width: 1200px; }
.exec-list { display: flex; flex-direction: column; gap: 12px; }
.exec-card { padding: 16px 20px; }
.exec-row { display: flex; align-items: center; gap: 14px; }
.exec-status-icon {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; font-size: 14px; flex-shrink: 0;
}
.exec-status-icon.completed { background: rgba(90,143,94,0.12); color: var(--green); }
.exec-status-icon.running { background: rgba(201,169,110,0.12); color: var(--accent); animation: spin 1s linear infinite; }
.exec-status-icon.failed { background: rgba(192,80,77,0.12); color: var(--red); }
@keyframes spin { to { transform: rotate(360deg); } }
.exec-main { flex: 1; display: flex; flex-direction: column; }
.exec-title { font-weight: 600; font-size: 14px; }
.exec-time { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.exec-duration { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
</style>
