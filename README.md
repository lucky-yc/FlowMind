# FlowMind — AI 智能体工作流编排平台

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Vue.js-3-42b883?logo=vuedotjs" />
  <img src="https://img.shields.io/badge/TypeScript-6-3178c6?logo=typescript" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/MySQL-5.7+-4479a1?logo=mysql" />
  <img src="https://img.shields.io/badge/Redis-7+-dc382d?logo=redis" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

> 对标 Dify 的开源 AI 智能体工作流编排平台，支持可视化工作流设计、智能体配置、任务调度与执行监控。

## ✨ 核心功能

### 🔀 可视化工作流编辑器
- **拖拽式操作**：从左侧面板拖拽节点到画布，支持 8 种节点类型
- **节点类型**：LLM 调用、条件分支、代码执行、输入/输出、工具调用、HTTP 请求、变量操作
- **连线可视化**：节点间通过拖拽端口建立连接，支持平滑曲线动画
- **实时配置**：选中节点后右侧面板展示节点参数配置
- **缩放/平移**：支持画布缩放、小地图导航、自适应画布

### 🤖 智能体管理
- 多类型智能体：聊天机器人、助手、工具型、工作流型
- 模型参数配置：Temperature 滑块、Max Tokens、System Prompt
- 工具配置：为智能体绑定外部工具
- 在线对话测试

### 📋 任务调度
- 多种调度模式：手动、单次、周期、Cron 表达式
- 优先级管理（1-10 级）
- 与工作流和智能体关联执行

### 📊 执行监控
- 实时执行状态追踪
- 节点级别执行结果展示
- 执行日志与错误追踪
- 仪表盘统计概览

## 🏗 技术架构

```
┌─────────────────────────────────────────────┐
│                   前端 (Vue 3)                │
│  Vite + TypeScript + Vue Flow + Element Plus │
│  Pinia 状态管理 + Vue Router                  │
├─────────────────────────────────────────────┤
│              REST API (FastAPI)              │
│  JWT 认证 · 请求限流 · 权限控制               │
├──────────┬──────────┬───────────────────────┤
│  MySQL   │  Redis   │   Celery (任务队列)    │
│ 持久化存储 │ 缓存/队列 │   异步任务执行        │
└──────────┴──────────┴───────────────────────┘
```

## 📁 项目结构

```
FlowMind/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── workflows.py   # 工作流 CRUD + 执行
│   │   │   ├── agents.py      # 智能体 CRUD + 对话
│   │   │   ├── tasks.py       # 任务 CRUD + 调度
│   │   │   └── dashboard.py   # 仪表盘统计
│   │   ├── core/              # 核心模块
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py    # 数据库连接
│   │   │   ├── redis_client.py# Redis 连接
│   │   │   ├── security.py    # JWT 认证
│   │   │   └── logging_config.py # 日志配置
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic Schema
│   │   └── main.py            # FastAPI 入口
│   ├── tests/                 # 单元测试
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/               # API 调用封装
│   │   ├── components/        # 可复用组件
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── styles/            # 全局样式
│   │   ├── types/             # TypeScript 类型
│   │   └── views/             # 页面视图
│   ├── index.html
│   └── vite.config.ts
├── docs/                       # 文档
│   ├── DEPLOYMENT.md          # 部署文档
│   └── USER_GUIDE.md          # 用户手册
└── README.md
```

## 🚀 快速开始

### 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.10+ |
| Node.js | 18+ |
| MySQL | 5.7+ |
| Redis | 6.0+ |

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

## 📡 API 接口

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 认证 | POST | `/api/v1/auth/register` | 用户注册 |
| 认证 | POST | `/api/v1/auth/login` | 用户登录 |
| 认证 | GET | `/api/v1/auth/me` | 获取当前用户 |
| 工作流 | GET | `/api/v1/workflows` | 工作流列表 |
| 工作流 | POST | `/api/v1/workflows` | 创建工作流 |
| 工作流 | PUT | `/api/v1/workflows/:id` | 更新工作流 |
| 工作流 | POST | `/api/v1/workflows/:id/execute` | 执行工作流 |
| 智能体 | GET | `/api/v1/agents` | 智能体列表 |
| 智能体 | POST | `/api/v1/agents` | 创建智能体 |
| 智能体 | POST | `/api/v1/agents/:id/chat` | 智能体对话 |
| 任务 | GET | `/api/v1/tasks` | 任务列表 |
| 任务 | POST | `/api/v1/tasks/:id/run` | 运行任务 |
| 仪表盘 | GET | `/api/v1/dashboard/stats` | 统计数据 |

## 🧪 测试

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

## 📄 许可证

MIT License

---

**FlowMind** — 让 AI 工作流编排变得简单而强大 ⚡
