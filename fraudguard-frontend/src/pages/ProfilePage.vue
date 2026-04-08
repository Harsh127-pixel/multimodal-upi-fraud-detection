<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="page-title sora">Settings & Profile</div>
      <div class="page-subtitle">Configure your multi-modal fraud detection preferences</div>
    </div>

    <div class="settings-grid">
      <!-- User Profile Card -->
      <div class="profile-card fg-card fade-up fade-up-2">
        <div class="avatar-wrap">
          <div class="avatar-bg">
            <q-icon name="account_circle" size="64px" color="primary" />
          </div>
          <div class="user-info">
            <div class="user-name sora">{{ authStore.userEmail || 'Security Analyst' }}</div>
            <div class="user-role mono">SYSTEM ADMINISTRATOR</div>
          </div>
        </div>
        <div class="profile-stats">
          <div class="p-stat">
            <div class="ps-val">42</div>
            <div class="ps-label">Reports Filed</div>
          </div>
          <div class="p-stat">
            <div class="ps-val">128</div>
            <div class="ps-label">UPIs Scanned</div>
          </div>
        </div>
      </div>

      <!-- Fusion Engine Config -->
      <div class="settings-panel fg-card fade-up fade-up-2">
        <div class="panel-header">
          <q-icon name="tune" size="20px" />
          <span class="mono">FUSION ENGINE CALIBRATION</span>
        </div>
        
        <div class="setting-item">
          <div class="si-left">
            <div class="si-title">Global Risk Threshold</div>
            <div class="si-desc">Minimum score to trigger automated bank-level blocking</div>
          </div>
          <div class="si-right">
            <q-slider v-model="settings.threshold" :min="10" :max="90" label color="primary" class="q-px-md" style="width: 120px" />
            <span class="mono-val">{{ settings.threshold }}%</span>
          </div>
        </div>

        <div class="setting-item">
          <div class="si-left">
            <div class="si-title">Auto-forward to 1930</div>
            <div class="si-desc">Automatically submit high-confidence fraud reports to the Cybercrime Portal</div>
          </div>
          <div class="si-right">
            <q-toggle v-model="settings.autoForward" color="primary" />
          </div>
        </div>

        <div class="setting-item">
          <div class="si-left">
            <div class="si-title">CTC Analysis Window</div>
            <div class="si-desc">Time window for call-to-transaction correlation (minutes)</div>
          </div>
          <div class="si-right">
            <q-select v-model="settings.ctcWindow" :options="[1, 5, 10, 15]" dense borderless class="mono-select" />
          </div>
        </div>
      </div>

      <!-- Model Registry -->
      <div class="settings-panel fg-card fade-up fade-up-3 full-row">
        <div class="panel-header">
          <q-icon name="hub" size="20px" />
          <span class="mono">ACTIVE MODEL REGISTRY (P13 SPEC)</span>
        </div>
        
        <div class="model-grid">
          <div v-for="model in models" :key="model.id" class="model-badge" :class="{ disabled: !model.active }">
            <div class="mb-top">
              <span class="mb-id mono">{{ model.id }}</span>
              <div class="mb-dot" :class="{ online: model.active }" />
            </div>
            <div class="mb-name">{{ model.name }}</div>
            <div class="mb-tech mono">{{ model.tech }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="footer-actions q-mt-xl fade-up fade-up-3">
      <q-btn unelevated color="primary" label="Save Changes" class="save-btn" @click="saveSettings" :loading="saving" />
      <q-btn flat color="negative" label="Sign Out" icon="logout" class="q-ml-sm" @click="logout" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useAuthStore } from 'src/stores/authStore'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const $q = useQuasar()
const router = useRouter()
const saving = ref(false)

const settings = reactive({
  threshold: 75,
  autoForward: true,
  ctcWindow: 5,
  anonymizeData: true
})

const models = [
  { id: 'M1', name: 'Transaction Scorer', tech: 'XGBOOST/BERT', active: true },
  { id: 'M2', name: 'UPI Reputation', tech: 'LIGHTGBM', active: true },
  { id: 'M3', name: 'Phish Patterns', tech: 'RANDOM FOREST', active: true },
  { id: 'M4', name: 'Voice Intent', tech: 'DISTIL-ROBERTA', active: true },
  { id: 'M5', name: 'On-Device Deepfake', tech: 'AASIST Q8', active: true },
  { id: 'M6', name: 'Graph Community', tech: 'GRAPHSAGE-SIM', active: true }
]

function saveSettings() {
  saving.value = true
  setTimeout(() => {
    saving.value = false
    $q.notify({ type: 'positive', message: 'Settings localized and saved', position: 'bottom-right' })
  }, 1000)
}

function logout() {
  authStore.logout()
  void router.push('/login')
}
</script>

<style scoped lang="scss">
.page-wrapper {
  padding: 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.header-section { margin-bottom: 32px; }

.settings-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 24px;

  @media (max-width: 800px) { grid-template-columns: 1fr; }
}

.full-row { grid-column: 1 / -1; }

// Profile Card
.profile-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.avatar-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-bg {
  width: 80px; height: 80px;
  border-radius: 20px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  display: flex; align-items: center; justify-content: center;
}

.user-name { font-size: 18px; font-weight: 700; color: var(--fg-text-primary); }
.user-role { font-size: 10px; color: var(--fg-blue); letter-spacing: 1px; }

.profile-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 16px;
  background: var(--fg-surface);
  border-radius: 12px;
}

.p-stat { text-align: center; }
.ps-val { font-size: 20px; font-weight: 800; color: var(--fg-text-primary); }
.ps-label { font-size: 10px; color: var(--fg-text-muted); text-transform: uppercase; }

// Panels
.settings-panel { padding: 24px; }

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  color: var(--fg-text-muted);
  font-size: 11px;
  border-bottom: 1px solid var(--fg-border);
  padding-bottom: 12px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  &:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
}

.si-title { font-size: 14px; font-weight: 600; color: var(--fg-text-primary); }
.si-desc { font-size: 12px; color: var(--fg-text-muted); line-height: 1.4; margin-top: 2px; }

.si-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mono-val {
  font-family: 'DM Mono', monospace;
  font-size: 13px;
  color: var(--fg-blue);
  background: var(--fg-blue-soft);
  padding: 2px 8px;
  border-radius: 4px;
}

.mono-select { font-family: 'DM Mono', monospace; font-size: 14px; color: var(--fg-text-primary); }

// Models
.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.model-badge {
  padding: 16px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 12px;
  
  &.disabled { opacity: 0.5; filter: grayscale(1); }
}

.mb-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.mb-id { font-size: 10px; font-weight: 700; color: var(--fg-text-muted); }
.mb-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--fg-muted);
  &.online { background: var(--fg-green); box-shadow: 0 0 6px var(--fg-green); }
}
.mb-name { font-size: 13px; font-weight: 700; color: var(--fg-text-primary); margin-bottom: 4px; }
.mb-tech { font-size: 9px; color: var(--fg-blue); }

.save-btn {
  padding: 12px 32px;
  border-radius: 12px;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(59,130,246,0.3);
}
</style>
