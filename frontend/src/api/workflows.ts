import client from "./client";

export const workflowApi = {
  list: (params?: any) => client.get("/workflows", { params }),
  get: (id: number) => client.get(`/workflows/${id}`),
  create: (data: any) => client.post("/workflows", data),
  update: (id: number, data: any) => client.put(`/workflows/${id}`, data),
  delete: (id: number) => client.delete(`/workflows/${id}`),
  execute: (id: number, input?: any) => client.post(`/workflows/${id}/execute`, input),
  executions: (id: number) => client.get(`/workflows/${id}/executions`),
};
