<template>
  <q-layout view="lHh Lpr lFf" class="bg-grey-1">
    <q-header bordered class="bg-white text-primary shadow-1">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
          class="q-mr-sm"
        />

        <q-toolbar-title class="text-weight-bold">
          FraudGuard
        </q-toolbar-title>

        <q-btn flat round dense icon="notifications">
          <q-badge floating color="red" rounded v-if="hasAlerts" />
          <q-menu>
            <q-list style="min-width: 150px">
              <q-item clickable v-close-popup>
                <q-item-section>No new notifications</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="bg-white"
    >
      <q-list padding>
        <q-item-label header class="text-grey-6 text-uppercase text-weight-bold letter-spacing-1">
          App Settings
        </q-item-label>

        <q-item clickable v-ripple exact to="/">
          <q-item-section avatar>
            <q-icon name="dashboard" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Dashboard</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable v-ripple exact to="/verify">
          <q-item-section avatar>
            <q-icon name="qr_code_scanner" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Verify UPI</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator spaced />

        <q-item clickable v-ripple exact to="/settings">
          <q-item-section avatar>
            <q-icon name="settings" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Settings</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- Bottom Navigation Footer -->
    <q-footer bordered class="bg-white text-grey-8 shadow-up-2">
      <q-tabs
        v-model="currentTab"
        no-caps
        active-color="primary"
        indicator-color="transparent"
        class="text-grey-7"
        dense
      >
        <q-route-tab
          name="dashboard"
          to="/"
          icon="space_dashboard"
          label="Dashboard"
        />
        <q-route-tab
          name="verify"
          to="/verify"
          icon="verified_user"
          label="Verify"
        />
        <q-route-tab
          name="report"
          to="/report"
          icon="report_problem"
          label="Report"
        />
        <q-route-tab
          name="alerts"
          to="/alerts"
          icon="notifications_active"
          label="Alerts"
        />
        <q-route-tab
          name="profile"
          to="/profile"
          icon="account_circle"
          label="Profile"
        />
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useFraudStore } from 'src/stores/fraudStore'

const leftDrawerOpen = ref(false);
const currentTab = ref('dashboard');
const fraudStore = useFraudStore()

const hasAlerts = computed(() => fraudStore.recentAlerts.length > 0)

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>

<style scoped>
.letter-spacing-1 {
  letter-spacing: 1px;
}
</style>

