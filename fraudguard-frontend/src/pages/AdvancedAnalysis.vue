<template>
  <q-page class="page-wrapper">

    <div class="page-title fade-up fade-up-1">Multi-modal Analysis</div>
    <div class="page-subtitle fade-up fade-up-1">Combine transaction data, SMS, and voice for comprehensive fraud detection</div>

    <div class="analysis-grid">

      <!-- Input Panel -->
      <div class="input-panel fade-up fade-up-2">

        <!-- Modality Tabs -->
        <div class="modality-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="modality-tab"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <q-icon :name="tab.icon" size="16px" />
            <span>{{ tab.label }}</span>
            <span v-if="tab.key === 'voice' && form.call_transcript" class="tab-dot" />
            <span v-if="tab.key === 'sms' && form.sms_text" class="tab-dot" />
          </button>
        </div>

        <!-- Transaction Tab -->
        <transition name="tab-fade" mode="out-in">
          <div v-if="activeTab === 'transaction'" key="tx" class="tab-content">
            <div class="field-grid">
              <div class="fg-field">
                <label class="fg-label mono">PAYEE UPI ID</label>
                <div class="fg-input-wrap">
                  <q-icon name="account_balance_wallet" size="14px" />
                  <input v-model="form.upi_id" placeholder="payee@bank" class="fg-input-el" />
                </div>
              </div>
              <div class="fg-field">
                <label class="fg-label mono">AMOUNT (₹)</label>
                <div class="fg-input-wrap">
                  <span class="input-prefix mono">₹</span>
                  <input v-model.number="form.amount" type="number" placeholder="0" class="fg-input-el" />
                </div>
              </div>
            </div>
            <div class="toggle-row">
              <div class="toggle-wrap" @click="form.is_post_call = !form.is_post_call">
                <div class="custom-toggle" :class="{ on: form.is_post_call }">
                  <div class="toggle-knob" />
                </div>
                <span class="toggle-label">Transaction initiated after a phone call?</span>
              </div>
              <span class="post-call-badge" :class="{ active: form.is_post_call }">
                {{ form.is_post_call ? 'HIGH RISK SIGNAL' : 'NOT FLAGGED' }}
              </span>
            </div>
          </div>

          <!-- SMS Tab -->
          <div v-else-if="activeTab === 'sms'" key="sms" class="tab-content">
            <div class="fg-field">
              <label class="fg-label mono">SMS CONTENT</label>
              <textarea
                v-model="form.sms_text"
                class="fg-textarea"
                rows="6"
                placeholder="Paste the suspicious SMS text here..."
              />
            </div>
            <div class="sms-tip">
              <q-icon name="lightbulb_outline" size="14px" style="color: var(--fg-amber)" />
              <span>Paste the exact SMS content. Our AI will detect phishing patterns, fake links, and urgency tactics.</span>
            </div>
          </div>

          <!-- Voice Tab -->
          <div v-else key="voice" class="tab-content">
            <div class="fg-field q-mb-md">
              <label class="fg-label mono">CALLER PHONE (FOR REPUTATION)</label>
              <div class="fg-input-wrap">
                <q-icon name="phone" size="14px" />
                <input v-model="voiceForm.caller_number" placeholder="+91 98XXX XXXXX" class="fg-input-el" />
                <button
                  v-if="voiceForm.caller_number"
                  class="truecaller-btn mono"
                  @click="checkTruecaller"
                  :disabled="truecallerLoading"
                >
                  CHECK
                </button>
              </div>
              <!-- Truecaller Result -->
              <div v-if="truecallerResult" class="truecaller-result" :class="{ spam: truecallerResult.is_spam }">
                <div class="tr-top">
                  <span class="tr-label mono">REPUTATION: {{ truecallerResult.is_spam ? 'SPAM' : 'CLEAN' }}</span>
                  <span class="tr-score mono">SCORE: {{ (truecallerResult.spam_score * 100).toFixed(0) }}%</span>
                </div>
                <div class="tr-tags" v-if="truecallerResult.labels.length">
                  <span v-for="tag in truecallerResult.labels" :key="tag" class="tr-tag">{{ tag }}</span>
                </div>
                <div class="tr-reports mono">Community Reports: {{ truecallerResult.community_reports }}</div>
              </div>
            </div>

            <div class="voice-controls">
              <div class="upload-zone" @click="triggerFileUpload" :class="{ 'has-file': audioFile }">
                <input ref="fileInput" type="file" accept=".mp3,.wav,audio/*" class="hidden-input" @change="onFileChange" />
                <q-icon :name="audioFile ? 'audio_file' : 'upload_file'" size="28px" :style="{ color: audioFile ? 'var(--fg-blue)' : 'var(--fg-text-muted)' }" />
                <div class="upload-label">{{ audioFile ? audioFile.name : 'Drop audio file or click to browse' }}</div>
                <div class="upload-sub mono">MP3, WAV supported</div>
                <button v-if="audioFile" class="upload-analyze-btn" @click.stop="uploadAudio">
                  <q-icon name="send" size="14px" />
                  Transcribe
                </button>
              </div>

              <div class="divider-or"><span>or</span></div>

              <button
                class="record-btn"
                :class="{ recording: isRecording }"
                @click="isRecording ? stopRecording() : startRecording()"
              >
                <div class="record-icon">
                  <q-icon :name="isRecording ? 'stop' : 'mic'" size="20px" />
                  <div v-if="isRecording" class="record-pulse" />
                </div>
                <span>{{ isRecording ? 'Stop Recording' : 'Record Voice Memo' }}</span>
              </button>
            </div>

            <div class="fg-field q-mt-md">
              <label class="fg-label mono">
                TRANSCRIPT
                <span v-if="transcriptionLoading" class="transcribing-label">
                  <q-spinner-dots size="12px" /> Transcribing...
                </span>
              </label>
              <textarea
                v-model="form.call_transcript"
                class="fg-textarea"
                rows="5"
                placeholder="AI transcription will appear here, or type manually..."
                :disabled="transcriptionLoading"
              />
            </div>
          </div>
        </transition>

        <button
          class="run-btn"
          @click="runAnalysis"
          :disabled="loading"
        >
          <template v-if="!loading">
            <q-icon name="analytics" size="18px" />
            Run Global Analysis
          </template>
          <template v-else>
            <q-spinner-dots size="20px" color="white" />
            Analyzing...
          </template>
        </button>
      </div>

      <!-- Result Panel -->
      <div class="result-panel">
        <transition name="result-fade" mode="out-in">

          <!-- Loading -->
          <div v-if="loading" key="loading" class="fg-card result-loading-card">
            <div class="analysis-progress">
              <div class="progress-ring">
                <q-spinner-radio size="64px" color="primary" />
              </div>
              <div class="progress-title sora">Running Analysis</div>
              <div class="progress-steps">
                <div class="p-step" v-for="step in analyzeSteps" :key="step" :class="{ done: analyzeProgress > analyzeSteps.indexOf(step) }">
                  <q-icon :name="analyzeProgress > analyzeSteps.indexOf(step) ? 'check_circle' : 'radio_button_unchecked'" size="13px" />
                  <span>{{ step }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Result -->
          <div v-else-if="result" key="result" class="fg-card result-display-card" :class="resultCardClass">
            <div class="result-top">
              <div class="result-label mono">GLOBAL RISK ASSESSMENT</div>
              <div class="result-modalities">
                <span class="modality-tag" v-for="m in result.modalities_analyzed" :key="m">{{ m }}</span>
              </div>
            </div>

            <div class="result-score-wrap">
              <svg viewBox="0 0 200 200" class="score-svg-full">
                <circle cx="100" cy="100" r="85" fill="none" stroke="var(--fg-border)" stroke-width="14" />
                <circle
                  cx="100" cy="100" r="85"
                  fill="none"
                  :stroke="resultScoreColor"
                  stroke-width="14"
                  stroke-linecap="round"
                  :stroke-dasharray="534"
                  :stroke-dashoffset="534 - (534 * result.global_score / 100)"
                  transform="rotate(-90 100 100)"
                  style="transition: stroke-dashoffset 1.2s ease"
                />
              </svg>
              <div class="score-inner">
                <div class="score-num sora" :style="{ color: resultScoreColor }">{{ result.global_score }}</div>
                <div class="score-txt mono">RISK SCORE</div>
              </div>
            </div>

            <div class="risk-level-badge" :class="resultCardClass">
              {{ result.risk_level }}
            </div>

            <div class="recommendation-box">
              <div class="rec-header">
                <q-icon name="smart_toy" size="15px" style="color: var(--fg-blue)" />
                <span class="mono">AI RECOMMENDATION</span>
              </div>
              <div class="rec-text">{{ result.recommendation }}</div>
            </div>

            <!-- Generative LLM Threat Intelligence -->
            <div class="genai-box q-mt-md" v-if="genAIBrief">
               <div class="rec-header">
                 <q-icon name="psychology_alt" size="16px" style="color: var(--fg-purple)" />
                 <span class="mono">GEN-AI THREAT BRIEF</span>
               </div>
               <div class="rec-text text-purple-2" style="font-family: var(--font-sora); font-size: 13px; line-height: 1.6;">
                  "{{ genAIBrief }}"
               </div>
            </div>

            <!-- XAI Impact Breakdown -->
            <div class="xai-impact-section q-mt-lg" v-if="result.impact_breakdown">
              <div class="result-label mono q-mb-sm">MODALITY IMPACT ANALYSIS</div>
              <div class="impact-grid">
                <div v-for="(val, mod) in result.impact_breakdown" :key="mod" class="impact-row">
                  <div class="impact-info">
                    <span class="impact-mod text-capitalize">{{ mod }}</span>
                    <span class="impact-pct mono">{{ val }}%</span>
                  </div>
                  <div class="impact-bar-bg">
                    <div class="impact-bar-fill" :style="{ width: val + '%', background: getModalityColor(mod) }" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Evidence Locker & FIR CTA -->
            <div class="evidence-cta q-mt-xl" v-if="result.global_score >= 10">
              <div class="evidence-card fg-card mini q-mb-md">
                <div class="row items-center no-wrap gap-md">
                   <div class="evidence-icon-wrap">
                     <q-icon name="enhanced_encryption" size="24px" color="blue" />
                   </div>
                   <div class="col">
                     <div class="text-subtitle2 sora text-white">Digital Evidence Locker</div>
                     <div class="text-caption text-grey-6">Create a tamper-proof evidence bundle for local storage.</div>
                   </div>
                   <q-btn
                     flat dense
                     label="Secure"
                     class="evidence-btn"
                     @click="secureEvidence"
                     :loading="securingEvidence"
                   />
                </div>
              </div>
              
              <!-- Legal Export FIR -->
              <div class="evidence-card fg-card mini q-mb-md">
                <div class="row items-center no-wrap gap-md">
                   <div class="evidence-icon-wrap" style="background: rgba(239, 68, 68, 0.15)">
                     <q-icon name="gavel" size="24px" color="red" />
                   </div>
                   <div class="col">
                     <div class="text-subtitle2 sora text-white">Automated FIR Export</div>
                     <div class="text-caption text-grey-6">Generate Cybercrime FIR payload for this incident.</div>
                   </div>
                   <q-btn
                     flat dense
                     label="Generate"
                     class="evidence-btn"
                     style="color: var(--fg-red)"
                     @click="generateFIR"
                     :loading="generatingFIR"
                   />
                </div>
              </div>

              <!-- Open Analyst Case -->
              <div class="evidence-card fg-card mini">
                <div class="row items-center no-wrap gap-md">
                   <div class="evidence-icon-wrap" style="background: rgba(139, 92, 246, 0.15)">
                     <q-icon name="folder_open" size="24px" color="purple" />
                   </div>
                   <div class="col">
                     <div class="text-subtitle2 sora text-white">Open Analyst Case</div>
                     <div class="text-caption text-grey-6">Route to Case Manager for investigation.</div>
                   </div>
                   <q-btn flat dense label="Open" class="evidence-btn" style="color: #a78bfa" @click="openAnalystCase" :loading="creatingCase" />
                </div>
              </div>
            </div>

            <!-- Fraud Timeline -->
            <div class="q-mt-xl" v-if="fraudTimeline.length > 0">
              <div class="result-label mono q-mb-md">FRAUD EVENT TIMELINE</div>
              <q-timeline dark color="blue">
                <q-timeline-entry
                  v-for="(evt, i) in fraudTimeline"
                  :key="i"
                  :color="evt.severity === 'CRITICAL' ? 'negative' : evt.severity === 'HIGH' ? 'warning' : evt.severity === 'SUCCESS' ? 'positive' : 'blue'"
                  :icon="evt.icon"
                  :subtitle="evt.offset_min === 0 ? 'T+0 (NOW)' : `T${evt.offset_min}m`"
                >
                  <div class="text-white text-subtitle2 sora">{{ evt.event }}</div>
                  <div class="text-grey-5 text-caption">{{ evt.detail }}</div>
                  <div class="mono text-xs text-grey-6">Detected by: {{ evt.detected_by }}</div>
                </q-timeline-entry>
              </q-timeline>
            </div>
          </div>

          <!-- Placeholder -->
          <div v-else key="placeholder" class="fg-card result-placeholder-card">
            <div class="placeholder-anim">
              <div class="hexagon-grid">
                <div class="hex" v-for="n in 7" :key="n" :class="`h${n}`" />
              </div>
            </div>
            <div class="placeholder-title sora">Multi-modal Engine Ready</div>
            <div class="placeholder-sub">Fill at least one data source and click Run Analysis</div>
            <div class="data-sources">
              <div class="ds-item" :class="{ active: !!form.upi_id }">
                <q-icon name="account_balance" size="14px" /> Transaction
              </div>
              <div class="ds-item" :class="{ active: !!form.sms_text }">
                <q-icon name="sms" size="14px" /> SMS
              </div>
              <div class="ds-item" :class="{ active: !!form.call_transcript }">
                <q-icon name="mic" size="14px" /> Voice
              </div>
            </div>
          </div>

        </transition>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import { api } from 'boot/axios'
import { useAuthStore } from 'src/stores/authStore'

interface AnalysisResult {
  global_score: number;
  risk_level: string;
  recommendation: string;
  modalities_analyzed: string[];
  impact_breakdown?: Record<string, number>;
}

interface TruecallerResult {
  phone_number: string;
  spam_score: number;
  is_spam: boolean;
  labels: string[];
  community_reports: number;
}

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()
const activeTab = ref('transaction')
const loading = ref(false)
const result = ref<AnalysisResult | null>(null)
const fraudTimeline = ref<Array<{offset_min: number; event: string; detail: string; severity: string; icon: string; detected_by: string}>>([])
const creatingCase = ref(false)
const audioFile = ref<File | null>(null)
const isRecording = ref(false)
const transcriptionLoading = ref(false)
const fileInput = ref<HTMLInputElement>()
const analyzeProgress = ref(0)
const truecallerResult = ref<TruecallerResult | null>(null)
const truecallerLoading = ref(false)
const securingEvidence = ref(false)
const generatingFIR = ref(false)
const genAIBrief = ref<string | null>(null)

const voiceForm = reactive({
  caller_number: '',
})

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []

const deviceId = `DEV-${navigator.userAgent.length}-${screen.width}x${screen.height}`

const form = reactive({
  upi_id: '', amount: 0, device_id: deviceId, timestamp: '',
  payer_upi_id: authStore.userEmail ?? 'unknown@upi',
  payer_device_id: deviceId, payer_account_age_days: 0,
  is_post_call: false, user_avg_amount: 0, user_tx_count: 0,
  sms_text: '', call_transcript: '',
})

const tabs = [
  { key: 'transaction', label: 'Transaction', icon: 'receipt_long' },
  { key: 'sms',         label: 'SMS',         icon: 'sms'          },
  { key: 'voice',       label: 'Voice',       icon: 'mic'          },
]

const analyzeSteps = [
  'Processing transaction features',
  'Analyzing SMS patterns',
  'Evaluating voice transcript',
  'Fusing modalities',
  'Generating risk assessment',
]

onMounted(async () => {
  form.timestamp = new Date().toISOString()
  try {
    const res = await api.get('/auth/me')
    if (res.data) {
      form.payer_account_age_days = res.data.account_age_days || 1
      form.user_avg_amount = res.data.avg_amount || 0
      form.user_tx_count = res.data.tx_count || 0
    }
  } catch { /* silent */ }
})

const resultScoreColor = computed(() => {
  if (!result.value) return 'var(--fg-blue)'
  const s = result.value.global_score
  if (s > 75) return 'var(--fg-red)'
  if (s > 40) return 'var(--fg-amber)'
  return 'var(--fg-green)'
})

const resultCardClass = computed(() => {
  if (!result.value) return ''
  if (result.value.global_score > 75) return 'danger'
  if (result.value.global_score > 40) return 'warn'
  return 'safe'
})

function triggerFileUpload() { fileInput.value?.click() }
function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) { audioFile.value = target.files[0] }
}

function uploadAudio() {
  if (audioFile.value) void processAudio(audioFile.value)
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []
    mediaRecorder.ondataavailable = (e) => { audioChunks.push(e.data) }
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: 'audio/wav' })
      const file = new File([blob], 'memo.wav', { type: 'audio/wav' })
      audioFile.value = file
      void processAudio(file)
    }
    mediaRecorder.start()
    isRecording.value = true
  } catch {
    $q.notify({ color: 'negative', message: 'Microphone access denied' })
  }
}

function stopRecording() {
  mediaRecorder?.stop()
  isRecording.value = false
}

async function processAudio(file: File) {
  transcriptionLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/audio/analyze', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    pollTranscriptionResult(response.data.task_id)
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to upload audio' })
    transcriptionLoading.value = false
  }
}

function pollTranscriptionResult(taskId: string) {
  const poll = async () => {
    try {
      const response = await api.get(`/audio/result/${taskId}`)
      if (response.data.status === 'complete') {
        form.call_transcript = response.data.transcription
        transcriptionLoading.value = false
        $q.notify({ color: 'positive', message: 'Transcription complete', icon: 'mic' })
        void triggerAnalyzeCall()
      } else if (response.data.status === 'failed') {
        throw new Error('failed')
      } else { setTimeout(() => { void poll() }, 2000) }
    } catch {
      $q.notify({ color: 'negative', message: 'Transcription failed' })
      transcriptionLoading.value = false
    }
  }
  void poll()
}

async function checkTruecaller() {
  if (!voiceForm.caller_number) return
  truecallerLoading.value = true
  try {
    const res = await api.post('/calls/truecaller/check', { phone_number: voiceForm.caller_number })
    truecallerResult.value = res.data
  } catch {
    $q.notify({ color: 'negative', message: 'Truecaller check failed' })
  } finally {
    truecallerLoading.value = false
  }
}

async function triggerAnalyzeCall() {
  if (!form.call_transcript) return
  try {
    const res = await api.post('/calls/analyze', {
      transcript: form.call_transcript,
      caller_number: voiceForm.caller_number || null,
      payer_upi_id: form.payer_upi_id
    })
    if (res.data.ctc_window_started) {
      $q.notify({
        color: 'warning',
        icon: 'timer',
        message: '5-Minute CTC Window Activated: High correlation risk for pending payments',
        timeout: 5000
      })
    }
  } catch { /* Silent */ }
}

const getModalityColor = (mod: string) => {
  switch (mod.toLowerCase()) {
    case 'transaction': return 'var(--fg-blue)'
    case 'sms': return 'var(--fg-cyan)'
    case 'voice': return 'var(--fg-amber)'
    case 'graph': return 'var(--fg-purple)'
    default: return 'var(--fg-primary)'
  }
}

async function secureEvidence() {
  if (!result.value) return
  securingEvidence.value = true
  try {
    const bundle = {
      tx_id: `SEC-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
      upi_id: form.upi_id || 'UNKNOWN',
      evidence_type: result.value.modalities_analyzed[0] || 'multimodal',
      content_hash: 'SIMULATED_CONTENT_HASH',
      metadata: {
        global_score: result.value.global_score,
        risk_level: result.value.risk_level,
        recommendation: result.value.recommendation
      }
    }
    const res = await api.post('/advanced/evidence/bundle', bundle)
    $q.notify({
      color: 'positive',
      icon: 'security',
      message: `Evidence Secured: ${res.data.bundle_hash.substr(0, 16)}...`,
      timeout: 5000,
      caption: 'Stored in IPFS-backed Evidence Locker (Simulated)'
    })
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to secure evidence' })
  } finally {
    securingEvidence.value = false
  }
}

async function runAnalysis() {
  loading.value = true; result.value = null; analyzeProgress.value = 0
  const steps = analyzeSteps.length
  const interval = setInterval(() => {
    if (analyzeProgress.value < steps) analyzeProgress.value++
  }, 700)

  try {
    const payload = {
      transaction: {
        upi_id: form.upi_id, amount: form.amount, device_id: form.device_id,
        timestamp: new Date().toISOString(), payer_upi_id: form.payer_upi_id,
        payer_device_id: form.payer_device_id, payer_account_age_days: form.payer_account_age_days,
        is_post_call: form.is_post_call, user_avg_amount: form.user_avg_amount, user_tx_count: form.user_tx_count,
      },
      sms_text: form.sms_text || null,
      call_transcript: form.call_transcript || null,
    }
    const response = await api.post('/multi/verify', payload)
    result.value = response.data
    
    // Automatically trigger GenAI LLM brief and timeline if result is generated
    void fetchGenAIBrief()
    if (response.data.global_score > 40) {
      void fetchTimeline(`TX-${Date.now()}`)
    }
  } catch {
    $q.notify({ color: 'negative', message: 'Analysis failed. Ensure all services are running.', icon: 'error' })
  } finally {
    clearInterval(interval)
    loading.value = false
  }
}

async function fetchGenAIBrief() {
  if (!result.value) return
  genAIBrief.value = null
  try {
    const res = await api.post('/genai/threat-brief', {
      tx_id: 'AI-TX-888',
      amount: form.amount || 0,
      risk_score: result.value.global_score,
      modalities_flagged: result.value.modalities_analyzed
    })
    genAIBrief.value = res.data.generated_brief
  } catch { /* Silent fail for LLM */ }
}

async function generateFIR() {
  if (!result.value) return
  generatingFIR.value = true
  try {
    const req = {
      tx_id: 'TX-INT-19803',
      evidence_bundle_hash: 'SIMULATED-EVIDENCE-HASH',
      victim_upi: form.payer_upi_id || 'unknown@upi',
      threat_description: genAIBrief.value || 'Multi-modal threat detected.'
    }
    await api.post('/legal/generate-fir', req)
    $q.notify({
      color: 'negative', icon: 'gavel',
      message: 'FIR Payload sent to 1930 Cybercrime Portal!',
      caption: 'Status: DRAFT_READY_FOR_FILING', timeout: 6000
    })
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to generate FIR.' })
  } finally {
    generatingFIR.value = false
  }
}

async function openAnalystCase() {
  if (!result.value) return
  creatingCase.value = true
  try {
    const res = await api.post('/cases/create', {
      tx_id: `TX-${Date.now()}`,
      upi_id: form.upi_id || 'unknown@upi',
      risk_score: result.value.global_score,
      risk_level: result.value.risk_level,
      summary: genAIBrief.value || result.value.recommendation
    })
    $q.notify({
      color: 'purple',
      icon: 'folder_open',
      message: `Case ${res.data.case_id} created!`,
      caption: 'Navigating to Case Manager...',
      timeout: 2000
    })
    setTimeout(() => { void router.push('/cases') }, 2000)
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to open case' })
  } finally {
    creatingCase.value = false
  }
}

async function fetchTimeline(txId: string) {
  fraudTimeline.value = []
  try {
    const res = await api.get(`/soc/timeline/${txId}`)
    fraudTimeline.value = res.data.timeline
  } catch { /* Silent */ }
}
</script>

<style scoped lang="scss">
.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;

  @media (max-width: 900px) { grid-template-columns: 1fr; }
}

// Input Panel
.input-panel {
  background: var(--fg-card);
  border: 1px solid var(--fg-border);
  border-radius: var(--fg-radius-lg);
  overflow: hidden;
}

.modality-tabs {
  display: flex;
  background: var(--fg-surface);
  border-bottom: 1px solid var(--fg-border);
}

.modality-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 13px 8px;
  border: none;
  background: none;
  color: var(--fg-text-muted);
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all 0.15s ease;

  &.active {
    color: var(--fg-blue);
    background: rgba(59,130,246,0.06);
    box-shadow: inset 0 -2px 0 var(--fg-blue);
  }

  .tab-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--fg-green);
    position: absolute;
    top: 10px; right: calc(50% - 16px);
  }
}

.tab-content { padding: 20px; }

.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px; }

.fg-field { display: flex; flex-direction: column; gap: 6px; }

.fg-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.2px;
  color: var(--fg-text-muted);
  text-transform: uppercase;
}

.fg-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 9px;
  padding: 0 12px;
  color: var(--fg-text-muted);
  transition: all 0.15s ease;

  &:focus-within {
    border-color: var(--fg-blue);
    box-shadow: 0 0 0 3px var(--fg-blue-glow);
    color: var(--fg-blue);
  }

  .input-prefix { font-size: 14px; }
}

.fg-input-el {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--fg-text-primary);
  font-family: 'DM Mono', monospace;
  font-size: 13px;
  padding: 11px 0;

  &::placeholder { color: var(--fg-text-muted); }
}

.fg-textarea {
  width: 100%;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 10px;
  padding: 12px;
  color: var(--fg-text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  resize: vertical;
  outline: none;
  transition: all 0.15s ease;

  &::placeholder { color: var(--fg-text-muted); }
  &:focus { border-color: var(--fg-blue); box-shadow: 0 0 0 3px var(--fg-blue-glow); }
  &:disabled { opacity: 0.5; }
}

.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.toggle-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.custom-toggle {
  width: 40px; height: 22px;
  border-radius: 11px;
  background: var(--fg-border);
  border: 1px solid var(--fg-muted);
  position: relative;
  transition: all 0.2s ease;
  flex-shrink: 0;

  &.on { background: var(--fg-blue); border-color: var(--fg-blue); }

  .toggle-knob {
    position: absolute;
    top: 2px; left: 2px;
    width: 16px; height: 16px;
    border-radius: 50%;
    background: white;
    transition: transform 0.2s ease;
    box-shadow: var(--fg-shadow-sm);
  }

  &.on .toggle-knob { transform: translateX(18px); }
}

.toggle-label { font-size: 13px; color: var(--fg-text-secondary); }

.post-call-badge {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  letter-spacing: 0.5px;
  background: rgba(42,58,85,0.6);
  color: var(--fg-text-muted);
  flex-shrink: 0;

  &.active { background: rgba(239,68,68,0.1); color: var(--fg-red); }
}

.sms-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(245,158,11,0.06);
  border: 1px solid rgba(245,158,11,0.15);
  border-radius: 8px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--fg-text-muted);
}

// Voice
.voice-controls { display: flex; flex-direction: column; gap: 0; }

.upload-zone {
  border: 2px dashed var(--fg-border);
  border-radius: 12px;
  padding: 28px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;

  &:hover { border-color: var(--fg-blue); background: var(--fg-blue-soft); }
  &.has-file { border-color: rgba(59,130,246,0.4); background: var(--fg-blue-soft); border-style: solid; }
}

.hidden-input { display: none; }
.upload-label { font-size: 13px; font-weight: 500; color: var(--fg-text-secondary); }
.upload-sub   { font-size: 11px; color: var(--fg-text-muted); font-family: 'DM Mono', monospace; }

.upload-analyze-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: var(--fg-blue);
  border: none;
  border-radius: 7px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 4px;
}

.divider-or {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--fg-text-muted);
  font-size: 12px;
  margin: 12px 0;

  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--fg-border);
  }
}

.truecaller-btn {
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.25);
  color: var(--fg-blue);
  font-size: 10px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 5px;
  cursor: pointer;
  
  &:hover { background: rgba(59,130,246,0.18); }
  &:disabled { opacity: 0.5; }
}

.truecaller-result {
  margin-top: 10px;
  padding: 12px;
  background: rgba(16,185,129,0.06);
  border: 1px solid rgba(16,185,129,0.15);
  border-radius: 9px;
  
  &.spam {
    background: rgba(239,68,68,0.06);
    border-color: rgba(239,68,68,0.15);
    
    .tr-label, .tr-score { color: var(--fg-red); }
  }
}

.tr-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.tr-label { font-size: 10px; font-weight: 700; color: var(--fg-green); }
.tr-score { font-size: 10px; font-weight: 700; color: var(--fg-green); }

.tr-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.tr-tag {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--fg-border);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 9px;
  color: var(--fg-text-secondary);
}

.tr-reports {
  font-size: 9px;
  color: var(--fg-text-muted);
}

.record-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 10px;
  color: var(--fg-text-secondary);
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &.recording {
    background: rgba(239,68,68,0.08);
    border-color: rgba(239,68,68,0.3);
    color: var(--fg-red);
  }
}

.record-icon { position: relative; }
.record-pulse {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 2px solid var(--fg-red);
  animation: record-pulse 1.2s ease infinite;
}

@keyframes record-pulse {
  0%   { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.8); opacity: 0; }
}

.transcribing-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--fg-blue);
  font-size: 10px;
  font-weight: 500;
  margin-left: 8px;
}

.run-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, var(--fg-blue), #2563EB);
  border: none;
  border-radius: 0 0 var(--fg-radius-lg) var(--fg-radius-lg);
  color: white;
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(59,130,246,0.3);
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    box-shadow: 0 6px 22px rgba(59,130,246,0.5);
    filter: brightness(1.05);
  }

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

// Result Panel
.result-panel { position: sticky; top: 80px; }

.result-loading-card {
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.analysis-progress { display: flex; flex-direction: column; align-items: center; gap: 20px; }
.progress-ring { margin-bottom: 4px; }
.progress-title { font-size: 18px; font-weight: 700; color: var(--fg-text-primary); }
.progress-steps { display: flex; flex-direction: column; gap: 8px; width: 100%; max-width: 240px; }
.p-step {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: var(--fg-text-muted);
  font-family: 'DM Mono', monospace;
  transition: color 0.3s ease;

  &.done { color: var(--fg-green); }
}

.result-display-card {
  padding: 24px;

  &.danger { border-color: rgba(239,68,68,0.3) !important; }
  &.warn   { border-color: rgba(245,158,11,0.3) !important; }
  &.safe   { border-color: rgba(16,185,129,0.3) !important; }
}

.result-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 10px;
}

.result-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.2px;
  color: var(--fg-text-muted);
  text-transform: uppercase;
}

.result-modalities { display: flex; gap: 6px; flex-wrap: wrap; }
.modality-tag {
  padding: 2px 8px;
  background: var(--fg-blue-soft);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 6px;
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: var(--fg-blue);
  text-transform: lowercase;
}

.score-svg-full { width: 180px; height: 180px; display: block; margin: 0 auto 16px; }
.score-inner {
  text-align: center;
  position: relative;
  margin-top: -20px;
}
.score-num { font-size: 56px; font-weight: 800; line-height: 1; }
.score-txt { font-size: 10px; letter-spacing: 1.5px; color: var(--fg-text-muted); margin-top: 4px; }

.risk-level-badge {
  display: inline-block;
  width: 100%;
  text-align: center;
  padding: 8px;
  border-radius: 10px;
  font-family: 'Sora', sans-serif;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 16px;

  &.safe   { background: rgba(16,185,129,0.1); color: var(--fg-green); }
  &.warn   { background: rgba(245,158,11,0.1); color: var(--fg-amber); }
  &.danger { background: rgba(239,68,68,0.1);  color: var(--fg-red);   }
}

.recommendation-box {
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 10px;
  padding: 14px;
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: var(--fg-text-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.rec-text { font-size: 13px; color: var(--fg-text-secondary); line-height: 1.6; }

// XAI Impact
.impact-grid { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.impact-row { display: flex; flex-direction: column; gap: 4px; }
.impact-info { display: flex; justify-content: space-between; font-size: 11px; }
.impact-mod { font-weight: 600; color: var(--fg-text-secondary); }
.impact-pct { color: var(--fg-text-muted); }
.impact-bar-bg { width: 100%; height: 4px; background: rgba(255,255,255,0.04); border-radius: 2px; }
.impact-bar-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }

// Evidence Locker
.evidence-card {
  padding: 12px;
  background: linear-gradient(135deg, rgba(59,130,246,0.05), rgba(6,182,212,0.05)) !important;
  border: 1px dashed var(--fg-blue) !important;
  
  &.mini { padding: 12px 16px; }
}
.evidence-icon-wrap {
  width: 40px; height: 40px;
  border-radius: 10px;
  background: rgba(59,130,246,0.1);
  display: flex; align-items: center; justify-content: center;
}
.evidence-btn {
  background: var(--fg-blue) !important;
  color: white !important;
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  padding: 4px 12px !important;
  border-radius: 6px !important;
}

// Placeholder
.result-placeholder-card {
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.placeholder-anim { margin-bottom: 8px; }
.hexagon-grid {
  width: 100px; height: 80px;
  position: relative;
  margin: 0 auto;
  display: flex; flex-wrap: wrap; gap: 4px; justify-content: center;
}

.hex {
  width: 20px; height: 20px;
  background: var(--fg-border);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  animation: hex-pulse 2s ease-in-out infinite;

  @for $i from 1 through 7 {
    &.h#{$i} { animation-delay: #{($i - 1) * 0.2}s; }
  }
}

@keyframes hex-pulse {
  0%, 100% { opacity: 0.2; transform: scale(0.9); }
  50%       { opacity: 0.8; transform: scale(1.05); }
}

.placeholder-title { font-size: 18px; font-weight: 700; color: var(--fg-text-primary); }
.placeholder-sub   { font-size: 13px; color: var(--fg-text-muted); }

.data-sources {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.ds-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 8px;
  border: 1px solid var(--fg-border);
  font-size: 12px;
  color: var(--fg-text-muted);
  transition: all 0.2s ease;

  &.active {
    border-color: rgba(16,185,129,0.3);
    color: var(--fg-green);
    background: rgba(16,185,129,0.06);
  }
}

// Transitions
.result-fade-enter-active, .result-fade-leave-active { transition: all 0.3s ease; }
.result-fade-enter-from   { opacity: 0; transform: translateY(10px) scale(0.98); }
.result-fade-leave-to     { opacity: 0; transform: translateY(-10px) scale(0.98); }

.tab-fade-enter-active, .tab-fade-leave-active { transition: all 0.2s ease; }
.tab-fade-enter-from   { opacity: 0; transform: translateX(8px); }
.tab-fade-leave-to     { opacity: 0; transform: translateX(-8px); }
</style>
