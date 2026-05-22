import client from "./client";

export interface LLMModelBrief {
  id: number;
  name: string;
  provider: string;
  model_id: string;
  is_active: boolean;
  supports_vision: boolean;
}

export interface LLMModelFull {
  id: number;
  name: string;
  provider: string;
  model_id: string;
  base_url: string;
  api_key: string;
  description: string;
  max_tokens: number;
  supports_streaming: boolean;
  supports_vision: boolean;
  config: Record<string, any>;
  owner_id: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export const modelApi = {
  list: (params?: any) => client.get("/models", { params }),
  brief: () => client.get<LLMModelBrief[]>("/models/brief"),
  get: (id: number) => client.get(`/models/${id}`),
  create: (data: any) => client.post("/models", data),
  update: (id: number, data: any) => client.put(`/models/${id}`, data),
  delete: (id: number) => client.delete(`/models/${id}`),
  toggle: (id: number) => client.post(`/models/${id}/toggle`),
};
