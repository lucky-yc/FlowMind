import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/login", name: "login", component: () => import("@/views/LoginView.vue"), meta: { public: true } },
  { path: "/", name: "dashboard", component: () => import("@/views/DashboardView.vue") },
  { path: "/workflows", name: "workflows", component: () => import("@/views/WorkflowsView.vue") },
  { path: "/workflows/:id", name: "workflow-editor", component: () => import("@/views/WorkflowEditorView.vue") },
  { path: "/agents", name: "agents", component: () => import("@/views/AgentsView.vue") },
  { path: "/agents/:id", name: "agent-detail", component: () => import("@/views/AgentDetailView.vue") },
  { path: "/models", name: "models", component: () => import("@/views/ModelsView.vue") },
  { path: "/tasks", name: "tasks", component: () => import("@/views/TasksView.vue") },
  { path: "/executions", name: "executions", component: () => import("@/views/ExecutionsView.vue") },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("token");
  if (!to.meta.public && !token) next("/login");
  else next();
});

export default router;
