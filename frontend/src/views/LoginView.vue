<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
    </div>
    <div class="login-container">
      <div class="login-card glass">
        <div class="login-brand">
          <div class="brand-logo">
            <svg width="48" height="48" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="url(#lg)" />
              <path d="M8 14h4l2-4 2 8 2-4h4" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              <defs><linearGradient id="lg" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#c9a96e" /><stop offset="1" stop-color="#7c6fa0" /></linearGradient></defs>
            </svg>
          </div>
          <h1 class="login-title">FlowMind</h1>
          <p class="login-subtitle">AI 智能体工作流编排平台</p>
        </div>

        <div class="login-tabs">
          <button class="tab" :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
          <button class="tab" :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
        </div>

        <form @submit.prevent="handleSubmit" class="login-form">
          <div class="form-group" v-if="mode === 'register'">
            <label>姓名</label>
            <input class="input" v-model="form.full_name" placeholder="你的姓名" />
          </div>
          <div class="form-group" v-if="mode === 'register'">
            <label>邮箱</label>
            <input class="input" v-model="form.email" type="email" placeholder="your@email.com" />
          </div>
          <div class="form-group">
            <label>用户名</label>
            <input class="input" v-model="form.username" placeholder="输入用户名" autofocus />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input class="input" v-model="form.password" type="password" placeholder="输入密码" />
          </div>
          <p class="error-msg" v-if="error">{{ error }}</p>
          <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
            {{ loading ? "处理中..." : mode === "login" ? "登录" : "注册" }}
          </button>
        </form>

        <div class="login-footer">
          <p>演示账号: admin / admin123</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();
const mode = ref<"login" | "register">("login");
const loading = ref(false);
const error = ref("");
const form = reactive({ username: "", password: "", email: "", full_name: "" });

async function handleSubmit() {
  loading.value = true;
  error.value = "";
  try {
    if (mode.value === "login") {
      await auth.login(form.username, form.password);
    } else {
      await auth.register(form);
    }
    router.push("/");
  } catch (e: any) {
    error.value = e.response?.data?.detail || "操作失败";
  }
  loading.value = false;
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--bg-page);
}
.login-bg { position: absolute; inset: 0; pointer-events: none; }
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}
.orb-1 {
  width: 500px; height: 500px;
  background: var(--accent);
  top: -150px; right: -100px;
  animation: float 20s ease-in-out infinite;
}
.orb-2 {
  width: 400px; height: 400px;
  background: var(--purple);
  bottom: -100px; left: -80px;
  animation: float 25s ease-in-out infinite reverse;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -20px); }
}
.login-container { position: relative; z-index: 1; width: 100%; max-width: 420px; padding: 20px; }
.login-card {
  padding: 40px 36px;
  border-radius: 20px;
  box-shadow: var(--shadow-lg);
}
.login-brand { text-align: center; margin-bottom: 32px; }
.brand-logo { margin-bottom: 16px; }
.login-title {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 400;
  font-style: italic;
  color: var(--text-primary);
  margin-bottom: 6px;
}
.login-subtitle { font-size: 14px; color: var(--text-muted); }
.login-tabs {
  display: flex;
  gap: 4px;
  background: var(--bg-surface);
  padding: 4px;
  border-radius: var(--radius-md);
  margin-bottom: 28px;
}
.tab {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-muted);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.tab.active {
  background: var(--bg-base);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}
.login-form { display: flex; flex-direction: column; gap: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.login-btn { width: 100%; justify-content: center; padding: 12px; font-size: 15px; }
.error-msg { color: var(--red); font-size: 13px; text-align: center; }
.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-subtle);
}
.login-footer p { font-size: 12px; color: var(--text-muted); }
</style>
