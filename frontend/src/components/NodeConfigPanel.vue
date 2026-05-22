<template>
  <div class="config-panel" v-if="node">
    <div class="panel-header">
      <h3>节点配置</h3>
      <button class="close-btn" @click="$emit('close')">✕</button>
    </div>
    <div class="panel-body">
      <div class="config-section">
        <label>节点名称</label>
        <input class="input" v-model="localData.label" @change="emitUpdate" />
      </div>
      <div class="config-section">
        <label>节点类型</label>
        <div class="node-type-badge" :style="{ background: typeInfo.color + '12', color: typeInfo.color }">
          {{ typeInfo.icon }} {{ typeInfo.label }}
        </div>
      </div>
      <div class="config-section">
        <label>描述</label>
        <textarea class="input" v-model="localData.description" @change="emitUpdate" rows="2" placeholder="节点描述..."></textarea>
      </div>

      <!-- LLM config -->
      <template v-if="node.type === 'llm'">
        <div class="config-section">
          <label>模型</label>
          <select class="input" v-model="localData.config.model" @change="emitUpdate">
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="claude-3-opus">Claude 3 Opus</option>
            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
          </select>
        </div>
        <div class="config-section">
          <label>System Prompt</label>
          <textarea class="input" v-model="localData.config.systemPrompt" @change="emitUpdate" rows="4" placeholder="系统提示词..."></textarea>
        </div>
        <div class="config-section">
          <label>Temperature: {{ (localData.config.temperature || 70) / 100 }}</label>
          <input type="range" min="0" max="100" v-model.number="localData.config.temperature" @change="emitUpdate" class="range-slider" />
        </div>
        <div class="config-section">
          <label>Max Tokens</label>
          <input class="input" type="number" v-model.number="localData.config.maxTokens" @change="emitUpdate" />
        </div>
      </template>

      <!-- HTTP config -->
      <template v-if="node.type === 'http'">
        <div class="config-section">
          <label>Method</label>
          <select class="input" v-model="localData.config.method" @change="emitUpdate">
            <option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option>
          </select>
        </div>
        <div class="config-section">
          <label>URL</label>
          <input class="input" v-model="localData.config.url" @change="emitUpdate" placeholder="https://api.example.com" />
        </div>
        <div class="config-section">
          <label>Headers (JSON)</label>
          <textarea class="input mono" v-model="localData.config.headers" @change="emitUpdate" rows="3" placeholder='{"Authorization": "Bearer ..."}'></textarea>
        </div>
      </template>

      <!-- Condition config -->
      <template v-if="node.type === 'condition'">
        <div class="config-section">
          <label>条件表达式</label>
          <textarea class="input mono" v-model="localData.config.expression" @change="emitUpdate" rows="3" placeholder='result.score > 0.8'></textarea>
        </div>
      </template>

      <!-- Code config -->
      <template v-if="node.type === 'code'">
        <div class="config-section">
          <label>语言</label>
          <select class="input" v-model="localData.config.language" @change="emitUpdate">
            <option>python</option><option>javascript</option>
          </select>
        </div>
        <div class="config-section">
          <label>代码</label>
          <textarea class="input mono" v-model="localData.config.code" @change="emitUpdate" rows="8" placeholder="# 在此编写代码..."></textarea>
        </div>
      </template>

      <!-- Variable config -->
      <template v-if="node.type === 'variable'">
        <div class="config-section">
          <label>变量名</label>
          <input class="input mono" v-model="localData.config.varName" @change="emitUpdate" placeholder="myVariable" />
        </div>
        <div class="config-section">
          <label>变量值</label>
          <input class="input" v-model="localData.config.varValue" @change="emitUpdate" placeholder="值或表达式" />
        </div>
      </template>
    </div>
    <div class="panel-footer">
      <button class="btn btn-danger btn-sm" @click="$emit('delete')">删除节点</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, computed } from "vue";
import { NODE_TYPES } from "@/types";

const props = defineProps<{ node: any }>();
const emit = defineEmits(["update", "close", "delete"]);

const typeInfo = computed(() => NODE_TYPES[props.node?.type] || NODE_TYPES.llm);

const localData = reactive({
  label: "",
  description: "",
  config: {} as any,
});

watch(() => props.node, (n) => {
  if (!n) return;
  localData.label = n.data?.label || "";
  localData.description = n.data?.description || "";
  localData.config = { ...(n.data?.config || {}) };
}, { immediate: true, deep: true });

function emitUpdate() {
  emit("update", {
    ...props.node,
    data: { ...props.node.data, label: localData.label, description: localData.description, config: { ...localData.config } },
  });
}
</script>

<style scoped>
.config-panel {
  width: 320px; height: 100%;
  background: var(--bg-base); border-left: 1px solid var(--border-subtle);
  display: flex; flex-direction: column; flex-shrink: 0;
}
.panel-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border-subtle);
}
.panel-header h3 { font-family: var(--font-display); font-size: 17px; font-weight: 400; font-style: italic; }
.close-btn {
  width: 28px; height: 28px; border: none; border-radius: var(--radius-sm);
  background: var(--bg-surface); color: var(--text-muted); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.close-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.panel-body { flex: 1; overflow-y: auto; padding: 16px 20px; }
.config-section { margin-bottom: 16px; }
.config-section label { display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; }
.node-type-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: var(--radius-sm);
  font-size: 13px; font-weight: 600;
}
.range-slider {
  width: 100%; height: 4px; -webkit-appearance: none; appearance: none;
  background: var(--bg-active); border-radius: 2px; outline: none;
}
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 16px; height: 16px;
  border-radius: 50%; background: var(--accent); cursor: pointer;
  box-shadow: 0 0 6px var(--accent-glow);
}
.mono { font-family: var(--font-mono); font-size: 12px; }
.panel-footer { padding: 16px 20px; border-top: 1px solid var(--border-subtle); }
</style>
