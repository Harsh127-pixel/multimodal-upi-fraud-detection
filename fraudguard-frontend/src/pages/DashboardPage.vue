<template>
  <q-page class="page-wrapper dot-grid-bg">

    <!-- ── Page Header ────────────────────────────────────────────── -->
    <div class="dashboard-header fade-up fade-up-1">
      <div>
        <div class="page-title">Security Dashboard</div>
        <div class="page-subtitle">Real-time UPI fraud protection overview</div>
      </div>
      <div class="header-time mono">
        {{ currentTime }}
      </div>
    </div>

    <!-- ── Safety Score + Stat Cards ─────────────────────────────── -->
    <div class="row q-col-gutter-md q-mb-xl">

      <!-- Safety Score Ring -->
      <div class="col-12 col-md-4 fade-up fade-up-1">
        <div class="fg-card score-panel">
          <div class="score-label mono">SAFETY SCORE</div>
          <div class="score-ring-wrap">
            <svg class="score-svg" viewBox="0 0 180 180">
              <circle
                cx="90" cy="90" r="72"
                fill="none"
                stroke="var(--fg-border)"
                stroke-width="12"
              />
              <circle
                cx="90" cy="90" r="72"
                fill="none"
                :stroke="scoreRingColor"
                stroke-width="12"
                stroke-linecap="round"
                :stroke-dasharray="452.4"
                :stroke-dashoffset="452.4 - (452.4 * fraudStore.safetyScore / 100)"
                transform="rotate(-90 90 90)"
                style="transition: stroke-dashoffset 1s ease, stroke 0.5s ease"
              />
            </svg>
            <div class="score-center">
              <div class="score-number sora" :style="{ color: scoreRingColor }">
                {{ fraudStore.safetyScore }}
              </div>
              <div class="score-sub mono">{{ scoreLabel }}</div>
            </div>
          </div>
          <div class="score-footer">
            <div class="score-indicator" :class="scoreClass">
              <span class="indicator-dot" />
              {{ scoreStatus }}
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="col-12 col-md-8">
        <div class="row q-col-gutter-md">
          <div
            v-for="(stat, i) in statCards"
            :key="stat.label"
            class="col-6"
            :class="`fade-up fade-up-${i + 2}`"
          >
            <div class="stat-card" :class="stat.accent">
              <div class="stat-icon" :style="{ background: stat.iconBg }">
                <q-icon :name="stat.icon" size="20px" :style="{ color: stat.iconColor }" />
              </div>
              <div class="stat-label">{{ stat.label }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trendUp ? 'up' : 'neutral'">
                <q-icon :name="stat.trendUp ? 'trending_up' : 'remove'" size="12px" />
                {{ stat.trend }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Recent Alerts ──────────────────────────────────────────── -->
    <div class="fg-card fade-up fade-up-3">
      <div class="section-header">
        <div class="section-title sora">
          <q-icon name="notifications_active" size="18px" class="text-blue-light q-mr-xs" />
          Recent Alerts
        </div>
        <router-link to="/alerts" class="section-link">View all →</router-link>
      </div>

      <div class="alerts-list">
        <transition-group name="alert-slide">
          <div
            v-for="alert in displayAlerts"
            :key="alert.id || alert.timestamp"
            class="alert-row"
            :class="alert.severity || 'low'"
          >
            <div class="alert-severity-bar" :class="alert.severity || 'low'" />

            <div class="alert-icon-wrap" :class="alert.severity || 'low'">
              <q-icon :name="alertIcon(alert.severity)" size="16px" />
            </div>

            <div class="alert-content">
              <div class="alert-type">{{ alert.type }}</div>
              <div class="alert-msg">{{ alert.message || `UPI: ${alert.upi_id || '—'}` }}</div>
            </div>

            <div class="alert-meta">
              <div v-if="alert.score !== undefined" class="alert-score-chip" :class="alert.severity">
                {{ alert.score }}
              </div>
              <div class="alert-time mono">{{ alert.timestamp }}</div>
            </div>
          </div>
        </transition-group>

        <div v-if="displayAlerts.length === 0" class="alerts-empty">
          <div class="empty-icon">
            <q-icon name="verified_user" size="40px" style="color: var(--fg-green)" />
          </div>
          <div class="empty-title sora">All Clear</div>
          <div class="empty-sub">No security threats detected</div>
        </div>
      </div>
    </div>

    <!-- ── Quick Actions ──────────────────────────────────────────── -->
    <div class="row q-col-gutter-md q-mt-lg fade-up fade-up-5">
      <div class="col-12">
        <div class="quick-actions-label mono">QUICK ACTIONS</div>
      </div>
      <div class="col-12 col-sm-4" v-for="action in quickActions" :key="action.label">
        <router-link :to="action.to" class="quick-action-card fg-card">
          <div class="qa-icon" :style="{ background: action.bg }">
            <q-icon :name="action.icon" size="22px" :style="{ color: action.color }" />
          </div>
          <div class="qa-title sora">{{ action.label }}</div>
          <div class="qa-desc">{{ action.desc }}</div>
          <div class="qa-arrow">→</div>
        </router-link>
      </div>
    </div>

  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { useFraudStore } from 'src/stores/fraudStore'
import type { Alert } from 'src/stores/fraudStore'

const $q = useQuasar()
const fraudStore = useFraudStore()

// Clock
const currentTime = ref('')
let clockInterval: ReturnType<typeof setInterval>
const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
onMounted(() => { updateTime(); clockInterval = setInterval(updateTime, 1000) })
onUnmounted(() => clearInterval(clockInterval))

// Score
const scoreRingColor = computed(() => {
  const s = fraudStore.safetyScore
  if (s > 70) return 'var(--fg-green)'
  if (s >= 40) return 'var(--fg-amber)'
  return 'var(--fg-red)'
})
const scoreLabel = computed(() => {
  const s = fraudStore.safetyScore
  if (s > 70) return 'SAFE'
  if (s >= 40) return 'MODERATE'
  return 'DANGER'
})
const scoreClass = computed(() => {
  const s = fraudStore.safetyScore
  if (s > 70) return 'safe'
  if (s >= 40) return 'warn'
  return 'danger'
})
const scoreStatus = computed(() => {
  const s = fraudStore.safetyScore
  if (s > 70) return 'Protected & Secure'
  if (s >= 40) return 'Elevated Risk Detected'
  return 'Immediate Attention Required'
})

// Stat cards
const statCards = computed(() => [
  {
    label: 'Transactions Today',
    value: fraudStore.stats.transactionsToday.toLocaleString(),
    icon: 'receipt_long',
    accent: 'blue',
    iconBg: 'rgba(59,130,246,0.1)',
    iconColor: 'var(--fg-blue)',
    trend: '+12 vs yesterday',
    trendUp: true,
  },
  {
    label: 'Frauds Blocked',
    value: fraudStore.stats.fraudsBlocked.toLocaleString(),
    icon: 'block',
    accent: 'red',
    iconBg: 'rgba(239,68,68,0.1)',
    iconColor: 'var(--fg-red)',
    trend: 'Last 24 hours',
    trendUp: false,
  },
  {
    label: 'Amount Saved',
    value: '₹48,200',
    icon: 'savings',
    accent: 'green',
    iconBg: 'rgba(16,185,129,0.1)',
    iconColor: 'var(--fg-green)',
    trend: 'This month',
    trendUp: true,
  },
  {
    label: 'Community Reports',
    value: fraudStore.stats.communityReports.toLocaleString(),
    icon: 'group',
    accent: 'amber',
    iconBg: 'rgba(245,158,11,0.1)',
    iconColor: 'var(--fg-amber)',
    trend: 'Pending review',
    trendUp: false,
  },
  {
    label: 'Attacks Neutralized',
    value: '104',
    icon: 'bolt',
    accent: 'purple',
    iconBg: 'rgba(168,85,247,0.1)',
    iconColor: 'var(--fg-purple)',
    trend: 'Via Honeypot system',
    trendUp: true,
  },
  {
    label: 'Device Health',
    value: '98%',
    icon: 'health_and_safety',
    accent: 'cyan',
    iconBg: 'rgba(6,182,212,0.1)',
    iconColor: 'var(--fg-cyan)',
    trend: 'OS Integrity: SECURE',
    trendUp: true,
  },
])

const displayAlerts = computed(() => fraudStore.recentAlerts.slice(0, 6))

function alertIcon(severity?: string) {
  if (severity === 'high') return 'error'
  if (severity === 'medium') return 'warning'
  return 'info'
}

// Quick actions
const quickActions = [
  { label: 'Verify UPI ID',      desc: 'Check a UPI address for fraud signals',  to: '/verify',   icon: 'verified_user',  color: 'var(--fg-blue)',  bg: 'rgba(59,130,246,0.1)' },
  { label: 'Mobile Shield',      desc: 'QR Sentry & SMS Sandbox tools',          to: '/mobile',   icon: 'smartphone',     color: 'var(--fg-cyan)',  bg: 'rgba(6,182,212,0.1)'  },
  { label: 'Multi-modal Scan',   desc: 'Analyze transaction + SMS + voice calls', to: '/advanced', icon: 'analytics',      color: 'var(--fg-amber)', bg: 'rgba(245,158,11,0.1)' },
  { label: 'Report Fraud',       desc: 'Submit a case to the database',           to: '/report',   icon: 'report_problem', color: 'var(--fg-red)',   bg: 'rgba(239,68,68,0.1)'  },
]

// Notifications for new alerts
watch(() => fraudStore.recentAlerts[0], (newAlert: Alert | undefined) => {
  if (!newAlert) return
  const cfg = newAlert.action === 'block'
    ? { color: 'negative', icon: 'block',         timeout: 8000 }
    : { color: 'warning',  icon: 'priority_high',  timeout: 5000 }
  $q.notify({
    ...cfg,
    message: `${newAlert.action === 'block' ? 'BLOCKED' : 'WARNING'}: ${newAlert.upi_id || newAlert.type} (Score: ${newAlert.score ?? '—'})`,
    position: 'top-right',
  })
}, { deep: true })
</script>

<style scoped lang="scss">
.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 28px;

  .header-time {
    font-size: 13px;
    color: var(--fg-text-muted);
    background: var(--fg-surface);
    border: 1px solid var(--fg-border);
    padding: 6px 14px;
    border-radius: 8px;
    letter-spacing: 1px;
  }
}

// Score Panel
.score-panel {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 100%;
}

.score-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.5px;
  color: var(--fg-text-muted);
  text-transform: uppercase;
  margin-bottom: 16px;
}

.score-ring-wrap {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 16px;
}

.score-svg {
  width: 100%;
  height: 100%;
  transform: scaleX(1);
}

.score-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-number {
  font-size: 44px;
  font-weight: 800;
  line-height: 1;
  transition: color 0.5s ease;
}

.score-sub {
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--fg-text-muted);
  margin-top: 4px;
}

.score-footer { width: 100%; margin-top: 4px; }

.score-indicator {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 99px;

  .indicator-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    animation: pulse-dot 2s infinite;
  }

  &.safe   { color: var(--fg-green); background: rgba(16,185,129,0.1); .indicator-dot { background: var(--fg-green); box-shadow: 0 0 6px var(--fg-green); } }
  &.warn   { color: var(--fg-amber); background: rgba(245,158,11,0.1); .indicator-dot { background: var(--fg-amber); } }
  &.danger { color: var(--fg-red);   background: rgba(239,68,68,0.1);  .indicator-dot { background: var(--fg-red); box-shadow: 0 0 6px var(--fg-red); } }
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(0.8); }
}

// Stat Card additions
.stat-trend {
  margin-top: 6px;
  font-size: 11px;
  font-family: 'DM Mono', monospace;
  color: var(--fg-text-muted);
  display: flex;
  align-items: center;
  gap: 4px;

  &.up { color: var(--fg-green); }
}

// Section Header
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--fg-border);
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--fg-text-primary);
  display: flex;
  align-items: center;
}

.section-link {
  font-size: 12px;
  color: var(--fg-blue);
  text-decoration: none;
  font-family: 'DM Mono', monospace;

  &:hover { opacity: 0.8; }
}

// Alerts List
.alerts-list { padding: 12px; }

.alert-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--fg-border);
  background: rgba(26, 34, 53, 0.5);
  margin-bottom: 6px;
  position: relative;
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover { background: var(--fg-card); border-color: var(--fg-muted); }
}

.alert-severity-bar {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  border-radius: 3px;

  &.high   { background: var(--fg-red); }
  &.medium { background: var(--fg-amber); }
  &.low    { background: var(--fg-blue); }
}

.alert-icon-wrap {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;

  &.high   { background: rgba(239,68,68,0.12);  color: var(--fg-red);   }
  &.medium { background: rgba(245,158,11,0.12); color: var(--fg-amber); }
  &.low    { background: rgba(59,130,246,0.12); color: var(--fg-blue);  }
}

.alert-content { flex: 1; min-width: 0; }
.alert-type { font-size: 13px; font-weight: 600; color: var(--fg-text-primary); }
.alert-msg  { font-size: 12px; color: var(--fg-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.alert-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }

.alert-score-chip {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;

  &.high   { background: rgba(239,68,68,0.15);  color: var(--fg-red);   }
  &.medium { background: rgba(245,158,11,0.15); color: var(--fg-amber); }
  &.low    { background: rgba(59,130,246,0.15); color: var(--fg-blue);  }
}

.alert-time { font-size: 11px; color: var(--fg-text-muted); }

// Empty state
.alerts-empty {
  padding: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.empty-icon {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.15);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
}

.empty-title { font-size: 18px; font-weight: 700; color: var(--fg-text-primary); }
.empty-sub   { font-size: 13px; color: var(--fg-text-muted); }

// Quick Actions
.quick-actions-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.5px;
  color: var(--fg-text-muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.quick-action-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px;
  text-decoration: none;
  cursor: pointer;
  position: relative;

  &:hover {
    transform: translateY(-2px);
    .qa-arrow { transform: translateX(4px); }
  }
}

.qa-icon {
  width: 44px; height: 44px;
  border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
}

.qa-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--fg-text-primary);
}

.qa-desc {
  font-size: 12px;
  color: var(--fg-text-muted);
  line-height: 1.4;
}

.qa-arrow {
  font-size: 18px;
  color: var(--fg-text-muted);
  position: absolute;
  top: 20px; right: 20px;
  transition: transform 0.2s ease;
}

// Transitions
.alert-slide-enter-active,
.alert-slide-leave-active { transition: all 0.3s ease; }
.alert-slide-enter-from   { opacity: 0; transform: translateX(-10px); }
.alert-slide-leave-to     { opacity: 0; transform: translateX(10px); }
</style>
