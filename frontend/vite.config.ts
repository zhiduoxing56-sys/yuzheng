import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const target = env.VITE_API_BASE_URL || "http://127.0.0.1:8765";

  return {
    plugins: [react()],
    resolve: { alias: { "@": "/src" } },
    server: {
      host: "0.0.0.0",
      port: 5173,
      strictPort: true,
      allowedHosts: true,
      proxy: {
        "/api": { target, changeOrigin: true },
        "/ws": { target: target.replace(/^http/, "ws"), ws: true, changeOrigin: true },
        "/carla/stream": {
          target: "http://8.137.160.51:8080",
          changeOrigin: true,
          rewrite: (path: string) => path.replace(/^\/carla/, ""),
        },
      },
    },
  };
});
