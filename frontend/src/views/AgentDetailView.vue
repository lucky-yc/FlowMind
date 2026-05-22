<template>
  <div class="agent-detail" v-if="agent">
    <div class="page-header">
      <h1>{{ agent.name }}</h1>
      <button class="btn" @click="$router.back()">← 返回</button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAgentStore } from "@/stores/agent";

const route = useRoute();
const store = useAgentStore();
const agent = ref<any>(null);

onMounted(async () => {
  const id = Number(route.params.id);
  await store.fetchAgent(id);
  agent.value = store.currentAgent;
});
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
</style>
