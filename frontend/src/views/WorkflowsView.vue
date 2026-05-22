<template>
  <div class="workflows-page">
    <div class="page-header">
      <h1>工作流</h1>
      <button class="btn btn-primary" @click="showCreate = true">
        <span>＋</span> 新建工作流
      </button>
    </div>

    <div class="filter-bar">
      <input class="input search-input" v-model="search" placeholder="搜索工作流..." @input="handleSearch" />
      <div class="filter-tabs">
        <button class="filter-tab" :class="{ active: filter === '' }" @click="filter = ''; load()">全部</button>
        <button class="filter-tab" :class="{ active: filter === 'draft' }" @click="filter = 'draft'; load()">草稿</button>
        <button class="filter-tab" :class="{ active: filter === 'active' }" @click="filter = 'active'; load()">活跃</button>
      </div>
    </div>

    <div class="grid-3 workflow-grid" v-if="store.workflows.length">
      <div class="workflow-card card" v-for="wf in store.workflows" :key="wf.id" @click="$router.push(`/workflows/${wf.id}`)">
        <div class="wf-header">
          <div class="wf-icon">⚡</div>
          <span class="badge" :class="`badge-${wf.status}`">{{ wf.status }}</span>
        </div>
        <h3 class="wf-name">{{ wf.name }}</h3>
        <p class="wf-desc">{{ wf.description || "暂无描述" }}</p>
        <div class="wf-meta">
          <span class="wf-nodes">{{ (wf.nodes || []).length }} 个节点</span>
          <span class="wf-version">v{{ wf.version }}</span>
        </div>
        <div class="wf-actions">
          <button class="btn btn-sm" @click.stop="handleExecute(wf.id)">▶ 运行</button>
          <button class="btn btn-sm btn-danger" @click.stop="handleDelete(wf.id)">删除</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">⚡</div>
      <h3>还没有工作流</h3>
      <p>创建你的第一个工作流，开始自动化之旅</p>
      <button class="btn btn-primary" @click="showCreate = true">新建工作流</button>
    </div>

    <!-- Create Modal -->
    <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
      <div class="modal glass">
        <h2 class="modal-title">新建工作流</h2>
        <form @submit.prevent="handleCreate">
          <div class="form-group">
            <label>名称</label>
            <input class="input" v-model="createForm.name" placeholder="工作流名称" required />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea class="input" v-model="createForm.description" placeholder="描述这个工作流的用途..." rows="3"></textarea>
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
import { useRouter } from "vue-router";
import { useWorkflowStore } from "@/stores/workflow";

const router = useRouter();
const store = useWorkflowStore();
const showCreate = ref(false);
const search = ref("");
const filter = ref("");
const createForm = reactive({ name: "", description: "" });

async function load() {
  await store.fetchWorkflows({ status: filter.value || undefined, search: search.value || undefined });
}

let searchTimer: any;
function handleSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(load, 300);
}

async function handleCreate() {
  const wf = await store.createWorkflow(createForm);
  showCreate.value = false;
  createForm.name = "";
  createForm.description = "";
  router.push(`/workflows/${wf.id}`);
}

async function handleExecute(id: number) {
  try {
    await store.executeWorkflow(id);
    alert("执行完成！");
  } catch { alert("执行失败"); }
}

async function handleDelete(id: number) {
  if (confirm("确定删除此工作流？")) await store.deleteWorkflow(id);
}

onMounted(load);
</script>

<style scoped>
.workflows-page { max-width: 1200px; }
.filter-bar { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.search-input { max-width: 320px; }
.filter-tabs { display: flex; gap: 4px; background: var(--bg-raised); padding: 4px; border-radius: var(--radius-md); }
.filter-tab {
  padding: 8px 16px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-muted);
  font-family: var(--font-body); font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
}
.filter-tab.active { background: var(--bg-surface); color: var(--text-primary); }
.workflow-card { cursor: pointer; }
.wf-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.wf-icon { font-size: 24px; }
.wf-name { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.wf-desc { font-size: 13px; color: var(--text-muted); margin-bottom: 14px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.wf-meta { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); margin-bottom: 14px; }
.wf-actions { display: flex; gap: 8px; }
.modal-overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal { width: 100%; max-width: 480px; padding: 32px; border-radius: var(--radius-lg); }
.modal-title { font-family: var(--font-display); font-size: 22px; font-weight: 700; margin-bottom: 24px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
</style>
