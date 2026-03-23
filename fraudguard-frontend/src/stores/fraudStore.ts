import { defineStore } from 'pinia'

export interface Alert {
  id?: string;
  type: string;
  message?: string;
  severity?: 'low' | 'medium' | 'high';
  timestamp: string;
  upi_id?: string;
  score?: number;
  action?: 'allow' | 'warn' | 'block';
  risk_signals?: string[];
}

export interface Transaction {
  id: string;
  amount: number;
  upi_id: string;
  status: 'scanned' | 'blocked' | 'suspicious';
  timestamp: string;
}

export const useFraudStore = defineStore('fraud', {
  state: () => ({
    safetyScore: 85,
    recentAlerts: [] as Alert[],
    transactionHistory: [] as Transaction[],
    stats: {
      transactionsToday: 124,
      fraudsBlocked: 3,
      communityReports: 12
    }
  }),
  actions: {
    setSafetyScore(score: number) {
      this.safetyScore = score
    },
    addAlert(alert: Alert) {
      this.recentAlerts.unshift(alert)
      if (this.recentAlerts.length > 50) this.recentAlerts.pop()
    },
    addTransaction(transaction: Transaction) {
      this.transactionHistory.unshift(transaction)
    }
  }
})
