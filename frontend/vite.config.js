import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api/auth': {
        target: 'http://backend-auth:8000',
        changeOrigin: true,
      },
      '/api/memos': {
        target: 'http://backend-api:8001',
        changeOrigin: true,
      },
    },
  },
})
