import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  define: {
    'import.meta.env.VITE_DEV_AUTH_BYPASS': JSON.stringify(process.env.VITE_DEV_AUTH_BYPASS),
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  }
})
