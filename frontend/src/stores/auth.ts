import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "@/types";
import { authApi } from "@/api/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string>(localStorage.getItem("token") || "");
  const user = ref<User | null>(null);
  const isLoggedIn = computed(() => !!token.value);

  async function login(username: string, password: string) {
    const { data } = await authApi.login(username, password);
    token.value = data.access_token;
    user.value = data.user;
    localStorage.setItem("token", data.access_token);
  }

  async function register(form: { username: string; email: string; password: string; full_name: string }) {
    const { data } = await authApi.register(form);
    token.value = data.access_token;
    user.value = data.user;
    localStorage.setItem("token", data.access_token);
  }

  async function fetchUser() {
    try {
      const { data } = await authApi.getMe();
      user.value = data;
    } catch {
      logout();
    }
  }

  function logout() {
    token.value = "";
    user.value = null;
    localStorage.removeItem("token");
  }

  return { token, user, isLoggedIn, login, register, fetchUser, logout };
});
