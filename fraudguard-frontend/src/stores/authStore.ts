import { defineStore } from 'pinia';
import { api } from 'boot/axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth_token'),
    userEmail: localStorage.getItem('auth_user'),
    expiry: localStorage.getItem('auth_expiry') ? parseInt(localStorage.getItem('auth_expiry') as string) : (null as number | null),
  }),

  getters: {
    isAuthenticated: (state) => {
      if (!state.token || !state.expiry) return false;
      return state.expiry > Date.now();
    },
  },

  actions: {
    async login(email: string, password: string) {
      try {
        const response = await api.post('/auth/login', { email, password });
        
        this.token = response.data.access_token;
        this.userEmail = response.data.user.email;
        // 7 days expiry in ms
        this.expiry = Date.now() + 7 * 24 * 60 * 60 * 1000;

        localStorage.setItem('auth_token', this.token as string);
        localStorage.setItem('auth_user', this.userEmail as string);
        localStorage.setItem('auth_expiry', this.expiry.toString());

        return response.data;
      } catch (error) {
        this.logout();
        throw error;
      }
    },

    async register(email: string, password: string) {
      return await api.post('/auth/register', { email, password });
    },

    logout() {
      this.token = null;
      this.userEmail = null;
      this.expiry = null;
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      localStorage.removeItem('auth_expiry');
    },

    rehydrate() {
      const token = localStorage.getItem('auth_token');
      const user = localStorage.getItem('auth_user');
      const expiry = localStorage.getItem('auth_expiry');

      if (token && user && expiry) {
        const expNum = parseInt(expiry);
        if (expNum > Date.now()) {
          this.token = token;
          this.userEmail = user;
          this.expiry = expNum;
        } else {
          this.logout();
        }
      }
    }
  },
});
