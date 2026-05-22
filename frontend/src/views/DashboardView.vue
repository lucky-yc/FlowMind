<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>工作台</h1>
      <span class="greeting">{{ greeting }}</span>
    </div>

    <div class="grid-4 stats-grid">
      <StatsCard icon="⚡" label="工作流" :value="stats?.workflow_count ?? 0" color="var(--accent)" />
      <StatsCard icon="🤖" label="智能体" :value="stats?.agent_count ?? 0" color="var(--purple)" />
      <StatsCard icon="📋" label="任务" :value="stats?.task_count ?? 0" color="var(--green)" />
      <StatsCard icon="🔍" label="执行次数" :value="stats?.execution_count ?? 0" color="var(--yellow)" />
    </div>

    <div class="dashboard-grid">
      <div class="card recent-section">
        <h3 class="section-title">最近执行</h3>
        <div class="exec-list" v-if="stats?.recent_executions?.length">
          <div class="exec-item" v-for="ex in stats.recent_executions" :key="ex.id">
            <span class="exec-status" :class="ex.status">
              {{ ex.status === "completed" ? "✓" : ex.status === "running" ? "⟳" : "✕" }}
            </span>
            <div class="exec-info">
              <span class="exec-name">执行 #{{ ex.id }}</span>
              <span class="exec-time">{{ formatTime(ex.started_at) }}</span>
            </div>
            <span class="exec-duration" v-if="ex.duration_ms">{{ ex.duration_ms }}ms</span>
          </div>
        </div>
        <div class="empty-state" v-else style="padding:40px">
          <p style="color:var(--text-muted)">暂无执行记录</p>
        </div>
      </div>

      <div class="card quick-actions">
        <h3 class="section-title">快速操作</h3>
        <div class="action-grid">
          <button class="action-card" @click="$router.push('/workflows')">
            <span class="action-icon">⚡</span>
            <span class="action-label">创建工作流</span>
          </button>
          <button class="action-card" @click="$router.push('/agents')">
            <span class="action-icon">🤖</span>
            <span class="action-label">新建智能体</span>
          </button>
          <button class="action-card" @click="$router.push('/tasks')">
            <span class="action-icon">📋</span>
            <span class="action-label">创建任务</span>
          </button>
          <button class="action-card" @click="$router.push('/executions')">
            <span class="action-icon">🔍</span>
            <span class="action-label">查看监控</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useTaskStore } from "@/stores/task";
import StatsCard from "@/components/StatsCard.vue";
import { dashboardApi } from "@/api/tasks";

const taskStore = useTaskStore();
const stats = ref<any>(null);

const greeting = computed(() => {
  const h = new Date().getHours();
  if (h < 6) return "夜深了";
  if (h < 12) return "早上好";
  if (h < 18) return "下午好";
  return "晚上好";
});

function formatTime(t: string) {
  if (!t) return "";
  return new Date(t).toLocaleString("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

onMounted(async () => {
  try {
    const { data } = await dashboardApi.stats();
    stats.value = data;
  } catch (e) { console.error(e); }
});
</script>

<style scoped>
.dashboard { max-width: 1200px; }
.greeting { font-size: 14px; color: var(--text-muted); font-style: italic; }
.stats-grid { margin-bottom: 28px; }
.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.section-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 400;
  font-style: italic;
  margin-bottom: 20px;
  color: var(--text-primary);
}
.exec-list { display: flex; flex-direction: column; gap: 12px; }
.exec-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px; border-radius: var(--radius-md);
  background: var(--bg-surface);
  transition: background 0.2s;
}
.exec-item:hover { background: var(--bg-hover); }
.exec-status {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; font-size: 13px;
}
.exec-status.completed { background: rgba(90,143,94,0.12); color: var(--green); }
.exec-status.running { background: rgba(201,169,110,0.12); color: var(--accent); }
.exec-status.failed { background: rgba(192,80,77,0.12); color: var(--red); }
.exec-info { flex: 1; display: flex; flex-direction: column; }
.exec-name { font-size: 13px; font-weight: 600; }
.exec-time { font-size: 11px; color: var(--text-muted); }
.exec-duration { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
.action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.action-card {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  padding: 24px 16px; border-radius: var(--radius-lg);
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  cursor: pointer; transition: all 0.2s;
}
.action-card:hover { border-color: var(--border-accent); background: var(--bg-hover); transform: translateY(-2px); }
.action-icon { font-size: 28px; }
.action-label { font-size: 13px; font-weight: 500; color: var(--text-secondary); }
@media (max-width: 900px) { .dashboard-grid { grid-template-columns: 1fr; } }
</style>
