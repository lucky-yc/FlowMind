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
import { useAuthStore } from "@/stores/auth";
import StatsCard from "@/components/StatsCard.vue";

const taskStore = useTaskStore();
const auth = useAuthStore();
const stats = computed(() => taskStore.stats);

const greeting = computed(() => {
  const h = new Date().getHours();
  const name = auth.user?.full_name || auth.user?.username || "";
  if (h < 6) return `夜深了，${name}，注意休息`;
  if (h < 12) return `早上好，${name}`;
  if (h < 18) return `下午好，${name}`;
  return `晚上好，${name}`;
});

function formatTime(iso?: string) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

onMounted(() => { taskStore.fetchStats(); });
</script>

<style scoped>
.dashboard { max-width: 1200px; }
.greeting { font-size: 14px; color: var(--text-muted); }
.stats-grid { margin-bottom: 28px; }
.dashboard-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; }
@media (max-width: 900px) { .dashboard-grid { grid-template-columns: 1fr; } }
.section-title { font-family: var(--font-display); font-size: 16px; font-weight: 600; margin-bottom: 20px; color: var(--text-secondary); }
.exec-list { display: flex; flex-direction: column; gap: 8px; }
.exec-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px; border-radius: var(--radius-md);
  background: var(--bg-base); transition: background 0.2s;
}
.exec-item:hover { background: var(--bg-hover); }
.exec-status {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
}
.exec-status.completed { background: rgba(16,185,129,0.15); color: var(--green); }
.exec-status.running { background: rgba(6,182,212,0.15); color: var(--accent); animation: spin 1.5s linear infinite; }
.exec-status.failed { background: rgba(239,68,68,0.15); color: var(--red); }
@keyframes spin { to { transform: rotate(360deg); } }
.exec-info { flex: 1; }
.exec-name { display: block; font-size: 14px; font-weight: 500; }
.exec-time { font-size: 12px; color: var(--text-muted); }
.exec-duration { font-size: 12px; color: var(--text-muted); font-family: var(--font-mono); }
.action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.action-card {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 20px; border-radius: var(--radius-md);
  background: var(--bg-base); border: 1px solid var(--border-subtle);
  cursor: pointer; transition: all 0.2s;
  font-family: var(--font-body); color: var(--text-secondary);
}
.action-card:hover { background: var(--bg-hover); border-color: var(--border-accent); transform: translateY(-2px); }
.action-icon { font-size: 28px; }
.action-label { font-size: 13px; font-weight: 500; }
</style>
