<template>
  <q-page class="page-wrapper">
    <div class="page-title fade-up fade-up-1">Report Fraud</div>
    <div class="page-subtitle fade-up fade-up-1">Help protect the community by reporting suspicious UPI activity</div>

    <div class="report-layout fade-up fade-up-2">

      <!-- Step Indicator -->
      <div class="step-bar">
        <div
          v-for="(s, i) in steps"
          :key="s.label"
          class="step-item"
          :class="{ active: step === i + 1, done: step > i + 1 }"
        >
          <div class="step-bubble">
            <q-icon v-if="step > i + 1" name="check" size="14px" />
            <span v-else>{{ i + 1 }}</span>
          </div>
          <div class="step-label">{{ s.label }}</div>
          <div v-if="i < steps.length - 1" class="step-line" :class="{ filled: step > i + 1 }" />
        </div>
      </div>

      <!-- Step Content -->
      <div class="step-content fg-card">
        <transition name="step-slide" mode="out-in">

          <!-- Step 1: Fraud Type -->
          <div v-if="step === 1" key="1" class="step-panel">
            <div class="step-title sora">What type of fraud did you encounter?</div>
            <div class="fraud-type-grid">
              <label
                v-for="type in fraudTypes"
                :key="type.value"
                class="fraud-type-card"
                :class="{ selected: form.fraud_type === type.value }"
              >
                <input type="radio" v-model="form.fraud_type" :value="type.value" class="hidden-radio" />
                <div class="ft-icon" :style="{ background: type.bg }">
                  <q-icon :name="type.icon" size="22px" :style="{ color: type.color }" />
                </div>
                <div class="ft-label">{{ type.label }}</div>
                <div class="ft-check">
                  <q-icon v-if="form.fraud_type === type.value" name="check_circle" size="16px" style="color: var(--fg-blue)" />
                </div>
              </label>
            </div>
          </div>

          <!-- Step 2: Details -->
          <div v-else-if="step === 2" key="2" class="step-panel">
            <div class="step-title sora">Provide incident details</div>
            <div class="details-form">
              <div class="form-row">
                <div class="fg-field">
                  <label class="fg-label mono">FRAUDULENT UPI ID *</label>
                  <div class="fg-input-wrap">
                    <q-icon name="person_off" size="14px" style="color: var(--fg-red)" />
                    <input v-model="form.upi_id" placeholder="suspect@bank" class="fg-input-el" />
                  </div>
                </div>
                <div class="fg-field">
                  <label class="fg-label mono">AMOUNT LOST (₹) *</label>
                  <div class="fg-input-wrap">
                    <span class="input-prefix mono" style="color: var(--fg-red)">₹</span>
                    <input v-model.number="form.amount_lost" type="number" placeholder="0" class="fg-input-el" />
                  </div>
                </div>
              </div>
              <div class="fg-field">
                <label class="fg-label mono">UTR / TRANSACTION NUMBER *</label>
                <div class="fg-input-wrap">
                  <q-icon name="receipt" size="14px" />
                  <input v-model="form.utr_number" placeholder="12-digit transaction number" class="fg-input-el" />
                </div>
              </div>
              <div class="fg-field">
                <label class="fg-label mono">DESCRIPTION</label>
                <textarea
                  v-model="form.description"
                  class="fg-textarea"
                  rows="4"
                  placeholder="Describe what happened — how you were approached, what was promised, etc."
                />
              </div>
            </div>
          </div>

          <!-- Step 3: Review & Submit -->
          <div v-else-if="step === 3 && !caseId" key="3" class="step-panel">
            <div class="step-title sora">Review & Submit</div>
            <div class="review-block">
              <div class="review-row">
                <span class="review-key mono">TYPE</span>
                <span class="review-val">{{ fraudTypes.find(t => t.value === form.fraud_type)?.label }}</span>
              </div>
              <div class="review-row">
                <span class="review-key mono">UPI ID</span>
                <span class="review-val mono">{{ form.upi_id }}</span>
              </div>
              <div class="review-row">
                <span class="review-key mono">AMOUNT</span>
                <span class="review-val" style="color: var(--fg-red)">₹{{ form.amount_lost?.toLocaleString() }}</span>
              </div>
              <div class="review-row">
                <span class="review-key mono">UTR</span>
                <span class="review-val mono">{{ form.utr_number }}</span>
              </div>
            </div>
            <div class="disclaimer q-mb-md">
              <q-icon name="info_outline" size="14px" style="color: var(--fg-blue)" />
              <span>Your report will be verified by our team and added to the community fraud database to protect others.</span>
            </div>

            <div class="fg-field portal-forward-field">
              <div class="toggle-wrap" @click="form.submit_to_1930 = !form.submit_to_1930">
                <div class="custom-toggle" :class="{ on: form.submit_to_1930 }">
                  <div class="toggle-knob" />
                </div>
                <div class="toggle-content">
                  <div class="toggle-label sora">Forward to Cybercrime Portal (1930)</div>
                  <div class="toggle-sub">Automatically file a formal case with the National Cybercrime Reporting Portal</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Success -->
          <div v-else-if="step === 3 && caseId" key="success" class="step-panel success-panel">
            <div class="success-icon">
              <q-icon name="task_alt" size="48px" style="color: var(--fg-green)" />
            </div>
            <div class="success-title sora">Report Submitted!</div>
            <div class="case-id-block">
              <div class="case-id-label mono">CASE ID</div>
              <div class="case-id mono">{{ caseId }}</div>
            </div>
            <div class="success-msg">
              Your report has been received. Our team will investigate and update the community fraud database.
            </div>

            <div v-if="portalStatus" class="portal-status-card" :class="{ 'is-loading': portalStatus.status === 'pending' }">
              <div class="ps-header">
                <q-icon :name="portalStatus.success ? 'verified' : 'pending_actions'" size="16px" :style="{ color: portalStatus.success ? 'var(--fg-green)' : 'var(--fg-blue)' }" />
                <span class="mono">CYBERCRIME PORTAL 1930</span>
              </div>
              <div class="ps-body">
                <div v-if="portalStatus.status === 'pending'" class="ps-pending">
                  <q-spinner-dots size="14px" /> Sending report to government portal...
                </div>
                <template v-else>
                  <div class="ps-ref mono">REF: {{ portalStatus.case_ref }}</div>
                  <div class="ps-ack">{{ portalStatus.response?.message || 'Case filed successfully' }}</div>
                </template>
              </div>
            </div>
            <router-link to="/" class="go-home-btn">
              <q-icon name="space_dashboard" size="16px" />
              Return to Dashboard
            </router-link>
          </div>

        </transition>
      </div>

      <!-- Navigation -->
      <div v-if="!caseId" class="step-nav">
        <button
          v-if="step > 1"
          class="nav-back"
          @click="step--"
        >
          ← Back
        </button>
        <div class="nav-spacer" />
        <button
          v-if="step < 3"
          class="nav-next"
          @click="nextStep"
          :disabled="isNextDisabled"
        >
          Continue →
        </button>
        <button
          v-if="step === 3"
          class="nav-submit"
          @click="submitReport"
          :disabled="loading"
        >
          <q-spinner-dots v-if="loading" size="18px" color="white" />
          <template v-else>
            <q-icon name="send" size="16px" />
            Submit Report
          </template>
        </button>
      </div>

    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const step = ref(1)
const loading = ref(false)
const caseId = ref<string | null>(null)

interface PortalStatus {
  status: string;
  success?: boolean;
  case_ref?: string;
  response?: { message: string };
}

const steps = [
  { label: 'Type' },
  { label: 'Details' },
  { label: 'Submit' },
]

const fraudTypes = [
  { value: 'fake_qr',       label: 'Fake QR Code',    icon: 'qr_code_2',      color: 'var(--fg-red)',   bg: 'rgba(239,68,68,0.1)'   },
  { value: 'impersonation', label: 'Impersonation',   icon: 'person_off',     color: 'var(--fg-amber)', bg: 'rgba(245,158,11,0.1)'  },
  { value: 'lottery',       label: 'Lottery Scam',    icon: 'casino',         color: 'var(--fg-blue)',  bg: 'rgba(59,130,246,0.1)'  },
  { value: 'investment',    label: 'Investment Fraud', icon: 'trending_down',  color: 'var(--fg-cyan)',  bg: 'rgba(6,182,212,0.1)'   },
  { value: 'other',         label: 'Other',            icon: 'more_horiz',    color: 'var(--fg-text-muted)', bg: 'rgba(75,94,122,0.2)' },
]

const form = reactive({
  upi_id: '', fraud_type: 'fake_qr',
  amount_lost: null as number | null,
  utr_number: '', description: '', evidence_url: null,
  submit_to_1930: true,
})

const portalStatus = ref<PortalStatus | null>(null)
let statusInterval: ReturnType<typeof setInterval> | null = null

const isNextDisabled = computed(() => {
  if (step.value === 1) return !form.fraud_type
  if (step.value === 2) return !form.upi_id || !form.amount_lost || !form.utr_number
  return false
})

function nextStep() {
  if (!isNextDisabled.value) step.value++
}

async function submitReport() {
  loading.value = true
  try {
    const response = await api.post('/reports/submit', form)
    caseId.value = response.data.case_id
    $q.notify({ type: 'positive', message: `Report submitted. Case: ${caseId.value}`, position: 'top' })
    
    if (form.submit_to_1930) {
      portalStatus.value = { status: 'pending' }
      startStatusPolling(caseId.value!)
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Failed to submit. Please try again.', position: 'top' })
  } finally { loading.value = false }
}

function startStatusPolling(id: string) {
  statusInterval = setInterval(() => {
    void (async () => {
      try {
        const res = await api.get(`/reports/portal-status/${id}`)
        if (res.data.status !== 'pending') {
          portalStatus.value = res.data
          if (statusInterval) clearInterval(statusInterval)
        }
      } catch { /* Silent */ }
    })()
  }, 2000)
}
</script>

<style scoped lang="scss">
.report-layout {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// Step Bar
.step-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 0 20px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  position: relative;
  flex: 1;
}

.step-bubble {
  width: 34px; height: 34px;
  border-radius: 50%;
  border: 2px solid var(--fg-border);
  background: var(--fg-surface);
  display: flex; align-items: center; justify-content: center;
  font-family: 'DM Mono', monospace;
  font-size: 13px;
  color: var(--fg-text-muted);
  transition: all 0.3s ease;
  z-index: 1;

  .step-item.active & {
    border-color: var(--fg-blue);
    background: var(--fg-blue);
    color: white;
    box-shadow: 0 0 14px rgba(59,130,246,0.4);
  }

  .step-item.done & {
    border-color: var(--fg-green);
    background: var(--fg-green);
    color: white;
  }
}

.step-label {
  font-size: 11px;
  font-family: 'DM Mono', monospace;
  color: var(--fg-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;

  .step-item.active & { color: var(--fg-blue); }
  .step-item.done  & { color: var(--fg-green); }
}

.step-line {
  position: absolute;
  top: 17px;
  left: calc(50% + 18px);
  right: calc(-50% + 18px);
  height: 2px;
  background: var(--fg-border);
  z-index: 0;
  transition: background 0.3s ease;

  &.filled { background: var(--fg-green); }
}

// Content
.step-content {
  overflow: hidden;
}

.step-panel { padding: 28px; }
.step-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--fg-text-primary);
  margin-bottom: 24px;
}

// Fraud type grid
.fraud-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.fraud-type-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px 12px;
  border: 1px solid var(--fg-border);
  border-radius: 12px;
  background: var(--fg-surface);
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  text-align: center;

  &:hover { border-color: var(--fg-muted); background: var(--fg-card); }

  &.selected {
    border-color: var(--fg-blue);
    background: var(--fg-blue-soft);
    box-shadow: var(--fg-shadow-blue);
  }
}

.hidden-radio { display: none; }
.ft-icon {
  width: 44px; height: 44px;
  border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
}
.ft-label { font-size: 12px; font-weight: 500; color: var(--fg-text-secondary); }
.ft-check { position: absolute; top: 8px; right: 8px; }

// Forward Toggle
.portal-forward-field {
  padding: 16px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 12px;
}

.toggle-wrap {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
}

.custom-toggle {
  width: 36px; height: 20px;
  border-radius: 10px;
  background: var(--fg-border);
  border: 1px solid var(--fg-muted);
  position: relative;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-top: 2px;
  &.on { background: var(--fg-blue); border-color: var(--fg-blue); }
  .toggle-knob {
    position: absolute; top: 2px; left: 2px;
    width: 14px; height: 14px; border-radius: 50%;
    background: white; transition: transform 0.2s ease;
  }
  &.on .toggle-knob { transform: translateX(16px); }
}

.toggle-content { flex: 1; }
.toggle-label { font-size: 13px; font-weight: 600; color: var(--fg-text-primary); }
.toggle-sub { font-size: 11px; color: var(--fg-text-muted); margin-top: 2px; line-height: 1.4; }

// Success
.success-panel {
  display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center;
}

.portal-status-card {
  width: 100%;
  padding: 16px;
  background: rgba(59,130,246,0.06);
  border: 1px solid rgba(59,130,246,0.15);
  border-radius: 10px;
  text-align: left;
  margin-top: 8px;
  
  &.is-loading {
    border-style: dashed;
    animation: portal-pulse 2s infinite;
  }
}

@keyframes portal-pulse {
  0% { border-color: rgba(59,130,246,0.15); }
  50% { border-color: rgba(59,130,246,0.4); }
  100% { border-color: rgba(59,130,246,0.15); }
}

.ps-header {
  display: flex; align-items: center; gap: 6px;
  font-size: 9px; font-weight: 700; color: var(--fg-text-muted);
  letter-spacing: 1px; margin-bottom: 8px;
}

.ps-pending { font-size: 11px; color: var(--fg-blue); font-weight: 500; }
.ps-ref { font-size: 13px; font-weight: 700; color: var(--fg-text-primary); margin-bottom: 2px; }
.ps-ack { font-size: 11px; color: var(--fg-text-muted); }

// Form
.details-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.fg-field { display: flex; flex-direction: column; gap: 6px; }
.fg-label {
  font-size: 10px; font-weight: 500; letter-spacing: 1.2px;
  color: var(--fg-text-muted); text-transform: uppercase;
}
.fg-input-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--fg-surface); border: 1px solid var(--fg-border);
  border-radius: 9px; padding: 0 12px; color: var(--fg-text-muted);
  transition: all 0.15s ease;

  &:focus-within {
    border-color: var(--fg-blue);
    box-shadow: 0 0 0 3px var(--fg-blue-glow);
    color: var(--fg-blue);
  }
}
.fg-input-el {
  flex: 1; background: none; border: none; outline: none;
  color: var(--fg-text-primary); font-family: 'DM Mono', monospace;
  font-size: 13px; padding: 11px 0;
  &::placeholder { color: var(--fg-text-muted); }
}
.input-prefix { font-size: 14px; }
.fg-textarea {
  width: 100%; background: var(--fg-surface); border: 1px solid var(--fg-border);
  border-radius: 10px; padding: 12px; color: var(--fg-text-primary);
  font-family: 'DM Sans', sans-serif; font-size: 13px; resize: vertical; outline: none;
  transition: all 0.15s ease;
  &::placeholder { color: var(--fg-text-muted); }
  &:focus { border-color: var(--fg-blue); box-shadow: 0 0 0 3px var(--fg-blue-glow); }
}

// Review
.review-block {
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.review-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--fg-border);

  &:last-child { border-bottom: none; }
}

.review-key { font-size: 11px; color: var(--fg-text-muted); letter-spacing: 0.8px; }
.review-val { font-size: 13px; color: var(--fg-text-primary); font-weight: 500; }

.disclaimer {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px; background: rgba(59,130,246,0.06);
  border: 1px solid rgba(59,130,246,0.15);
  border-radius: 8px;
  font-size: 12px; color: var(--fg-text-muted);
}

// Success
.success-panel {
  display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center;
}
.success-icon {
  width: 80px; height: 80px;
  border-radius: 50%;
  background: rgba(16,185,129,0.1);
  border: 1px solid rgba(16,185,129,0.2);
  display: flex; align-items: center; justify-content: center;
}
.success-title { font-size: 22px; font-weight: 700; color: var(--fg-text-primary); }
.case-id-block {
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 10px;
  padding: 14px 24px;
  text-align: center;
}
.case-id-label { font-size: 10px; color: var(--fg-text-muted); letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; }
.case-id { font-size: 18px; font-weight: 700; color: var(--fg-blue); }
.success-msg { font-size: 13px; color: var(--fg-text-muted); line-height: 1.6; max-width: 400px; }
.go-home-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 24px;
  background: var(--fg-blue);
  border-radius: 10px;
  color: white; text-decoration: none;
  font-size: 14px; font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(59,130,246,0.3);

  &:hover { background: #2563EB; transform: translateY(-1px); }
}

// Navigation
.step-nav {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-spacer { flex: 1; }
.nav-back {
  padding: 11px 20px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 9px;
  color: var(--fg-text-secondary);
  font-family: 'DM Mono', monospace;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover { border-color: var(--fg-muted); color: var(--fg-text-primary); }
}
.nav-next {
  padding: 11px 24px;
  background: var(--fg-blue);
  border: none;
  border-radius: 9px;
  color: white;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(59,130,246,0.3);
  transition: all 0.2s ease;

  &:hover:not(:disabled) { background: #2563EB; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.nav-submit {
  @extend .nav-next;
  display: flex; align-items: center; gap: 8px;
  background: var(--fg-green);
  box-shadow: 0 4px 14px rgba(16,185,129,0.3);
  &:hover:not(:disabled) { background: #059669; }
}

// Transitions
.step-slide-enter-active, .step-slide-leave-active { transition: all 0.25s ease; }
.step-slide-enter-from { opacity: 0; transform: translateX(20px); }
.step-slide-leave-to   { opacity: 0; transform: translateX(-20px); }
</style>
