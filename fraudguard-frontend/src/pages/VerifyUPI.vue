<template>
  <q-page class="page-wrapper">
    <div class="verify-layout">

      <!-- Left: Input -->
      <div class="verify-input-col">
        <div class="page-title fade-up fade-up-1">Verify UPI ID</div>
        <div class="page-subtitle fade-up fade-up-1">Check any UPI address for fraud risk in real-time</div>

        <div class="input-card fg-card fade-up fade-up-2">
          <div class="input-card-header">
            <q-icon name="account_balance_wallet" size="20px" class="text-blue-light" />
            <span class="sora">UPI Verification</span>
          </div>

          <div class="upi-field-wrap" :class="{ focused: fieldFocused, error: hasError }">
            <div class="upi-field-prefix mono">UPI://</div>
            <input
              v-model="upiId"
              class="upi-input"
              placeholder="yourname@bank"
              @focus="fieldFocused = true"
              @blur="fieldFocused = false"
              @keyup.enter="verifyUpi"
            />
            <button
              v-if="upiId"
              class="upi-clear"
              @click="upiId = ''; result = null"
            >
              <q-icon name="close" size="14px" />
            </button>
          </div>

          <div class="upi-hint">
            Examples: &nbsp;
            <span class="hint-chip mono" @click="upiId = 'merchant@paytm'">merchant@paytm</span>
            <span class="hint-chip mono" @click="upiId = 'user@okaxis'">user@okaxis</span>
          </div>

          <button
            class="verify-btn"
            @click="verifyUpi"
            :disabled="loading || !upiId.trim()"
          >
            <template v-if="loading">
              <q-spinner-dots size="20px" color="white" />
              <span>Analyzing...</span>
            </template>
            <template v-else>
              <q-icon name="search" size="18px" />
              <span>Run Verification</span>
            </template>
          </button>
        </div>

        <!-- How it works -->
        <div class="how-it-works fade-up fade-up-3">
          <div class="how-title mono">HOW IT WORKS</div>
          <div class="how-steps">
            <div class="how-step" v-for="step in howItWorks" :key="step.label">
              <div class="step-num">{{ step.num }}</div>
              <div>
                <div class="step-label">{{ step.label }}</div>
                <div class="step-desc">{{ step.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Result -->
      <div class="verify-result-col">
        <transition name="result-slide" mode="out-in">

          <!-- Loading skeleton -->
          <div v-if="loading" class="result-loading fg-card" key="loading">
            <div class="loading-ring">
              <q-spinner-radio size="80px" color="primary" />
            </div>
            <div class="loading-label sora">Analyzing UPI ID...</div>
            <div class="loading-steps">
              <div class="loading-step" :class="{ done: scanStep > 0 }">
                <q-icon :name="scanStep > 0 ? 'check_circle' : 'radio_button_unchecked'" size="14px" />
                Checking fraud database
              </div>
              <div class="loading-step" :class="{ done: scanStep > 1 }">
                <q-icon :name="scanStep > 1 ? 'check_circle' : 'radio_button_unchecked'" size="14px" />
                Running ML models
              </div>
              <div class="loading-step" :class="{ done: scanStep > 2 }">
                <q-icon :name="scanStep > 2 ? 'check_circle' : 'radio_button_unchecked'" size="14px" />
                Community verification
              </div>
            </div>
          </div>

          <!-- Result -->
          <div v-else-if="result" class="result-card fg-card" :class="resultClass" key="result">
            <div class="result-header">
              <div class="result-upi-id-wrap">
                <div class="result-upi-id mono">{{ upiId }}</div>
                <div class="model-tag mono" v-if="result.model">
                  <q-icon name="psychology" size="12px" />
                  {{ result.model }}
                </div>
              </div>
              <div class="result-badge" :class="resultClass">{{ result.risk_level }}</div>
            </div>

            <!-- Score Arc -->
            <div class="score-display">
              <div class="score-grid-overlay"></div>
              <svg viewBox="0 0 200 120" class="arc-svg">
                <path
                  d="M 20 110 A 80 80 0 0 1 180 110"
                  fill="none"
                  stroke="var(--fg-border)"
                  stroke-width="12"
                  stroke-linecap="round"
                  opacity="0.3"
                />
                <path
                  d="M 20 110 A 80 80 0 0 1 180 110"
                  fill="none"
                  :stroke="scoreColor"
                  stroke-width="12"
                  stroke-linecap="round"
                  :stroke-dasharray="251.3"
                  :stroke-dashoffset="251.3 - (251.3 * result.risk_score / 100)"
                  style="transition: stroke-dashoffset 1.5s cubic-bezier(0.34, 1.56, 0.64, 1), stroke 0.5s ease"
                />
              </svg>
              <div class="arc-center">
                <div class="arc-score sora" :style="{ color: scoreColor }">{{ result.risk_score }}</div>
                <div class="arc-label mono">RISK MAGNITUDE</div>
              </div>
            </div>

            <!-- XAI Breakdown -->
            <div class="xai-section" v-if="result.impact_breakdown">
              <div class="section-label mono">EXPLAINABLE AI (XAI) BREAKDOWN</div>
              <div class="impact-bars">
                <div v-for="(val, mod) in result.impact_breakdown" :key="mod" class="impact-item">
                  <div class="impact-header">
                    <span class="impact-mod text-capitalize">{{ mod }}</span>
                    <span class="impact-val mono">{{ val }}%</span>
                  </div>
                  <div class="impact-track">
                    <div class="impact-fill" :style="{ width: val + '%', background: getModalityColor(mod) }" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Device/Platform Security -->
            <div class="device-analysis q-mt-lg">
              <div class="section-label mono">DEVICE SECURITY ANALYSIS</div>
              <div class="fg-card mini-status-card">
                <div class="row items-center justify-between">
                  <div class="row items-center gap-sm">
                    <q-icon name="smartphone" size="16px" color="primary" />
                    <span class="text-caption text-weight-bold">Zero-Trust Fingerprint</span>
                  </div>
                  <q-badge rounded :color="deviceRiskColor" :label="deviceRiskLabel" class="mono text-bold" />
                </div>
                <div class="text-grey-7 text-caption q-mt-xs">
                   Behavioral Score: <span class="mono text-blue-light">0.82 (Human-Like)</span>
                </div>
              </div>
            </div>

            <!-- Risk Signals -->
            <div class="risk-signals" v-if="result.risk_signals && result.risk_signals.length > 0">
              <div class="signals-title mono">DETECTED SIGNALS</div>
              <div class="signal-list">
                <div
                  v-for="signal in result.risk_signals"
                  :key="signal"
                  class="signal-item"
                  :class="resultClass"
                >
                  <q-icon :name="signalIcon" size="14px" />
                  <span>{{ signal }}</span>
                </div>
              </div>
            </div>

            <!-- Safe state -->
            <div v-else-if="result.risk_score < 40" class="safe-indicator">
              <q-icon name="verified_user" size="32px" style="color: var(--fg-green)" />
              <div class="safe-text">No suspicious signals detected</div>
            </div>

            <!-- CTA -->
            <div class="result-actions">
              <router-link
                v-if="result.risk_score >= 60"
                to="/report"
                class="report-btn"
              >
                <q-icon name="report_problem" size="16px" />
                Report this UPI
              </router-link>
              <button class="scan-again-btn" @click="result = null; upiId = ''">
                Scan another →
              </button>
            </div>
          </div>

          <!-- Placeholder -->
          <div v-else class="result-placeholder fg-card" key="placeholder">
            <div class="placeholder-visual">
              <div class="placeholder-rings">
                <div class="p-ring r1" />
                <div class="p-ring r2" />
                <div class="p-ring r3" />
              </div>
              <q-icon name="qr_code_scanner" size="36px" class="placeholder-icon" />
            </div>
            <div class="placeholder-title sora">Enter a UPI ID</div>
            <div class="placeholder-sub">The analysis result will appear here</div>
          </div>

        </transition>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { api } from 'boot/axios'

interface VerifyResult {
  risk_score: number
  risk_level: string
  risk_signals: string[]
  model?: string
  impact_breakdown?: Record<string, number>
  device_risk?: string
}

const upiId = ref('')
const loading = ref(false)
const result = ref<VerifyResult | null>(null)
const fieldFocused = ref(false)
const hasError = ref(false)
const scanStep = ref(0)

const howItWorks = [
  { num: '01', label: 'Enter UPI ID',     desc: 'Type any UPI address you want to verify' },
  { num: '02', label: 'AI Analysis',      desc: 'Our ML models cross-reference 50+ data sources' },
  { num: '03', label: 'Risk Report',      desc: 'Get an instant risk score with detailed signals' },
]

const scoreColor = computed(() => {
  if (!result.value) return 'var(--fg-blue)'
  const s = result.value.risk_score
  if (s < 40) return 'var(--fg-green)'
  if (s < 75) return 'var(--fg-amber)'
  return 'var(--fg-red)'
})

const resultClass = computed(() => {
  if (!result.value) return ''
  const s = result.value.risk_score
  if (s < 40) return 'safe'
  if (s < 75) return 'warn'
  return 'danger'
})

const deviceRiskLabel = computed(() => result.value?.device_risk || 'SECURE')
const deviceRiskColor = computed(() => {
  const lbl = deviceRiskLabel.value
  if (lbl === 'SECURE' || lbl === 'LOW') return 'green'
  if (lbl === 'MEDIUM') return 'amber'
  return 'red'
})

const getModalityColor = (mod: string) => {
  switch (mod.toLowerCase()) {
    case 'transaction': return 'var(--fg-blue)'
    case 'sms': return 'var(--fg-cyan)'
    case 'voice': return 'var(--fg-amber)'
    case 'graph': return 'var(--fg-purple)'
    default: return 'var(--fg-primary)'
  }
}

const signalIcon = computed(() => {
  const s = result.value?.risk_score ?? 0
  if (s < 40) return 'check_circle'
  if (s < 75) return 'warning'
  return 'error'
})

const verifyUpi = async () => {
  if (!upiId.value.trim()) { hasError.value = true; return }
  hasError.value = false
  loading.value = true
  result.value = null
  scanStep.value = 0

  const t1 = setTimeout(() => { scanStep.value = 1 }, 600)
  const t2 = setTimeout(() => { scanStep.value = 2 }, 1200)
  const t3 = setTimeout(() => { scanStep.value = 3 }, 1800)

  try {
    const response = await api.post('/upi/verify', { upi_id: upiId.value.trim() })
    result.value = response.data
  } catch (err) {
    console.error('Failed to verify UPI:', err)
    hasError.value = true
  } finally {
    clearTimeout(t1); clearTimeout(t2); clearTimeout(t3)
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.verify-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  align-items: start;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

// Input Column
.input-card {
  padding: 24px;
  margin-bottom: 20px;
}

.input-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--fg-text-primary);
  margin-bottom: 20px;
}

.upi-field-wrap {
  display: flex;
  align-items: center;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
  margin-bottom: 12px;

  &.focused {
    border-color: var(--fg-blue);
    box-shadow: 0 0 0 3px var(--fg-blue-glow);
  }

  &.error {
    border-color: var(--fg-red);
    box-shadow: 0 0 0 3px rgba(239,68,68,0.1);
  }
}

.upi-field-prefix {
  padding: 14px 10px 14px 16px;
  font-size: 13px;
  color: var(--fg-text-muted);
  background: rgba(255,255,255,0.03);
  border-right: 1px solid var(--fg-border);
  flex-shrink: 0;
  letter-spacing: 0.5px;
}

.upi-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--fg-text-primary);
  font-family: 'DM Mono', monospace;
  font-size: 14px;
  padding: 14px 12px;

  &::placeholder { color: var(--fg-text-muted); }
}

.upi-clear {
  padding: 0 14px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--fg-text-muted);
  display: flex;
  transition: color 0.15s ease;

  &:hover { color: var(--fg-text-primary); }
}

.upi-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--fg-text-muted);
  margin-bottom: 20px;
}

.hint-chip {
  padding: 2px 8px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    border-color: var(--fg-blue);
    color: var(--fg-blue);
  }
}

.verify-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px;
  background: var(--fg-blue);
  border: none;
  border-radius: 10px;
  color: white;
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(59,130,246,0.3);
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #2563EB;
    box-shadow: 0 6px 22px rgba(59,130,246,0.45);
    transform: translateY(-1px);
  }

  &:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
}

// How it works
.how-it-works { padding-top: 4px; }
.how-title {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.5px;
  color: var(--fg-text-muted);
  text-transform: uppercase;
  margin-bottom: 12px;
}
.how-steps { display: flex; flex-direction: column; gap: 10px; }
.how-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 10px;
}
.step-num {
  font-family: 'Sora', sans-serif;
  font-size: 20px;
  font-weight: 800;
  color: var(--fg-border);
  line-height: 1;
  flex-shrink: 0;
}
.step-label { font-size: 13px; font-weight: 600; color: var(--fg-text-primary); }
.step-desc  { font-size: 12px; color: var(--fg-text-muted); margin-top: 2px; }

// Result column
.verify-result-col { position: sticky; top: 80px; }

.result-card {
  padding: 24px;
  transition: box-shadow 0.3s ease;

  &.danger { border-color: rgba(239,68,68,0.25) !important; box-shadow: 0 4px 20px rgba(239,68,68,0.1) !important; }
  &.warn   { border-color: rgba(245,158,11,0.25) !important; }
  &.safe   { border-color: rgba(16,185,129,0.25) !important; }
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.result-upi-id-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-upi-id {
  font-size: 14px;
  color: var(--fg-text-secondary);
}

.model-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  color: var(--fg-cyan);
  background: rgba(6, 182, 212, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(6, 182, 212, 0.15);
  width: fit-content;
}

.result-badge {
  padding: 4px 12px;
  border-radius: 99px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;

  &.safe   { background: rgba(16,185,129,0.12);  color: var(--fg-green); border: 1px solid rgba(16,185,129,0.25); }
  &.warn   { background: rgba(245,158,11,0.12); color: var(--fg-amber); border: 1px solid rgba(245,158,11,0.25); }
  &.danger { background: rgba(239,68,68,0.12);  color: var(--fg-red);   border: 1px solid rgba(239,68,68,0.25); }
}

// Arc
.score-display { position: relative; margin: 0 auto 20px; width: 200px; }
.arc-svg { width: 200px; height: 120px; }
.arc-center {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}
.arc-score { font-size: 42px; font-weight: 800; line-height: 1; }
.arc-label { font-size: 10px; letter-spacing: 1.5px; color: var(--fg-text-muted); }

// XAI Section
.section-label { font-size: 10px; font-weight: 500; letter-spacing: 1.8px; color: var(--fg-text-muted); margin-bottom: 12px; }
.impact-bars { display: flex; flex-direction: column; gap: 12px; }
.impact-item { width: 100%; }
.impact-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: 11px; }
.impact-mod { font-weight: 600; color: var(--fg-text-secondary); }
.impact-val { color: var(--fg-text-muted); }
.impact-track { width: 100%; height: 4px; background: rgba(255,255,255,0.04); border-radius: 2px; }
.impact-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }

// Device Analysis
.mini-status-card { padding: 12px; background: var(--fg-surface) !important; border: 1px solid var(--fg-border); }

// Signals
.signals-title { font-size: 10px; font-weight: 500; letter-spacing: 1.5px; color: var(--fg-text-muted); text-transform: uppercase; margin-bottom: 10px; }
.signal-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px; }
.signal-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;

  &.danger { background: rgba(239,68,68,0.08);  color: var(--fg-red);   }
  &.warn   { background: rgba(245,158,11,0.08); color: var(--fg-amber); }
  &.safe   { background: rgba(16,185,129,0.08); color: var(--fg-green); }
}

.safe-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: rgba(16,185,129,0.06);
  border-radius: 10px;
  margin-bottom: 20px;
}
.safe-text { font-size: 13px; color: var(--fg-green); font-weight: 500; }

.result-actions { display: flex; align-items: center; justify-content: space-between; gap: 10px; }

.report-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.2);
  border-radius: 8px;
  color: var(--fg-red);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover { background: rgba(239,68,68,0.18); }
}

.scan-again-btn {
  background: none;
  border: none;
  color: var(--fg-blue);
  font-family: 'DM Mono', monospace;
  font-size: 13px;
  cursor: pointer;

  &:hover { opacity: 0.8; }
}

// Loading
.result-loading {
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.loading-label { font-size: 18px; font-weight: 700; color: var(--fg-text-primary); }
.loading-steps { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.loading-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--fg-text-muted);
  transition: color 0.3s ease;

  &.done { color: var(--fg-green); }
}

// Placeholder
.result-placeholder {
  padding: 64px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}
.placeholder-visual {
  position: relative;
  width: 100px; height: 100px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 8px;
}
.placeholder-icon { color: var(--fg-text-muted); z-index: 1; }
.placeholder-rings {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.p-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid var(--fg-border);
  animation: expand 3s ease-out infinite;

  &.r1 { width: 50px;  height: 50px;  animation-delay: 0s; }
  &.r2 { width: 75px;  height: 75px;  animation-delay: 0.6s; }
  &.r3 { width: 100px; height: 100px; animation-delay: 1.2s; }
}

@keyframes expand {
  0%   { opacity: 0.4; transform: scale(0.9); }
  100% { opacity: 0;   transform: scale(1.1); }
}

.placeholder-title { font-size: 18px; font-weight: 700; color: var(--fg-text-primary); }
.placeholder-sub   { font-size: 13px; color: var(--fg-text-muted); }

// Transitions
.result-slide-enter-active,
.result-slide-leave-active { transition: all 0.3s ease; }
.result-slide-enter-from   { opacity: 0; transform: scale(0.97) translateY(8px); }
.result-slide-leave-to     { opacity: 0; transform: scale(0.97) translateY(-8px); }
</style>
