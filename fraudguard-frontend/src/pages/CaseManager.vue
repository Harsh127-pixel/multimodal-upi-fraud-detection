<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="row items-center justify-between">
        <div>
          <div class="page-title sora">Analyst Case Manager</div>
          <div class="page-subtitle">Investigate flagged transactions and track resolution</div>
        </div>
        <div class="row items-center gap-md">
          <q-chip color="blue" icon="folder" text-color="white" :label="`${stats.total || 0} Total Cases`" class="mono" />
          <q-btn color="primary" icon="add" label="New Case" @click="showCreateDialog = true" outline class="mono" />
        </div>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-row q-mt-lg fade-up fade-up-2">
      <div class="stat-pill open"> <q-icon name="pending" size="16px" /> {{ stats.open || 0 }} Open </div>
      <div class="stat-pill investigating"> <q-icon name="manage_search" size="16px" /> {{ stats.investigating || 0 }} Investigating </div>
      <div class="stat-pill resolved"> <q-icon name="check_circle" size="16px" /> {{ stats.resolved || 0 }} Resolved </div>
      <div class="stat-pill critical"> <q-icon name="bolt" size="16px" /> {{ stats.critical || 0 }} Critical </div>
    </div>

    <!-- Case Table -->
    <div class="fg-card q-mt-xl fade-up fade-up-3">
      <div class="section-label mono q-mb-md">ACTIVE CASE QUEUE</div>

      <div v-if="cases.length === 0" class="empty-state q-py-xl">
        <q-icon name="folder_open" size="48px" color="blue-grey-8" />
        <div class="q-mt-md text-grey">No cases yet. Run an Advanced Analysis and open a case from the result.</div>
      </div>

      <q-list v-else dark separator>
        <q-item v-for="c in cases" :key="c.case_id" clickable @click="openCase(c)" class="case-row">
          <q-item-section avatar>
            <q-icon :name="riskIcon(c.risk_level)" :color="riskColor(c.risk_level)" size="24px" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="mono text-bold text-white">{{ c.case_id }}</q-item-label>
            <q-item-label caption>{{ c.upi_id }} — {{ c.summary }}</q-item-label>
          </q-item-section>
          <q-item-section>
            <q-chip :color="statusColor(c.status)" size="sm" :label="c.status.toUpperCase()" class="mono" dense />
          </q-item-section>
          <q-item-section side>
            <div class="mono text-bold" :style="{color: c.risk_level === 'CRITICAL' ? '#ef4444' : '#f59e0b'}">
              {{ c.risk_score }}
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    </div>

    <!-- Case Detail Dialog -->
    <q-dialog v-model="showDetail" maximized>
      <q-card dark class="detail-dialog">
        <q-card-section class="row items-center q-mb-sm">
          <div class="text-h6 sora">{{ selectedCase?.case_id }}</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showDetail = false" />
        </q-card-section>
        <q-card-section v-if="selectedCase" class="q-pt-none">
          <div class="row q-col-gutter-xl">
            <div class="col-12 col-md-6">
              <div class="mono text-grey-5 q-mb-xs">UPI TARGET</div>
              <div class="mono text-red-4 text-h6">{{ selectedCase.upi_id }}</div>
              <div class="q-mt-md">
                <div class="mono text-grey-5 q-mb-xs">RISK</div>
                <q-chip :color="riskColor(selectedCase.risk_level)" :label="`${selectedCase.risk_score} — ${selectedCase.risk_level}`" class="mono text-bold" />
              </div>
              <div class="q-mt-lg">
                <div class="mono text-grey-5 q-mb-xs">UPDATE STATUS</div>
                <q-btn-group flat>
                  <q-btn label="Investigating" color="warning" @click="updateStatus('investigating')" :loading="updating" unelevated />
                  <q-btn label="Resolved" color="positive" @click="updateStatus('resolved')" :loading="updating" unelevated />
                  <q-btn label="False Positive" color="grey-7" @click="updateStatus('false_positive')" :loading="updating" unelevated />
                </q-btn-group>
              </div>
              <div class="q-mt-lg">
                <q-input v-model="noteText" dark filled type="textarea" label="Add analyst note..." class="fg-input q-mb-sm" />
                <q-btn color="primary" label="Add Note" icon="note_add" @click="addNote" :loading="updating" unelevated />
              </div>
            </div>
            <div class="col-12 col-md-6">
              <div class="mono text-grey-5 q-mb-xs">ANALYST NOTES</div>
              <div v-if="!selectedCase.notes?.length" class="text-grey-6">No notes yet.</div>
              <q-timeline dark color="blue" v-else>
                <q-timeline-entry v-for="(note, i) in selectedCase.notes" :key="i" :subtitle="note.timestamp" icon="note">
                  {{ note.text }}
                </q-timeline-entry>
              </q-timeline>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()

interface CaseNote { text: string; timestamp: string; }
interface Case {
  case_id: string; tx_id: string; upi_id: string;
  risk_score: number; risk_level: string; summary: string;
  status: string; assigned_to: string;
  notes: CaseNote[]; resolution: string | null;
  created_at: string; updated_at: string;
}
interface CaseStats { total: number; open: number; investigating: number; resolved: number; false_positive: number; critical: number; }

const cases = ref<Case[]>([])
const stats = ref<Partial<CaseStats>>({})
const showDetail = ref(false)
const showCreateDialog = ref(false)
const selectedCase = ref<Case | null>(null)
const noteText = ref('')
const updating = ref(false)

function riskColor(level: string) {
  if (level === 'CRITICAL') return 'negative'
  if (level === 'MEDIUM') return 'warning'
  return 'positive'
}

function riskIcon(level: string) {
  if (level === 'CRITICAL') return 'dangerous'
  if (level === 'MEDIUM') return 'warning'
  return 'check_circle'
}

function statusColor(status: string) {
  if (status === 'open') return 'blue'
  if (status === 'investigating') return 'warning'
  if (status === 'resolved') return 'positive'
  return 'grey'
}

async function fetchCases() {
  try {
    const [caseRes, statsRes] = await Promise.all([
      api.get('/cases/list'),
      api.get('/cases/stats/summary')
    ])
    cases.value = caseRes.data.cases
    stats.value = statsRes.data
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to load cases' })
  }
}

function openCase(c: Case) {
  selectedCase.value = { ...c }
  showDetail.value = true
}

async function updateStatus(status: string) {
  if (!selectedCase.value) return
  updating.value = true
  try {
    const res = await api.patch(`/cases/${selectedCase.value.case_id}`, { status })
    selectedCase.value = res.data.case
    await fetchCases()
    $q.notify({ color: 'positive', message: `Status updated to ${status}` })
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to update' })
  } finally {
    updating.value = false
  }
}

async function addNote() {
  if (!selectedCase.value || !noteText.value) return
  updating.value = true
  try {
    const res = await api.patch(`/cases/${selectedCase.value.case_id}`, { notes: noteText.value })
    selectedCase.value = res.data.case
    noteText.value = ''
    $q.notify({ color: 'positive', message: 'Note added' })
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to add note' })
  } finally {
    updating.value = false
  }
}

onMounted(fetchCases)
</script>

<style scoped lang="scss">
.page-wrapper { padding: 32px; max-width: 1200px; margin: 0 auto; }

.stats-row {
  display: flex; gap: 12px; flex-wrap: wrap;
}

.stat-pill {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 20px;
  font-family: var(--font-mono); font-size: 13px;
  border: 1px solid var(--fg-border);
  
  &.open { background: rgba(59, 130, 246, 0.12); color: #93c5fd; }
  &.investigating { background: rgba(245, 158, 11, 0.12); color: #fcd34d; }
  &.resolved { background: rgba(16, 185, 129, 0.12); color: #6ee7b7; }
  &.critical { background: rgba(239, 68, 68, 0.12); color: #fca5a5; }
}

.case-row { border-radius: 8px; margin-bottom: 2px; cursor: pointer; transition: background 0.15s; &:hover { background: rgba(255,255,255,0.04); } }

.empty-state { display: flex; flex-direction: column; align-items: center; }

.detail-dialog {
  background: var(--fg-surface-dark);
  min-height: 100vh;
}
</style>
