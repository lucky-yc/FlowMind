<template>
  <div class="custom-node" :class="{ selected: data.selected }" :style="nodeStyle">
    <div class="node-header" :style="{ background: typeInfo.color + '10', borderBottom: `1px solid ${typeInfo.color}25` }">
      <span class="node-icon">{{ typeInfo.icon }}</span>
      <span class="node-label">{{ nodeData.label }}</span>
    </div>
    <div class="node-body">
      <span class="node-type-text">{{ typeInfo.label }}</span>
      <span class="node-desc" v-if="nodeData.description">{{ nodeData.description }}</span>
    </div>
    <!-- Handles -->
    <Handle v-if="nodeType !== 'input'" type="target" :position="Position.Left" :style="handleStyle" />
    <Handle v-if="nodeType !== 'output'" type="source" :position="Position.Right" :style="handleStyle" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Handle, Position } from "@vue-flow/core";
import { NODE_TYPES } from "@/types";

const props = defineProps<{ data: any }>();

const nodeData = computed(() => props.data?.data || {});
const nodeType = computed(() => nodeData.value.node_type || "llm");
const typeInfo = computed(() => NODE_TYPES[nodeType.value] || NODE_TYPES.llm);

const nodeStyle = computed(() => ({
  borderColor: typeInfo.value.color + "35",
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
  min-width: 180px;
  background: var(--bg-raised);
  border: 2px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: var(--font-body);
}
.custom-node:hover, .custom-node.selected {
  box-shadow: var(--shadow-lg);
}
.node-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
}
.node-icon { font-size: 16px; }
.node-label { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.node-body { padding: 8px 14px 12px; }
.node-type-text { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.node-desc { display: block; font-size: 11px; color: var(--text-muted); margin-top: 4px; opacity: 0.7; }
</style>
