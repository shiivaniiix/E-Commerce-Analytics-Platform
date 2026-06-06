import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Forward /api requests to the FastAPI backend.
      // IMPORTANT: do NOT strip the /api prefix — the backend mounts all
      // routes under API_PREFIX="/api" (see backend/app/main.py). Rewriting
      // it away caused GET /api/products/1 to hit the backend as
      // /products/1 -> 404. Keep the prefix intact.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
