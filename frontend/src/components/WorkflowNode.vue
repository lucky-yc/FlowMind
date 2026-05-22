<template>
  <div class="custom-node" :class="{ selected: data.selected, 'has-error': hasError }" :style="nodeStyle">
    <div class="node-header" :style="{ background: typeInfo.color + '10', borderBottom: `1px solid ${typeInfo.color}25` }">
      <span class="node-icon">{{ typeInfo.icon }}</span>
      <span class="node-label">{{ nodeData.label }}</span>
    </div>
    <div class="node-body">
      <span class="node-type-text">{{ typeInfo.label }}</span>
      <span class="node-desc" v-if="nodeData.description">{{ nodeData.description }}</span>
      <!-- 配置摘要 badges -->
      <div class="node-badges" v-if="badges.length">
        <span v-for="(badge, i) in badges" :key="i" class="node-badge" :style="{ background: badge.color + '12', color: badge.color }">
          {{ badge.text }}
        </span>
      </div>
    </div>
    <!-- 校验错误指示器 -->
    <div class="error-indicator" v-if="hasError" title="配置不完整">⚠</div>
    <!-- Handles -->
    <Handle v-if="nodeType !== 'input'" type="target" :position="Position.Left" :style="handleStyle" />
    <Handle v-if="nodeType !== 'output'" type="source" :position="Position.Right" :style="handleStyle" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Handle, Position } from "@vue-flow/core";
import { NODE_TYPES, validateNodeConfig } from "@/types";

const props = defineProps<{ data: any }>();

const nodeData = computed(() => props.data?.data || {});
const nodeType = computed(() => nodeData.value.node_type || "llm");
const typeInfo = computed(() => NODE_TYPES[nodeType.value] || NODE_TYPES.llm);
const config = computed(() => nodeData.value.config || {});

/** 校验是否有错误 */
const hasError = computed(() => {
  const err = validateNodeConfig(nodeType.value, config.value);
  return !!err;
});

/** 根据节点类型生成摘要 badges */
const badges = computed(() => {
  const c = config.value;
  const list: { text: string; color: string }[] = [];

  switch (nodeType.value) {
    case "llm":
      if (c.model) list.push({ text: c.model, color: "#c9a96e" });
      if (c.jsonMode) list.push({ text: "JSON", color: "#7c6fa0" });
      if (c.temperature !== undefined) {
        const t = c.temperature / 100;
        list.push({ text: `T=${t.toFixed(1)}`, color: "#9a8e80" });
      }
      break;
    case "http":
      if (c.method) {
        const colors: Record<string, string> = { GET: "#5a8f5e", POST: "#c9a96e", PUT: "#6a8fba", DELETE: "#c0504d", PATCH: "#7c6fa0" };
        list.push({ text: c.method, color: colors[c.method] || "#9a8e80" });
      }
      if (c.url) {
        // 显示域名部分
        try {
          const host = new URL(c.url.replace(/\{\{.*?\}\}/g, "https://x")).hostname;
          list.push({ text: host, color: "#6a8fba" });
        } catch (_e) {
          list.push({ text: c.url.slice(0, 20) + "...", color: "#6a8fba" });
        }
      }
      break;
    case "condition":
      if (c.operator) {
        const opLabels: Record<string, string> = {
          equals: "==", not_equals: "!=", contains: "包含", not_contains: "不包含",
          gt: ">", lt: "<", gte: ">=", lte: "<=", is_empty: "空", is_not_empty: "非空", regex: "正则",
        };
        list.push({ text: opLabels[c.operator] || c.operator, color: "#c9a030" });
      }
      break;
    case "code":
      if (c.language) list.push({ text: c.language, color: "#7c6fa0" });
      if (c.timeout) list.push({ text: `${c.timeout}s`, color: "#9a8e80" });
      break;
    case "tool":
      if (c.toolName) list.push({ text: c.toolName, color: "#c97a3a" });
      if (c.retryCount > 0) list.push({ text: `重试×${c.retryCount}`, color: "#9a8e80" });
      break;
    case "input":
      if (c.inputFormat) list.push({ text: c.inputFormat, color: "#5a8f5e" });
      break;
    case "output":
      if (c.outputFormat) list.push({ text: c.outputFormat, color: "#c0504d" });
      break;
    case "variable":
      if (c.operation) {
        const ops: Record<string, string> = { set: "=", append: "+=", increment: "++", transform: "转换" };
        list.push({ text: ops[c.operation] || c.operation, color: "#b06a8a" });
      }
      if (c.varName) list.push({ text: c.varName, color: "#b06a8a" });
      break;
  }

  return list;
});

const nodeStyle = computed(() => ({
  borderColor: hasError.value ? "#c0504d55" : typeInfo.value.color + "35",
}));

const handleStyle = computed(() => ({
  width: "10px",
  height: "10px",
  background: typeInfo.value.color,
  border: "2px solid " + typeInfo.value.color + "50",
}));
</script>

<style scoped>
.custom-node {
  min-width: 180px; max-width: 240px;
  background: var(--bg-raised);
  border: 2px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: var(--font-body);
  position: relative;
}
.custom-node:hover, .custom-node.selected {
  box-shadow: var(--shadow-lg);
}
.custom-node.has-error {
  border-color: rgba(192, 80, 77, 0.4);
}
.error-indicator {
  position: absolute; top: -6px; right: -6px;
  width: 20px; height: 20px;
  background: #c0504d; color: #fff;
  border-radius: 50%; font-size: 11px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px rgba(192, 80, 77, 0.3);
  z-index: 5;
}
.node-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
}
.node-icon { font-size: 16px; }
.node-label { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.node-body { padding: 6px 14px 12px; }
.node-type-text { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; }
.node-desc { display: block; font-size: 11px; color: var(--text-muted); margin-top: 3px; opacity: 0.7;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
.node-badges { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.node-badge {
  display: inline-block;
  padding: 2px 7px; border-radius: 4px;
  font-size: 10px; font-weight: 600; font-family: var(--font-mono);
  letter-spacing: 0.02em; white-space: nowrap;
}
</style>
