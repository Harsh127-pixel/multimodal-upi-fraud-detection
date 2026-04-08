<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="row items-center justify-between">
        <div>
          <div class="page-title sora">SOC Operations Center</div>
          <div class="page-subtitle">Live Security Operations — Auto-refreshes every 30s</div>
        </div>
        <div class="row items-center gap-md">
          <q-chip :color="isLive ? 'positive' : 'grey'" icon="fiber_manual_record" text-color="white" label="LIVE" class="mono pulsing" />
          <q-btn flat icon="refresh" label="Refresh" color="blue" @click="fetchAll" class="mono" />
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid fade-up fade-up-2">
      <div class="kpi-card danger-card">
        <q-icon name="block" size="28px" class="kpi-icon" />
        <div class="kpi-val sora">{{ metrics.blocked_today }}</div>
        <div class="kpi-label mono">BLOCKED TODAY</div>
      </div>
      <div class="kpi-card safe-card">
        <q-icon name="check_circle_outline" size="28px" class="kpi-icon" />
        <div class="kpi-val sora">{{ metrics.allowed_today?.toLocaleString() }}</div>
        <div class="kpi-label mono">ALLOWED TODAY</div>
      </div>
      <div class="kpi-card warn-card">
        <q-icon name="campaign" size="28px" class="kpi-icon" />
        <div class="kpi-val sora">{{ metrics.honeypot_hits_today }}</div>
        <div class="kpi-label mono">HONEYPOT HITS</div>
      </div>
      <div class="kpi-card blue-card">
        <q-icon name="folder_open" size="28px" class="kpi-icon" />
        <div class="kpi-val sora">{{ metrics.active_cases }}</div>
        <div class="kpi-label mono">ACTIVE CASES</div>
      </div>
      <div class="kpi-card purple-card">
        <q-icon name="dark_mode" size="28px" class="kpi-icon" />
        <div class="kpi-val sora">{{ metrics.darkweb_alerts }}</div>
        <div class="kpi-label mono">DARKWEB ALERTS</div>
      </div>
      <div class="kpi-card neutral-card">
        <q-icon name="speed" size="28px" class="kpi-icon" />
        <div class="kpi-val sora">{{ metrics.avg_response_ms }}ms</div>
        <div class="kpi-label mono">AVG RESPONSE</div>
      </div>
    </div>

    <div class="row q-col-gutter-xl q-mt-lg">
      <!-- Threat Heatmap (Indian Cities) -->
      <div class="col-12 col-md-7 fade-up fade-up-3">
        <div class="fg-card">
          <div class="section-label mono q-mb-md">INDIA TRANSACTION RISK HEATMAP</div>
          <div class="map-placeholder">
            <svg viewBox="0 0 600 520" class="india-map-svg">
              <!-- Simplified India outline placeholder -->
              <rect width="600" height="520" fill="rgba(255,255,255,0.02)" rx="12" />
              <text x="300" y="260" text-anchor="middle" fill="rgba(255,255,255,0.1)" font-size="80" font-family="sans-serif">🇮🇳</text>
              <!-- Heatmap dots -->
              <g v-for="(pt, i) in heatmap" :key="i">
                <circle
                  :cx="lngToX(pt.lng)"
                  :cy="latToY(pt.lat)"
                  :r="Math.max(8, pt.fraud_count * 1.5)"
                  :fill="riskColor(pt.risk_level)"
                  opacity="0.7"
                  class="heatmap-dot"
                />
                <text :x="lngToX(pt.lng)" :y="latToY(pt.lat) + 20" text-anchor="middle" fill="rgba(255,255,255,0.7)" font-size="10">{{ pt.city }}</text>
              </g>
            </svg>
          </div>
          <div class="row q-mt-sm" style="gap: 16px">
            <div class="row items-center gap-xs"><span class="dot" style="background:#10b981"></span><span class="text-caption text-grey">Low</span></div>
            <div class="row items-center gap-xs"><span class="dot" style="background:#f59e0b"></span><span class="text-caption text-grey">Medium</span></div>
            <div class="row items-center gap-xs"><span class="dot" style="background:#ef4444"></span><span class="text-caption text-grey">High</span></div>
          </div>
        </div>
      </div>

      <!-- Top Threats Panel -->
      <div class="col-12 col-md-5 fade-up fade-up-4">
        <div class="fg-card full-height">
          <div class="section-label mono q-mb-md">TOP ACTIVE THREAT ACTORS</div>
          <q-list dark separator>
            <q-item v-for="t in threats" :key="t.rank" class="threat-item">
              <q-item-section avatar>
                <q-avatar :color="t.status === 'BLACKLISTED' ? 'negative' : 'warning'" text-color="white" size="36px" class="mono text-bold">
                  #{{ t.rank }}
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label class="mono text-bold text-red-4">{{ t.upi_id }}</q-item-label>
                <q-item-label caption>{{ t.type }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <div class="column items-end">
                  <div class="mono text-bold">{{ t.hits }} hits</div>
                  <q-chip :color="t.status === 'BLACKLISTED' ? 'negative' : 'warning'" size="xs" :label="t.status" dense />
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </div>
      </div>
    </div>

    <!-- Block Rate Meter -->
    <div class="fg-card q-mt-xl fade-up fade-up-5">
      <div class="section-label mono q-mb-md">SYSTEM BLOCK RATE</div>
      <div class="row items-center gap-xl">
        <div class="block-rate-display sora">{{ metrics.block_rate_pct }}%</div>
        <div class="col">
          <q-linear-progress
            :value="(metrics.block_rate_pct || 0) / 100"
            size="24px"
            :color="(metrics.block_rate_pct || 0) > 2 ? 'negative' : 'positive'"
            track-color="rgba(255,255,255,0.08)"
            style="border-radius: 12px"
          />
          <div class="row justify-between q-mt-xs">
            <span class="text-caption text-grey">0% (No Fraud)</span>
            <span class="text-caption text-grey">Uptime: {{ metrics.uptime_pct }}%</span>
            <span class="text-caption text-grey">100% (Full Block)</span>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const isLive = ref(true)

interface SOCMetrics {
  blocked_today: number
  allowed_today: number
  block_rate_pct: number
  honeypot_hits_today: number
  active_cases: number
  darkweb_alerts: number
  uptime_pct: number
  avg_response_ms: number
}

interface HeatmapPoint {
  city: string; lat: number; lng: number; tx_count: number; fraud_count: number; risk_level: string;
}

interface ThreatEntry {
  rank: number; upi_id: string; hits: number; type: string; status: string;
}

const metrics = ref<Partial<SOCMetrics>>({})
const heatmap = ref<HeatmapPoint[]>([])
const threats = ref<ThreatEntry[]>([])

// Map lat/lng to SVG coords (simplified India bounding box)
const LAT_MAX = 37, LAT_MIN = 8, LNG_MAX = 97, LNG_MIN = 68
function latToY(lat: number) { return ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * 480 + 20 }
function lngToX(lng: number) { return ((lng - LNG_MIN) / (LNG_MAX - LNG_MIN)) * 560 + 20 }
function riskColor(level: string) {
  if (level === 'HIGH') return '#ef4444'
  if (level === 'MEDIUM') return '#f59e0b'
  return '#10b981'
}

async function fetchAll() {
  try {
    const [m, h, t] = await Promise.all([
      api.get('/soc/metrics'),
      api.get('/soc/heatmap'),
      api.get('/soc/top-threats'),
    ])
    metrics.value = m.data
    heatmap.value = h.data.points
    threats.value = t.data.threats
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to fetch SOC data' })
  }
}

let timer: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  void fetchAll()
  timer = setInterval(() => { void fetchAll() }, 30000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped lang="scss">
.page-wrapper { padding: 32px; max-width: 1400px; margin: 0 auto; }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-top: 28px;
  @media (max-width: 1100px) { grid-template-columns: repeat(3, 1fr); }
  @media (max-width: 600px) { grid-template-columns: repeat(2, 1fr); }
}

.kpi-card {
  padding: 20px 16px;
  border-radius: 14px;
  border: 1px solid var(--fg-border);
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  transition: transform 0.2s;
  &:hover { transform: translateY(-2px); }
}

.danger-card { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); .kpi-icon { color: #ef4444; } }
.safe-card { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); .kpi-icon { color: #10b981; } }
.warn-card { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.3); .kpi-icon { color: #f59e0b; } }
.blue-card { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); .kpi-icon { color: #3b82f6; } }
.purple-card { background: rgba(139, 92, 246, 0.1); border-color: rgba(139, 92, 246, 0.3); .kpi-icon { color: #8b5cf6; } }
.neutral-card { background: rgba(255,255,255,0.04); .kpi-icon { color: var(--fg-text-secondary); } }

.kpi-val { font-size: 28px; font-weight: 700; color: var(--fg-text-primary); line-height: 1; }
.kpi-label { font-size: 10px; letter-spacing: 0.08em; color: var(--fg-text-secondary); }

.map-placeholder { background: rgba(255,255,255,0.02); border-radius: 12px; overflow: hidden; }
.india-map-svg { width: 100%; height: auto; min-height: 320px; }
.heatmap-dot { transition: r 0.5s; }

.threat-item { padding: 12px 0; }
.block-rate-display { font-size: 42px; font-weight: 700; color: var(--fg-text-primary); min-width: 100px; }
.dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }

.pulsing {
  animation: pulse-glow 2s infinite;
}
@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
