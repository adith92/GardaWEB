import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/garda-api": {
        target: "http://127.0.0.1:8808",
        changeOrigin: false,
        rewrite: (path) => path.replace(/^\/garda-api/, ""),
      },
    },
  },
});
