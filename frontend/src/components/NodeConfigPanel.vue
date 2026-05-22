<template>
  <div class="config-panel" v-if="node">
    <div class="panel-header">
      <h3>节点配置</h3>
      <button class="close-btn" @click="$emit('close')">✕</button>
    </div>
    <div class="panel-body">
      <!-- 通用字段 -->
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

      <div class="section-divider"></div>

      <!-- ═══════ LLM 配置 ═══════ -->
      <template v-if="nodeType === 'llm'">
        <div class="config-section">
          <label>模型</label>
          <select class="input" v-model="localData.config.model" @change="emitUpdate" v-if="modelStore.briefModels.length">
            <option v-for="m in modelStore.briefModels" :key="m.id" :value="m.model_id">
              {{ m.name }} ({{ m.provider }})
            </option>
          </select>
          <select class="input" v-model="localData.config.model" @change="emitUpdate" v-else>
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="claude-3-opus">Claude 3 Opus</option>
            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
            <option value="claude-3-haiku">Claude 3 Haiku</option>
          </select>
        </div>
        <div class="config-section">
          <label>System Prompt</label>
          <textarea class="input" v-model="localData.config.systemPrompt" @change="emitUpdate" rows="3" placeholder="系统提示词..."></textarea>
        </div>
        <div class="config-section">
          <label>User Prompt 模板</label>
          <textarea class="input mono" v-model="localData.config.userPrompt" @change="emitUpdate" rows="4" placeholder="用户提示词，可用 {{变量名}} 引用上游数据"></textarea>
          <span class="input-hint">支持 {{variable}} 语法引用工作流变量</span>
        </div>
        <div class="config-section">
          <label>Temperature: {{ (localData.config.temperature || 70) / 100 }}</label>
          <div class="range-row">
            <span class="range-label">精确</span>
            <input type="range" min="0" max="100" v-model.number="localData.config.temperature" @change="emitUpdate" class="range-slider" />
            <span class="range-label">创意</span>
          </div>
        </div>
        <div class="config-row">
          <div class="config-section flex-1">
            <label>Max Tokens</label>
            <input class="input" type="number" min="1" max="128000" v-model.number="localData.config.maxTokens" @change="emitUpdate" />
          </div>
          <div class="config-section flex-1">
            <label>超时 (秒)</label>
            <input class="input" type="number" min="5" max="300" v-model.number="localData.config.timeout" @change="emitUpdate" />
          </div>
        </div>
        <div class="config-section">
          <label class="checkbox-label">
            <input type="checkbox" v-model="localData.config.jsonMode" @change="emitUpdate" />
            <span>JSON 输出模式</span>
          </label>
        </div>
      </template>

      <!-- ═══════ HTTP 配置 ═══════ -->
      <template v-if="nodeType === 'http'">
        <div class="config-section">
          <label>请求方法</label>
          <div class="method-selector">
            <button v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m"
              class="method-btn" :class="{ active: localData.config.method === m, [m.toLowerCase()]: true }"
              @click="localData.config.method = m; emitUpdate()">{{ m }}</button>
          </div>
        </div>
        <div class="config-section">
          <label>URL</label>
          <input class="input mono" v-model="localData.config.url" @change="emitUpdate" placeholder="https://api.example.com/path" />
          <span class="input-hint">支持 {{variable}} 语法</span>
        </div>
        <div class="config-section">
          <label>请求体类型</label>
          <select class="input" v-model="localData.config.bodyType" @change="emitUpdate">
            <option value="json">JSON</option>
            <option value="form">Form Data</option>
            <option value="raw">Raw Text</option>
            <option value="none">无</option>
          </select>
        </div>
        <div class="config-section" v-if="localData.config.bodyType !== 'none'">
          <label>请求体</label>
          <textarea class="input mono" v-model="localData.config.body" @change="emitUpdate" rows="4" :placeholder="bodyPlaceholder"></textarea>
        </div>
        <div class="config-section">
          <label>Headers (JSON)</label>
          <textarea class="input mono" v-model="localData.config.headers" @change="emitUpdate" rows="3" placeholder='{"Authorization": "Bearer ..."}'></textarea>
        </div>
        <div class="config-row">
          <div class="config-section flex-1">
            <label>超时 (秒)</label>
            <input class="input" type="number" min="1" max="300" v-model.number="localData.config.timeout" @change="emitUpdate" />
          </div>
          <div class="config-section flex-1">
            <label>重试次数</label>
            <input class="input" type="number" min="0" max="10" v-model.number="localData.config.retryCount" @change="emitUpdate" />
          </div>
        </div>
        <div class="config-section">
          <label class="checkbox-label">
            <input type="checkbox" v-model="localData.config.followRedirects" @change="emitUpdate" />
            <span>跟随重定向</span>
          </label>
        </div>
      </template>

      <!-- ═══════ 条件分支配置 ═══════ -->
      <template v-if="nodeType === 'condition'">
        <div class="config-section">
          <label>条件表达式</label>
          <input class="input mono" v-model="localData.config.expression" @change="emitUpdate" placeholder="result.status" />
          <span class="input-hint">引用上游输出的字段路径</span>
        </div>
        <div class="config-section">
          <label>比较运算符</label>
          <select class="input" v-model="localData.config.operator" @change="emitUpdate">
            <option value="equals">等于 (==)</option>
            <option value="not_equals">不等于 (!=)</option>
            <option value="contains">包含</option>
            <option value="not_contains">不包含</option>
            <option value="gt">大于 (>)</option>
            <option value="lt">小于 (<)</option>
            <option value="gte">大于等于 (>=)</option>
            <option value="lte">小于等于 (<=)</option>
            <option value="is_empty">为空</option>
            <option value="is_not_empty">不为空</option>
            <option value="regex">正则匹配</option>
          </select>
        </div>
        <div class="config-section" v-if="!['is_empty', 'is_not_empty'].includes(localData.config.operator)">
          <label>比较值</label>
          <input class="input" v-model="localData.config.value" @change="emitUpdate" placeholder="比较的目标值" />
        </div>
        <div class="config-section" v-if="['contains','not_contains','equals','not_equals','regex'].includes(localData.config.operator)">
          <label class="checkbox-label">
            <input type="checkbox" v-model="localData.config.caseSensitive" @change="emitUpdate" />
            <span>区分大小写</span>
          </label>
        </div>
        <div class="config-hint-box">
          <span class="hint-icon">💡</span>
          <span>条件为真走 <strong>True</strong> 分支，为假走 <strong>False</strong> 分支。请确保连接了对应的下游节点。</span>
        </div>
      </template>

      <!-- ═══════ 代码执行配置 ═══════ -->
      <template v-if="nodeType === 'code'">
        <div class="config-row">
          <div class="config-section flex-1">
            <label>语言</label>
            <select class="input" v-model="localData.config.language" @change="emitUpdate">
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
            </select>
          </div>
          <div class="config-section flex-1">
            <label>超时 (秒)</label>
            <input class="input" type="number" min="5" max="120" v-model.number="localData.config.timeout" @change="emitUpdate" />
          </div>
        </div>
        <div class="config-section">
          <label>输出变量名</label>
          <input class="input mono" v-model="localData.config.outputVar" @change="emitUpdate" placeholder="result" />
          <span class="input-hint">代码中赋值此变量将作为节点输出</span>
        </div>
        <div class="config-section">
          <label>代码</label>
          <textarea class="input mono code-editor" v-model="localData.config.code" @change="emitUpdate" rows="10"
            :placeholder="codePlaceholder" spellcheck="false"></textarea>
        </div>
        <div class="config-hint-box">
          <span class="hint-icon">📝</span>
          <span>{{ localData.config.language === 'python' ? 'Python: 使用 `inputs` 字典访问上游数据，将结果赋给 `' + (localData.config.outputVar || 'result') + '`' : 'JS: 使用 `inputs` 对象访问上游数据，将结果赋给 `' + (localData.config.outputVar || 'result') + '`' }}</span>
        </div>
      </template>

      <!-- ═══════ 工具调用配置 ═══════ -->
      <template v-if="nodeType === 'tool'">
        <div class="config-section">
          <label>工具名称</label>
          <input class="input" v-model="localData.config.toolName" @change="emitUpdate" placeholder="search / calculator / ..." />
        </div>
        <div class="config-section">
          <label>参数 (JSON)</label>
          <textarea class="input mono" v-model="localData.config.parametersStr" @change="onParamsChange" rows="4"
            placeholder='{"query": "{{input}}"}'></textarea>
          <span class="input-hint">支持 {{variable}} 语法引用上游输出</span>
        </div>
        <div class="config-row">
          <div class="config-section flex-1">
            <label>超时 (秒)</label>
            <input class="input" type="number" min="5" max="300" v-model.number="localData.config.timeout" @change="emitUpdate" />
          </div>
          <div class="config-section flex-1">
            <label>重试次数</label>
            <input class="input" type="number" min="0" max="10" v-model.number="localData.config.retryCount" @change="emitUpdate" />
          </div>
        </div>
        <div class="config-section" v-if="localData.config.retryCount > 0">
          <label>重试间隔 (秒)</label>
          <input class="input" type="number" min="1" max="60" v-model.number="localData.config.retryDelay" @change="emitUpdate" />
        </div>
      </template>

      <!-- ═══════ 输入节点配置 ═══════ -->
      <template v-if="nodeType === 'input'">
        <div class="config-section">
          <label>输入格式</label>
          <select class="input" v-model="localData.config.inputFormat" @change="emitUpdate">
            <option value="text">纯文本</option>
            <option value="json">JSON</option>
            <option value="file">文件</option>
          </select>
        </div>
        <div class="config-section" v-if="localData.config.inputFormat === 'json'">
          <label>输入 Schema (JSON)</label>
          <textarea class="input mono" v-model="localData.config.schemaStr" @change="onSchemaChange" rows="4"
            placeholder='[{"name":"query","type":"string","required":true}]'></textarea>
        </div>
        <div class="config-section">
          <label>默认值</label>
          <textarea class="input" v-model="localData.config.defaultValue" @change="emitUpdate" rows="2" placeholder="当无外部输入时使用此默认值"></textarea>
        </div>
      </template>

      <!-- ═══════ 输出节点配置 ═══════ -->
      <template v-if="nodeType === 'output'">
        <div class="config-section">
          <label>输出格式</label>
          <select class="input" v-model="localData.config.outputFormat" @change="emitUpdate">
            <option value="json">JSON</option>
            <option value="text">纯文本</option>
            <option value="markdown">Markdown</option>
          </select>
        </div>
        <div class="config-section">
          <label>输出模板</label>
          <textarea class="input mono" v-model="localData.config.template" @change="emitUpdate" rows="4"
            placeholder="使用 {{field}} 引用上游节点输出字段"></textarea>
          <span class="input-hint">留空则直接透传上游完整输出</span>
        </div>
        <div class="config-section">
          <label>输出字段映射</label>
          <div class="field-mapping" v-for="(field, idx) in localData.config.fields" :key="idx">
            <input class="input mono field-input" v-model="field.from" @change="emitUpdate" placeholder="上游字段" />
            <span class="field-arrow">→</span>
            <input class="input mono field-input" v-model="field.to" @change="emitUpdate" placeholder="输出字段" />
            <button class="field-remove-btn" @click="removeField(idx)">✕</button>
          </div>
          <button class="btn btn-sm add-field-btn" @click="addField">+ 添加字段映射</button>
        </div>
      </template>

      <!-- ═══════ 变量操作配置 ═══════ -->
      <template v-if="nodeType === 'variable'">
        <div class="config-section">
          <label>操作类型</label>
          <select class="input" v-model="localData.config.operation" @change="emitUpdate">
            <option value="set">赋值</option>
            <option value="append">追加</option>
            <option value="increment">自增</option>
            <option value="transform">转换</option>
          </select>
        </div>
        <div class="config-section">
          <label>变量名</label>
          <input class="input mono" v-model="localData.config.varName" @change="emitUpdate" placeholder="myVariable" />
          <span class="input-hint" :class="{ 'input-error': varNameError }">{{ varNameError || '字母/下划线开头，可含数字' }}</span>
        </div>
        <div class="config-section" v-if="['set', 'append'].includes(localData.config.operation)">
          <label>变量值</label>
          <input class="input" v-model="localData.config.varValue" @change="emitUpdate" placeholder="值或 {{表达式}}" />
        </div>
        <div class="config-section">
          <label>变量类型</label>
          <select class="input" v-model="localData.config.varType" @change="emitUpdate">
            <option value="string">字符串</option>
            <option value="number">数字</option>
            <option value="boolean">布尔</option>
            <option value="array">数组</option>
            <option value="object">对象</option>
          </select>
        </div>
      </template>

      <!-- 校验错误 -->
      <div class="validation-error" v-if="validationError">
        <span class="error-icon">⚠️</span>
        <span>{{ validationError }}</span>
      </div>
    </div>

    <div class="panel-footer">
      <button class="btn btn-danger btn-sm" @click="$emit('delete')">🗑 删除节点</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, computed } from "vue";
import { NODE_TYPES, getDefaultConfig, validateNodeConfig } from "@/types";
import { useModelStore } from "@/stores/model";

const modelStore = useModelStore();

const props = defineProps<{ node: any }>();
const emit = defineEmits(["update", "close", "delete"]);

/** 正确的类型判断：从 node.data.node_type 获取 */
const nodeType = computed(() => props.node?.data?.node_type || "llm");
const typeInfo = computed(() => NODE_TYPES[nodeType.value] || NODE_TYPES.llm);

const localData = reactive({
  label: "",
  description: "",
  config: {} as Record<string, any>,
});

/** 同步节点数据到本地 */
watch(() => props.node, (n) => {
  // 当 LLM 节点首次加载时，确保简要模型列表已拉取
  if (n?.data?.node_type === "llm" && !modelStore.briefModels.length) {
    modelStore.fetchBriefModels();
  }
  if (!n) return;
  localData.label = n.data?.label || "";
  localData.description = n.data?.description || "";
  const incoming = n.data?.config || {};
  const defaults = getDefaultConfig(nodeType.value);
  // 合并默认值，不覆盖已有配置
  localData.config = { ...defaults, ...incoming };

  // tool 节点：parameters 对象转字符串用于编辑
  if (nodeType.value === "tool" && localData.config.parameters && !localData.config.parametersStr) {
    localData.config.parametersStr = JSON.stringify(localData.config.parameters, null, 2);
  }
  // input 节点：schema 数组转字符串
  if (nodeType.value === "input" && localData.config.inputSchema && !localData.config.schemaStr) {
    localData.config.schemaStr = JSON.stringify(localData.config.inputSchema, null, 2);
  }
}, { immediate: true, deep: true });

/** 校验 */
const validationError = computed(() => validateNodeConfig(nodeType.value, localData.config));

/** 变量名校验 */
const varNameError = computed(() => {
  if (nodeType.value !== "variable") return "";
  const name = localData.config.varName;
  if (!name) return "";
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(name)) return "变量名格式不合法";
  return "";
});

/** body placeholder 根据类型变化 */
const bodyPlaceholder = computed(() => {
  const t = localData.config.bodyType;
  if (t === "json") return '{"key": "value"}';
  if (t === "form") return "key1=value1&key2=value2";
  return "请求体内容...";
});

const codePlaceholder = computed(() => {
  const v = localData.config.outputVar || "result";
  return localData.config.language === "python"
    ? `# 访问上游输入\nquery = inputs.get("query", "")\n\n# 处理逻辑\n${v} = {"answer": query.upper()}`
    : `// 访问上游输入\nconst query = inputs.query || "";\n\n// 处理逻辑\nconst ${v} = { answer: query.toUpperCase() };`;
});

/** 发送更新 */
function emitUpdate() {
  emit("update", {
    ...props.node,
    data: {
      ...props.node.data,
      label: localData.label,
      description: localData.description,
      config: { ...localData.config },
    },
  });
}

/** tool 参数 JSON 解析 */
function onParamsChange() {
  try {
    localData.config.parameters = localData.config.parametersStr
      ? JSON.parse(localData.config.parametersStr)
      : {};
  } catch (_e) {
    // 保持原文，让校验处理
  }
  emitUpdate();
}

/** input schema JSON 解析 */
function onSchemaChange() {
  try {
    localData.config.inputSchema = localData.config.schemaStr
      ? JSON.parse(localData.config.schemaStr)
      : [];
  } catch (_e) {
    // 保持原文
  }
  emitUpdate();
}

/** 输出字段映射操作 */
function addField() {
  if (!localData.config.fields) localData.config.fields = [];
  localData.config.fields.push({ from: "", to: "" });
  emitUpdate();
}
function removeField(idx: number) {
  localData.config.fields.splice(idx, 1);
  emitUpdate();
}
</script>

<style scoped>
.config-panel {
  width: 340px; height: 100%;
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
.config-section { margin-bottom: 14px; }
.config-section label { display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.06em; }
.node-type-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 12px; border-radius: var(--radius-sm);
  font-size: 13px; font-weight: 600;
}
.section-divider { height: 1px; background: var(--border-subtle); margin: 12px 0 16px; }
.config-row { display: flex; gap: 12px; }
.flex-1 { flex: 1; }

/* Range slider */
.range-row { display: flex; align-items: center; gap: 8px; }
.range-label { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
.range-slider {
  flex: 1; height: 4px; -webkit-appearance: none; appearance: none;
  background: var(--bg-active); border-radius: 2px; outline: none;
}
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 16px; height: 16px;
  border-radius: 50%; background: var(--accent); cursor: pointer;
  box-shadow: 0 0 6px var(--accent-glow);
}

/* Method selector */
.method-selector { display: flex; gap: 4px; }
.method-btn {
  padding: 5px 10px; border: 1px solid var(--border-default); border-radius: var(--radius-sm);
  background: var(--bg-surface); color: var(--text-secondary); font-size: 11px; font-weight: 700;
  cursor: pointer; transition: all 0.15s; font-family: var(--font-mono);
}
.method-btn:hover { border-color: var(--border-accent); }
.method-btn.active { color: #fff; border-color: transparent; }
.method-btn.active.get { background: #5a8f5e; }
.method-btn.active.post { background: #c9a96e; }
.method-btn.active.put { background: #6a8fba; }
.method-btn.active.delete { background: #c0504d; }
.method-btn.active.patch { background: #7c6fa0; }

/* Checkbox */
.checkbox-label {
  display: flex !important; align-items: center; gap: 8px;
  font-size: 13px !important; font-weight: 500 !important; text-transform: none !important; letter-spacing: 0 !important;
  color: var(--text-primary) !important; cursor: pointer;
}
.checkbox-label input[type="checkbox"] {
  width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer;
}

/* Hint & error */
.input-hint { display: block; font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.input-error { color: var(--red) !important; }
.config-hint-box {
  display: flex; gap: 8px; padding: 10px 12px; margin-bottom: 14px;
  background: rgba(201, 169, 110, 0.06); border: 1px solid rgba(201, 169, 110, 0.15);
  border-radius: var(--radius-sm); font-size: 12px; color: var(--text-secondary); line-height: 1.5;
}
.hint-icon { flex-shrink: 0; }

/* Validation error */
.validation-error {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; margin-top: 8px;
  background: rgba(192, 80, 77, 0.06); border: 1px solid rgba(192, 80, 77, 0.2);
  border-radius: var(--radius-sm); font-size: 12px; color: var(--red);
}
.error-icon { flex-shrink: 0; }

/* Code editor */
.code-editor {
  font-family: var(--font-mono); font-size: 12px; line-height: 1.6;
  tab-size: 2; white-space: pre; overflow-x: auto;
}

/* Field mapping */
.field-mapping {
  display: flex; align-items: center; gap: 6px; margin-bottom: 6px;
}
.field-input { flex: 1; padding: 6px 8px !important; font-size: 12px !important; }
.field-arrow { color: var(--text-muted); font-size: 12px; flex-shrink: 0; }
.field-remove-btn {
  width: 24px; height: 24px; border: none; border-radius: 4px;
  background: transparent; color: var(--text-muted); cursor: pointer;
  font-size: 12px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
}
.field-remove-btn:hover { background: rgba(192, 80, 77, 0.1); color: var(--red); }
.add-field-btn { margin-top: 4px; border-style: dashed; }

.mono { font-family: var(--font-mono); font-size: 12px; }
.panel-footer { padding: 14px 20px; border-top: 1px solid var(--border-subtle); }
</style>
