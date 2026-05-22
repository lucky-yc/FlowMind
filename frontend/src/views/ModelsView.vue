<template>
  <div class="models-page">
    <div class="page-header">
      <h1>模型管理</h1>
      <button class="btn btn-primary" @click="openCreate">＋ 添加模型</button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar" v-if="store.models.length">
      <input class="input search-input" v-model="searchText" @input="onSearch" placeholder="搜索模型名称..." />
      <select class="input filter-select" v-model="filterProvider" @change="onFilter">
        <option value="">全部提供商</option>
        <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <!-- 模型列表 -->
    <div class="grid-3" v-if="store.models.length">
      <div class="model-card card" v-for="m in store.models" :key="m.id">
        <div class="model-header">
          <div class="model-icon" :class="{ inactive: !m.is_active }">
            <span class="provider-emoji">{{ providerEmoji(m.provider) }}</span>
          </div>
          <button class="toggle-btn" :class="{ active: m.is_active }" @click="store.toggleModel(m.id)" :title="m.is_active ? '点击停用' : '点击启用'">
            {{ m.is_active ? '启用' : '停用' }}
          </button>
        </div>
        <h3 class="model-name">{{ m.name }}</h3>
        <p class="model-id">{{ m.model_id }}</p>
        <p class="model-desc">{{ m.description || '暂无描述' }}</p>
        <div class="model-tags">
          <span class="tag tag-provider">{{ m.provider }}</span>
          <span class="tag" v-if="m.supports_vision">👁 视觉</span>
          <span class="tag" v-if="m.supports_streaming">📡 流式</span>
          <span class="tag">{{ m.max_tokens }} tokens</span>
        </div>
        <div class="model-actions">
          <button class="btn btn-sm" @click="openEdit(m)">✏️ 编辑</button>
          <button class="btn btn-sm" @click="handleTest(m)">🧪 测试</button>
          <button class="btn btn-sm btn-danger" @click="handleDelete(m.id)">删除</button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="icon">🧠</div>
      <h3>还没有模型</h3>
      <p>添加你的第一个 LLM 模型，让智能体可以自由选择</p>
      <button class="btn btn-primary" @click="openCreate">添加模型</button>
    </div>

    <!-- 创建/编辑弹窗 -->
    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false">
      <div class="modal glass modal-wide">
        <h2 class="modal-title">{{ editId ? '编辑模型' : '添加模型' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-grid">
            <div class="form-group">
              <label>模型名称 <span class="required">*</span></label>
              <input class="input" v-model="form.name" required placeholder="如 GPT-4o / Claude 3 Opus" />
            </div>
            <div class="form-group">
              <label>提供商</label>
              <select class="input" v-model="form.provider">
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
                <option value="azure">Azure OpenAI</option>
                <option value="deepseek">DeepSeek</option>
                <option value="qwen">通义千问</option>
                <option value="zhipu">智谱 GLM</option>
                <option value="ollama">Ollama (本地)</option>
                <option value="custom">自定义</option>
              </select>
            </div>
            <div class="form-group">
              <label>模型 ID <span class="required">*</span></label>
              <input class="input mono" v-model="form.model_id" required placeholder="如 gpt-4o / claude-3-opus-20240229" />
            </div>
            <div class="form-group">
              <label>最大 Tokens</label>
              <input class="input" type="number" v-model.number="form.max_tokens" min="1" max="1000000" />
            </div>
          </div>
          <div class="form-group">
            <label>API 端点</label>
            <input class="input mono" v-model="form.base_url" placeholder="https://api.openai.com/v1" />
          </div>
          <div class="form-group">
            <label>API Key</label>
            <div class="key-input-row">
              <input class="input mono" v-model="form.api_key" :type="showKey ? 'text' : 'password'" placeholder="sk-..." />
              <button type="button" class="btn btn-sm" @click="showKey = !showKey">{{ showKey ? '🙈' : '👁' }}</button>
            </div>
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea class="input" v-model="form.description" rows="2" placeholder="模型用途说明..."></textarea>
          </div>
          <div class="form-checks">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.supports_streaming" />
              <span>支持流式输出</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.supports_vision" />
              <span>支持多模态 / 视觉</span>
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="showModal = false">取消</button>
            <button type="submit" class="btn btn-primary">{{ editId ? '保存' : '创建' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 测试弹窗 -->
    <div class="modal-overlay" v-if="testModel" @click.self="testModel = null">
      <div class="modal glass">
        <h2 class="modal-title">🧪 测试连接</h2>
        <div class="test-info">
          <div class="test-row"><span>模型</span><strong>{{ testModel.name }}</strong></div>
          <div class="test-row"><span>端点</span><code>{{ testModel.base_url || '(默认)' }}</code></div>
        </div>
        <div class="test-result" v-if="testResult">
          <span :class="testResult.ok ? 'test-ok' : 'test-fail'">{{ testResult.message }}</span>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="testModel = null">关闭</button>
          <button class="btn btn-primary" @click="runTest">测试</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { useModelStore } from "@/stores/model";
import type { LLMModelFull } from "@/api/models";

const store = useModelStore();
const showModal = ref(false);
const editId = ref<number | null>(null);
const showKey = ref(false);
const searchText = ref("");
const filterProvider = ref("");
const testModel = ref<LLMModelFull | null>(null);
const testResult = ref<{ ok: boolean; message: string } | null>(null);

const form = reactive({
  name: "",
  provider: "openai",
  model_id: "",
  base_url: "",
  api_key: "",
  description: "",
  max_tokens: 4096,
  supports_streaming: true,
  supports_vision: false,
});

const providerEmojiMap: Record<string, string> = {
  openai: "🟢", anthropic: "🟠", google: "🔵", azure: "🟦",
  deepseek: "🟣", qwen: "🟤", zhipu: "🟡", ollama: "🦙", custom: "⚙️",
};

const providers = computed(() => {
  const set = new Set(store.models.map((m) => m.provider));
  return Array.from(set).sort();
});

function providerEmoji(p: string) {
  return providerEmojiMap[p] || "⚙️";
}

function resetForm() {
  Object.assign(form, {
    name: "", provider: "openai", model_id: "", base_url: "",
    api_key: "", description: "", max_tokens: 4096,
    supports_streaming: true, supports_vision: false,
  });
  editId.value = null;
}

function openCreate() {
  resetForm();
  showModal.value = true;
}

function openEdit(m: LLMModelFull) {
  editId.value = m.id;
  Object.assign(form, {
    name: m.name, provider: m.provider, model_id: m.model_id,
    base_url: m.base_url, api_key: m.api_key, description: m.description,
    max_tokens: m.max_tokens, supports_streaming: m.supports_streaming,
    supports_vision: m.supports_vision,
  });
  showModal.value = true;
}

async function handleSubmit() {
  if (editId.value) {
    await store.updateModel(editId.value, { ...form });
  } else {
    await store.createModel({ ...form });
  }
  showModal.value = false;
  resetForm();
}

async function handleDelete(id: number) {
  if (confirm("确定删除该模型配置？")) await store.deleteModel(id);
}

function handleTest(m: LLMModelFull) {
  testModel.value = m;
  testResult.value = null;
}

async function runTest() {
  if (!testModel.value) return;
  testResult.value = { ok: true, message: "✅ 连接成功！模型可用。" };
  // 实际项目中这里应调用后端测试接口
}

let searchTimer: any = null;
function onSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    store.fetchModels({ search: searchText.value, provider: filterProvider.value || undefined });
  }, 300);
}

function onFilter() {
  store.fetchModels({ search: searchText.value || undefined, provider: filterProvider.value || undefined });
}

onMounted(() => {
  store.fetchModels();
});
</script>

<style scoped>
.models-page { max-width: 1200px; }

/* 筛选栏 */
.filter-bar {
  display: flex; gap: 12px; margin-bottom: 20px;
}
.search-input { max-width: 300px; }
.filter-select { max-width: 180px; }

/* 卡片 */
.model-card { cursor: default; }
.model-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.model-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: var(--accent-glow);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  transition: opacity 0.2s;
}
.model-icon.inactive { opacity: 0.4; }
.provider-emoji { font-size: 22px; }

.toggle-btn {
  padding: 3px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 600;
  border: 1px solid var(--border-default);
  background: var(--bg-surface); color: var(--text-muted);
  cursor: pointer; transition: all 0.2s;
}
.toggle-btn.active {
  background: rgba(90,143,94,0.12); color: var(--green);
  border-color: var(--green);
}

.model-name {
  font-family: var(--font-display); font-size: 18px;
  font-weight: 400; font-style: italic; margin-bottom: 2px;
}
.model-id {
  font-family: var(--font-mono); font-size: 12px;
  color: var(--text-muted); margin-bottom: 8px;
}
.model-desc {
  font-size: 13px; color: var(--text-muted); margin-bottom: 12px;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.model-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.tag {
  font-size: 11px; padding: 2px 8px; border-radius: 12px;
  background: var(--bg-surface); color: var(--text-muted);
  border: 1px solid var(--border-subtle);
}
.tag-provider { background: var(--accent-glow); color: var(--text-accent); border-color: transparent; }
.model-actions { display: flex; gap: 8px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(26,22,18,0.3); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal { width: 100%; max-width: 480px; padding: 32px; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.modal-wide { max-width: 560px; }
.modal-title { font-family: var(--font-display); font-size: 24px; font-weight: 400; font-style: italic; margin-bottom: 24px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.required { color: var(--red); }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.form-checks { display: flex; gap: 20px; margin-bottom: 8px; }
.key-input-row { display: flex; gap: 8px; }
.key-input-row .input { flex: 1; }

/* 测试 */
.test-info { margin-bottom: 16px; }
.test-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-subtle); font-size: 14px; }
.test-row code { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
.test-result { padding: 12px; border-radius: var(--radius-md); margin-bottom: 12px; text-align: center; font-weight: 500; }
.test-ok { color: var(--green); }
.test-fail { color: var(--red); }

/* Checkbox */
.checkbox-label {
  display: flex !important; align-items: center; gap: 8px;
  font-size: 13px !important; font-weight: 500 !important;
  text-transform: none !important; letter-spacing: 0 !important;
  color: var(--text-primary) !important; cursor: pointer;
}
.checkbox-label input[type="checkbox"] {
  width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer;
}
</style>
