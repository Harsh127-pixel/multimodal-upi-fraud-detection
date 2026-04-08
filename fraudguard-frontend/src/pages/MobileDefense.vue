<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="row items-center justify-between">
        <div>
          <div class="page-title sora">Mobile Defense</div>
          <div class="page-subtitle">Proactive protection for your mobile environment</div>
        </div>
        <q-chip
          :color="healthColor"
          text-color="white"
          :label="'DEVICESTATUS: ' + status.overall_health"
          class="status-chip mono"
          icon="shield"
        />
      </div>
    </div>

    <div class="defense-grid">
      <!-- Device Telemetry Panel -->
      <div class="defense-col fade-up fade-up-2">
        <div class="fg-card telemetry-card">
          <div class="section-label mono">DEVICE TELEMETRY & INTEGRITY</div>
          
          <div class="health-gauge q-my-lg">
             <q-knob
                readonly
                v-model="status.score"
                size="120px"
                :thickness="0.15"
                :color="healthColor"
                track-color="rgba(255,255,255,0.05)"
                class="knob-sora"
              >
                <div class="knob-inner">
                  <div class="knob-val sora">{{ status.score }}</div>
                  <div class="knob-label mono">SECURITY</div>
                </div>
              </q-knob>
          </div>

          <div class="telemetry-items">
            <div class="tel-item" :class="{ danger: tele.is_rooted }">
              <q-icon :name="tele.is_rooted ? 'warning' : 'check_circle'" size="16px" />
              <span class="col">OS Integrity (Root Detection)</span>
              <span class="mono">{{ tele.is_rooted ? 'COMPROMISED' : 'SECURE' }}</span>
            </div>
            <div class="tel-item" :class="{ danger: tele.active_overlay_apps.length > 0 }">
              <q-icon :name="tele.active_overlay_apps.length > 0 ? 'visibility' : 'visibility_off'" size="16px" />
              <span class="col">Remote Overlay Apps</span>
              <span class="mono">{{ tele.active_overlay_apps.length || 'NONE' }}</span>
            </div>
            <div class="tel-item">
              <q-icon name="sim_card" size="16px" />
              <span class="col">SIM Slot #1</span>
              <span class="mono">{{ tele.sim_serial.substr(0,12) }}...</span>
            </div>
             <div class="tel-item">
              <q-icon name="location_on" size="16px" />
              <span class="col">Geofence Status</span>
              <span class="mono">ACTIVE (INDIA)</span>
            </div>
            <div class="tel-item" :class="{ danger: tele.wifi_security === 'OPEN' || tele.wifi_security === 'WEP' }">
              <q-icon name="wifi" size="16px" />
              <span class="col">Network Security</span>
              <span class="mono">{{ tele.wifi_security }}</span>
            </div>
            <div class="tel-item" :class="{ danger: tele.accessibility_services_enabled }">
              <q-icon name="touch_app" size="16px" />
              <span class="col">Accessibility Intent Guard</span>
              <span class="mono">{{ tele.accessibility_services_enabled ? 'TRIGGERED' : 'SAFE' }}</span>
            </div>
            <div class="tel-item">
              <q-icon name="keyboard" size="16px" />
              <span class="col">Active Keyboards</span>
              <span class="mono">{{ tele.active_keyboards.length }}</span>
            </div>
          </div>

          <div class="threat-list q-mt-lg" v-if="status.threats.length > 0">
            <div class="threat-header mono">ACTIVE THREATS</div>
            <div v-for="(threat, i) in status.threats" :key="i" class="threat-row">
               <q-icon name="bolt" color="red" size="14px" />
               <span>{{ threat }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Shielding Tools -->
      <div class="defense-col fade-up fade-up-3">
        <div class="fg-card tools-card">
          <div class="section-label mono">ACTIVE SHIELDING TOOLS</div>
          
          <div class="tool-section q-mb-xl">
             <div class="tool-header row items-center gap-md q-mb-md">
                <div class="tool-icon bg-cyan"><q-icon name="qr_code_scanner" color="white" /></div>
                <div>
                   <div class="text-subtitle2 sora text-white">QR Sentry</div>
                   <div class="text-caption text-grey-6">Scan and verify UPI QR codes before payment.</div>
                </div>
             </div>
             <q-input
                v-model="qrData"
                placeholder="Paste UPI deep link (e.g. upi://pay?pa=...)"
                filled
                dark
                class="fg-input"
             >
                <template v-slot:append>
                   <q-btn flat icon="radar" @click="verifyQR" color="cyan" :loading="scanningQR" />
                </template>
             </q-input>
             <div v-if="qrResult" class="q-mt-sm result-box" :class="qrResult.status.toLowerCase()">
                <div class="row items-center gap-sm">
                   <q-icon :name="qrResult.status === 'SECURE' ? 'verified' : 'error'" size="14px" />
                   <span class="mono text-bold">{{ qrResult.status }}</span>
                </div>
                <div class="text-caption" v-if="qrResult.reason">{{ qrResult.reason }}</div>
                <div class="text-caption" v-if="qrResult.merchant">Merchant: {{ qrResult.merchant }}</div>
             </div>
          </div>

          <div class="tool-section q-mb-xl">
             <div class="tool-header row items-center gap-md q-mb-md">
                <div class="tool-icon bg-blue"><q-icon name="surfing" color="white" /></div>
                <div>
                   <div class="text-subtitle2 sora text-white">SMS Link Sandbox</div>
                   <div class="text-caption text-grey-6">Detonate suspicious URLs in an isolated browser.</div>
                </div>
             </div>
             <q-input
                v-model="smsUrl"
                placeholder="https://axis-bank-update.xyz/..."
                filled
                dark
                class="fg-input"
             >
                <template v-slot:append>
                   <q-btn flat icon="biotech" @click="sandboxLink" color="blue" :loading="sandboxing" />
                </template>
             </q-input>
             <div v-if="smsResult" class="q-mt-sm result-box" :class="smsResult.status.toLowerCase()">
                <div class="row items-center gap-sm">
                   <q-icon :name="smsResult.status === 'SAFE' ? 'check_circle' : 'mood_bad'" size="14px" />
                   <span class="mono text-bold">{{ smsResult.status }} - {{ smsResult.threat_type || 'CLEAR' }}</span>
                </div>
                <div class="text-caption">Final URL: {{ smsResult.final_url }}</div>
             </div>
          </div>

          <div class="tool-section q-mb-xl">
             <div class="tool-header row items-center gap-md q-mb-md">
                <div class="tool-icon bg-purple"><q-icon name="content_paste_search" color="white" /></div>
                <div>
                   <div class="text-subtitle2 sora text-white">Clipboard Poisoning Sentry</div>
                   <div class="text-caption text-grey-6">Scan pasted strings for known scammer profiles.</div>
                </div>
             </div>
             <q-input
                v-model="clipboardText"
                placeholder="Paste copied UPI id or Bank Acc..."
                filled
                dark
                class="fg-input"
             >
                <template v-slot:append>
                   <q-btn flat icon="screen_search_desktop" @click="scanClipboard" color="purple" :loading="scanningClipboard" />
                </template>
             </q-input>
             <div v-if="clipboardResult" class="q-mt-sm result-box" :class="clipboardResult.status === 'POISONED' ? 'danger' : 'safe'">
                <div class="row items-center gap-sm">
                   <q-icon :name="clipboardResult.status === 'CLEAN' ? 'check_circle' : 'warning'" size="14px" />
                   <span class="mono text-bold">{{ clipboardResult.status }}</span>
                </div>
                <div class="text-caption" v-if="clipboardResult.intercepted_match">Intercepted Match: {{ clipboardResult.intercepted_match }}</div>
             </div>
          </div>

          <div class="tool-section">
             <div class="tool-header row items-center gap-md q-mb-md">
                <div class="tool-icon bg-orange"><q-icon name="ring_volume" color="white" /></div>
                <div>
                   <div class="text-subtitle2 sora text-white">Vishing Call Interceptor</div>
                   <div class="text-caption text-grey-6">Filter numbers against the cybercrime global blacklist & check deepfake probability.</div>
                </div>
             </div>
             <q-input
                v-model="callId"
                placeholder="Enter caller number (+91...)"
                filled
                dark
                class="fg-input"
             >
                <template v-slot:append>
                   <q-btn flat icon="call_end" @click="interceptCall" color="orange" :loading="interceptingCall" />
                </template>
             </q-input>
             <div v-if="callResult" class="q-mt-sm result-box" :class="callResult.action === 'DROP_CALL' ? 'danger' : 'safe'">
                <div class="row items-center gap-sm">
                   <q-icon :name="callResult.action === 'ALLOW' ? 'check_circle' : 'call_missed'" size="14px" />
                   <span class="mono text-bold">{{ callResult.action }}</span>
                </div>
                <div class="text-caption">Deepfake Match Prob: {{ (callResult.deepfake_probability * 100).toFixed(1) }}%</div>
             </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

interface QRResult {
  status: string;
  reason?: string;
  merchant?: string;
  risk_score?: number;
}

interface SMSResult {
  status: string;
  threat_type?: string;
  final_url: string;
  screenshot_url?: string;
}

interface ClipboardResult {
  status: string;
  intercepted_match?: string;
  action_taken: string;
}

interface CallResult {
  action: string;
  reason: string;
  deepfake_probability: number;
}

const $q = useQuasar()

const tele = reactive({
  device_id: 'FG-MOB-X992',
  is_rooted: false,
  active_overlay_apps: [] as string[],
  sim_serial: '8991001299384882771Q',
  location: { lat: 12.9716, lng: 77.5946 },
  ips_connected: ['192.168.1.5'],
  wifi_security: 'WPA2',
  active_keyboards: ['com.google.android.inputmethod.latin'],
  accessibility_services_enabled: false
})

const status = reactive({
  overall_health: 'SECURE',
  threats: [] as string[],
  score: 100,
  recommendations: [] as string[]
})

const qrData = ref('')
const scanningQR = ref(false)
const qrResult = ref<QRResult | null>(null)

const smsUrl = ref('')
const sandboxing = ref(false)
const smsResult = ref<SMSResult | null>(null)

const clipboardText = ref('')
const scanningClipboard = ref(false)
const clipboardResult = ref<ClipboardResult | null>(null)

const callId = ref('')
const interceptingCall = ref(false)
const callResult = ref<CallResult | null>(null)

const healthColor = computed(() => {
  if (status.overall_health === 'COMPROMISED') return 'negative'
  if (status.overall_health === 'WARNED') return 'amber'
  return 'positive'
})

async function fetchTelemetry() {
  try {
    const res = await api.post('/mobile/telemetry', tele)
    Object.assign(status, res.data)
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to sync mobile telemetry' })
  }
}

async function verifyQR() {
  if (!qrData.value) return
  scanningQR.value = true
  try {
    const res = await api.post('/mobile/qr/verify', { qr_data: qrData.value })
    qrResult.value = res.data
  } finally {
    scanningQR.value = false
  }
}

async function sandboxLink() {
  if (!smsUrl.value) return
  sandboxing.value = true
  try {
    const res = await api.post('/mobile/sms/sandbox', { url: smsUrl.value, sms_text: 'Manual analysis' })
    smsResult.value = res.data
  } finally {
    sandboxing.value = false
  }
}

async function scanClipboard() {
  if (!clipboardText.value) return
  scanningClipboard.value = true
  try {
    const res = await api.post('/mobile/clipboard/scan', { pasted_text: clipboardText.value })
    clipboardResult.value = res.data
  } finally {
    scanningClipboard.value = false
  }
}

async function interceptCall() {
  if (!callId.value) return
  interceptingCall.value = true
  try {
    const res = await api.post('/mobile/call/intercept', { caller_id: callId.value, caller_name: 'Unknown' })
    callResult.value = res.data
  } finally {
    interceptingCall.value = false
  }
}

// Simulation: Randomly trigger threats for demo
onMounted(async () => {
  await fetchTelemetry()
  setTimeout(() => {
    void (async () => {
      tele.active_keyboards = ['com.hacker.evilkeyboard']
      tele.accessibility_services_enabled = true
      await fetchTelemetry()
      $q.notify({
        color: 'negative',
        icon: 'keyboard',
        message: 'CRITICAL: Untrusted Keyboard & Accessibility Abuse Detected',
        caption: 'Payment gateway blocked until keyboard is reverted'
      })
    })()
  }, 10000)
})
</script>

<style scoped lang="scss">
.page-wrapper {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.defense-grid {
  display: grid;
  grid-template-columns: 440px 1fr;
  gap: 24px;
  @media (max-width: 900px) { grid-template-columns: 1fr; }
}

.status-chip {
  padding: 0 16px;
  font-weight: 700;
  letter-spacing: 1px;
}

.health-gauge {
  display: flex;
  justify-content: center;
}

.knob-inner {
  text-align: center;
}
.knob-val { font-size: 32px; font-weight: 800; line-height: 1; color: white; }
.knob-label { font-size: 10px; color: var(--fg-text-muted); margin-top: 4px; }

.telemetry-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tel-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--fg-text-secondary);

  &.danger {
    background: rgba(239, 68, 68, 0.05);
    border-color: rgba(239, 68, 68, 0.2);
    color: var(--fg-red);
  }
}

.threat-header {
  font-size: 11px;
  color: var(--fg-red);
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.threat-row {
  font-size: 12px;
  color: var(--fg-red);
  background: rgba(239, 68, 68, 0.08);
  padding: 8px 12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.tool-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}

.bg-cyan { background: var(--fg-cyan); box-shadow: 0 4px 12px rgba(6,182,212,0.3); }
.bg-blue { background: var(--fg-blue); box-shadow: 0 4px 12px rgba(59,130,246,0.3); }

.result-box {
  padding: 10px;
  border-radius: 8px;
  font-size: 12px;
  
  &.secure, &.safe { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: var(--fg-green); }
  &.malicious, &.danger { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: var(--fg-red); }
}

.fg-input :deep(.q-field__control) {
  border-radius: 12px !important;
  background: rgba(255,255,255,0.03) !important;
}
</style>
