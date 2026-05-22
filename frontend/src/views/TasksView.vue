<template>
  <div class="tasks-page">
    <div class="page-header">
      <h1>任务调度</h1>
      <button class="btn btn-primary" @click="showCreate = true">＋ 新建任务</button>
    </div>

    <div class="tasks-table card" v-if="store.tasks.length">
      <div class="table-header">
        <span class="col-name">任务名称</span>
        <span class="col-schedule">调度类型</span>
        <span class="col-priority">优先级</span>
        <span class="col-status">状态</span>
        <span class="col-actions">操作</span>
      </div>
      <div class="table-row" v-for="task in store.tasks" :key="task.id">
        <span class="col-name">
          <span class="task-name">{{ task.name }}</span>
          <span class="task-desc">{{ task.description }}</span>
        </span>
        <span class="col-schedule">
          <span class="schedule-badge">{{ scheduleLabels[task.schedule_type] || task.schedule_type }}</span>
        </span>
        <span class="col-priority">
          <div class="priority-bar">
            <div class="priority-fill" :style="{ width: task.priority * 10 + '%', background: priorityColor(task.priority) }"></div>
          </div>
          <span class="priority-num">{{ task.priority }}</span>
        </span>
        <span class="col-status"><span class="badge" :class="`badge-${task.status}`">{{ task.status }}</span></span>
        <span class="col-actions">
          <button class="btn btn-sm" @click="handleRun(task.id)">▶ 运行</button>
          <button class="btn btn-sm btn-danger" @click="handleDelete(task.id)">删除</button>
        </span>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">📋</div>
      <h3>还没有任务</h3>
      <p>创建任务来调度你的工作流和智能体</p>
    </div>

    <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
      <div class="modal glass">
        <h2 class="modal-title">新建任务</h2>
        <form @submit.prevent="handleCreate">
          <div class="form-group"><label>名称</label><input class="input" v-model="form.name" required placeholder="任务名称" /></div>
          <div class="form-group"><label>描述</label><textarea class="input" v-model="form.description" rows="2"></textarea></div>
          <div class="form-row">
            <div class="form-group"><label>调度类型</label>
              <select class="input" v-model="form.schedule_type">
                <option value="manual">手动</option>
                <option value="once">单次</option>
                <option value="interval">周期</option>
                <option value="cron">Cron</option>
              </select>
            </div>
            <div class="form-group"><label>优先级 (1-10)</label><input class="input" type="number" v-model.number="form.priority" min="1" max="10" /></div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="showCreate = false">取消</button>
            <button type="submit" class="btn btn-primary">创建</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useTaskStore } from "@/stores/task";

const store = useTaskStore();
const showCreate = ref(false);
const form = reactive({ name: "", description: "", schedule_type: "manual", priority: 5 });

const scheduleLabels: Record<string, string> = { manual: "手动", once: "单次", interval: "周期", cron: "Cron" };
function priorityColor(p: number) {
  if (p >= 8) return "var(--red)";
  if (p >= 5) return "var(--yellow)";
  return "var(--green)";
}

async function handleCreate() {
  await store.createTask(form);
  showCreate.value = false;
  form.name = ""; form.description = "";
}
async function handleRun(id: number) { try { await store.runTask(id); alert("运行成功"); } catch { alert("运行失败"); } }
async function handleDelete(id: number) { if (confirm("确定删除？")) await store.deleteTask(id); }
onMounted(() => store.fetchTasks());
</script>

<style scoped>
.tasks-page { max-width: 1200px; }
.tasks-table { padding: 0; overflow: hidden; }
.table-header, .table-row {
  display: grid; grid-template-columns: 2fr 1fr 120px 100px 140px;
  align-items: center; padding: 12px 20px; gap: 12px;
}
.table-header {
  background: var(--bg-surface);
  font-size: 12px; font-weight: 600; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-subtle);
}
.table-row {
  border-bottom: 1px solid var(--border-subtle);
  transition: background 0.2s;
}
.table-row:last-child { border-bottom: none; }
.table-row:hover { background: var(--bg-surface); }
.task-name { display: block; font-weight: 600; font-size: 14px; }
.task-desc { display: block; font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.schedule-badge {
  font-size: 12px; padding: 3px 10px; border-radius: 12px;
  background: var(--bg-surface); color: var(--text-secondary); border: 1px solid var(--border-subtle);
}
.priority-bar { width: 60px; height: 4px; background: var(--bg-active); border-radius: 2px; overflow: hidden; display: inline-block; vertical-align: middle; margin-right: 8px; }
.priority-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }
.priority-num { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
.modal-overlay { position: fixed; inset: 0; z-index: 100; background: rgba(26,22,18,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; }
.modal { width: 100%; max-width: 480px; padding: 32px; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.modal-title { font-family: var(--font-display); font-size: 24px; font-weight: 400; font-style: italic; margin-bottom: 24px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
</style>
