import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // 127.0.0.1, not localhost: node can resolve localhost to ::1, uvicorn listens on IPv4
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
})
