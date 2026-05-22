<template>
  <div class="executions-page">
    <div class="page-header">
      <h1>执行监控</h1>
      <button class="btn" @click="load">🔄 刷新</button>
    </div>

    <div class="exec-grid" v-if="executions.length">
      <div class="exec-card card" v-for="ex in executions" :key="ex.id" @click="selectedExecution = ex">
        <div class="exec-top">
          <span class="exec-status-icon" :class="ex.status">
            {{ ex.status === 'completed' ? '✓' : ex.status === 'running' ? '⟳' : '✕' }}
          </span>
          <div class="exec-info">
            <span class="exec-title">执行 #{{ ex.id }}</span>
            <span class="exec-sub">工作流 #{{ ex.workflow_id || '-' }} · 任务 #{{ ex.task_id || '-' }}</span>
          </div>
          <span class="badge" :class="`badge-${ex.status}`">{{ ex.status }}</span>
        </div>
        <div class="exec-metrics">
          <div class="metric">
            <span class="metric-label">开始时间</span>
            <span class="metric-value">{{ formatTime(ex.started_at) }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">耗时</span>
            <span class="metric-value mono">{{ ex.duration_ms ? ex.duration_ms + 'ms' : '-' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">🔍</div>
      <h3>暂无执行记录</h3>
      <p>运行工作流或任务后，执行记录会显示在这里</p>
    </div>

    <!-- Execution Detail Drawer -->
    <div class="modal-overlay" v-if="selectedExecution" @click.self="selectedExecution = null">
      <div class="drawer glass">
        <div class="drawer-header">
          <h3>执行详情 #{{ selectedExecution.id }}</h3>
          <button class="close-btn" @click="selectedExecution = null">✕</button>
        </div>
        <div class="drawer-body">
          <div class="detail-row">
            <span class="detail-label">状态</span>
            <span class="badge" :class="`badge-${selectedExecution.status}`">{{ selectedExecution.status }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">开始时间</span>
            <span>{{ selectedExecution.started_at }}</span>
          </div>
          <div class="detail-row" v-if="selectedExecution.finished_at">
            <span class="detail-label">结束时间</span>
            <span>{{ selectedExecution.finished_at }}</span>
          </div>
          <div class="detail-row" v-if="selectedExecution.duration_ms">
            <span class="detail-label">耗时</span>
            <span class="mono">{{ selectedExecution.duration_ms }}ms</span>
          </div>
          <div class="detail-section" v-if="selectedExecution.error_message">
            <h4>错误信息</h4>
            <pre class="error-box">{{ selectedExecution.error_message }}</pre>
          </div>
          <div class="detail-section">
            <h4>输入数据</h4>
            <pre class="code-box">{{ JSON.stringify(selectedExecution.input_data, null, 2) }}</pre>
          </div>
          <div class="detail-section">
            <h4>输出数据</h4>
            <pre class="code-box">{{ JSON.stringify(selectedExecution.output_data, null, 2) }}</pre>
          </div>
          <div class="detail-section" v-if="Object.keys(selectedExecution.node_results || {}).length">
            <h4>节点结果</h4>
            <div class="node-results">
              <div class="node-result-item" v-for="(val, key) in selectedExecution.node_results" :key="String(key)">
                <span class="nr-key">{{ key }}</span>
                <pre class="nr-val">{{ JSON.stringify(val, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { workflowApi } from "@/api/workflows";
import type { Execution } from "@/types";

const executions = ref<Execution[]>([]);
const selectedExecution = ref<Execution | null>(null);

function formatTime(iso?: string) {
  if (!iso) return "-";
  return new Date(iso).toLocaleString("zh-CN");
}

async function load() {
  try {
    // Fetch all recent executions across workflows
    const { data } = await workflowApi.list({ page_size: 1 });
    const allExecs: Execution[] = [];
    for (const wf of (data.items || [])) {
      try {
        const { data: execs } = await workflowApi.executions(wf.id);
        allExecs.push(...execs);
      } catch {}
    }
    executions.value = allExecs.sort((a, b) => (b.id || 0) - (a.id || 0)).slice(0, 50);
  } catch {}
}

onMounted(load);
</script>

<style scoped>
.executions-page { max-width: 1200px; }
.exec-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }
.exec-card { cursor: pointer; }
.exec-top { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.exec-status-icon {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; flex-shrink: 0;
}
.exec-status-icon.completed { background: rgba(16,185,129,0.15); color: var(--green); }
.exec-status-icon.running { background: rgba(6,182,212,0.15); color: var(--accent); animation: spin 1.5s linear infinite; }
.exec-status-icon.failed { background: rgba(239,68,68,0.15); color: var(--red); }
@keyframes spin { to { transform: rotate(360deg); } }
.exec-info { flex: 1; }
.exec-title { display: block; font-size: 15px; font-weight: 600; }
.exec-sub { font-size: 12px; color: var(--text-muted); }
.exec-metrics { display: flex; gap: 24px; }
.metric-label { display: block; font-size: 11px; color: var(--text-muted); margin-bottom: 2px; }
.metric-value { font-size: 13px; font-weight: 500; }
.mono { font-family: var(--font-mono); }
.modal-overlay { position: fixed; inset: 0; z-index: 100; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; justify-content: flex-end; }
.drawer {
  width: 500px; height: 100vh; overflow-y: auto;
  background: var(--bg-base); border-left: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-lg);
}
.drawer-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--border-subtle); }
.drawer-header h3 { font-size: 17px; font-weight: 600; }
.close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 20px; }
.drawer-body { padding: 24px; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border-subtle); }
.detail-label { font-size: 13px; color: var(--text-muted); }
.detail-section { margin-top: 20px; }
.detail-section h4 { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 10px; }
.code-box, .error-box {
  background: var(--bg-raised); padding: 14px; border-radius: var(--radius-md);
  font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary);
  max-height: 200px; overflow-y: auto; white-space: pre-wrap;
  border: 1px solid var(--border-subtle);
}
.error-box { border-color: rgba(239,68,68,0.3); color: var(--red); }
.node-results { display: flex; flex-direction: column; gap: 8px; }
.node-result-item { padding: 10px; background: var(--bg-raised); border-radius: var(--radius-md); }
.nr-key { font-size: 12px; font-weight: 600; color: var(--accent); display: block; margin-bottom: 6px; }
.nr-val { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); white-space: pre-wrap; margin: 0; }
</style>
