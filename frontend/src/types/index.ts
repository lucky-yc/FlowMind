export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  avatar_url: string;
  role: string;
  is_active: boolean;
  created_at?: string;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    node_type: string;
    config: Record<string, any>;
    description?: string;
  };
  width?: number;
  height?: number;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  label?: string;
  animated?: boolean;
  type?: string;
}

export interface Workflow {
  id: number;
  name: string;
  description: string;
  status: "draft" | "active" | "paused" | "archived";
  owner_id: number;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  variables: Record<string, any>;
  config: Record<string, any>;
  version: number;
  is_template: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Agent {
  id: number;
  name: string;
  description: string;
  agent_type: "chatbot" | "assistant" | "tool" | "workflow";
  model_name: string;
  system_prompt: string;
  temperature: number;
  max_tokens: number;
  tools: Record<string, any>[];
  knowledge_bases: string[];
  config: Record<string, any>;
  owner_id: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Task {
  id: number;
  name: string;
  description: string;
  workflow_id?: number;
  agent_id?: number;
  creator_id: number;
  schedule_type: "manual" | "cron" | "interval" | "once";
  schedule_config: Record<string, any>;
  status: string;
  priority: number;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface Execution {
  id: number;
  task_id?: number;
  workflow_id?: number;
  status: "running" | "completed" | "failed";
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  node_results: Record<string, any>;
  error_message?: string;
  started_at?: string;
  finished_at?: string;
  duration_ms?: number;
}

export interface ExecutionLog {
  id: number;
  execution_id: number;
  node_id?: string;
  level: "info" | "warning" | "error" | "debug";
  message: string;
  data?: Record<string, any>;
  timestamp?: string;
}

export interface DashboardStats {
  workflow_count: number;
  agent_count: number;
  task_count: number;
  execution_count: number;
  active_workflows: number;
  recent_executions: any[];
}

/* ─── Node Type Definitions ─── */

export interface NodeTypeInfo {
  label: string;
  icon: string;
  color: string;
  desc: string;
  /** 默认 config 值，拖拽创建节点时自动填入 */
  defaultConfig: Record<string, any>;
  /** config 校验：返回 null 表示通过，否则返回错误信息 */
  validate?: (config: Record<string, any>) => string | null;
}

export const NODE_TYPES: Record<string, NodeTypeInfo> = {
  llm: {
    label: "LLM 调用",
    icon: "🤖",
    color: "#c9a96e",
    desc: "调用大语言模型",
    defaultConfig: {
      model: "gpt-4o",
      systemPrompt: "",
      userPrompt: "",
      temperature: 70,
      maxTokens: 2048,
      jsonMode: false,
      variables: [],
      timeout: 60,
    },
    validate: (c) => {
      if (!c.model) return "请选择模型";
      if (c.maxTokens && (c.maxTokens < 1 || c.maxTokens > 128000)) return "Max Tokens 范围 1~128000";
      return null;
    },
  },
  condition: {
    label: "条件分支",
    icon: "🔀",
    color: "#c9a030",
    desc: "根据条件进行分支",
    defaultConfig: {
      expression: "",
      operator: "contains",
      value: "",
      caseSensitive: false,
    },
    validate: (c) => {
      if (!c.expression && !c.value) return "请填写条件表达式或比较值";
      return null;
    },
  },
  code: {
    label: "代码执行",
    icon: "⚡",
    color: "#7c6fa0",
    desc: "运行自定义代码",
    defaultConfig: {
      language: "python",
      code: "",
      inputVars: [],
      outputVar: "result",
      timeout: 30,
    },
    validate: (c) => {
      if (!c.code?.trim()) return "请编写代码";
      return null;
    },
  },
  input: {
    label: "输入节点",
    icon: "📥",
    color: "#5a8f5e",
    desc: "工作流输入",
    defaultConfig: {
      inputSchema: [],
      defaultValue: "",
      inputFormat: "text",
    },
  },
  output: {
    label: "输出节点",
    icon: "📤",
    color: "#c0504d",
    desc: "工作流输出",
    defaultConfig: {
      outputFormat: "json",
      template: "",
      fields: [],
    },
  },
  tool: {
    label: "工具调用",
    icon: "🔧",
    color: "#c97a3a",
    desc: "调用外部工具",
    defaultConfig: {
      toolName: "",
      parameters: {},
      timeout: 30,
      retryCount: 0,
      retryDelay: 1,
    },
    validate: (c) => {
      if (!c.toolName) return "请选择工具";
      return null;
    },
  },
  http: {
    label: "HTTP 请求",
    icon: "🌐",
    color: "#6a8fba",
    desc: "发送HTTP请求",
    defaultConfig: {
      method: "GET",
      url: "",
      headers: "{}",
      body: "",
      bodyType: "json",
      timeout: 30,
      retryCount: 0,
      retryDelay: 1,
      followRedirects: true,
    },
    validate: (c) => {
      if (!c.url?.trim()) return "请填写 URL";
      try {
        if (c.headers && typeof c.headers === "string") JSON.parse(c.headers);
      } catch (_e) {
        return "Headers 必须是合法 JSON";
      }
      return null;
    },
  },
  variable: {
    label: "变量操作",
    icon: "📦",
    color: "#b06a8a",
    desc: "变量赋值与转换",
    defaultConfig: {
      varName: "",
      varValue: "",
      varType: "string",
      operation: "set",
    },
    validate: (c) => {
      if (!c.varName?.trim()) return "请填写变量名";
      if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(c.varName)) return "变量名只能包含字母、数字和下划线";
      return null;
    },
  },
};

/** 获取节点默认配置（深拷贝） */
export function getDefaultConfig(nodeType: string): Record<string, any> {
  const info = NODE_TYPES[nodeType];
  return info ? JSON.parse(JSON.stringify(info.defaultConfig)) : {};
}

/** 校验节点配置 */
export function validateNodeConfig(nodeType: string, config: Record<string, any>): string | null {
  const info = NODE_TYPES[nodeType];
  if (!info?.validate) return null;
  return info.validate(config);
}
