<template>
  <q-page padding class="bg-grey-2">
    <div class="max-width-container q-mx-auto">
      <div class="text-h4 text-weight-bold q-mb-lg text-primary">Advanced Multi-modal Analysis</div>
      
      <div class="row q-col-gutter-lg">
        <!-- Input Section -->
        <div class="col-12 col-md-7">
          <q-card class="shadow-2 rounded-borders">
            <q-tabs
              v-model="tab"
              dense
              class="text-grey"
              active-color="primary"
              indicator-color="primary"
              align="justify"
              narrow-indicator
            >
              <q-tab name="transaction" icon="settings_ethernet" label="Transaction" />
              <q-tab name="sms" icon="sms" label="SMS Text" />
              <q-tab name="voice" icon="mic" label="Voice Transcript" />
            </q-tabs>

            <q-separator />

            <q-tab-panels v-model="tab" animated>
              <q-tab_panel name="transaction">
                <div class="row q-col-gutter-sm">
                  <div class="col-12 col-sm-6">
                    <q-input v-model="form.upi_id" label="Payee UPI ID" outlined dense />
                  </div>
                  <div class="col-12 col-sm-6">
                    <q-input v-model.number="form.amount" type="number" label="Amount" outlined dense />
                  </div>
                  <div class="col-12">
                    <q-checkbox v-model="form.is_post_call" label="Transaction initiated after a call?" color="primary" />
                  </div>
                </div>
              </q-tab_panel>

              <q-tab_panel name="sms">
                <q-input
                  v-model="form.sms_text"
                  type="textarea"
                  label="Paste SMS content here..."
                  outlined
                  rows="5"
                />
              </q-tab_panel>

              <q-tab_panel name="voice">
                <q-input
                  v-model="form.call_transcript"
                  type="textarea"
                  label="Paste voice transcript here..."
                  outlined
                  rows="5"
                />
              </q-tab_panel>
            </q-tab-panels>

            <q-card-actions align="right" class="q-pa-md">
              <q-btn 
                label="Run Global Analysis" 
                color="primary" 
                icon="analytics" 
                unelevated 
                size="lg"
                class="full-width"
                @click="runAnalysis"
                :loading="loading"
              />
            </q-card-actions>
          </q-card>
        </div>

        <!-- Result Section -->
        <div class="col-12 col-md-5">
          <q-card v-if="result" class="shadow-2 rounded-borders full-height flex flex-center text-center">
            <q-card-section>
              <div class="text-subtitle1 text-grey-7 q-mb-sm">Global Risk Score</div>
              
              <q-circular-progress
                show-value
                class="q-ma-md"
                :value="result.global_score"
                size="150px"
                :thickness="0.2"
                :color="result.global_score > 75 ? 'red' : (result.global_score > 40 ? 'orange' : 'green')"
                track-color="grey-3"
              >
                <span class="text-h3 text-weight-bold">{{ result.global_score }}</span>
              </q-circular-progress>

              <div class="text-h5 text-weight-bold q-mt-md" :class="scoreColorClass">
                {{ result.risk_level }}
              </div>
              
              <q-banner dense class="bg-grey-3 rounded-borders q-mt-lg text-left">
                <template v-slot:avatar>
                  <q-icon name="lightbulb" color="amber" />
                </template>
                <div class="text-weight-medium">AI Recommendation:</div>
                <div class="text-caption text-grey-9">{{ result.recommendation }}</div>
              </q-banner>

              <div class="q-mt-md text-left">
                <div class="text-caption text-grey-6 q-mb-xs">Modalities Integrated:</div>
                <div class="flex q-gutter-xs">
                  <q-badge v-for="m in result.modalities_analyzed" :key="m" color="blue-2" text-color="blue-10">
                    {{ m }}
                  </q-badge>
                </div>
              </div>
            </q-card-section>
          </q-card>
          
          <q-card v-else class="shadow-2 rounded-borders full-height flex flex-center border-dashed">
            <div class="text-grey-5 q-pa-xl">
              <q-icon name="query_stats" size="64px" class="q-mb-md" />
              <div>Fill the data and run analysis to see the report</div>
            </div>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const tab = ref('transaction')
const loading = ref(false)
const result = ref<any>(null)

const form = reactive({
  upi_id: '',
  amount: 0,
  device_id: 'DEV-999',
  timestamp: new Date().toISOString(),
  payer_upi_id: 'me@upi',
  payer_device_id: 'DEV-999',
  payer_account_age_days: 365,
  is_post_call: false,
  user_avg_amount: 500,
  user_tx_count: 50,
  sms_text: '',
  call_transcript: ''
})

const scoreColorClass = computed(() => {
  if (!result.value) return ''
  if (result.value.global_score > 75) return 'text-red'
  if (result.value.global_score > 40) return 'text-orange-9'
  return 'text-green'
})

const runAnalysis = async () => {
  loading.value = true
  result.value = null
  
  try {
    const payload = {
      transaction: {
        upi_id: form.upi_id,
        amount: form.amount,
        device_id: form.device_id,
        timestamp: form.timestamp,
        payer_upi_id: form.payer_upi_id,
        payer_device_id: form.payer_device_id,
        payer_account_age_days: form.payer_account_age_days,
        is_post_call: form.is_post_call,
        user_avg_amount: form.user_avg_amount,
        user_tx_count: form.user_tx_count
      },
      sms_text: form.sms_text || null,
      call_transcript: form.call_transcript || null
    }

    const response = await fetch('/api/multi/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      result.value = await response.json()
      $q.notify({
        color: result.value.global_score > 40 ? 'negative' : 'positive',
        message: 'Analysis Complete',
        icon: 'done_all'
      })
    } else {
      throw new Error('Analysis failed')
    }
  } catch (err) {
    $q.notify({
      color: 'negative',
      message: 'Failed to run multimodal analysis. Ensure models are trained.',
      icon: 'error'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.max-width-container {
  max-width: 1000px;
}
.border-dashed {
  border: 2px dashed #e0e0e0;
}
</style>
