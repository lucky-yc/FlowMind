# FlowMind Frontend

Vue 3 + TypeScript + Vite 前端项目。

## 技术栈

- **Vue 3** — 组合式 API + `<script setup>`
- **TypeScript** — 类型安全
- **Vite** — 快速开发与构建
- **Vue Flow** — 可视化节点编辑器
- **Pinia** — 状态管理
- **Vue Router** — SPA 路由
- **Element Plus** — UI 组件库
- **Axios** — HTTP 请求

## 开发

```bash
npm install
npm run dev       # 启动开发服务器 (http://localhost:5173)
npm run build     # 构建生产版本
npm run preview   # 预览构建产物
```

## 目录结构

```
src/
├── api/           # API 调用封装 (auth, workflows, agents, models, tasks)
├── components/    # 可复用组件 (AppSidebar, WorkflowNode, NodeConfigPanel, StatsCard)
├── router/        # 路由配置
├── stores/        # Pinia 状态管理 (auth, workflow, agent, model, task)
├── styles/        # 全局样式与主题变量
├── types/         # TypeScript 类型定义 + 节点类型注册
└── views/         # 页面视图 (Dashboard, Workflows, Agents, Models, Tasks, Executions, Login)
```

## 相关文档

- [项目主页](../README.md)
- [用户手册](../docs/USER_GUIDE.md)
- [部署文档](../docs/DEPLOYMENT.md)
