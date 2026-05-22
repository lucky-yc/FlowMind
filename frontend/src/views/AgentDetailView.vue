<template>
  <div class="agent-detail" v-if="agent">
    <div class="page-header">
      <h1>{{ agent.name }}</h1>
      <div class="header-actions">
        <button class="btn" @click="handleEdit">编辑</button>
        <button class="btn" @click="$router.back()">← 返回</button>
      </div>
    </div>

    <div class="detail-grid">
      <div class="card info-card">
        <h3 class="section-title">基本信息</h3>
        <div class="info-row"><span class="label">类型</span><span class="value">{{ agent.agent_type }}</span></div>
        <div class="info-row"><span class="label">模型</span><span class="value">{{ agent.model_name }}</span></div>
        <div class="info-row"><span class="label">状态</span><span class="badge" :class="agent.is_active ? 'badge-active' : 'badge-draft'">{{ agent.is_active ? '活跃' : '停用' }}</span></div>
        <div class="info-row"><span class="label">Temperature</span><span class="value">{{ (agent.temperature || 70) / 100 }}</span></div>
        <div class="info-row"><span class="label">Max Tokens</span><span class="value">{{ agent.max_tokens }}</span></div>
      </div>

      <div class="card config-card">
        <h3 class="section-title">系统提示词</h3>
        <pre class="prompt-text">{{ agent.system_prompt || "暂未配置系统提示词" }}</pre>
      </div>
    </div>

    <!-- Edit Modal -->
    <div class="modal-overlay" v-if="showEdit" @click.self="showEdit = false">
      <div class="modal glass">
        <h2 class="modal-title">编辑智能体</h2>
        <form @submit.prevent="handleUpdate">
          <div class="form-group"><label>名称</label><input class="input" v-model="editForm.name" required placeholder="智能体名称" /></div>
          <div class="form-group"><label>描述</label><textarea class="input" v-model="editForm.description" rows="2" placeholder="描述..."></textarea></div>
          <div class="form-group"><label>类型</label>
            <select class="input" v-model="editForm.agent_type">
              <option value="chatbot">聊天机器人</option>
              <option value="assistant">助手</option>
              <option value="tool">工具型</option>
              <option value="workflow">工作流型</option>
            </select>
          </div>
          <div class="form-group"><label>模型</label>
            <select class="input" v-model="editForm.model_name" v-if="modelStore.briefModels.length">
              <option v-for="m in modelStore.briefModels" :key="m.id" :value="m.model_id">
                {{ m.name }} ({{ m.provider }})
              </option>
            </select>
            <select class="input" v-model="editForm.model_name" v-else>
              <option>GPT-4</option><option>GPT-4o</option><option>Claude 3 Opus</option><option>Claude 3 Sonnet</option>
            </select>
            <span class="input-hint" v-if="!modelStore.briefModels.length">
              暂无已配置模型，使用默认选项。<router-link to="/models">去添加</router-link>
            </span>
          </div>
          <div class="form-group"><label>系统提示词</label><textarea class="input" v-model="editForm.system_prompt" rows="4" placeholder="输入系统提示词..."></textarea></div>
          <div class="form-group"><label>Temperature (0-100)</label><input class="input" type="number" v-model.number="editForm.temperature" min="0" max="100" /></div>
          <div class="form-group"><label>Max Tokens</label><input class="input" type="number" v-model.number="editForm.max_tokens" min="1" max="128000" /></div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="showEdit = false">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAgentStore } from "@/stores/agent";
import { useModelStore } from "@/stores/model";

const route = useRoute();
const store = useAgentStore();
const modelStore = useModelStore();
const agent = ref<any>(null);
const showEdit = ref(false);
const editForm = reactive({ name: "", description: "", agent_type: "chatbot", model_name: "GPT-4", system_prompt: "", temperature: 70, max_tokens: 4096 });

onMounted(async () => {
  const id = Number(route.params.id);
  await store.fetchAgent(id);
  agent.value = store.currentAgent;
  modelStore.fetchBriefModels();
});

function handleEdit() {
  if (!agent.value) return;
  editForm.name = agent.value.name;
  editForm.description = agent.value.description;
  editForm.agent_type = agent.value.agent_type;
  editForm.model_name = agent.value.model_name;
  editForm.system_prompt = agent.value.system_prompt || "";
  editForm.temperature = agent.value.temperature || 70;
  editForm.max_tokens = agent.value.max_tokens || 4096;
  showEdit.value = true;
}

async function handleUpdate() {
  if (!agent.value) return;
  await store.updateAgent(agent.value.id, { ...editForm });
  // Refresh agent data
  await store.fetchAgent(agent.value.id);
  agent.value = store.currentAgent;
  showEdit.value = false;
}
</script>

<style scoped>
.agent-detail { max-width: 1000px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.section-title { font-family: var(--font-display); font-size: 18px; font-weight: 400; font-style: italic; margin-bottom: 20px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border-subtle); }
.info-row:last-child { border-bottom: none; }
.info-row .label { font-size: 13px; color: var(--text-muted); }
.info-row .value { font-size: 14px; font-weight: 500; }
.prompt-text {
  font-family: var(--font-mono); font-size: 13px;
  color: var(--text-secondary); white-space: pre-wrap;
  background: var(--bg-surface); padding: 16px;
  border-radius: var(--radius-md); line-height: 1.6;
}
.header-actions { display: flex; gap: 8px; }
.modal-overlay { position: fixed; inset: 0; z-index: 100; background: rgba(26,22,18,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; }
.modal { width: 100%; max-width: 520px; padding: 32px; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.modal-title { font-family: var(--font-display); font-size: 24px; font-weight: 400; font-style: italic; margin-bottom: 24px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.input-hint { display: block; font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.input-hint a { color: var(--text-accent); }
</style>
