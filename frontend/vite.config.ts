import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// Detect if running in Docker (backend service available)
const isDocker = process.env.DOCKER === 'true' || process.env.NODE_ENV === 'docker'
const backendUrl = isDocker ? 'http://backend:8000' : 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',  // Required for Docker
    port: 5173,
    // Enable HMR with polling for Docker's file system
    watch: {
      usePolling: true,
      interval: 1000,
    },
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
        timeout: 120000,  // 2 min timeout for ML processing
      },
      '/uploads': {
        target: backendUrl,
        changeOrigin: true,
      },
      '/ws': {
        target: backendUrl.replace('http', 'ws'),
        ws: true,
      },
    },
  },
})
