import client from "./client";

export const agentApi = {
  list: (params?: any) => client.get("/agents", { params }),
  get: (id: number) => client.get(`/agents/${id}`),
  create: (data: any) => client.post("/agents", data),
  update: (id: number, data: any) => client.put(`/agents/${id}`, data),
  delete: (id: number) => client.delete(`/agents/${id}`),
  chat: (id: number, message: string) => client.post(`/agents/${id}/chat`, { message }),
};
