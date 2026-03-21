<template>
  <q-page padding class="bg-grey-1 q-pb-xl">
    <div class="row q-col-gutter-lg justify-center">
      <!-- Safety Score Meter -->
      <div class="col-12 col-md-6 flex flex-center q-pt-lg">
        <q-card flat class="bg-transparent text-center" style="width: 100%">
          <div class="text-h6 text-grey-8 q-mb-md">Overall Safety Score</div>
          <q-circular-progress
            show-value
            class="q-ma-md"
            :value="fraudStore.safetyScore"
            size="200px"
            :thickness="0.15"
            :color="scoreColor"
            track-color="grey-3"
            animation-speed="600"
          >
            <div class="column items-center">
              <span class="text-h2 text-weight-bolder" :class="`text-${scoreColor}`">
                {{ fraudStore.safetyScore }}
              </span>
              <span class="text-caption text-grey-6 text-uppercase text-weight-bold">Safe</span>
            </div>
          </q-circular-progress>
          <div class="text-subtitle1 q-mt-md" :class="`text-${scoreColor}`">
            {{ scoreLabel }}
          </div>
        </q-card>
      </div>

      <!-- Quick Stats -->
      <div class="col-12">
        <div class="row q-col-gutter-md">
          <div class="col-4">
            <q-card bordered class="text-center shadow-1">
              <q-card-section class="q-pa-sm">
                <div class="text-h6 text-primary">{{ fraudStore.stats.transactionsToday }}</div>
                <div class="text-caption text-grey-7">Scanned Today</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-4">
            <q-card bordered class="text-center shadow-1">
              <q-card-section class="q-pa-sm">
                <div class="text-h6 text-negative">{{ fraudStore.stats.fraudsBlocked }}</div>
                <div class="text-caption text-grey-7">Frauds Blocked</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-4">
            <q-card bordered class="text-center shadow-1">
              <q-card-section class="q-pa-sm">
                <div class="text-h6 text-orange-8">{{ fraudStore.stats.communityReports }}</div>
                <div class="text-caption text-grey-7">Reports</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Recent Alerts -->
      <div class="col-12">
        <q-card flat bordered class="q-mt-md rounded-borders shadow-1">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-subtitle1 text-weight-bold">Recent Alerts</div>
            <q-space />
            <q-btn flat round dense icon="more_horiz" />
          </q-card-section>

          <q-card-section>
            <q-list separator>
              <q-item v-for="alert in limitedAlerts" :key="alert.id" class="q-py-md px-none">
                <q-item-section avatar>
                  <q-icon 
                    :name="alert.severity === 'high' ? 'error' : (alert.severity === 'medium' ? 'warning' : 'info')" 
                    :color="alert.severity === 'high' ? 'red' : (alert.severity === 'medium' ? 'amber' : 'blue')" 
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-medium">{{ alert.type }}</q-item-label>
                  <q-item-label caption lines="2">{{ alert.message }}</q-item-label>
                </q-item-section>
                <q-item-section side top>
                  <q-item-label caption>{{ alert.timestamp }}</q-item-label>
                </q-item-section>
              </q-item>

              <div v-if="limitedAlerts.length === 0" class="q-pa-xl text-center">
                <q-icon name="check_circle_outline" size="xl" color="green-4" />
                <div class="text-grey-6 q-mt-md font-medium">All systems normal. No recent threats.</div>
              </div>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useFraudStore } from 'src/stores/fraudStore'

const $q = useQuasar()
const fraudStore = useFraudStore()

// Watch for incoming real-time alerts
watch(() => fraudStore.recentAlerts[0], (newAlert) => {
  if (!newAlert) return
  
  if (newAlert.action === 'block') {
    $q.notify({
      color: 'negative',
      message: `Transaction BLOCKED: ${newAlert.upi_id} (Score: ${newAlert.score})`,
      icon: 'block',
      timeout: 8000,
      position: 'top'
    })
  } else if (newAlert.action === 'warn') {
    $q.notify({
      color: 'warning',
      message: `Suspicious Transaction: ${newAlert.upi_id} (Score: ${newAlert.score})`,
      icon: 'priority_high',
      timeout: 5000,
      position: 'top'
    })
  }
}, { deep: true })

const limitedAlerts = computed(() => fraudStore.recentAlerts.slice(0, 5))

const scoreColor = computed(() => {
  const score = fraudStore.safetyScore
  if (score > 70) return 'green'
  if (score >= 40) return 'amber'
  return 'red'
})

const scoreLabel = computed(() => {
  const score = fraudStore.safetyScore
  if (score > 70) return 'High Safety Level'
  if (score >= 40) return 'Moderate Safety Level'
  return 'Low Safety Level'
})
</script>

<style scoped>
.font-medium {
  font-weight: 500;
}
</style>
