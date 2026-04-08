<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="row items-center justify-between">
        <div>
          <div class="page-title sora">Security Alerts</div>
          <div class="page-subtitle">Real-time monitoring of fraud attempts and network threats</div>
        </div>
        <div class="header-actions">
          <q-btn flat class="mono-btn" label="Mark all read" icon="done_all" />
        </div>
      </div>
    </div>

    <div class="alerts-layout">
      <!-- Global Threat Feed -->
      <div class="alerts-feed fade-up fade-up-2">
        <div class="section-label mono">LIVE THREAT FEED (GLOBAL)</div>
        <div class="feed-container">
          <div v-for="alert in globalAlerts" :key="alert.id" class="alert-card" :class="alert.level">
            <div class="alert-icon-wrap">
              <q-icon :name="alert.icon" size="20px" />
            </div>
            <div class="alert-content">
              <div class="alert-top">
                <span class="alert-title sora">{{ alert.title }}</span>
                <span class="alert-time">{{ alert.time }}</span>
              </div>
              <div class="alert-desc">{{ alert.description }}</div>
              <div class="alert-tags">
                <span v-for="tag in alert.tags" :key="tag" class="alert-tag mono">{{ tag }}</span>
              </div>
            </div>
            <div class="alert-level-indicator" />
          </div>
        </div>
      </div>

      <!-- Personal Notifications -->
      <div class="side-panel fade-up fade-up-3">
        <div class="fg-card mini-analytics">
          <div class="panel-label mono">NETWORK STATUS</div>
          <div class="status-row">
            <div class="status-item">
              <div class="status-dot online" />
              <span>FraudGuard Nodes</span>
            </div>
            <span class="mono">ACTIVE</span>
          </div>
          <div class="status-row">
            <div class="status-item">
              <div class="status-dot warning" />
              <span>1930 Portal API</span>
            </div>
            <span class="mono">DEGRADED</span>
          </div>
          <div class="status-row">
            <div class="status-item">
              <div class="status-dot online" />
              <span>M6 Graph Scorer</span>
            </div>
            <span class="mono">STABLE</span>
          </div>
        </div>

        <div class="fg-card security-tip q-mb-lg">
          <div class="panel-label mono">SECURITY RECOMMENDER</div>
          <div class="tip-content">
            <q-icon name="lightbulb" size="24px" color="amber" />
            <p>Your multi-modal fusion threshold is currently at <strong>40%</strong>. We recommend increasing it to <strong>60%</strong> for better recall on deepfake attempts.</p>
          </div>
          <q-btn flat color="primary" label="Optimize Settings" class="full-width" to="/settings" />
        </div>

        <!-- Strategic Intelligence Feed -->
        <div class="fg-card intel-feed">
          <div class="panel-label mono">STRATEGIC INTELLIGENCE</div>
          <div class="intel-items">
            <div v-for="intel in intelligenceFeed" :key="intel.id" class="intel-item">
              <div class="intel-top">
                <q-icon :name="intel.icon" size="14px" :color="intel.color" />
                <span class="intel-source mono">{{ intel.source }}</span>
              </div>
              <div class="intel-body">{{ intel.message }}</div>
              <div class="intel-time mono">{{ intel.time }}</div>
            </div>
          </div>
          <q-btn flat dense label="Full Recon Briefing →" class="intel-footer-btn full-width q-mt-md" />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const globalAlerts = ref([
  {
    id: 1,
    title: 'Coordinated Phishing Campaign',
    description: 'A new surge in "KYC Update" SMS scams has been detected across major banks. M1 patterns updated.',
    time: '2 mins ago',
    level: 'critical',
    icon: 'security',
    tags: ['M1-BERT', 'SMS-PHISH', 'NETWORK-WIDE']
  },
  {
    id: 2,
    title: 'Synthetic Voice Pattern Match',
    description: 'AASIST detector flagged a suspicious call script originating from a known high-risk VOIP block.',
    time: '14 mins ago',
    level: 'warning',
    icon: 'voice_over_off',
    tags: ['M5-AASIST', 'DEEPFAKE', 'VOICE']
  },
  {
    id: 3,
    title: 'New High-Risk UPI Node',
    description: 'M6 Graph Scorer identified a new "star" topology node connecting multiple reported fraud handles.',
    time: '1 hour ago',
    level: 'warning',
    icon: 'hub',
    tags: ['M6-GRAPH', 'TOPOLOGY', 'PREEMPTIVE']
  },
  {
    id: 4,
    title: 'Registry Model Update',
    description: 'M2 LightGBM model weights synchronized with the nightly training pipeline.',
    time: '4 hours ago',
    level: 'info',
    icon: 'auto_awesome',
    tags: ['M2-LGBM', 'UPDATE']
  }
])

const intelligenceFeed = ref([
  {
    id: 101,
    source: 'DARK_WEB_RECON',
    message: 'UPI handles related to "Axis Bank" mentioned in leak forum "BreachX".',
    time: '18h ago',
    icon: 'visibility',
    color: 'red'
  },
  {
    id: 102,
    source: 'FEDERATED_INTEL',
    message: 'Global blacklist hit: IP block 103.44.xx flagged in 4 major nodes.',
    time: '3d ago',
    icon: 'share',
    color: 'blue'
  },
  {
    id: 103,
    source: 'HITCHHIKER_SYSTEM',
    message: 'Active scanning attempt detected via Honeypot ID "charity@upi". Attacker neutralized.',
    time: '5d ago',
    icon: 'bolt',
    color: 'amber'
  }
])
</script>

<style scoped lang="scss">
.page-wrapper {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section { margin-bottom: 32px; }

.alerts-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  align-items: start;

  @media (max-width: 1000px) { grid-template-columns: 1fr; }
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--fg-text-muted);
  letter-spacing: 1.5px;
  margin-bottom: 16px;
}

.feed-container { display: flex; flex-direction: column; gap: 16px; }

.alert-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--fg-card);
  border: 1px solid var(--fg-border);
  border-radius: var(--fg-radius-lg);
  position: relative;
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover {
    transform: translateX(4px);
    border-color: var(--fg-muted);
    box-shadow: var(--fg-shadow-lg);
  }

  &.critical { .alert-icon-wrap { background: rgba(239, 68, 68, 0.1); color: var(--fg-red); } .alert-level-indicator { background: var(--fg-red); } }
  &.warning  { .alert-icon-wrap { background: rgba(245, 158, 11, 0.1); color: var(--fg-amber); } .alert-level-indicator { background: var(--fg-amber); } }
  &.info     { .alert-icon-wrap { background: rgba(59, 130, 246, 0.1); color: var(--fg-blue); } .alert-level-indicator { background: var(--fg-blue); } }
}

.alert-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-content { flex: 1; }

.alert-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.alert-title { font-size: 16px; font-weight: 700; color: var(--fg-text-primary); }
.alert-time { font-size: 11px; color: var(--fg-text-muted); }
.alert-desc { font-size: 13px; color: var(--fg-text-secondary); line-height: 1.5; margin-bottom: 12px; }

.alert-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.alert-tag {
  font-size: 9px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--fg-border);
  color: var(--fg-text-muted);
}

.alert-level-indicator {
  position: absolute;
  top: 0; right: 0; width: 4px; height: 100%;
}

.panel-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--fg-text-muted);
  letter-spacing: 1.2px;
  margin-bottom: 12px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--fg-border);
  font-size: 12px;
  &:last-child { border-bottom: none; }
}

.status-item { display: flex; align-items: center; gap: 8px; color: var(--fg-text-secondary); }
.status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  &.online { background: var(--fg-green); box-shadow: 0 0 8px var(--fg-green); }
  &.warning { background: var(--fg-amber); animation: pulse 1.5s infinite; }
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

.tip-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  margin-bottom: 20px;
  p { font-size: 13px; color: var(--fg-text-secondary); line-height: 1.6; margin: 0; }
}

// Intel Feed
.intel-feed { padding: 16px; border: 1px dashed var(--fg-blue) !important; background: rgba(59,130,246,0.02) !important; }
.intel-items { display: flex; flex-direction: column; gap: 16px; }
.intel-item { border-left: 2px solid var(--fg-border); padding-left: 12px; }
.intel-top { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.intel-source { font-size: 9px; font-weight: 700; color: var(--fg-text-muted); }
.intel-body { font-size: 12px; color: var(--fg-text-secondary); line-height: 1.4; }
.intel-time { font-size: 9px; color: var(--fg-text-muted); margin-top: 4px; }
.intel-footer-btn { font-size: 10px; color: var(--fg-blue); font-family: 'DM Mono', monospace; }
</style>
