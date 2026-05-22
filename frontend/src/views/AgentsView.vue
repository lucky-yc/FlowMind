<template>
  <div class="agents-page">
    <div class="page-header">
      <h1>智能体</h1>
      <button class="btn btn-primary" @click="showCreate = true">＋ 新建智能体</button>
    </div>

    <div class="grid-3" v-if="store.agents.length">
      <div class="agent-card card" v-for="agent in store.agents" :key="agent.id" @click="$router.push(`/agents/${agent.id}`)">
        <div class="agent-header">
          <div class="agent-avatar" :style="{ background: typeColors[agent.agent_type] || 'var(--accent)' }">
            {{ agent.name.charAt(0) }}
          </div>
          <div class="agent-status-dot" :class="{ active: agent.is_active }"></div>
        </div>
        <h3 class="agent-name">{{ agent.name }}</h3>
        <p class="agent-desc">{{ agent.description || "暂无描述" }}</p>
        <div class="agent-meta">
          <span class="agent-model">{{ agent.model_name }}</span>
          <span class="agent-type">{{ agent.agent_type }}</span>
        </div>
        <div class="agent-actions">
          <button class="btn btn-sm" @click.stop="handleEdit(agent)">编辑</button>
          <button class="btn btn-sm" @click.stop="handleChat(agent)">💬 对话</button>
          <button class="btn btn-sm btn-danger" @click.stop="handleDelete(agent.id)">删除</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">🤖</div>
      <h3>还没有智能体</h3>
      <p>创建你的第一个 AI 智能体</p>
      <button class="btn btn-primary" @click="showCreate = true">新建智能体</button>
    </div>

    <!-- Create Modal -->
    <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
      <div class="modal glass">
        <h2 class="modal-title">新建智能体</h2>
        <form @submit.prevent="handleCreate">
          <div class="form-group"><label>名称</label><input class="input" v-model="form.name" required placeholder="智能体名称" /></div>
          <div class="form-group"><label>描述</label><textarea class="input" v-model="form.description" rows="2" placeholder="描述..."></textarea></div>
          <div class="form-group"><label>类型</label>
            <select class="input" v-model="form.agent_type">
              <option value="chatbot">聊天机器人</option>
              <option value="assistant">助手</option>
              <option value="tool">工具型</option>
              <option value="workflow">工作流型</option>
            </select>
          </div>
          <div class="form-group"><label>模型</label>
            <select class="input" v-model="form.model_name" v-if="modelStore.briefModels.length">
              <option v-for="m in modelStore.briefModels" :key="m.id" :value="m.model_id">
                {{ m.name }} ({{ m.provider }})
              </option>
            </select>
            <select class="input" v-model="form.model_name" v-else>
              <option>GPT-4</option><option>GPT-4o</option><option>Claude 3 Opus</option><option>Claude 3 Sonnet</option>
            </select>
            <span class="input-hint" v-if="!modelStore.briefModels.length">
              暂无已配置模型，使用默认选项。<router-link to="/models">去添加</router-link>
            </span>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="showCreate = false">取消</button>
            <button type="submit" class="btn btn-primary">创建</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Modal -->
    <div class="modal-overlay" v-if="showEdit && editingAgent" @click.self="showEdit = false">
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

    <!-- Chat Modal -->
    <div class="modal-overlay" v-if="chatAgent" @click.self="chatAgent = null">
      <div class="modal glass chat-modal">
        <div class="chat-header">
          <h3>💬 {{ chatAgent.name }}</h3>
          <button class="close-btn" @click="chatAgent = null">✕</button>
        </div>
        <div class="chat-messages" ref="chatBox">
          <div v-for="(msg, i) in chatMessages" :key="i" class="chat-msg" :class="msg.role">
            <div class="msg-bubble">{{ msg.content }}</div>
          </div>
        </div>
        <div class="chat-input-area">
          <input class="input" v-model="chatInput" @keyup.enter="sendChat" placeholder="输入消息..." />
          <button class="btn btn-primary" @click="sendChat">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from "vue";
import { useAgentStore } from "@/stores/agent";
import { useModelStore } from "@/stores/model";
import { agentApi } from "@/api/agents";
const store = useAgentStore();
const modelStore = useModelStore();
const showCreate = ref(false);
const showEdit = ref(false);
const editingAgent = ref<any>(null);
const chatAgent = ref<any>(null);
const chatMessages = ref<any[]>([]);
const chatInput = ref("");
const chatBox = ref<HTMLElement>();

const typeColors: Record<string, string> = {
  chatbot: "var(--accent)", assistant: "var(--purple)", tool: "var(--orange)", workflow: "var(--green)",
};

const form = reactive({ name: "", description: "", agent_type: "chatbot", model_name: "GPT-4" });
const editForm = reactive({ name: "", description: "", agent_type: "chatbot", model_name: "GPT-4", system_prompt: "", temperature: 70, max_tokens: 4096 });

async function handleCreate() {
  await store.createAgent({ ...form, temperature: 70, max_tokens: 4096 });
  showCreate.value = false;
  form.name = ""; form.description = "";
}

async function handleDelete(id: number) {
  if (confirm("确定删除？")) await store.deleteAgent(id);
}

function handleEdit(agent: any) {
  editingAgent.value = agent;
  editForm.name = agent.name;
  editForm.description = agent.description;
  editForm.agent_type = agent.agent_type;
  editForm.model_name = agent.model_name;
  editForm.system_prompt = agent.system_prompt || "";
  editForm.temperature = agent.temperature || 70;
  editForm.max_tokens = agent.max_tokens || 4096;
  showEdit.value = true;
}

async function handleUpdate() {
  if (!editingAgent.value) return;
  await store.updateAgent(editingAgent.value.id, { ...editForm });
  showEdit.value = false;
  editingAgent.value = null;
}

function handleChat(agent: any) {
  chatAgent.value = agent;
  chatMessages.value = [{ role: "assistant", content: `你好！我是${agent.name}，有什么可以帮助你的？` }];
}

async function sendChat() {
  if (!chatInput.value.trim()) return;
  const msg = chatInput.value;
  chatMessages.value.push({ role: "user", content: msg });
  chatInput.value = "";
  await nextTick();
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
  try {
    const { data } = await agentApi.chat(chatAgent.value.id, msg);
    chatMessages.value.push({ role: "assistant", content: data.response });
  } catch (_e) {
    chatMessages.value.push({ role: "assistant", content: "请求失败，请重试。" });
  }
  await nextTick();
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
}

onMounted(() => { store.fetchAgents(); modelStore.fetchBriefModels(); });
</script>

<style scoped>
.agents-page { max-width: 1200px; }
.agent-card { cursor: pointer; }
.agent-header { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; position: relative; }
.agent-avatar {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 800; color: #fff;
}
.agent-status-dot {
  position: absolute; top: 0; right: 0;
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--text-muted);
}
.agent-status-dot.active { background: var(--green); box-shadow: 0 0 6px rgba(90,143,94,0.4); }
.agent-name { font-family: var(--font-display); font-size: 18px; font-weight: 400; font-style: italic; margin-bottom: 6px; }
.agent-desc { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.agent-meta { display: flex; gap: 8px; margin-bottom: 14px; }
.agent-model, .agent-type {
  font-size: 11px; padding: 3px 8px; border-radius: 12px;
  background: var(--bg-surface); color: var(--text-muted); border: 1px solid var(--border-subtle);
}
.agent-actions { display: flex; gap: 8px; }
.modal-overlay { position: fixed; inset: 0; z-index: 100; background: rgba(26,22,18,0.3); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; }
.modal { width: 100%; max-width: 480px; padding: 32px; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.modal-title { font-family: var(--font-display); font-size: 24px; font-weight: 400; font-style: italic; margin-bottom: 24px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.chat-modal { max-width: 520px; height: 500px; display: flex; flex-direction: column; padding: 0; }
.chat-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--border-subtle); }
.chat-header h3 { font-family: var(--font-display); font-size: 18px; font-weight: 400; font-style: italic; }
.close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 18px; }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.chat-msg.user { align-self: flex-end; }
.chat-msg.assistant { align-self: flex-start; }
.msg-bubble {
  max-width: 80%; padding: 10px 14px; border-radius: 14px;
  font-size: 14px; line-height: 1.5;
}
.chat-msg.user .msg-bubble { background: var(--accent); color: #fff; border-bottom-right-radius: 4px; }
.chat-msg.assistant .msg-bubble { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-bottom-left-radius: 4px; }
.chat-input-area { display: flex; gap: 8px; padding: 16px 20px; border-top: 1px solid var(--border-subtle); }
.chat-input-area .input { flex: 1; }
.input-hint { display: block; font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.input-hint a { color: var(--text-accent); }
</style>
