import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      // Proxy API calls during dev if you prefer not to set VITE_API_BASE_URL
      // '/sessions': 'http://localhost:8000',
      // '/personas': 'http://localhost:8000',
      // '/health': 'http://localhost:8000',
    },
  },
})
