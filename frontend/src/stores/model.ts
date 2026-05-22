import { defineStore } from "pinia";
import { ref } from "vue";
import type { LLMModelBrief, LLMModelFull } from "@/api/models";
import { modelApi } from "@/api/models";

export const useModelStore = defineStore("model", () => {
  const models = ref<LLMModelFull[]>([]);
  const briefModels = ref<LLMModelBrief[]>([]);
  const currentModel = ref<LLMModelFull | null>(null);
  const loading = ref(false);
  const total = ref(0);

  async function fetchModels(params?: any) {
    loading.value = true;
    try {
      const { data } = await modelApi.list(params);
      models.value = data.items;
      total.value = data.total;
    } finally {
      loading.value = false;
    }
  }

  /** 获取简要列表（下拉选择用） */
  async function fetchBriefModels() {
    try {
      const { data } = await modelApi.brief();
      briefModels.value = data;
    } catch {
      // 静默失败
    }
  }

  async function fetchModel(id: number) {
    const { data } = await modelApi.get(id);
    currentModel.value = data;
  }

  async function createModel(model: any) {
    const { data } = await modelApi.create(model);
    models.value.unshift(data);
    // 刷新简要列表
    await fetchBriefModels();
    return data;
  }

  async function updateModel(id: number, updates: any) {
    const { data } = await modelApi.update(id, updates);
    const idx = models.value.findIndex((m) => m.id === id);
    if (idx >= 0) models.value[idx] = data;
    await fetchBriefModels();
    return data;
  }

  async function deleteModel(id: number) {
    await modelApi.delete(id);
    models.value = models.value.filter((m) => m.id !== id);
    await fetchBriefModels();
  }

  async function toggleModel(id: number) {
    const { data } = await modelApi.toggle(id);
    const idx = models.value.findIndex((m) => m.id === id);
    if (idx >= 0) models.value[idx].is_active = data.is_active;
    await fetchBriefModels();
  }

  return {
    models, briefModels, currentModel, loading, total,
    fetchModels, fetchBriefModels, fetchModel,
    createModel, updateModel, deleteModel, toggleModel,
  };
});
