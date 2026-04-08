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

// Dev → proxy via quasar.config.ts; Production → real subdomain
const isProd = process.env.NODE_ENV === 'production'
const API_BASE = isProd
  ? 'https://fraudguard-api.harshbhojwani.in/api'
  : '/api'

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
