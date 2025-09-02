import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Dev server proxy so relative fetch('/rag/query') hits FastAPI (port 8000) instead of Vite
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5176,
    host: true,
    proxy: {
      '/rag': 'http://localhost:8001',
      '/metrics': 'http://localhost:8001',
      '/audio': 'http://localhost:8001',
      '/config': 'http://localhost:8001',
      '/health': 'http://localhost:8001',
    },
  },
});
