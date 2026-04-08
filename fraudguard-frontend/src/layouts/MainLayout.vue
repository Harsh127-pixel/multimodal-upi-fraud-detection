<template>
  <q-layout view="lHh Lpr lFf" class="bg-navy">

    <!-- ── Header ───────────────────────────────────────────────────── -->
    <q-header class="header-bar">
      <q-toolbar class="header-toolbar">
        <q-btn
          flat dense round
          icon="menu"
          class="text-secondary q-mr-sm header-menu-btn"
          @click="toggleLeftDrawer"
        />

        <div class="header-logo">
          <div class="logo-mark">
            <q-icon name="shield" size="18px" class="text-blue-light" />
          </div>
          <span class="logo-text sora">FraudGuard</span>
        </div>

        <q-space />

        <div class="header-actions">
          <!-- Alert bell -->
          <q-btn flat round dense class="header-icon-btn">
            <div class="icon-btn-inner">
              <q-icon name="notifications_none" size="20px" />
              <span v-if="hasAlerts" class="alert-pip" />
            </div>
            <q-menu class="fg-menu" anchor="bottom right" self="top right">
              <div class="menu-header">Notifications</div>
              <q-separator class="q-ma-none" style="background: var(--fg-border)" />
              <div v-if="fraudStore.recentAlerts.length === 0" class="menu-empty">
                <q-icon name="check_circle_outline" size="28px" style="color: var(--fg-green)" />
                <div>All clear</div>
              </div>
              <div v-else class="menu-alerts">
                <div
                  v-for="alert in fraudStore.recentAlerts.slice(0, 4)"
                  :key="alert.id || alert.timestamp"
                  class="menu-alert-item"
                >
                  <div class="menu-alert-dot" :class="alert.severity" />
                  <div>
                    <div class="menu-alert-title">{{ alert.type }}</div>
                    <div class="menu-alert-time">{{ alert.timestamp }}</div>
                  </div>
                </div>
              </div>
            </q-menu>
          </q-btn>

          <!-- User avatar -->
          <q-btn flat round dense class="header-icon-btn user-btn">
            <div class="user-avatar">
              {{ userInitial }}
            </div>
            <q-menu class="fg-menu" anchor="bottom right" self="top right">
              <div class="menu-header">{{ authStore.userEmail }}</div>
              <q-separator style="background: var(--fg-border)" />
              <q-item clickable v-close-popup @click="handleLogout" class="menu-logout-item">
                <q-item-section avatar>
                  <q-icon name="logout" size="16px" />
                </q-item-section>
                <q-item-section>Sign out</q-item-section>
              </q-item>
            </q-menu>
          </q-btn>
        </div>
      </q-toolbar>
    </q-header>

    <!-- ── Sidebar ──────────────────────────────────────────────────── -->
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      :width="240"
      class="sidebar"
    >
      <div class="sidebar-content">
        <div class="sidebar-section-label">Navigation</div>

        <nav class="sidebar-nav">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="nav-item"
            :class="{ active: isActive(item.to) }"
          >
            <q-icon :name="item.icon" size="18px" class="nav-icon" />
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </router-link>
        </nav>

        <div class="sidebar-section-label q-mt-lg">System</div>
        <nav class="sidebar-nav">
          <router-link to="/settings" class="nav-item" :class="{ active: isActive('/settings') }">
            <q-icon name="tune" size="18px" class="nav-icon" />
            <span class="nav-label">Settings</span>
          </router-link>
        </nav>

        <!-- Mini status panel -->
        <div class="sidebar-status">
          <div class="status-dot active" />
          <span>System Online</span>
        </div>
      </div>
    </q-drawer>

    <!-- ── Main Content ─────────────────────────────────────────────── -->
    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- ── Bottom Nav (mobile) ───────────────────────────────────────── -->
    <q-footer class="bottom-nav">
      <div class="bottom-nav-inner">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="bottom-nav-item"
          :class="{ active: isActive(item.to) }"
        >
          <q-icon :name="isActive(item.to) ? item.iconActive || item.icon : item.icon" size="22px" />
          <span>{{ item.label }}</span>
        </router-link>
      </div>
    </q-footer>

  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFraudStore } from 'src/stores/fraudStore'
import { useAuthStore } from 'src/stores/authStore'
import { connectWebSocket, disconnect } from 'src/boot/websocket'

const route = useRoute()
const router = useRouter()
const leftDrawerOpen = ref(false)
const fraudStore = useFraudStore()
const authStore = useAuthStore()

interface NavItem {
  to: string;
  label: string;
  icon: string;
  iconActive: string;
  badge?: string | number;
}

const navItems: NavItem[] = [
  { to: '/',          label: 'Dashboard',  icon: 'space_dashboard',      iconActive: 'space_dashboard'  },
  { to: '/verify',    label: 'Verify',     icon: 'verified_user',         iconActive: 'verified_user'    },
  { to: '/advanced',  label: 'Advanced',   icon: 'analytics',             iconActive: 'analytics'        },
  { to: '/analytics', label: 'Reports',    icon: 'bar_chart',             iconActive: 'bar_chart'        },
  { to: '/report',    label: 'Report',     icon: 'report_problem',        iconActive: 'report_problem'   },
  { to: '/alerts',    label: 'Alerts',     icon: 'notifications_none',    iconActive: 'notifications'    },
  { to: '/mobile',    label: 'Mobile',     icon: 'smartphone',            iconActive: 'smartphone'       },
  { to: '/graph',     label: 'Graph',      icon: 'hub',                   iconActive: 'hub'              },
  { to: '/community', label: 'Watch',      icon: 'groups',                iconActive: 'groups'           },
  { to: '/soc',       label: 'SOC',        icon: 'monitor_heart',         iconActive: 'monitor_heart'    },
  { to: '/cases',     label: 'Cases',      icon: 'folder_open',           iconActive: 'folder_open'      },
  { to: '/scanner',   label: 'Scanner',    icon: 'document_scanner',      iconActive: 'document_scanner' },
  { to: '/playbook',  label: 'Playbook',   icon: 'play_circle',           iconActive: 'play_circle'      },
  { to: '/riskmap',   label: 'Risk Map',   icon: 'map',                   iconActive: 'map'              },
]

const hasAlerts = computed(() => fraudStore.recentAlerts.length > 0)
const userInitial = computed(() => (authStore.userEmail?.[0] ?? 'U').toUpperCase())

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function toggleLeftDrawer() { leftDrawerOpen.value = !leftDrawerOpen.value }

async function handleLogout() {
  authStore.logout()
  disconnect()
  await router.push('/login')
}

const handleWS = () => {
  if (authStore.isAuthenticated && authStore.userEmail) {
    connectWebSocket(authStore.userEmail)
  } else { disconnect() }
}

onMounted(handleWS)
onUnmounted(disconnect)
watch(() => authStore.isAuthenticated, handleWS)
</script>

<style scoped lang="scss">
.bg-navy { background: var(--fg-navy); }

// Header
.header-bar {
  background: rgba(10, 15, 30, 0.85) !important;
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--fg-border);
  box-shadow: none;
}

.header-toolbar {
  height: 58px;
  padding: 0 18px;
  gap: 8px;
}

.header-menu-btn { color: var(--fg-text-secondary) !important; }

.header-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;

  .logo-mark {
    width: 32px; height: 32px;
    border-radius: 8px;
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.2);
    display: flex; align-items: center; justify-content: center;
  }

  .logo-text {
    font-size: 17px;
    font-weight: 700;
    color: var(--fg-text-primary);
    letter-spacing: -0.3px;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.header-icon-btn {
  width: 36px; height: 36px;
  border-radius: 9px !important;
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--fg-border) !important;
  color: var(--fg-text-secondary) !important;
  transition: all 0.15s ease;

  &:hover {
    background: rgba(255,255,255,0.08) !important;
    color: var(--fg-text-primary) !important;
  }

  .icon-btn-inner {
    position: relative;
    display: flex;
    .alert-pip {
      position: absolute;
      top: -1px; right: -1px;
      width: 7px; height: 7px;
      border-radius: 50%;
      background: var(--fg-red);
      border: 1.5px solid var(--fg-navy);
    }
  }
}

.user-btn {
  .user-avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--fg-blue), var(--fg-cyan));
    color: white;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 12px;
    display: flex; align-items: center; justify-content: center;
  }
}

// Sidebar
.sidebar {
  background: var(--fg-slate) !important;
  border-right: 1px solid var(--fg-border) !important;
}

.sidebar-content {
  padding: 20px 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-section-label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--fg-text-muted);
  padding: 0 12px;
  margin-bottom: 6px;
}

.sidebar-nav { display: flex; flex-direction: column; gap: 2px; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 9px;
  text-decoration: none;
  color: var(--fg-text-secondary);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;

  &:hover {
    background: rgba(255,255,255,0.05);
    color: var(--fg-text-primary);
  }

  &.active {
    background: var(--fg-blue-soft);
    color: var(--fg-blue);
    border: 1px solid rgba(59, 130, 246, 0.15);

    .nav-icon { color: var(--fg-blue) !important; }
  }

  .nav-icon { color: var(--fg-text-muted); transition: color 0.15s ease; }
  .nav-label { flex: 1; }
  .nav-badge {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    background: var(--fg-red);
    color: white;
    border-radius: 99px;
    padding: 2px 6px;
  }
}

.sidebar-status {
  margin-top: auto;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: var(--fg-text-muted);

  .status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    &.active { background: var(--fg-green); box-shadow: 0 0 6px var(--fg-green); }
  }
}

// Bottom Nav
.bottom-nav {
  background: var(--fg-slate) !important;
  border-top: 1px solid var(--fg-border) !important;

  @media (min-width: 1024px) { display: none; }
}

.bottom-nav-inner {
  display: flex;
  justify-content: space-around;
  padding: 8px 0 4px;
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  text-decoration: none;
  color: var(--fg-text-muted);
  font-size: 10px;
  font-family: 'DM Sans', sans-serif;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.15s ease;

  &.active {
    color: var(--fg-blue);
  }
}

// Menu dropdown
:deep(.fg-menu) {
  background: var(--fg-card) !important;
  border: 1px solid var(--fg-border) !important;
  border-radius: var(--fg-radius-md) !important;
  box-shadow: var(--fg-shadow-lg) !important;
  min-width: 240px;
}

.menu-header {
  padding: 14px 16px 10px;
  font-family: 'Sora', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: var(--fg-text-primary);
}

.menu-empty {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--fg-text-muted);
  font-size: 13px;
}

.menu-alerts { padding: 8px; }
.menu-alert-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 7px;
  cursor: pointer;

  &:hover { background: rgba(255,255,255,0.04); }
}

.menu-alert-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  &.high   { background: var(--fg-red); }
  &.medium { background: var(--fg-amber); }
  &.low    { background: var(--fg-blue); }
}

.menu-alert-title { font-size: 13px; color: var(--fg-text-primary); font-weight: 500; }
.menu-alert-time  { font-size: 11px; color: var(--fg-text-muted); font-family: 'DM Mono', monospace; }

.menu-logout-item {
  color: var(--fg-red) !important;
  margin: 6px;
  border-radius: 8px;
  font-size: 13px;
}
</style>
