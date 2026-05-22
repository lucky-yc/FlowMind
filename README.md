# FlowMind — AI 智能体工作流编排平台

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Vue.js-3-42b883?logo=vuedotjs" />
  <img src="https://img.shields.io/badge/TypeScript-5-3178c6?logo=typescript" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/MySQL-5.7+-4479a1?logo=mysql" />
  <img src="https://img.shields.io/badge/Redis-7+-dc382d?logo=redis" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

> 对标 Dify 的开源 AI 智能体工作流编排平台，支持可视化工作流设计、智能体配置、模型管理、任务调度与执行监控。

---

## ✨ 核心功能

### 🔀 可视化工作流编辑器
- **拖拽式操作**：从左侧面板拖拽节点到画布，支持 8 种节点类型
- **节点类型**：LLM 调用、条件分支、代码执行、输入/输出、工具调用、HTTP 请求、变量操作
- **连线可视化**：节点间通过拖拽端口建立连接，支持平滑曲线动画
- **实时配置**：选中节点后右侧面板展示节点参数配置
- **缩放/平移**：支持画布缩放、小地图导航、自适应画布

### 🤖 智能体管理
- 多类型智能体：聊天机器人、助手、工具型、工作流型
- **模型自由选择**：从已配置的模型列表中选择，而非硬编码选项
- 模型参数配置：Temperature 滑块、Max Tokens、System Prompt
- 工具配置：为智能体绑定外部工具
- 在线对话测试

### 🧠 模型管理
- **统一模型配置**：集中管理所有可用的 LLM 模型提供商
- **多提供商支持**：预设 OpenAI、Anthropic、Google、Azure、DeepSeek、通义千问、智谱 GLM、Ollama 等 9 种提供商
- **自定义接入**：支持任意 OpenAI 兼容 API 端点
- **灵活配置**：API Key、Base URL、Max Tokens、流式输出、多模态支持等独立配置
- **一键启停**：启用/停用模型，停用后自动从选择列表中隐藏
- **搜索筛选**：按提供商筛选、按名称搜索

### 📋 任务调度
- 多种调度模式：手动、单次、周期、Cron 表达式
- 优先级管理（1-10 级）
- 与工作流和智能体关联执行

### 📊 执行监控
- 实时执行状态追踪
- 节点级别执行结果展示
- 执行日志与错误追踪
- 仪表盘统计概览

---

## 🏗 技术架构

```
┌─────────────────────────────────────────────────┐
│                   前端 (Vue 3)                    │
│  Vite + TypeScript + Vue Flow + Element Plus     │
│  Pinia 状态管理 + Vue Router                      │
├─────────────────────────────────────────────────┤
│              REST API (FastAPI)                   │
│  JWT 认证 · 请求限流 · 权限控制                    │
├──────────┬──────────┬───────────────────────────┤
│  MySQL   │  Redis   │   Celery (任务队列)        │
│ 持久化存储 │ 缓存/队列 │   异步任务执行            │
└──────────┴──────────┴───────────────────────────┘
```

### 技术栈详情

| 层级 | 技术 | 用途 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | 组件化 SPA 开发 |
| 构建工具 | Vite | 快速热重载与构建 |
| 流程编辑 | Vue Flow | 可视化节点画布 |
| UI 组件 | Element Plus | 表单、弹窗、消息提示 |
| 状态管理 | Pinia | 响应式全局状态 |
| 路由 | Vue Router | SPA 页面导航 |
| 后端框架 | FastAPI | 高性能异步 API |
| ORM | SQLAlchemy | 数据库模型与查询 |
| 数据校验 | Pydantic v2 | 请求/响应 Schema |
| 认证 | JWT + bcrypt | Token 认证与密码哈希 |
| 数据库 | MySQL | 持久化存储 |
| 缓存 | Redis | 会话缓存与任务队列 |

---

## 📁 项目结构

```
FlowMind/
├── backend/                        # Python 后端
│   ├── app/
│   │   ├── api/                   # API 路由层
│   │   │   ├── auth.py            # 认证接口（注册/登录/用户信息）
│   │   │   ├── workflows.py       # 工作流 CRUD + 执行
│   │   │   ├── agents.py          # 智能体 CRUD + 对话
│   │   │   ├── models.py          # 模型管理 CRUD + 启停 + 简要列表
│   │   │   ├── tasks.py           # 任务 CRUD + 调度
│   │   │   ├── dashboard.py       # 仪表盘统计
│   │   │   └── deps.py            # 公共依赖（分页参数）
│   │   ├── core/                  # 核心模块
│   │   │   ├── config.py          # 环境变量配置
│   │   │   ├── database.py        # SQLAlchemy 引擎与会话
│   │   │   ├── redis_client.py    # Redis 连接
│   │   │   ├── security.py        # JWT 生成/验证 + 密码哈希
│   │   │   └── logging_config.py  # 日志配置
│   │   ├── models/                # SQLAlchemy 数据库模型
│   │   │   ├── user.py            # 用户表
│   │   │   ├── workflow.py        # 工作流表
│   │   │   ├── agent.py           # 智能体表
│   │   │   ├── model_provider.py  # LLM 模型配置表
│   │   │   ├── task.py            # 任务/执行/日志表
│   │   │   └── log.py             # 系统日志表
│   │   ├── schemas/               # Pydantic 请求/响应 Schema
│   │   │   ├── user.py
│   │   │   ├── workflow.py
│   │   │   ├── agent.py
│   │   │   ├── model_provider.py  # 模型 CRUD Schema
│   │   │   └── task.py
│   │   ├── services/              # 业务逻辑层（扩展用）
│   │   └── main.py                # FastAPI 应用入口
│   ├── tests/                     # 单元测试
│   └── requirements.txt
│
├── frontend/                       # Vue 3 前端
│   ├── src/
│   │   ├── api/                   # API 调用封装
│   │   │   ├── client.ts          # Axios 实例与拦截器
│   │   │   ├── auth.ts            # 认证 API
│   │   │   ├── workflows.ts       # 工作流 API
│   │   │   ├── agents.ts          # 智能体 API
│   │   │   ├── models.ts          # 模型管理 API
│   │   │   └── tasks.ts           # 任务 API
│   │   ├── components/            # 可复用组件
│   │   │   ├── AppSidebar.vue     # 侧边栏导航
│   │   │   ├── WorkflowNode.vue   # 工作流节点组件
│   │   │   ├── NodeConfigPanel.vue# 节点配置面板
│   │   │   └── StatsCard.vue      # 统计卡片
│   │   ├── router/                # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/                # Pinia 状态管理
│   │   │   ├── auth.ts            # 认证状态
│   │   │   ├── workflow.ts        # 工作流状态
│   │   │   ├── agent.ts           # 智能体状态
│   │   │   ├── model.ts           # 模型管理状态
│   │   │   └── task.ts            # 任务状态
│   │   ├── styles/                # 全局样式
│   │   │   └── main.css           # 主题变量 + 基础样式
│   │   ├── types/                 # TypeScript 类型定义
│   │   │   └── index.ts           # 通用类型 + 节点类型定义
│   │   └── views/                 # 页面视图
│   │       ├── DashboardView.vue  # 工作台仪表盘
│   │       ├── WorkflowsView.vue  # 工作流列表
│   │       ├── WorkflowEditorView.vue # 工作流编辑器
│   │       ├── AgentsView.vue     # 智能体管理
│   │       ├── AgentDetailView.vue# 智能体详情
│   │       ├── ModelsView.vue     # 模型管理
│   │       ├── TasksView.vue      # 任务调度
│   │       ├── ExecutionsView.vue # 执行监控
│   │       └── LoginView.vue      # 登录/注册
│   ├── index.html
│   └── vite.config.ts
│
├── docs/                           # 文档
│   ├── DEPLOYMENT.md              # 部署文档
│   └── USER_GUIDE.md              # 用户手册
└── README.md
```

---

## 🚀 快速开始

### 环境要求

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Python | 3.10 | 3.12+ |
| Node.js | 18.0 | 20+ |
| MySQL | 5.7 | 8.0+ |
| Redis | 6.0 | 7.0+ |

### 1. 克隆项目

```bash
git clone https://github.com/lucky-yc/FlowMind.git
cd FlowMind
```

### 2. 后端启动

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# 配置数据库（创建 .env 文件）
cat > .env << EOF
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=flowmind
SECRET_KEY=your-secret-key-here
EOF

# 创建数据库
mysql -u root -p -e "CREATE DATABASE flowmind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

### 4. 构建生产版本

```bash
cd frontend
npm run build
```

构建产物位于 `frontend/dist/`，配合 Nginx 部署。详见 [部署文档](docs/DEPLOYMENT.md)。

---

## 📡 API 接口

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录（返回 JWT Token） |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |

### 工作流

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/workflows` | 工作流列表（分页） |
| POST | `/api/v1/workflows` | 创建工作流 |
| GET | `/api/v1/workflows/:id` | 工作流详情 |
| PUT | `/api/v1/workflows/:id` | 更新工作流 |
| DELETE | `/api/v1/workflows/:id` | 删除工作流 |
| POST | `/api/v1/workflows/:id/execute` | 执行工作流 |

### 智能体

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/agents` | 智能体列表（分页） |
| POST | `/api/v1/agents` | 创建智能体 |
| GET | `/api/v1/agents/:id` | 智能体详情 |
| PUT | `/api/v1/agents/:id` | 更新智能体 |
| DELETE | `/api/v1/agents/:id` | 删除智能体 |
| POST | `/api/v1/agents/:id/chat` | 与智能体对话 |

### 模型管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/models` | 模型列表（分页，支持 provider/search 筛选） |
| GET | `/api/v1/models/brief` | 简要列表（仅返回启用模型的 id/name/provider，供下拉选择） |
| POST | `/api/v1/models` | 添加模型配置 |
| GET | `/api/v1/models/:id` | 模型详情 |
| PUT | `/api/v1/models/:id` | 更新模型配置 |
| DELETE | `/api/v1/models/:id` | 删除模型配置 |
| POST | `/api/v1/models/:id/toggle` | 切换启用/停用状态 |

### 任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/tasks` | 任务列表（分页） |
| POST | `/api/v1/tasks` | 创建任务 |
| POST | `/api/v1/tasks/:id/run` | 手动运行任务 |

### 仪表盘

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/dashboard/stats` | 统计概览数据 |

---

## 🧠 模型管理详解

模型管理是 FlowMind 的核心功能之一，让智能体和工作流 LLM 节点能够从统一的模型配置中自由选择。

### 支持的提供商

| 提供商 | 标识 | 典型端点 |
|--------|------|---------|
| OpenAI | `openai` | `https://api.openai.com/v1` |
| Anthropic | `anthropic` | `https://api.anthropic.com` |
| Google | `google` | `https://generativelanguage.googleapis.com` |
| Azure OpenAI | `azure` | `https://{resource}.openai.azure.com` |
| DeepSeek | `deepseek` | `https://api.deepseek.com` |
| 通义千问 | `qwen` | `https://dashscope.aliyuncs.com` |
| 智谱 GLM | `zhipu` | `https://open.bigmodel.cn` |
| Ollama (本地) | `ollama` | `http://localhost:11434` |
| 自定义 | `custom` | 任意 OpenAI 兼容端点 |

### 数据模型

```
llm_models
├── id                  # 主键
├── name                # 显示名称 (如 "GPT-4o")
├── provider            # 提供商标识
├── model_id            # API 模型标识 (如 "gpt-4o")
├── base_url            # API 端点
├── api_key             # API Key
├── description         # 模型说明
├── max_tokens          # 默认最大 Token
├── supports_streaming  # 是否支持流式输出
├── supports_vision     # 是否支持多模态/视觉
├── config              # 额外配置 (JSON)
├── owner_id            # 所属用户
├── is_active           # 启用状态
├── created_at          # 创建时间
└── updated_at          # 更新时间
```

### 工作原理

1. **配置模型**：在「模型管理」页面添加 LLM 提供商配置
2. **智能体选择**：创建智能体时，模型下拉列表自动加载已启用的模型
3. **工作流节点**：LLM 节点的模型选择同样从模型管理列表动态加载
4. **启停控制**：停用模型后，下拉列表自动过滤，不影响已有配置

---

## 🧪 测试

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 📚 相关文档

- [部署文档](docs/DEPLOYMENT.md) — 环境配置、Docker 部署、Nginx 反向代理
- [用户手册](docs/USER_GUIDE.md) — 功能使用指南

---

## 📄 许可证

MIT License

---

**FlowMind** — 让 AI 工作流编排变得简单而强大 ⚡
