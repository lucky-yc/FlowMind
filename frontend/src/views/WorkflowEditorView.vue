<template>
  <div class="editor-layout">
    <!-- Left: Node Palette -->
    <div class="node-palette glass">
      <div class="palette-header">
        <h3>节点库</h3>
      </div>
      <div class="palette-list">
        <div
          v-for="(info, key) in NODE_TYPES"
          :key="key"
          class="palette-item"
          draggable="true"
          @dragstart="onDragStart($event, String(key))"
        >
          <span class="pi-icon" :style="{ background: info.color + '20', color: info.color }">{{ info.icon }}</span>
          <div class="pi-info">
            <span class="pi-name">{{ info.label }}</span>
            <span class="pi-desc">{{ info.desc }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Center: Canvas -->
    <div class="editor-center">
      <div class="editor-toolbar glass">
        <div class="toolbar-left">
          <input
            class="wf-name-input"
            v-model="workflowName"
            @blur="saveWorkflow"
            placeholder="工作流名称"
          />
          <span class="wf-status badge" :class="`badge-${workflowStatus}`">{{ workflowStatus }}</span>
        </div>
        <div class="toolbar-center">
          <button class="toolbar-btn" @click="undo" title="撤销">↩</button>
          <button class="toolbar-btn" @click="redo" title="重做">↪</button>
          <div class="toolbar-sep"></div>
          <button class="toolbar-btn" @click="doZoomIn" title="放大">＋</button>
          <button class="toolbar-btn" @click="doZoomOut" title="缩小">－</button>
          <button class="toolbar-btn" @click="doFitView" title="适应画布">⊞</button>
        </div>
        <div class="toolbar-right">
          <button class="btn btn-sm" @click="saveWorkflow" :disabled="saving">
            {{ saving ? "保存中..." : "💾 保存" }}
          </button>
          <button class="btn btn-sm btn-primary" @click="runWorkflow" :disabled="running">
            {{ running ? "执行中..." : "▶ 运行" }}
          </button>
        </div>
      </div>

      <VueFlow
        ref="vueFlowRef"
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-viewport="{ zoom: 1, x: 0, y: 0 }"
        :min-zoom="0.2"
        :max-zoom="4"
        :snap-to-grid="true"
        :snap-grid="[20, 20]"
        class="flow-canvas"
        @node-click="onNodeClick"
        @pane-click="onPaneClick"
        @connect="onConnect"
        @drop="onDrop"
        @dragover="onDragOver"
      >
        <template #node-custom="nodeProps">
          <WorkflowNode :data="nodeProps" />
        </template>
        <Background :gap="20" :size="1" pattern-color="rgba(99,179,237,0.05)" />
        <Controls position="bottom-left" />
        <MiniMap
          position="bottom-right"
          :node-color="miniMapNodeColor"
          style="background: var(--bg-raised); border: 1px solid var(--border-subtle); border-radius: 8px;"
        />
      </VueFlow>

      <!-- Execution Result Overlay -->
      <div class="exec-overlay glass" v-if="executionResult">
        <div class="exec-header">
          <h4>执行结果</h4>
          <button class="close-btn" @click="executionResult = null">✕</button>
        </div>
        <div class="exec-body">
          <div class="exec-status-big" :class="executionResult.status">
            {{ executionResult.status === 'completed' ? '✓ 执行成功' : '✕ 执行失败' }}
          </div>
          <pre class="exec-output">{{ JSON.stringify(executionResult.output_data, null, 2) }}</pre>
        </div>
      </div>
    </div>

    <!-- Right: Config Panel -->
    <NodeConfigPanel
      :node="selectedNode"
      @update="onNodeUpdate"
      @close="selectedNode = null"
      @delete="deleteSelectedNode"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { VueFlow, useVueFlow } from "@vue-flow/core";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import { MiniMap } from "@vue-flow/minimap";
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";
import "@vue-flow/controls/dist/style.css";
import "@vue-flow/minimap/dist/style.css";
import WorkflowNode from "@/components/WorkflowNode.vue";
import NodeConfigPanel from "@/components/NodeConfigPanel.vue";
import { useWorkflowStore } from "@/stores/workflow";
import { NODE_TYPES } from "@/types";

const route = useRoute();
const store = useWorkflowStore();
const { fitView: _fitView, zoomIn: _zoomIn, zoomOut: _zoomOut, addNodes, addEdges, removeNodes } = useVueFlow();
const doFitView = () => _fitView();
const doZoomIn = () => _zoomIn();
const doZoomOut = () => _zoomOut();

const nodes = ref<any[]>([]);
const edges = ref<any[]>([]);
const selectedNode = ref<any>(null);
const workflowName = ref("");
const workflowStatus = ref("draft");
const saving = ref(false);
const running = ref(false);
const executionResult = ref<any>(null);
const workflowId = ref(Number(route.params.id));

let history: any[] = [];
let historyIdx = -1;

function pushHistory() {
  history = history.slice(0, historyIdx + 1);
  history.push(JSON.stringify({ nodes: nodes.value, edges: edges.value }));
  historyIdx = history.length - 1;
}
function undo() {
  if (historyIdx > 0) { historyIdx--; const s = JSON.parse(history[historyIdx]); nodes.value = s.nodes; edges.value = s.edges; }
}
function redo() {
  if (historyIdx < history.length - 1) { historyIdx++; const s = JSON.parse(history[historyIdx]); nodes.value = s.nodes; edges.value = s.edges; }
}

watch([nodes, edges], () => { pushHistory(); }, { deep: true });

onMounted(async () => {
  if (workflowId.value) {
    await store.fetchWorkflow(workflowId.value);
    const wf = store.currentWorkflow;
    if (wf) {
      workflowName.value = wf.name;
      workflowStatus.value = wf.status;
      nodes.value = (wf.nodes || []).map((n: any) => ({
        ...n,
        type: "custom",
        data: { ...n.data, node_type: n.type },
      }));
      edges.value = wf.edges || [];
    }
  } else {
    // Default start/end nodes for new workflow
    nodes.value = [
      { id: "start", type: "custom", position: { x: 100, y: 300 }, data: { label: "开始", node_type: "input", config: {}, description: "工作流入口" } },
      { id: "end", type: "custom", position: { x: 700, y: 300 }, data: { label: "结束", node_type: "output", config: {}, description: "工作流出口" } },
    ];
    workflowName.value = "未命名工作流";
  }
  pushHistory();
});

let nodeIdCounter = 100;
function onDragStart(event: DragEvent, nodeType: string) {
  event.dataTransfer?.setData("application/nodeType", nodeType);
  event.dataTransfer!.effectAllowed = "move";
}

function onDragOver(event: DragEvent) {
  event.preventDefault();
  event.dataTransfer!.dropEffect = "move";
}

function onDrop(event: DragEvent) {
  const nodeType = event.dataTransfer?.getData("application/nodeType");
  if (!nodeType) return;
  const info = NODE_TYPES[nodeType];
  if (!info) return;
  const bounds = (event.target as Element).closest(".vue-flow")?.getBoundingClientRect();
  if (!bounds) return;
  const position = { x: event.clientX - bounds.left - 90, y: event.clientY - bounds.top - 25 };
  const newNode = {
    id: `node_${++nodeIdCounter}`,
    type: "custom",
    position,
    data: { label: info.label, node_type: nodeType, config: {}, description: info.desc },
  };
  addNodes([newNode]);
}

function onConnect(params: any) {
  const edge = {
    id: `e_${params.source}_${params.target}`,
    source: params.source,
    target: params.target,
    sourceHandle: params.sourceHandle,
    targetHandle: params.targetHandle,
    animated: true,
    type: "smoothstep",
  };
  addEdges([edge]);
}

function onNodeClick({ node }: any) {
  selectedNode.value = node;
}

function onPaneClick() {
  selectedNode.value = null;
}

function onNodeUpdate(updatedNode: any) {
  const idx = nodes.value.findIndex((n) => n.id === updatedNode.id);
  if (idx >= 0) {
    nodes.value[idx] = { ...nodes.value[idx], data: { ...updatedNode.data } };
  }
}

function deleteSelectedNode() {
  if (!selectedNode.value) return;
  removeNodes([selectedNode.value.id]);
  selectedNode.value = null;
}

async function saveWorkflow() {
  saving.value = true;
  try {
    const payload = {
      name: workflowName.value,
      nodes: nodes.value.map((n) => ({ id: n.id, type: n.data.node_type, position: n.position, data: n.data })),
      edges: edges.value,
    };
    if (workflowId.value) {
      await store.updateWorkflow(workflowId.value, payload);
    } else {
      const wf = await store.createWorkflow(payload);
      workflowId.value = wf.id;
    }
  } catch (e) { console.error(e); }
  saving.value = false;
}

async function runWorkflow() {
  running.value = true;
  try {
    await saveWorkflow();
    if (workflowId.value) {
      executionResult.value = await store.executeWorkflow(workflowId.value);
    }
  } catch (e) { console.error(e); }
  running.value = false;
}

function miniMapNodeColor(node: any) {
  const type = node.data?.node_type || node.type;
  return NODE_TYPES[type]?.color || "#64748b";
}
</script>

<style scoped>
.editor-layout { display: flex; height: calc(100vh - var(--header-height)); margin: -28px; }

/* Node Palette */
.node-palette {
  width: 240px; flex-shrink: 0;
  display: flex; flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-base);
}
.palette-header { padding: 16px 18px; border-bottom: 1px solid var(--border-subtle); }
.palette-header h3 { font-size: 14px; font-weight: 600; color: var(--text-secondary); }
.palette-list { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 6px; }
.palette-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: var(--radius-md);
  background: var(--bg-raised); border: 1px solid var(--border-subtle);
  cursor: grab; transition: all 0.2s; user-select: none;
}
.palette-item:hover {
  border-color: var(--border-accent);
  box-shadow: 0 0 16px var(--accent-glow);
  transform: translateX(4px);
}
.palette-item:active { cursor: grabbing; transform: scale(0.97); }
.pi-icon {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.pi-info { display: flex; flex-direction: column; min-width: 0; }
.pi-name { font-size: 13px; font-weight: 600; }
.pi-desc { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Center Canvas */
.editor-center { flex: 1; display: flex; flex-direction: column; position: relative; }
.editor-toolbar {
  height: 48px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px; border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-base); flex-shrink: 0;
}
.toolbar-left, .toolbar-center, .toolbar-right { display: flex; align-items: center; gap: 8px; }
.wf-name-input {
  background: transparent; border: 1px solid transparent;
  color: var(--text-primary); font-family: var(--font-display);
  font-size: 16px; font-weight: 600; padding: 4px 8px; border-radius: var(--radius-sm);
  width: 200px; transition: border-color 0.2s;
}
.wf-name-input:focus { border-color: var(--border-accent); background: var(--bg-raised); outline: none; }
.toolbar-btn {
  width: 32px; height: 32px; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm);
  background: var(--bg-surface); color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
  transition: all 0.2s;
}
.toolbar-btn:hover { background: var(--bg-hover); border-color: var(--border-accent); color: var(--text-primary); }
.toolbar-sep { width: 1px; height: 20px; background: var(--border-subtle); margin: 0 4px; }
.flow-canvas { flex: 1; background: var(--bg-deepest); }

/* Execution Overlay */
.exec-overlay {
  position: absolute; top: 60px; right: 16px; width: 360px; max-height: 400px;
  border-radius: var(--radius-lg); overflow: hidden; z-index: 10;
  background: rgba(17,24,39,0.9); backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle); box-shadow: var(--shadow-lg);
}
.exec-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid var(--border-subtle); }
.exec-header h4 { font-size: 14px; font-weight: 600; }
.close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 16px; }
.exec-body { padding: 18px; }
.exec-status-big { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
.exec-status-big.completed { color: var(--green); }
.exec-status-big.failed { color: var(--red); }
.exec-output {
  background: var(--bg-deep); padding: 12px; border-radius: var(--radius-md);
  font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary);
  max-height: 200px; overflow-y: auto; white-space: pre-wrap;
}
</style>
