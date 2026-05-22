import { defineStore } from "pinia";
import { ref } from "vue";
import type { Agent } from "@/types";
import { agentApi } from "@/api/agents";

export const useAgentStore = defineStore("agent", () => {
  const agents = ref<Agent[]>([]);
  const currentAgent = ref<Agent | null>(null);
  const loading = ref(false);
  const total = ref(0);

  async function fetchAgents(params?: any) {
    loading.value = true;
    try {
      const { data } = await agentApi.list(params);
      agents.value = data.items;
      total.value = data.total;
    } finally {
      loading.value = false;
    }
  }

  async function fetchAgent(id: number) {
    const { data } = await agentApi.get(id);
    currentAgent.value = data;
  }

  async function createAgent(agent: any) {
    const { data } = await agentApi.create(agent);
    agents.value.unshift(data);
    return data;
  }

  async function updateAgent(id: number, updates: any) {
    const { data } = await agentApi.update(id, updates);
    const idx = agents.value.findIndex((a) => a.id === id);
    if (idx >= 0) agents.value[idx] = data;
    return data;
  }

  async function deleteAgent(id: number) {
    await agentApi.delete(id);
    agents.value = agents.value.filter((a) => a.id !== id);
  }

  return { agents, currentAgent, loading, total, fetchAgents, fetchAgent, createAgent, updateAgent, deleteAgent };
});
