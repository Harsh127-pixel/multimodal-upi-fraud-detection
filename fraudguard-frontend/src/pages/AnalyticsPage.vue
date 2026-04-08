<template>
  <q-page class="page-wrapper">

    <div class="page-title fade-up fade-up-1">Analytics & Reports</div>
    <div class="page-subtitle fade-up fade-up-1">Fraud detection insights and transaction history</div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner fade-up">
      <q-icon name="error_outline" size="18px" />
      <span>{{ error }}</span>
      <button class="retry-btn" @click="fetchData">Retry</button>
    </div>

    <!-- Stat Cards -->
    <div class="row q-col-gutter-md q-mb-xl">
      <div
        v-for="(card, i) in statCards"
        :key="card.label"
        class="col-6 col-md-3"
        :class="`fade-up fade-up-${i + 1}`"
      >
        <div class="stat-card" :class="card.accent">
          <div class="stat-icon" :style="{ background: card.iconBg }">
            <q-icon :name="card.icon" size="18px" :style="{ color: card.iconColor }" />
          </div>
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value">{{ card.value }}</div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div v-if="!loading" class="row q-col-gutter-md q-mb-xl">
      <div class="col-12 col-md-5 fade-up fade-up-3">
        <div class="fg-card chart-card">
          <div class="chart-header">
            <div class="chart-title sora">Fraud Types</div>
            <div class="chart-subtitle">Distribution by category</div>
          </div>
          <apexchart
            type="donut"
            height="280"
            :options="donutOptions"
            :series="donutSeries"
          />
        </div>
      </div>
      <div class="col-12 col-md-7 fade-up fade-up-4">
        <div class="fg-card chart-card">
          <div class="chart-header">
            <div class="chart-title sora">Daily Fraud Attempts</div>
            <div class="chart-subtitle">Last 30 days trend</div>
          </div>
          <apexchart
            type="area"
            height="280"
            :options="areaOptions"
            :series="areaSeries"
          />
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <q-spinner-dots color="primary" size="60px" />
      <div class="loading-text">Loading analytics...</div>
    </div>

    <!-- Transaction Table -->
    <div v-if="!loading" class="fg-card fade-up fade-up-5">
      <div class="table-header">
        <div class="table-title sora">Transaction History</div>
        <div class="filter-tabs">
          <button
            v-for="f in filters"
            :key="f.value"
            class="filter-tab"
            :class="{ active: activeFilter === f.value }"
            @click="activeFilter = f.value"
          >
            {{ f.label }}
          </button>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>UPI ID</th>
              <th class="text-right">Amount</th>
              <th class="text-center">Score</th>
              <th class="text-center">Action</th>
              <th class="text-center">Post-Call</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="tx in filteredTransactions"
              :key="tx.id"
              class="data-row"
            >
              <td class="mono text-muted">{{ formatDate(tx.timestamp) }}</td>
              <td class="mono">{{ tx.upi_id }}</td>
              <td class="text-right font-medium">₹{{ tx.amount.toLocaleString() }}</td>
              <td class="text-center">
                <span class="score-chip" :class="scoreClass(tx.score)">
                  {{ tx.score }}
                </span>
              </td>
              <td class="text-center">
                <span class="action-chip" :class="tx.action">
                  {{ tx.action }}
                </span>
              </td>
              <td class="text-center">
                <q-icon
                  v-if="tx.post_call_flag"
                  name="call"
                  size="14px"
                  style="color: var(--fg-red)"
                />
                <q-icon v-else name="remove" size="14px" style="color: var(--fg-border)" />
              </td>
            </tr>
            <tr v-if="filteredTransactions.length === 0">
              <td colspan="6" class="empty-row">No transactions found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from 'boot/axios'
import VueApexCharts from 'vue3-apexcharts'

const apexchart = VueApexCharts

interface Summary {
  total_transactions: number;
  total_frauds_blocked: number;
  total_amount_protected: number;
  community_reports: number;
  fraud_by_type: { fake_qr: number; impersonation: number; lottery: number; investment: number; other: number };
  daily_fraud_attempts: Array<{ date: string; count: number }>;
}

interface TxRecord {
  id: string; upi_id: string; amount: number;
  score: number; is_fraud: boolean; timestamp: string;
  post_call_flag: boolean; action: string;
}

const loading = ref(true)
const error = ref<string | null>(null)
const activeFilter = ref('all')
const summary = ref<Summary | null>(null)
const history = ref<TxRecord[]>([])

const filters = [
  { value: 'all',   label: 'All' },
  { value: 'block', label: 'Blocked' },
  { value: 'warn',  label: 'Warned' },
  { value: 'allow', label: 'Allowed' },
]

onMounted(fetchData)

async function fetchData() {
  loading.value = true; error.value = null
  try {
    const [sr, hr] = await Promise.all([api.get('/analytics/summary'), api.get('/transactions/history')])
    summary.value = sr.data; history.value = hr.data
  } catch {
    error.value = 'Failed to load analytics. Check your connection.'
  } finally { loading.value = false }
}

const statCards = computed(() => {
  if (!summary.value) return []
  return [
    { label: 'Total Scanned',     value: summary.value.total_transactions.toLocaleString(),           icon: 'receipt_long',   accent: 'blue',  iconBg: 'rgba(59,130,246,0.1)',  iconColor: 'var(--fg-blue)'  },
    { label: 'Frauds Blocked',    value: summary.value.total_frauds_blocked.toLocaleString(),         icon: 'block',          accent: 'red',   iconBg: 'rgba(239,68,68,0.1)',   iconColor: 'var(--fg-red)'   },
    { label: 'Amount Protected',  value: `₹${summary.value.total_amount_protected.toLocaleString()}`, icon: 'savings',        accent: 'green', iconBg: 'rgba(16,185,129,0.1)',  iconColor: 'var(--fg-green)' },
    { label: 'Community Reports', value: summary.value.community_reports.toLocaleString(),            icon: 'group',          accent: 'amber', iconBg: 'rgba(245,158,11,0.1)',  iconColor: 'var(--fg-amber)' },
  ]
})

const donutSeries = computed(() => {
  if (!summary.value) return []
  const { fraud_by_type: f } = summary.value
  return [f.fake_qr||0, f.impersonation||0, f.lottery||0, f.investment||0, f.other||0]
})

const donutOptions = {
  labels: ['Fake QR', 'Impersonation', 'Lottery', 'Investment', 'Other'],
  colors: ['#EF4444', '#F59E0B', '#3B82F6', '#10B981', '#6366F1'],
  legend: { position: 'bottom' as const, labels: { colors: '#8B9AB8' } },
  chart: { toolbar: { show: false }, background: 'transparent' },
  dataLabels: { style: { fontFamily: 'DM Mono, monospace', fontSize: '11px' } },
  plotOptions: { pie: { donut: { size: '65%' } } },
  theme: { mode: 'dark' as const },
}

const areaSeries = computed(() => {
  if (!summary.value) return []
  return [{ name: 'Attempts', data: summary.value.daily_fraud_attempts.map(d => d.count) }]
})

const areaOptions = computed(() => {
  if (!summary.value) return {}
  return {
    chart: { toolbar: { show: false }, background: 'transparent' },
    colors: ['#3B82F6'],
    stroke: { curve: 'smooth' as const, width: 2 },
    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.3, opacityTo: 0.01, stops: [0, 90] } },
    xaxis: { type: 'datetime' as const, categories: summary.value.daily_fraud_attempts.map(d => d.date), labels: { style: { colors: '#8B9AB8', fontFamily: 'DM Mono', fontSize: '11px' } } },
    yaxis: { min: 0, labels: { style: { colors: '#8B9AB8', fontFamily: 'DM Mono', fontSize: '11px' } } },
    grid: { borderColor: 'rgba(42, 58, 85, 0.8)', xaxis: { lines: { show: false } } },
    theme: { mode: 'dark' as const },
    tooltip: { theme: 'dark' as const },
  }
})

const filteredTransactions = computed(() => {
  if (activeFilter.value === 'all') return history.value
  return history.value.filter(tx => tx.action === activeFilter.value)
})

function scoreClass(s: number) {
  if (s < 40) return 'safe'
  if (s < 75) return 'warn'
  return 'danger'
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' · ' + d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}
</script>

<style scoped lang="scss">
.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.2);
  border-radius: 10px;
  color: var(--fg-red);
  font-size: 13px;
  margin-bottom: 20px;

  .retry-btn {
    margin-left: auto;
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 6px;
    color: var(--fg-red);
    padding: 4px 12px;
    font-size: 12px;
    cursor: pointer;
    font-family: 'DM Mono', monospace;
  }
}

.chart-card { padding: 20px; }

.chart-header { margin-bottom: 16px; }
.chart-title { font-size: 15px; font-weight: 600; color: var(--fg-text-primary); }
.chart-subtitle { font-size: 12px; color: var(--fg-text-muted); margin-top: 2px; }

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px;
}
.loading-text { font-size: 14px; color: var(--fg-text-muted); font-family: 'DM Mono', monospace; }

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--fg-border);
  flex-wrap: wrap;
  gap: 12px;
}

.table-title { font-size: 15px; font-weight: 600; color: var(--fg-text-primary); }

.filter-tabs {
  display: flex;
  gap: 4px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 9px;
  padding: 3px;
}

.filter-tab {
  padding: 5px 14px;
  border-radius: 6px;
  border: none;
  background: none;
  color: var(--fg-text-muted);
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;

  &.active {
    background: var(--fg-card);
    color: var(--fg-blue);
    box-shadow: var(--fg-shadow-sm);
  }
}

.table-wrap { overflow-x: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;

  th {
    padding: 12px 16px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--fg-text-muted);
    border-bottom: 1px solid var(--fg-border);
    white-space: nowrap;
    text-align: left;
  }

  td {
    padding: 11px 16px;
    font-size: 13px;
    color: var(--fg-text-secondary);
    border-bottom: 1px solid rgba(42, 58, 85, 0.5);
    white-space: nowrap;
  }

  .data-row:hover td {
    background: var(--fg-blue-soft);
  }

  .empty-row {
    text-align: center;
    color: var(--fg-text-muted);
    padding: 48px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
  }
}

.score-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 22px;
  border-radius: 6px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 600;

  &.safe   { background: rgba(16,185,129,0.12);  color: var(--fg-green); }
  &.warn   { background: rgba(245,158,11,0.12); color: var(--fg-amber); }
  &.danger { background: rgba(239,68,68,0.12);  color: var(--fg-red);   }
}

.action-chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 6px;
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;

  &.allow { background: rgba(16,185,129,0.1); color: var(--fg-green); }
  &.warn  { background: rgba(245,158,11,0.1); color: var(--fg-amber); }
  &.block { background: rgba(239,68,68,0.1);  color: var(--fg-red);   }
}

.font-medium { font-weight: 600; color: var(--fg-text-primary) !important; }
.text-muted  { color: var(--fg-text-muted) !important; }
.text-right  { text-align: right; }
.text-center { text-align: center; }
</style>
