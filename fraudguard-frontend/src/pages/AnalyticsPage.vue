<template>
  <q-page class="q-pa-md bg-grey-1">
    <div class="row q-col-gutter-md q-mb-lg">
      <div v-for="card in statCards" :key="card.label" class="col-12 col-sm-6 col-md-3">
        <q-card :class="`bg-${card.color} text-white shadow-2 rounded-borders`">
          <q-card-section>
            <div class="text-subtitle2 text-uppercase letter-spacing-1 q-mb-xs">{{ card.label }}</div>
            <div class="text-h4 text-weight-bold">{{ card.value }}</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-banner v-if="error" class="bg-negative text-white q-mb-md rounded-borders shadow-1">
      <template v-slot:avatar>
        <q-icon name="error" />
      </template>
      {{ error }}
      <template v-slot:action>
        <q-btn flat color="white" label="Retry" @click="fetchData" />
      </template>
    </q-banner>

    <div v-if="loading" class="flex flex-center q-pa-xl">
      <q-spinner-dots color="primary" size="80px" />
    </div>

    <template v-else>
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-md-5">
          <q-card class="shadow-2 rounded-borders">
            <q-card-section class="bg-white">
              <div class="text-h6 text-grey-8">Fraud Types</div>
            </q-card-section>
            <q-card-section>
              <apexchart type="donut" height="300" :options="donutOptions" :series="donutSeries" />
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-7">
          <q-card class="shadow-2 rounded-borders">
            <q-card-section class="bg-white">
              <div class="text-h6 text-grey-8">Daily Fraud Attempts (Last 30 Days)</div>
            </q-card-section>
            <q-card-section>
              <apexchart type="area" height="300" :options="areaOptions" :series="areaSeries" />
            </q-card-section>
          </q-card>
        </div>
      </div>

      <q-card class="shadow-2 rounded-borders overflow-hidden">
        <q-tabs
          v-model="activeFilter"
          dense
          class="text-grey-7 bg-white"
          active-color="primary"
          indicator-color="primary"
          align="left"
          narrow-indicator
        >
          <q-tab name="all" label="All" />
          <q-tab name="block" label="Blocked" />
          <q-tab name="warn" label="Warned" />
          <q-tab name="allow" label="Allowed" />
        </q-tabs>

        <q-separator />

        <q-table
          :rows="filteredTransactions"
          :columns="columns"
          row-key="id"
          flat
          :pagination="{ rowsPerPage: 15 }"
          class="bg-white"
        >
          <template v-slot:body-cell-score="props">
            <q-td :props="props">
              <q-chip
                :color="getScoreColor(props.value)"
                text-color="white"
                size="sm"
                class="text-weight-bold"
              >
                {{ props.value }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-action="props">
            <q-td :props="props">
              <q-badge
                :color="getActionColor(props.value)"
                class="text-uppercase text-weight-bold"
                style="padding: 4px 8px"
              >
                {{ props.value }}
              </q-badge>
            </q-td>
          </template>

          <template v-slot:body-cell-post_call_flag="props">
            <q-td :props="props">
              <q-icon
                v-if="props.value"
                name="call"
                color="red"
                size="xs"
              >
                <q-tooltip>Post-Call Transaction</q-tooltip>
              </q-icon>
              <q-icon v-else name="check" color="grey-4" size="xs" />
            </q-td>
          </template>

          <template v-slot:body-cell-amount="props">
            <q-td :props="props">
              ₹{{ props.value.toLocaleString() }}
            </q-td>
          </template>

          <template v-slot:body-cell-timestamp="props">
            <q-td :props="props">
              {{ formatDate(props.value) }}
            </q-td>
          </template>
        </q-table>
      </q-card>
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from 'boot/axios'
import VueApexCharts from 'vue3-apexcharts'

const apexchart = VueApexCharts

const loading = ref(true)
const error = ref<string | null>(null)
const activeFilter = ref('all')
const summary = ref<any>(null)
const history = ref<any[]>([])

onMounted(async () => {
  await fetchData()
})

async function fetchData() {
  loading.value = true
  error.value = null
  try {
    const [summaryRes, historyRes] = await Promise.all([
      api.get('/analytics/summary'),
      api.get('/transactions/history')
    ])
    summary.value = summaryRes.data
    history.value = historyRes.data
  } catch (err) {
    console.error('Fetch error:', err)
    error.value = 'Failed to load analytics data. Please check your connection.'
  } finally {
    loading.value = false
  }
}

const statCards = computed(() => {
  if (!summary.value) return []
  return [
    { label: 'Total Transactions Scanned', value: summary.value.total_transactions.toLocaleString(), color: 'blue' },
    { label: 'Frauds Blocked', value: summary.value.total_frauds_blocked.toLocaleString(), color: 'red' },
    { label: 'Amount Protected', value: `₹${summary.value.total_amount_protected.toLocaleString()}`, color: 'green' },
    { label: 'Community Reports', value: summary.value.community_reports.toLocaleString(), color: 'amber' }
  ]
})

const donutSeries = computed(() => {
  if (!summary.value) return []
  const { fraud_by_type } = summary.value
  return [
    fraud_by_type.fake_qr || 0,
    fraud_by_type.impersonation || 0,
    fraud_by_type.lottery || 0,
    fraud_by_type.investment || 0,
    fraud_by_type.other || 0
  ]
})

const donutOptions: any = {
  labels: ["Fake QR", "Impersonation", "Lottery", "Investment", "Other"],
  colors: ["#E24B4A", "#BA7517", "#534AB7", "#0F6E56", "#888780"],
  legend: { position: 'bottom' },
  chart: { toolbar: { show: false } }
}

const areaSeries = computed(() => {
  if (!summary.value) return []
  return [{
    name: 'Attempts',
    data: summary.value.daily_fraud_attempts.map((d: any) => d.count)
  }]
})

const areaOptions = computed<any>(() => {
  if (!summary.value) return {}
  return {
    chart: { toolbar: { show: false } },
    colors: ["#E24B4A"],
    stroke: { curve: 'smooth' },
    fill: { opacity: 0.3 },
    xaxis: {
      type: 'datetime',
      categories: summary.value.daily_fraud_attempts.map((d: any) => d.date)
    },
    yaxis: {
      min: 0
    }
  }
})

const columns: any[] = [
  { name: 'timestamp', label: 'Time', field: 'timestamp', align: 'left', sortable: true },
  { name: 'upi_id', label: 'UPI ID', field: 'upi_id', align: 'left', sortable: true },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right', sortable: true },
  { name: 'score', label: 'Score', field: 'score', align: 'center', sortable: true },
  { name: 'action', label: 'Action', field: 'action', align: 'center', sortable: true },
  { name: 'post_call_flag', label: 'Post-Call', field: 'post_call_flag', align: 'center' }
]

const filteredTransactions = computed(() => {
  if (activeFilter.value === 'all') return history.value
  return history.value.filter(tx => tx.action === activeFilter.value)
})

function getScoreColor(score: number) {
  if (score < 40) return 'green'
  if (score < 75) return 'amber'
  return 'red'
}

function getActionColor(action: string) {
  if (action === 'allow') return 'green'
  if (action === 'warn') return 'amber'
  return 'red'
}

function formatDate(isoStr: string) {
  const date = new Date(isoStr)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ', ' + date.toLocaleDateString()
}
</script>

<style scoped>
.letter-spacing-1 {
  letter-spacing: 1px;
}
.rounded-borders {
  border-radius: 12px;
}
</style>
