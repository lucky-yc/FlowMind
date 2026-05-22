<template>
  <div class="agent-detail" v-if="agent">
    <div class="page-header">
      <div class="header-left">
        <button class="btn btn-sm" @click="$router.push('/agents')">← 返回</button>
        <h1>{{ agent.name }}</h1>
      </div>
      <button class="btn btn-primary" @click="handleSave" :disabled="saving">
        {{ saving ? "保存中..." : "💾 保存" }}
      </button>
    </div>

    <div class="detail-grid">
      <div class="card config-section">
        <h3 class="section-title">基本信息</h3>
        <div class="form-group"><label>名称</label><input class="input" v-model="form.name" /></div>
        <div class="form-group"><label>描述</label><textarea class="input" v-model="form.description" rows="3"></textarea></div>
        <div class="form-row">
          <div class="form-group"><label>类型</label>
            <select class="input" v-model="form.agent_type">
              <option value="chatbot">聊天机器人</option><option value="assistant">助手</option>
              <option value="tool">工具型</option><option value="workflow">工作流型</option>
            </select>
          </div>
          <div class="form-group"><label>模型</label>
            <select class="input" v-model="form.model_name">
              <option>GPT-4</option><option>GPT-4o</option><option>GPT-3.5 Turbo</option>
              <option>Claude 3 Opus</option><option>Claude 3 Sonnet</option>
            </select>
          </div>
        </div>
      </div>

      <div class="card config-section">
        <h3 class="section-title">模型参数</h3>
        <div class="form-group">
          <label>Temperature: {{ form.temperature / 100 }}</label>
          <div class="slider-container">
            <span class="slider-label">精确</span>
            <input type="range" min="0" max="100" v-model.number="form.temperature" class="range-slider" />
            <span class="slider-label">创意</span>
          </div>
        </div>
        <div class="form-group">
          <label>Max Tokens</label>
          <input class="input" type="number" v-model.number="form.max_tokens" />
        </div>
      </div>

      <div class="card config-section full-width">
        <h3 class="section-title">系统提示词</h3>
        <textarea class="input system-prompt" v-model="form.system_prompt" rows="8"
          placeholder="定义智能体的角色、能力和行为规范..."></textarea>
      </div>

      <div class="card config-section">
        <h3 class="section-title">工具配置</h3>
        <div class="tools-list">
          <div class="tool-item" v-for="(tool, i) in form.tools" :key="i">
            <span class="tool-name">{{ tool.name || '工具 ' + (i+1) }}</span>
            <button class="btn btn-sm btn-danger" @click="form.tools.splice(i, 1)">移除</button>
          </div>
          <button class="btn btn-sm" @click="form.tools.push({ name: '新工具', type: 'api' })">＋ 添加工具</button>
        </div>
      </div>

      <div class="card config-section">
        <h3 class="section-title">状态</h3>
        <div class="status-toggle">
          <span :class="{ active: form.is_active }">{{ form.is_active ? "已启用" : "已禁用" }}</span>
          <button class="toggle-btn" :class="{ on: form.is_active }" @click="form.is_active = !form.is_active">
            <div class="toggle-thumb"></div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAgentStore } from "@/stores/agent";

const route = useRoute();
const router = useRouter();
const store = useAgentStore();
const saving = ref(false);
const agent = ref<any>(null);

const form = reactive({
  name: "", description: "", agent_type: "chatbot", model_name: "GPT-4",
  system_prompt: "", temperature: 70, max_tokens: 4096,
  tools: [] as any[], is_active: true,
});

onMounted(async () => {
  const id = Number(route.params.id);
  await store.fetchAgent(id);
  agent.value = store.currentAgent;
  if (agent.value) {
    Object.assign(form, {
      name: agent.value.name, description: agent.value.description,
      agent_type: agent.value.agent_type, model_name: agent.value.model_name,
      system_prompt: agent.value.system_prompt, temperature: agent.value.temperature,
      max_tokens: agent.value.max_tokens, tools: [...(agent.value.tools || [])],
      is_active: agent.value.is_active,
    });
  }
});

async function handleSave() {
  saving.value = true;
  try {
    await store.updateAgent(agent.value.id, { ...form });
    alert("保存成功！");
  } catch { alert("保存失败"); }
  saving.value = false;
}
</script>

<style scoped>
.agent-detail { max-width: 1000px; }
.header-left { display: flex; align-items: center; gap: 16px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.full-width { grid-column: 1 / -1; }
.section-title { font-family: var(--font-display); font-size: 15px; font-weight: 600; margin-bottom: 18px; color: var(--text-secondary); }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-muted); margin-bottom: 6px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.system-prompt { font-family: var(--font-mono); font-size: 13px; line-height: 1.6; }
.slider-container { display: flex; align-items: center; gap: 12px; }
.slider-label { font-size: 11px; color: var(--text-muted); }
.range-slider {
  flex: 1; height: 4px; -webkit-appearance: none; appearance: none;
  background: var(--bg-active); border-radius: 2px; outline: none;
}
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 16px; height: 16px;
  border-radius: 50%; background: var(--accent); cursor: pointer;
  box-shadow: 0 0 8px var(--accent-glow);
}
.tools-list { display: flex; flex-direction: column; gap: 8px; }
.tool-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: var(--bg-base); border-radius: var(--radius-md); }
.tool-name { font-size: 14px; }
.status-toggle { display: flex; align-items: center; justify-content: space-between; }
.status-toggle span { font-size: 14px; font-weight: 500; }
.status-toggle span.active { color: var(--green); }
.toggle-btn {
  width: 48px; height: 26px; border-radius: 13px; border: none;
  background: var(--bg-active); cursor: pointer; position: relative;
  transition: background 0.3s;
}
.toggle-btn.on { background: var(--green); }
.toggle-thumb {
  position: absolute; top: 3px; left: 3px;
  width: 20px; height: 20px; border-radius: 50%;
  background: #fff; transition: transform 0.3s;
}
.toggle-btn.on .toggle-thumb { transform: translateX(22px); }
</style>
