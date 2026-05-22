<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-grid"></div>
    </div>
    <div class="login-container">
      <div class="login-card glass">
        <div class="login-brand">
          <div class="brand-logo">
            <svg width="48" height="48" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="url(#lg)" />
              <path d="M8 14h4l2-4 2 8 2-4h4" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              <defs><linearGradient id="lg" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#06b6d4" /><stop offset="1" stop-color="#8b5cf6" /></linearGradient></defs>
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

const form = reactive({
  username: "",
  password: "",
  email: "",
  full_name: "",
});

async function handleSubmit() {
  error.value = "";
  loading.value = true;
  try {
    if (mode.value === "login") {
      await auth.login(form.username, form.password);
    } else {
      await auth.register(form);
    }
    router.push("/");
  } catch (e: any) {
    error.value = e.response?.data?.detail || "操作失败，请重试";
  } finally {
    loading.value = false;
  }
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
  background: var(--bg-deepest);
}
.login-bg { position: absolute; inset: 0; pointer-events: none; }
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: float 8s ease-in-out infinite;
}
.orb-1 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(6,182,212,0.15), transparent 70%);
  top: -100px; left: -100px;
}
.orb-2 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(139,92,246,0.12), transparent 70%);
  bottom: -80px; right: -80px;
  animation-delay: -4s;
}
.bg-grid {
  position: absolute; inset: 0;
  background-image: radial-gradient(circle at 1px 1px, rgba(99,179,237,0.04) 1px, transparent 0);
  background-size: 40px 40px;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -20px) scale(1.1); }
}
.login-container { position: relative; z-index: 1; width: 100%; max-width: 420px; padding: 20px; }
.login-card {
  border-radius: 24px;
  padding: 48px 40px;
  background: rgba(17,24,39,0.75);
  backdrop-filter: blur(40px);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-lg);
}
.login-brand { text-align: center; margin-bottom: 32px; }
.brand-logo { margin-bottom: 16px; }
.brand-logo svg { width: 48px; height: 48px; }
.login-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 4px;
}
.login-subtitle { color: var(--text-muted); font-size: 14px; }
.login-tabs { display: flex; gap: 4px; margin-bottom: 28px; background: var(--bg-base); border-radius: var(--radius-md); padding: 4px; }
.tab {
  flex: 1; padding: 10px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-muted); font-family: var(--font-body);
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.tab.active { background: var(--bg-surface); color: var(--text-primary); }
.login-form { display: flex; flex-direction: column; gap: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.error-msg { color: var(--red); font-size: 13px; text-align: center; padding: 8px; background: rgba(239,68,68,0.1); border-radius: var(--radius-sm); }
.login-btn { width: 100%; padding: 14px; font-size: 16px; font-weight: 700; border-radius: var(--radius-md); margin-top: 4px; }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.login-footer { margin-top: 24px; text-align: center; }
.login-footer p { font-size: 12px; color: var(--text-muted); }
</style>
