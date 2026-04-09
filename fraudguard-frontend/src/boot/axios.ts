import { boot } from 'quasar/wrappers'
import { type App } from 'vue'
import axios, { type AxiosInstance } from 'axios'
import { useAuthStore } from 'src/stores/authStore'

declare module 'vue' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

// Use environment variable for production, fallback to local for development
let API_BASE = process.env.API_URL || 'http://localhost:8000/api'

// Force protocol if missing
if (API_BASE && !API_BASE.startsWith('http')) {
  API_BASE = `https://${API_BASE}`
}

const api = axios.create({ baseURL: API_BASE })

// Add Request Interceptor for JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token && config.url?.startsWith('/')) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default boot(({ app }: { app: App }) => {
  // Rehydrate auth store on startup to recover session
  const authStore = useAuthStore()
  authStore.rehydrate()

  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }
