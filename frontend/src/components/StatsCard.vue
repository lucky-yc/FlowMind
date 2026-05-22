<template>
  <div class="stats-card card">
    <div class="stats-icon" :style="{ background: `${color}15`, color: color }">
      {{ icon }}
    </div>
    <div class="stats-content">
      <span class="stats-value">{{ animatedValue }}</span>
      <span class="stats-label">{{ label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";

const props = defineProps<{ icon: string; label: string; value: number; color: string }>();
const animatedValue = ref(0);

function animateTo(target: number) {
  const duration = 600;
  const start = animatedValue.value;
  const diff = target - start;
  if (diff === 0) return;
  const startTime = performance.now();
  function step(now: number) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    animatedValue.value = Math.round(start + diff * ease);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

watch(() => props.value, (v) => animateTo(v));
onMounted(() => { if (props.value) animateTo(props.value); });
</script>

<style scoped>
.stats-card { display: flex; align-items: center; gap: 16px; }
.stats-icon {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-md);
  font-size: 22px; flex-shrink: 0;
}
.stats-content { display: flex; flex-direction: column; }
.stats-value {
  font-family: var(--font-display);
  font-size: 28px; font-weight: 800;
  line-height: 1;
}
.stats-label { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
</style>
