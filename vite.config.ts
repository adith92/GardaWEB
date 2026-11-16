import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";
export default defineConfig({
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
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
