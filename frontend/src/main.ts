import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

/* Self-hosted fonts (replaces Google Fonts) */
import "@fontsource-variable/outfit";
import "@fontsource-variable/dm-sans";
import "@fontsource/instrument-serif/index.css";
import "@fontsource/instrument-serif/400-italic.css";
import "@fontsource-variable/jetbrains-mono";

import App from "./App.vue";
import router from "./router";
import "./styles/main.css";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ElementPlus, { size: "default" });
app.mount("#app");
