import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    darkMode: localStorage.getItem('darkMode') === 'true',
    notifications: {
      enabled: true,
      sound: true,
      vibration: true,
    },
    apiBaseUrl: '/api',
  }),
  actions: {
    toggleDarkMode() {
      this.darkMode = !this.darkMode
      localStorage.setItem('darkMode', String(this.darkMode))
    },
    updateNotifications(updates: Partial<typeof useSettingsStore.prototype.state.notifications>) {
      this.notifications = { ...this.notifications, ...updates }
    },
  },
})
