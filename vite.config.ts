import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      external: ['electron', 'electron-dev']
    }
  },
  // Set the base path for production builds
  base: './',
  // Ensure the dev server runs on the correct port
  server: {
    port: 5173,
    strictPort: false, // Allow Vite to try another port if 5173 is busy
  }
})