<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="page-title sora">Bulk Transaction Scanner</div>
      <div class="page-subtitle">Upload a bank statement CSV to scan all transactions simultaneously</div>
    </div>

    <!-- Upload Zone -->
    <div class="upload-zone fg-card fade-up fade-up-2" :class="{ dragover }"
      @dragover.prevent="dragover = true"
      @dragleave="dragover = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()">
      <input ref="fileInput" type="file" accept=".csv" style="display:none" @change="onFileChange" />
      <q-icon name="upload_file" size="56px" color="blue-4" />
      <div class="upload-title sora q-mt-md">Drop your CSV here or click to browse</div>
      <div class="upload-sub mono q-mt-xs text-grey-6">Required columns: upi_id, amount (and optionally narration)</div>
      <div v-if="fileName" class="upload-filename q-mt-md">
        <q-chip icon="description" color="blue-9" text-color="white" :label="fileName" />
      </div>

      <!-- CSV format hint -->
      <div class="format-hint q-mt-md mono text-caption text-grey-6">
        Example: <code>upi_id,amount,narration</code> or <code>payee,debit,description</code>
      </div>
    </div>

    <div class="row justify-center q-mt-lg fade-up fade-up-3">
      <q-btn
        size="lg" color="primary" icon="scanner" label="Run Batch Analysis"
        @click="runBulkScan" :loading="scanning" :disable="!selectedFile"
        class="sora scan-btn" unelevated
      />
    </div>

    <!-- Results -->
    <div v-if="results.length > 0" class="q-mt-xl fade-up fade-up-4">
      <!-- Summary KPIs -->
      <div class="bulk-stats-row q-mb-xl">
        <div class="bulk-stat safe-stat">
          <div class="bs-val sora">{{ safeCount }}</div>
          <div class="bs-label mono">SAFE</div>
        </div>
        <div class="bulk-stat warn-stat">
          <div class="bs-val sora">{{ medCount }}</div>
          <div class="bs-label mono">MEDIUM</div>
        </div>
        <div class="bulk-stat danger-stat">
          <div class="bs-val sora">{{ critCount }}</div>
          <div class="bs-label mono">CRITICAL</div>
        </div>
        <div class="bulk-stat">
          <div class="bs-val sora">{{ totalAmount.toLocaleString('en-IN', {style:'currency',currency:'INR', maximumFractionDigits:0}) }}</div>
          <div class="bs-label mono">TOTAL SCANNED</div>
        </div>
      </div>

      <!-- Risk filter tabs -->
      <div class="row q-mb-md gap-md">
        <q-btn-group flat>
          <q-btn :color="filterLevel === 'all' ? 'primary' : 'grey-8'" label="All" @click="filterLevel = 'all'" unelevated />
          <q-btn :color="filterLevel === 'CRITICAL' ? 'negative' : 'grey-8'" label="Critical" @click="filterLevel = 'CRITICAL'" unelevated />
          <q-btn :color="filterLevel === 'MEDIUM' ? 'warning' : 'grey-8'" label="Medium" @click="filterLevel = 'MEDIUM'" unelevated />
          <q-btn :color="filterLevel === 'LOW' ? 'positive' : 'grey-8'" label="Safe" @click="filterLevel = 'LOW'" unelevated />
        </q-btn-group>
        <q-space />
        <q-chip icon="flag" color="negative" :label="`${flaggedCount} Flagged`" class="mono" />
      </div>

      <!-- Scrollable results table -->
      <q-table
        dark flat :rows="filteredResults" :columns="columns"
        row-key="row" :rows-per-page-options="[25, 50, 100]"
        class="fg-table"
      >
        <template #body-cell-risk_level="props">
          <q-td :props="props">
            <q-chip
              :color="riskChipColor(props.value)" :label="props.value"
              dense class="mono text-bold" text-color="white"
            />
          </q-td>
        </template>
        <template #body-cell-risk_score="props">
          <q-td :props="props">
            <div class="mono text-bold" :style="{color: scoreColor(props.value)}">{{ props.value }}</div>
          </q-td>
        </template>
        <template #body-cell-amount="props">
          <q-td :props="props" class="mono">₹{{ props.value?.toLocaleString() }}</q-td>
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const fileName = ref('')
const dragover = ref(false)
const scanning = ref(false)
const filterLevel = ref('all')

interface ScanResult {
  row: number; upi_id: string; amount: number; narration: string;
  risk_score: number; risk_level: string; flagged: boolean;
}
const results = ref<ScanResult[]>([])

const columns = [
  { name: 'row',        label: '#',          field: 'row',        align: 'left' as const,  sortable: true },
  { name: 'upi_id',     label: 'UPI ID',     field: 'upi_id',     align: 'left' as const,  sortable: true },
  { name: 'amount',     label: 'Amount',     field: 'amount',     align: 'right' as const, sortable: true },
  { name: 'risk_score', label: 'Risk Score', field: 'risk_score', align: 'center' as const,sortable: true },
  { name: 'risk_level', label: 'Risk Level', field: 'risk_level', align: 'center' as const,sortable: true },
  { name: 'narration',  label: 'Narration',  field: 'narration',  align: 'left' as const  },
]

const filteredResults = computed(() =>
  filterLevel.value === 'all' ? results.value : results.value.filter(r => r.risk_level === filterLevel.value)
)
const safeCount    = computed(() => results.value.filter(r => r.risk_level === 'LOW').length)
const medCount     = computed(() => results.value.filter(r => r.risk_level === 'MEDIUM').length)
const critCount    = computed(() => results.value.filter(r => r.risk_level === 'CRITICAL').length)
const flaggedCount = computed(() => results.value.filter(r => r.flagged).length)
const totalAmount  = computed(() => results.value.reduce((s, r) => s + r.amount, 0))

function riskChipColor(level: string) {
  if (level === 'CRITICAL') return 'negative'
  if (level === 'MEDIUM') return 'warning'
  return 'positive'
}
function scoreColor(score: number) {
  if (score > 75) return '#ef4444'
  if (score > 40) return '#f59e0b'
  return '#10b981'
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) { selectedFile.value = input.files[0]; fileName.value = input.files[0].name }
}

function onDrop(e: DragEvent) {
  dragover.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f && f.name.endsWith('.csv')) { selectedFile.value = f; fileName.value = f.name }
  else $q.notify({ color: 'warning', message: 'Please drop a valid CSV file' })
}

async function runBulkScan() {
  if (!selectedFile.value) return
  scanning.value = true
  results.value = []
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    const res = await api.post('/scanner/bulk', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    results.value = res.data.results
    $q.notify({ color: 'positive', icon: 'done_all', message: `Scanned ${res.data.total_rows} rows — ${res.data.flagged_count} flagged` })
  } catch {
    $q.notify({ color: 'negative', message: 'Scan failed. Check server.' })
  } finally {
    scanning.value = false
  }
}
</script>

<style scoped lang="scss">
.page-wrapper { padding: 32px; max-width: 1200px; margin: 0 auto; }

.upload-zone {
  border: 2px dashed var(--fg-border);
  border-radius: 20px;
  display: flex; flex-direction: column; align-items: center;
  padding: 48px 24px;
  cursor: pointer;
  transition: all 0.25s;
  text-align: center;
  &.dragover, &:hover { border-color: var(--fg-blue); background: rgba(59, 130, 246, 0.06); }
}
.upload-title { font-size: 20px; font-weight: 600; color: var(--fg-text-primary); }
.upload-sub { font-size: 13px; }
.scan-btn { padding: 12px 48px; border-radius: 12px; font-weight: 700; }

.bulk-stats-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  @media (max-width: 700px) { grid-template-columns: repeat(2, 1fr); }
}
.bulk-stat {
  background: rgba(255,255,255,0.03); border: 1px solid var(--fg-border);
  border-radius: 14px; padding: 20px 16px; text-align: center;
}
.safe-stat { border-color: rgba(16,185,129,0.3); }
.warn-stat { border-color: rgba(245,158,11,0.3); }
.danger-stat { border-color: rgba(239,68,68,0.3); }
.bs-val { font-size: 30px; font-weight: 700; color: var(--fg-text-primary); }
.bs-label { font-size: 11px; letter-spacing: 0.07em; color: var(--fg-text-secondary); margin-top: 4px; }

.fg-table { background: transparent; color: white; }
</style>
