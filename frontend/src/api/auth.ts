import client from "./client";

export const authApi = {
  login: (username: string, password: string) =>
    client.post("/auth/login", { username, password }),
  register: (data: { username: string; email: string; password: string; full_name: string }) =>
    client.post("/auth/register", data),
  getMe: () => client.get("/auth/me"),
  updateMe: (data: any) => client.put("/auth/me", data),
};
