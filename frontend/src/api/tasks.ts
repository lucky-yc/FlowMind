import client from "./client";

export const taskApi = {
  list: (params?: any) => client.get("/tasks", { params }),
  get: (id: number) => client.get(`/tasks/${id}`),
  create: (data: any) => client.post("/tasks", data),
  update: (id: number, data: any) => client.put(`/tasks/${id}`, data),
  delete: (id: number) => client.delete(`/tasks/${id}`),
  run: (id: number) => client.post(`/tasks/${id}/run`),
  executions: (id: number) => client.get(`/tasks/${id}/executions`),
};

export const dashboardApi = {
  stats: () => client.get("/dashboard/stats"),
};
