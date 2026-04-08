<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="page-title sora">India Fraud Risk Map</div>
      <div class="page-subtitle">State-level fraud density — Click a state for a breakdown</div>
    </div>

    <div class="row q-col-gutter-xl q-mt-md">
      <!-- SVG Map -->
      <div class="col-12 col-md-7 fade-up fade-up-2">
        <div class="fg-card">
          <div class="section-label mono q-mb-md">CHOROPLETH — FRAUD DENSITY BY STATE</div>
          <div class="map-wrap">
            <svg viewBox="0 0 520 580" class="india-svg">
              <!-- Simplified state shapes via ellipses + labels (representational) -->
              <g v-for="state in states" :key="state.code"
                class="state-group"
                @click="selectState(state)"
                :class="{ selected: selectedState?.code === state.code }">
                <ellipse
                  :cx="state.cx" :cy="state.cy"
                  :rx="state.rx" :ry="state.ry"
                  :fill="densityFill(state.risk_score)"
                  stroke="rgba(255,255,255,0.15)"
                  stroke-width="1"
                  class="state-shape"
                />
                <text :x="state.cx" :y="state.cy + 4" text-anchor="middle"
                  fill="rgba(255,255,255,0.85)" font-size="9" font-family="monospace">
                  {{ state.code }}
                </text>
              </g>
            </svg>
          </div>
          <!-- Legend -->
          <div class="legend-row q-mt-md">
            <div class="legend-item" v-for="l in legend" :key="l.label">
              <span class="legend-dot" :style="{ background: l.color }"></span>
              <span class="text-caption text-grey">{{ l.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- State Detail Panel -->
      <div class="col-12 col-md-5 fade-up fade-up-3">
        <div class="fg-card full-height" v-if="!selectedState">
          <div class="empty-prompt">
            <q-icon name="touch_app" size="48px" color="blue-grey-7" />
            <div class="q-mt-md text-grey">Click a state on the map to view its fraud breakdown</div>
          </div>
        </div>
        <div class="fg-card full-height" v-else>
          <div class="section-label mono q-mb-md">{{ selectedState.name.toUpperCase() }}</div>
          <div class="state-score-ring q-mb-lg">
            <div class="ring-val sora" :style="{ color: densityFill(selectedState.risk_score) }">
              {{ selectedState.risk_score }}
            </div>
            <div class="ring-label mono">RISK INDEX</div>
          </div>

          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6">
              <div class="state-mini-stat">
                <div class="sms-val mono">{{ selectedState.total_cases }}</div>
                <div class="sms-label mono">Cases/Month</div>
              </div>
            </div>
            <div class="col-6">
              <div class="state-mini-stat">
                <div class="sms-val mono">₹{{ (selectedState.avg_loss / 1000).toFixed(0) }}K</div>
                <div class="sms-label mono">Avg Loss</div>
              </div>
            </div>
          </div>

          <div class="section-label mono q-mb-sm">TOP SCAM TYPES</div>
          <div class="scam-list">
            <div v-for="(scam, i) in selectedState.top_scams" :key="i" class="scam-entry">
              <div class="row items-center justify-between q-mb-xs">
                <span class="mono q-ml-xs text-caption text-white">{{ scam.type }}</span>
                <span class="mono text-caption" :style="{ color: densityFill(scam.pct * 100) }">{{ Math.floor(scam.pct * 100) }}%</span>
              </div>
              <q-linear-progress :value="scam.pct" :color="scam.pct > 0.5 ? 'negative' : 'warning'" track-color="rgba(255,255,255,0.07)" size="6px" style="border-radius:6px" />
            </div>
          </div>

          <div class="q-mt-lg">
            <div class="section-label mono q-mb-sm">KNOWN HOT-ZONES</div>
            <div class="row gap-sm">
              <q-chip v-for="z in selectedState.hot_districts" :key="z" color="red-10" text-color="white" :label="z" dense class="mono" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface State {
  code: string; name: string; cx: number; cy: number; rx: number; ry: number;
  risk_score: number; total_cases: number; avg_loss: number;
  top_scams: { type: string; pct: number }[];
  hot_districts: string[];
}

const states: State[] = [
  { code: 'JH', name: 'Jharkhand',    cx: 375, cy: 270, rx: 28, ry: 22, risk_score: 98, total_cases: 1820, avg_loss: 48000, top_scams: [{type:'Utility Scam', pct:0.72},{type:'OTP Phishing',pct:0.18},{type:'Lottery',pct:0.10}], hot_districts:['Jamtara','Deoghar','Giridih'] },
  { code: 'MH', name: 'Maharashtra',  cx: 200, cy: 330, rx: 42, ry: 30, risk_score: 84, total_cases: 3200, avg_loss: 62000, top_scams: [{type:'Investment Fraud',pct:0.55},{type:'Romance Scam',pct:0.25},{type:'KYC',pct:0.20}], hot_districts:['Thane','Pune','Nagpur'] },
  { code: 'DL', name: 'Delhi',        cx: 275, cy: 160, rx: 20, ry: 16, risk_score: 79, total_cases: 2900, avg_loss: 71000, top_scams: [{type:'Job Fraud',pct:0.42},{type:'Loan Fraud',pct:0.38},{type:'UPI Scam',pct:0.20}], hot_districts:['Outer Delhi','Shahdara','North East'] },
  { code: 'UP', name: 'Uttar Pradesh',cx: 320, cy: 200, rx: 48, ry: 30, risk_score: 76, total_cases: 4100, avg_loss: 35000, top_scams: [{type:'Utility Scam',pct:0.48},{type:'Agricultural Fraud',pct:0.30},{type:'Lottery',pct:0.22}], hot_districts:['Mathura','Agra','Varanasi'] },
  { code: 'RJ', name: 'Rajasthan',    cx: 190, cy: 200, rx: 48, ry: 36, risk_score: 68, total_cases: 1650, avg_loss: 28000, top_scams: [{type:'Land Fraud',pct:0.45},{type:'KYC',pct:0.35},{type:'Marriage Scam',pct:0.20}], hot_districts:['Jaipur','Jodhpur','Alwar'] },
  { code: 'KA', name: 'Karnataka',    cx: 220, cy: 430, rx: 36, ry: 28, risk_score: 62, total_cases: 1900, avg_loss: 55000, top_scams: [{type:'Tech Support',pct:0.50},{type:'Crypto Scam',pct:0.30},{type:'OTP',pct:0.20}], hot_districts:['Bengaluru','Mysuru','Hubballi'] },
  { code: 'WB', name: 'West Bengal',  cx: 420, cy: 290, rx: 28, ry: 32, risk_score: 58, total_cases: 990, avg_loss: 22000, top_scams: [{type:'Job Fraud',pct:0.55},{type:'Lottery',pct:0.30},{type:'Insurance',pct:0.15}], hot_districts:['Kolkata','Howrah','Murshidabad'] },
  { code: 'TN', name: 'Tamil Nadu',   cx: 270, cy: 490, rx: 36, ry: 26, risk_score: 52, total_cases: 1200, avg_loss: 41000, top_scams: [{type:'Govt Scheme Fraud',pct:0.45},{type:'OTP',pct:0.35},{type:'Loan',pct:0.20}], hot_districts:['Chennai','Coimbatore','Tiruchirappalli'] },
  { code: 'GJ', name: 'Gujarat',      cx: 130, cy: 280, rx: 40, ry: 28, risk_score: 48, total_cases: 880, avg_loss: 33000, top_scams: [{type:'Trading Scam',pct:0.50},{type:'Diamond Fraud',pct:0.30},{type:'UPI',pct:0.20}], hot_districts:['Surat','Ahmedabad','Vadodara'] },
  { code: 'MP', name: 'Madhya Pradesh',cx:265, cy:260, rx:44, ry:30, risk_score: 44, total_cases: 760, avg_loss: 19000, top_scams: [{type:'Agricultural',pct:0.60},{type:'Land Fraud',pct:0.25},{type:'Lottery',pct:0.15}], hot_districts:['Bhopal','Indore','Gwalior'] },
  { code: 'HR', name: 'Haryana',      cx: 255, cy: 148, rx: 26, ry: 18, risk_score: 41, total_cases: 610, avg_loss: 31000, top_scams: [{type:'Job Fraud',pct:0.55},{type:'Matrimony',pct:0.30},{type:'KYC',pct:0.15}], hot_districts:['Gurugram','Faridabad','Nuh'] },
  { code: 'AP', name: 'Andhra Pradesh',cx:290, cy:415,rx:38,ry:26, risk_score: 38, total_cases: 820, avg_loss: 27000, top_scams: [{type:'Chit Fund Fraud',pct:0.50},{type:'Loan App',pct:0.30},{type:'OTP',pct:0.20}], hot_districts:['Visakhapatnam','Guntur','Krishna'] },
]

const selectedState = ref<State | null>(null)

const legend = [
  { label: 'Critical (80-100)', color: '#ef4444' },
  { label: 'High (60-79)',      color: '#f97316' },
  { label: 'Medium (40-59)',    color: '#f59e0b' },
  { label: 'Low (0-39)',        color: '#10b981' },
]

function densityFill(score: number): string {
  if (score >= 80) return '#ef4444'
  if (score >= 60) return '#f97316'
  if (score >= 40) return '#f59e0b'
  return '#10b981'
}

function selectState(s: State) {
  selectedState.value = s
}
</script>

<style scoped lang="scss">
.page-wrapper { padding: 32px; max-width: 1300px; margin: 0 auto; }
.map-wrap { background: rgba(255,255,255,0.02); border-radius: 16px; overflow: hidden; }
.india-svg { width: 100%; height: auto; min-height: 380px; }
.state-group { cursor: pointer; }

.state-shape {
  transition: opacity 0.2s, filter 0.2s;
  &:hover { opacity: 0.8; filter: brightness(1.25); }
}
.state-group.selected .state-shape { filter: brightness(1.4); stroke: white; stroke-width: 2; }

.legend-row { display: flex; gap: 16px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }

.state-score-ring {
  background: rgba(255,255,255,0.03); border-radius: 16px;
  padding: 20px; text-align: center;
}
.ring-val { font-size: 48px; font-weight: 800; line-height: 1; }
.ring-label { font-size: 11px; letter-spacing: 0.08em; color: var(--fg-text-secondary); }

.state-mini-stat {
  background: rgba(255,255,255,0.04); border-radius: 10px;
  padding: 12px; text-align: center;
}
.sms-val { font-size: 22px; font-weight: 700; color: var(--fg-text-primary); }
.sms-label { font-size: 10px; letter-spacing: 0.07em; color: var(--fg-text-secondary); }

.scam-list { display: flex; flex-direction: column; gap: 10px; }

.empty-prompt { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; text-align: center; }
</style>
