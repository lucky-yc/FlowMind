import { defineStore } from "pinia";
import { ref } from "vue";
import type { Task, Execution } from "@/types";
import { taskApi, dashboardApi } from "@/api/tasks";

export const useTaskStore = defineStore("task", () => {
  const tasks = ref<Task[]>([]);
  const executions = ref<Execution[]>([]);
  const loading = ref(false);
  const total = ref(0);
  const stats = ref<any>(null);

  async function fetchTasks(params?: any) {
    loading.value = true;
    try {
      const { data } = await taskApi.list(params);
      tasks.value = data.items;
      total.value = data.total;
    } finally {
      loading.value = false;
    }
  }

  async function createTask(task: any) {
    const { data } = await taskApi.create(task);
    tasks.value.unshift(data);
    return data;
  }

  async function deleteTask(id: number) {
    await taskApi.delete(id);
    tasks.value = tasks.value.filter((t) => t.id !== id);
  }

  async function runTask(id: number) {
    const { data } = await taskApi.run(id);
    return data;
  }

  async function fetchStats() {
    const { data } = await dashboardApi.stats();
    stats.value = data;
  }

  return { tasks, executions, loading, total, stats, fetchTasks, createTask, deleteTask, runTask, fetchStats };
});
