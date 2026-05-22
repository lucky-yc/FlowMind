import { defineStore } from "pinia";
import { ref } from "vue";
import type { Workflow } from "@/types";
import { workflowApi } from "@/api/workflows";

export const useWorkflowStore = defineStore("workflow", () => {
  const workflows = ref<Workflow[]>([]);
  const currentWorkflow = ref<Workflow | null>(null);
  const loading = ref(false);
  const total = ref(0);

  async function fetchWorkflows(params?: any) {
    loading.value = true;
    try {
      const { data } = await workflowApi.list(params);
      workflows.value = data.items;
      total.value = data.total;
    } finally {
      loading.value = false;
    }
  }

  async function fetchWorkflow(id: number) {
    loading.value = true;
    try {
      const { data } = await workflowApi.get(id);
      currentWorkflow.value = data;
    } finally {
      loading.value = false;
    }
  }

  async function createWorkflow(workflow: any) {
    const { data } = await workflowApi.create(workflow);
    workflows.value.unshift(data);
    return data;
  }

  async function updateWorkflow(id: number, updates: any) {
    const { data } = await workflowApi.update(id, updates);
    const idx = workflows.value.findIndex((w) => w.id === id);
    if (idx >= 0) workflows.value[idx] = data;
    if (currentWorkflow.value?.id === id) currentWorkflow.value = data;
    return data;
  }

  async function deleteWorkflow(id: number) {
    await workflowApi.delete(id);
    workflows.value = workflows.value.filter((w) => w.id !== id);
  }

  async function executeWorkflow(id: number, input?: any) {
    const { data } = await workflowApi.execute(id, input);
    return data;
  }

  return { workflows, currentWorkflow, loading, total, fetchWorkflows, fetchWorkflow, createWorkflow, updateWorkflow, deleteWorkflow, executeWorkflow };
});
