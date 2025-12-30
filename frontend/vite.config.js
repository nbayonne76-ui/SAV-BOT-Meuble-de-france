import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Allow external access
    open: true,
    allowedHosts: [
      'evelyne-pareve-carlee.ngrok-free.dev',
      '.ngrok-free.dev', // Wildcard for any ngrok free domain
      'tiny-sides-joke.loca.lt',
      '.loca.lt', // Wildcard for any localtunnel domain
      '80d6ed62da3d971e-156-214-105-102.serveousercontent.com',
      'acb77702b15057e9-156-214-105-102.serveousercontent.com',
      'dbe890f00fa68127-156-214-105-102.serveousercontent.com',
      '11e8832be8632b4c-156-214-105-102.serveousercontent.com',
      '.serveousercontent.com' // Wildcard for Serveo
    ],
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false
      },
      '/uploads': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
