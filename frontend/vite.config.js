import { fileURLToPath, URL } from 'node:url'
import path from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    strictPort: true,
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': 'credentialless',
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'onnxruntime-web/wasm': fileURLToPath(new URL('./node_modules/onnxruntime-web/dist/ort.wasm.bundle.min.mjs', import.meta.url)),
      'onnxruntime-web': fileURLToPath(new URL('./node_modules/onnxruntime-web/dist/ort.bundle.min.mjs', import.meta.url)),
    },
  },
  build: {
    outDir: path.resolve(__dirname, '../backend/static/frontend'),
    emptyOutDir: true,
  },
})
