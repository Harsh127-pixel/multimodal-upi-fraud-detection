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

// Standard relative path for devServer proxy compatibility
const api = axios.create({ baseURL: '/api' })

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
