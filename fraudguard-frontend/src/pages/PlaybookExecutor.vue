<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="page-title sora">Incident Playbook Executor</div>
      <div class="page-subtitle">Automated 6-step response runbook for CRITICAL incidents</div>
    </div>

    <!-- Trigger Panel -->
    <div class="fg-card fade-up fade-up-2 q-mb-xl">
      <div class="section-label mono q-mb-md">TRIGGER PLAYBOOK</div>
      <div class="row q-col-gutter-lg">
        <div class="col-12 col-md-4">
          <q-input v-model="form.tx_id" dark filled label="Transaction ID" class="fg-input" />
        </div>
        <div class="col-12 col-md-4">
          <q-input v-model="form.upi_id" dark filled label="Threat UPI ID" class="fg-input" />
        </div>
        <div class="col-12 col-md-2">
          <q-input v-model.number="form.risk_score" dark filled type="number" label="Risk Score" class="fg-input" />
        </div>
        <div class="col-12 col-md-2 flex items-end">
          <q-btn color="negative" icon="play_arrow" label="Execute" @click="startPlaybook"
            :loading="running" unelevated class="full-width sora" style="height:56px; border-radius:12px" />
        </div>
      </div>
    </div>

    <!-- Stepper Display -->
    <div v-if="runId" class="fg-card fade-up fade-up-3">
      <div class="row q-mb-xl items-center justify-between">
        <div class="section-label mono">PLAYBOOK RUN: {{ runId }}</div>
        <q-chip :color="runStatus === 'complete' ? 'positive' : 'orange'" class="mono" :label="runStatus.toUpperCase()" />
      </div>

      <div class="steps-grid">
        <div
          v-for="(s, i) in STEPS" :key="i"
          class="step-card"
          :class="getStepClass(i)"
        >
          <div class="step-icon-wrap">
            <q-icon :name="s.icon" size="26px" :color="getStepIconColor(i)" />
          </div>
          <div class="col">
            <div class="step-name sora">{{ s.name }}</div>
            <div class="step-detail mono text-grey-6">{{ s.detail }}</div>
          </div>
          <div class="step-indicator">
            <q-spinner v-if="getStepClass(i) === 'active'" color="orange" size="24px" />
            <q-icon v-else-if="getStepClass(i) === 'done'" name="check_circle" color="positive" size="24px" />
            <q-icon v-else name="radio_button_unchecked" color="grey-7" size="24px" />
          </div>
        </div>
      </div>

      <div v-if="runStatus === 'complete'" class="complete-banner q-mt-xl">
        <q-icon name="verified_user" size="36px" color="positive" />
        <div class="q-ml-md">
          <div class="text-h6 sora text-positive">Playbook Executed Successfully</div>
          <div class="mono text-grey-5 text-caption">All 6 response steps completed — Threat neutralized.</div>
        </div>
      </div>
    </div>

    <!-- Pre-defined Playbooks -->
    <div class="fg-card q-mt-xl fade-up fade-up-4">
      <div class="section-label mono q-mb-md">AVAILABLE PLAYBOOKS</div>
      <div class="playbooks-grid">
        <div v-for="pb in presets" :key="pb.name" class="preset-card" @click="loadPreset(pb)">
          <q-icon :name="pb.icon" size="28px" :color="pb.color" />
          <div class="q-ml-md">
            <div class="text-subtitle2 sora text-white">{{ pb.name }}</div>
            <div class="text-caption text-grey-6 mono">{{ pb.desc }}</div>
          </div>
          <q-space />
          <q-badge :color="pb.color" :label="pb.severity" class="mono" />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()

const STEPS = [
  { name: "Freeze Suspected Account",  icon: "lock",            detail: "Sending freeze signal to NPCI gateway..." },
  { name: "Alert Victim via SMS",       icon: "sms",             detail: "Dispatching high-priority alert to victim..." },
  { name: "Notify Bank Fraud Desk",     icon: "account_balance", detail: "Posting incident to bank Fraud Cell..." },
  { name: "Blacklist Threat Actor",     icon: "block",           detail: "Adding to global adaptive blacklist..." },
  { name: "Create Priority Case",       icon: "folder_special",  detail: "Routing to Tier-1 analyst queue..." },
  { name: "File Auto-FIR Draft",        icon: "gavel",           detail: "Generating 1930 portal FIR payload..." },
]

const presets = [
  { name: 'Jamtara Utility Scam', icon: 'electric_bolt', color: 'negative', severity: 'CRITICAL', desc: 'Electricity/water bill scam originating from Jamtara belt', txId: 'TX-JAM-001', upi: 'helpdesk.sbi99@upi', score: 96 },
  { name: 'Lottery Prize Fraud',  icon: 'emoji_events',  color: 'warning',  severity: 'HIGH',     desc: 'Fake prize notification with UPI payment link',          txId: 'TX-LOT-002', upi: 'lotteryprize@ybl',    score: 82 },
  { name: 'KYC Impersonation',    icon: 'badge',         color: 'orange',   severity: 'HIGH',     desc: 'Scammer impersonating bank KYC officer via call',        txId: 'TX-KYC-003', upi: 'fakekyc@okaxis',       score: 78 },
  { name: 'Mule Account Chain',   icon: 'hub',           color: 'purple',   severity: 'CRITICAL', desc: 'Multi-hop fund laundering through mule accounts',        txId: 'TX-MUL-004', upi: 'scammer@upi',          score: 94 },
]

const form = reactive({ tx_id: '', upi_id: '', risk_score: 95 })
const runId = ref('')
const runStatus = ref('idle')
const completedSteps = ref(0)
const running = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

function getStepClass(index: number) {
  if (index < completedSteps.value) return 'done'
  if (index === completedSteps.value && runStatus.value === 'running') return 'active'
  return 'pending'
}

function getStepIconColor(index: number) {
  const cls = getStepClass(index)
  if (cls === 'done') return 'positive'
  if (cls === 'active') return 'warning'
  return 'grey-7'
}

function loadPreset(pb: typeof presets[0]) {
  form.tx_id = pb.txId
  form.upi_id = pb.upi
  form.risk_score = pb.score
}

async function startPlaybook() {
  if (!form.tx_id || !form.upi_id) {
    $q.notify({ color: 'warning', message: 'Fill in TX ID and UPI ID' })
    return
  }
  running.value = true
  completedSteps.value = 0
  runStatus.value = 'running'

  try {
    const res = await api.post('/playbook/execute', {
      tx_id: form.tx_id, upi_id: form.upi_id, risk_score: form.risk_score
    })
    runId.value = res.data.run_id
    pollPlaybook()
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to start playbook' })
    running.value = false
  }
}

async function pollStep() {
  try {
    const res = await api.get(`/playbook/status/${runId.value}`)
    completedSteps.value = res.data.steps_completed
    runStatus.value = res.data.status

    if (res.data.status === 'complete') {
      if (pollTimer) clearInterval(pollTimer)
      running.value = false
      $q.notify({ color: 'positive', icon: 'verified_user', message: 'Incident Playbook Complete — Threat Neutralized!', timeout: 4000 })
    }
  } catch {
    if (pollTimer) clearInterval(pollTimer)
    running.value = false
  }
}

function pollPlaybook() {
  pollTimer = setInterval(() => { void pollStep() }, 900)
}
</script>

<style scoped lang="scss">
.page-wrapper { padding: 32px; max-width: 1100px; margin: 0 auto; }

.steps-grid { display: flex; flex-direction: column; gap: 12px; }

.step-card {
  display: flex; align-items: center; gap: 16px;
  padding: 16px 20px; border-radius: 14px;
  border: 1px solid var(--fg-border);
  background: rgba(255,255,255,0.02);
  transition: all 0.35s;

  &.active {
    border-color: rgba(245, 158, 11, 0.5);
    background: rgba(245, 158, 11, 0.08);
    .step-name { color: #fcd34d; }
  }
  &.done {
    border-color: rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.05);
    .step-name { color: #6ee7b7; }
  }
  &.pending { opacity: 0.4; }
}

.step-icon-wrap {
  width: 48px; height: 48px; border-radius: 12px;
  background: rgba(255,255,255,0.06);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-name { font-size: 15px; font-weight: 600; color: var(--fg-text-secondary); line-height: 1.3; }
.step-detail { font-size: 12px; }

.complete-banner {
  display: flex; align-items: center; padding: 20px;
  background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 14px;
}

.playbooks-grid { display: flex; flex-direction: column; gap: 10px; }
.preset-card {
  display: flex; align-items: center; gap: 12px; padding: 14px 18px;
  border: 1px solid var(--fg-border); border-radius: 12px;
  cursor: pointer; transition: all 0.2s;
  &:hover { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.2); transform: translateX(4px); }
}
</style>
