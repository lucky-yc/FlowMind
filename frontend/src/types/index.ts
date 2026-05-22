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

export const NODE_TYPES: Record<string, { label: string; icon: string; color: string; desc: string }> = {
  llm: { label: "LLM 调用", icon: "🤖", color: "#c9a96e", desc: "调用大语言模型" },
  condition: { label: "条件分支", icon: "🔀", color: "#c9a030", desc: "根据条件进行分支" },
  code: { label: "代码执行", icon: "⚡", color: "#7c6fa0", desc: "运行自定义代码" },
  input: { label: "输入节点", icon: "📥", color: "#5a8f5e", desc: "工作流输入" },
  output: { label: "输出节点", icon: "📤", color: "#c0504d", desc: "工作流输出" },
  tool: { label: "工具调用", icon: "🔧", color: "#c97a3a", desc: "调用外部工具" },
  http: { label: "HTTP 请求", icon: "🌐", color: "#6a8fba", desc: "发送HTTP请求" },
  variable: { label: "变量操作", icon: "📦", color: "#b06a8a", desc: "变量赋值与转换" },
};
