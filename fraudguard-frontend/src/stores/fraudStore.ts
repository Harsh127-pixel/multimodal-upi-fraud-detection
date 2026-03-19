import { defineStore } from 'pinia'

export interface Alert {
  id: string;
  type: string;
  message: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
}

export const useFraudStore = defineStore('fraud', {
  state: () => ({
    recentAlerts: [] as Alert[],
    isMonitoring: false,
    stats: {
      totalChecks: 0,
      threatsDetected: 0,
    },
  }),
  getters: {
    highSeverityAlerts: (state) => state.recentAlerts.filter(a => a.severity === 'high'),
  },
  actions: {
    addAlert(alert: Alert) {
      this.recentAlerts.unshift(alert)
      if (this.recentAlerts.length > 50) this.recentAlerts.pop()
    },
    toggleMonitoring(status?: boolean) {
      this.isMonitoring = status ?? !this.isMonitoring
    },
  },
})
