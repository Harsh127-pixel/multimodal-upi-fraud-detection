<template>
  <q-page padding class="flex flex-center bg-grey-1">
    <div class="q-pa-md" style="max-width: 450px; width: 100%">
      <q-card class="shadow-2 rounded-borders">
        <q-card-section class="bg-primary text-white">
          <div class="text-h5 text-center text-weight-medium">Verify UPI</div>
        </q-card-section>

        <q-card-section class="q-pt-lg">
          <q-input
            v-model="upiId"
            label="UPI ID"
            outlined
            dense
            color="primary"
            placeholder="e.g. user@bank"
            @keyup.enter="verifyUpi"
          >
            <template v-slot:prepend>
              <q-icon name="account_balance_wallet" />
            </template>
          </q-input>
          
          <q-btn
            color="primary"
            class="full-width q-mt-md rounded-borders"
            label="Verify"
            size="lg"
            unelevated
            @click="verifyUpi"
            :loading="loading"
          />
        </q-card-section>

        <!-- Use a transition for smooth appearance -->
        <q-slide-transition>
          <q-card-section v-if="result" class="text-center q-pb-lg">
            <q-separator class="q-mb-md" />
            
            <div class="text-h6 text-grey-8 q-mb-md">Risk Analysis</div>
            
            <q-circular-progress
              show-value
              class="q-ma-md"
              :value="result.risk_score"
              size="120px"
              :thickness="0.22"
              :color="scoreColor"
              track-color="grey-3"
            >
              <span class="text-h4 text-weight-bold" :class="`text-${scoreColor}`">
                {{ result.risk_score }}
              </span>
            </q-circular-progress>
            
            <div class="text-subtitle1 q-mb-lg text-uppercase text-weight-bold tracking-wide">
              Risk Level: <span :class="`text-${scoreColor}`">{{ result.risk_level }}</span>
            </div>

            <q-list bordered separator class="rounded-borders text-left bg-white shadow-1" v-if="result.risk_signals && result.risk_signals.length > 0">
              <q-item v-for="(signal, index) in result.risk_signals" :key="index" class="q-py-md">
                <q-item-section avatar>
                  <q-icon :name="signalIcon" :color="scoreColor" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ signal }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-slide-transition>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const upiId = ref('')
const loading = ref(false)
const result = ref<{
  risk_score: number;
  risk_level: string;
  risk_signals: string[];
} | null>(null)

const scoreColor = computed(() => {
  if (!result.value) return 'grey'
  if (result.value.risk_score < 40) return 'green'
  if (result.value.risk_score < 75) return 'amber'
  return 'red'
})

const signalIcon = computed(() => {
  if (!result.value) return 'info'
  if (result.value.risk_score < 40) return 'check_circle'
  if (result.value.risk_score < 75) return 'warning'
  return 'error'
})

const verifyUpi = async () => {
  if (!upiId.value.trim()) return
  loading.value = true
  result.value = null
  
  try {
    const response = await fetch('http://localhost:8000/api/upi/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ upi_id: upiId.value.trim() })
    })
    
    if (response.ok) {
      result.value = await response.json()
    } else {
      console.error('Failed to verify UPI')
    }
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tracking-wide {
  letter-spacing: 0.05em;
}
</style>
