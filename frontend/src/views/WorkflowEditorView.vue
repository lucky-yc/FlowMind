<template>
  <div class="editor-layout" @keydown="onKeyDown" tabindex="0" ref="editorRoot">
    <!-- Left: Node Palette -->
    <div class="node-palette">
      <div class="palette-header">
        <h3>节点库</h3>
      </div>
      <div class="palette-list">
        <div
          v-for="(info, type) in NODE_TYPES" :key="type"
          class="palette-item"
          draggable="true"
          @dragstart="(e) => onDragStart(e, String(type))"
        >
          <div class="pi-icon" :style="{ background: info.color + '15', color: info.color }">{{ info.icon }}</div>
          <div class="pi-info">
            <span class="pi-name">{{ info.label }}</span>
            <span class="pi-desc">{{ info.desc }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Center: Canvas -->
    <div class="editor-center">
      <div class="editor-toolbar">
        <div class="toolbar-left">
          <input class="wf-name-input" v-model="workflowName" placeholder="工作流名称" />
          <span class="badge" :class="`badge-${workflowStatus}`">{{ workflowStatus }}</span>
        </div>
        <div class="toolbar-center">
          <button class="toolbar-btn" @click="doZoomOut" title="缩小 (Ctrl+-)">−</button>
          <button class="toolbar-btn" @click="doFitView" title="适应 (Ctrl+0)">⊞</button>
          <button class="toolbar-btn" @click="doZoomIn" title="放大 (Ctrl+=)">+</button>
          <div class="toolbar-sep"></div>
          <button class="toolbar-btn" @click="undo" title="撤销 (Ctrl+Z)">↩</button>
          <button class="toolbar-btn" @click="redo" title="重做 (Ctrl+Y)">↪</button>
        </div>
        <div class="toolbar-right">
          <span class="toolbar-info" v-if="nodes.length">{{ nodes.length }} 节点 · {{ edges.length }} 连线</span>
          <button class="btn btn-sm" :disabled="saving" @click="saveWorkflow">
            {{ saving ? '保存中...' : '💾 保存' }}
          </button>
          <button class="btn btn-sm btn-primary" :disabled="running" @click="runWorkflow">
            {{ running ? '运行中...' : '▶ 运行' }}
          </button>
        </div>
      </div>

      <VueFlow
        class="flow-canvas"
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-edge-options="{ type: 'smoothstep', animated: true }"
        @connect="onConnect"
        @node-click="onNodeClick"
        @pane-click="onPaneClick"
        @edge-click="onEdgeClick"
        @dragover="onDragOver"
        @drop="onDrop"
      >
        <template #node-custom="nodeProps">
          <WorkflowNode :data="nodeProps" />
        </template>
        <Background :gap="20" :size="1" pattern-color="rgba(26,22,18,0.06)" />
        <Controls />
        <MiniMap
          :node-color="miniMapNodeColor"
          style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px;"
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

      <!-- Toast 通知 -->
      <div class="toast" v-if="toast" :class="toast.type">{{ toast.message }}</div>
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
import { ref, onMounted, watch, nextTick } from "vue";
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
import { NODE_TYPES, getDefaultConfig } from "@/types";

const route = useRoute();
const store = useWorkflowStore();
const { fitView: _fitView, zoomIn: _zoomIn, zoomOut: _zoomOut, addNodes, addEdges, removeNodes, removeEdges, getNodes, getEdges } = useVueFlow();
const doFitView = () => _fitView();
const doZoomIn = () => _zoomIn();
const doZoomOut = () => _zoomOut();

const editorRoot = ref<HTMLElement>();
const nodes = ref<any[]>([]);
const edges = ref<any[]>([]);
const selectedNode = ref<any>(null);
const workflowName = ref("");
const workflowStatus = ref("draft");
const saving = ref(false);
const running = ref(false);
const executionResult = ref<any>(null);
const workflowId = ref(Number(route.params.id));
const toast = ref<{ message: string; type: string } | null>(null);

let history: any[] = [];
let historyIdx = -1;
let historyLock = false;

function pushHistory() {
  if (historyLock) return;
  history = history.slice(0, historyIdx + 1);
  history.push(JSON.stringify({ nodes: nodes.value, edges: edges.value }));
  historyIdx = history.length - 1;
}
function undo() {
  if (historyIdx > 0) {
    historyLock = true;
    historyIdx--;
    const s = JSON.parse(history[historyIdx]);
    nodes.value = s.nodes;
    edges.value = s.edges;
    nextTick(() => { historyLock = false; });
  }
}
function redo() {
  if (historyIdx < history.length - 1) {
    historyLock = true;
    historyIdx++;
    const s = JSON.parse(history[historyIdx]);
    nodes.value = s.nodes;
    edges.value = s.edges;
    nextTick(() => { historyLock = false; });
  }
}

watch([nodes, edges], () => { pushHistory(); }, { deep: true });

/** Toast 提示 */
function showToast(message: string, type = "info") {
  toast.value = { message, type };
  setTimeout(() => { toast.value = null; }, 2500);
}

onMounted(async () => {
  // 让编辑器容器可接收键盘事件
  editorRoot.value?.focus();

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
    nodes.value = [
      { id: "start", type: "custom", position: { x: 100, y: 300 }, data: { label: "开始", node_type: "input", config: getDefaultConfig("input"), description: "工作流入口" } },
      { id: "end", type: "custom", position: { x: 700, y: 300 }, data: { label: "结束", node_type: "output", config: getDefaultConfig("output"), description: "工作流出口" } },
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
    data: { label: info.label, node_type: nodeType, config: getDefaultConfig(nodeType), description: info.desc },
  };
  addNodes([newNode]);
  showToast(`已添加 ${info.label} 节点`);
}

/** 连接验证 */
function onConnect(params: any) {
  const sourceNode = nodes.value.find((n) => n.id === params.source);
  const targetNode = nodes.value.find((n) => n.id === params.target);
  if (!sourceNode || !targetNode) return;

  const sourceType = sourceNode.data?.node_type;
  const targetType = targetNode.data?.node_type;

  // 不允许自连
  if (params.source === params.target) {
    showToast("不能连接到自身", "error");
    return;
  }

  // 输入节点只能作为源（没有入边）
  if (targetType === "input") {
    showToast("输入节点不能作为连接目标", "error");
    return;
  }

  // 输出节点只能作为目标（没有出边）
  if (sourceType === "output") {
    showToast("输出节点不能作为连接源", "error");
    return;
  }

  // 检查是否已存在相同连线
  const exists = edges.value.some(
    (e) => e.source === params.source && e.target === params.target
  );
  if (exists) {
    showToast("该连接已存在", "error");
    return;
  }

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

/** 点击边显示信息 */
function onEdgeClick({ edge }: any) {
  showToast(`连线: ${edge.source} → ${edge.target}`, "info");
}

function onNodeUpdate(updatedNode: any) {
  const idx = nodes.value.findIndex((n) => n.id === updatedNode.id);
  if (idx >= 0) {
    nodes.value[idx] = { ...nodes.value[idx], data: { ...updatedNode.data } };
    // 同步 selectedNode
    if (selectedNode.value?.id === updatedNode.id) {
      selectedNode.value = nodes.value[idx];
    }
  }
}

function deleteSelectedNode() {
  if (!selectedNode.value) return;
  const id = selectedNode.value.id;
  // 同时删除关联的边
  const relatedEdges = edges.value.filter((e) => e.source === id || e.target === id);
  if (relatedEdges.length) {
    removeEdges(relatedEdges.map((e) => e.id));
  }
  removeNodes([id]);
  selectedNode.value = null;
  showToast("节点已删除");
}

/** 键盘快捷键 */
function onKeyDown(e: KeyboardEvent) {
  // Delete / Backspace 删除选中节点
  if ((e.key === "Delete" || e.key === "Backspace") && selectedNode.value) {
    // 避免在 input/textarea 中触发
    const tag = (e.target as HTMLElement)?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
    e.preventDefault();
    deleteSelectedNode();
    return;
  }

  // Ctrl+Z 撤销
  if (e.key === "z" && (e.ctrlKey || e.metaKey) && !e.shiftKey) {
    const tag = (e.target as HTMLElement)?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    e.preventDefault();
    undo();
    return;
  }

  // Ctrl+Y 或 Ctrl+Shift+Z 重做
  if ((e.key === "y" && (e.ctrlKey || e.metaKey)) || (e.key === "z" && (e.ctrlKey || e.metaKey) && e.shiftKey)) {
    const tag = (e.target as HTMLElement)?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    e.preventDefault();
    redo();
    return;
  }

  // Escape 取消选中
  if (e.key === "Escape") {
    selectedNode.value = null;
  }
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
    showToast("保存成功 ✓", "success");
  } catch (e) {
    console.error(e);
    showToast("保存失败", "error");
  }
  saving.value = false;
}

async function runWorkflow() {
  running.value = true;
  try {
    await saveWorkflow();
    if (workflowId.value) {
      executionResult.value = await store.executeWorkflow(workflowId.value);
      showToast("执行完成", "success");
    }
  } catch (e) {
    console.error(e);
    showToast("执行失败", "error");
  }
  running.value = false;
}

function miniMapNodeColor(node: any) {
  const type = node.data?.node_type || node.type;
  return NODE_TYPES[type]?.color || "#9a8e80";
}
</script>

<style scoped>
.editor-layout { display: flex; height: calc(100vh - var(--header-height)); margin: -28px; outline: none; }

/* Node Palette */
.node-palette {
  width: 240px; flex-shrink: 0;
  display: flex; flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-base);
}
.palette-header { padding: 16px 18px; border-bottom: 1px solid var(--border-subtle); }
.palette-header h3 { font-family: var(--font-display); font-size: 16px; font-weight: 400; font-style: italic; color: var(--text-secondary); }
.palette-list { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 6px; }
.palette-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: var(--radius-md);
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  cursor: grab; transition: all 0.2s; user-select: none;
}
.palette-item:hover {
  border-color: var(--border-accent);
  box-shadow: var(--shadow-sm);
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
.toolbar-info { font-size: 11px; color: var(--text-muted); margin-right: 4px; }
.wf-name-input {
  background: transparent; border: 1px solid transparent;
  color: var(--text-primary); font-family: var(--font-display);
  font-size: 18px; font-weight: 400; font-style: italic; padding: 4px 8px; border-radius: var(--radius-sm);
  width: 200px; transition: border-color 0.2s;
}
.wf-name-input:focus { border-color: var(--border-accent); background: var(--bg-surface); outline: none; }
.toolbar-btn {
  width: 32px; height: 32px; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm);
  background: var(--bg-surface); color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
  transition: all 0.2s;
}
.toolbar-btn:hover { background: var(--bg-hover); border-color: var(--border-accent); color: var(--text-primary); }
.toolbar-sep { width: 1px; height: 20px; background: var(--border-subtle); margin: 0 4px; }
.flow-canvas { flex: 1; background: var(--bg-page); }

/* Execution Overlay */
.exec-overlay {
  position: absolute; top: 60px; right: 16px; width: 360px; max-height: 400px;
  border-radius: var(--radius-lg); overflow: hidden; z-index: 10;
  box-shadow: var(--shadow-lg);
}
.exec-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid var(--border-subtle); }
.exec-header h4 { font-family: var(--font-display); font-size: 16px; font-weight: 400; font-style: italic; }
.close-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 16px; }
.exec-body { padding: 18px; }
.exec-status-big { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
.exec-status-big.completed { color: var(--green); }
.exec-status-big.failed { color: var(--red); }
.exec-output {
  background: var(--bg-surface); padding: 12px; border-radius: var(--radius-md);
  font-family: var(--font-mono); font-size: 12px; color: var(--text-secondary);
  max-height: 200px; overflow-y: auto; white-space: pre-wrap;
}

/* Toast */
.toast {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  padding: 10px 20px; border-radius: var(--radius-md);
  font-size: 13px; font-weight: 500; z-index: 20;
  box-shadow: var(--shadow-lg);
  animation: toast-in 0.3s ease;
}
.toast.info { background: var(--bg-base); color: var(--text-primary); border: 1px solid var(--border-subtle); }
.toast.success { background: rgba(90,143,94,0.1); color: var(--green); border: 1px solid rgba(90,143,94,0.25); }
.toast.error { background: rgba(192,80,77,0.1); color: var(--red); border: 1px solid rgba(192,80,77,0.25); }
@keyframes toast-in { from { opacity: 0; transform: translateX(-50%) translateY(10px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
</style>
