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
              <q-tab-panel name="transaction">
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
              </q-tab-panel>

              <q-tab-panel name="sms">
                <q-input
                  v-model="form.sms_text"
                  type="textarea"
                  label="Paste SMS content here..."
                  outlined
                  rows="5"
                />
              </q-tab-panel>

              <q-tab-panel name="voice">
                <div class="q-gutter-y-md">
                  <div class="row q-col-gutter-md items-center">
                    <div class="col-12 col-sm-6">
                      <q-file
                        v-model="audioFile"
                        label="Upload Audio (.mp3, .wav)"
                        outlined
                        dense
                        accept=".mp3,.wav,audio/*"
                      >
                        <template v-slot:prepend>
                          <q-icon name="attach_file" />
                        </template>
                        <template v-slot:after v-if="audioFile">
                          <q-btn round dense flat icon="send" color="primary" @click="uploadAudio" :loading="transcriptionLoading" />
                        </template>
                      </q-file>
                    </div>
                    <div class="col-12 col-sm-6 text-center">
                      <q-btn
                        :color="isRecording ? 'red' : 'primary'"
                        :icon="isRecording ? 'stop' : 'mic'"
                        :label="isRecording ? 'Stop Recording' : 'Record Memo'"
                        @click="isRecording ? stopRecording() : startRecording()"
                        unelevated
                        :loading="transcriptionLoading && isRecording"
                      />
                      <div v-if="isRecording" class="text-caption text-red q-mt-xs anim-pulse">recording...</div>
                    </div>
                  </div>

                  <q-separator />

                  <div class="text-subtitle2 text-grey-7 q-mb-xs">Transcript</div>
                  <q-input
                    v-model="form.call_transcript"
                    type="textarea"
                    label="AI Transcription will appear here..."
                    outlined
                    rows="4"
                    :loading="transcriptionLoading"
                  />
                </div>
              </q-tab-panel>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import { useAuthStore } from 'src/stores/authStore'

interface AnalysisResult {
  global_score: number;
  risk_level: string;
  recommendation: string;
  modalities_analyzed: string[];
}

const $q = useQuasar()
const authStore = useAuthStore()
const tab = ref('transaction')
const loading = ref(false)
const result = ref<AnalysisResult | null>(null)

// Generate a stable device fingerprint for this browser session
const deviceId = `DEV-${navigator.userAgent.length}-${screen.width}x${screen.height}`

// Audio Recording State
const audioFile = ref<File | null>(null)
const isRecording = ref(false)
const transcriptionLoading = ref(false)
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []

const form = reactive({
  upi_id: '',
  amount: 0,
  device_id: deviceId,
  timestamp: new Date().toISOString(),
  payer_upi_id: authStore.userEmail ?? 'unknown@upi',
  payer_device_id: deviceId,
  payer_account_age_days: 0,
  is_post_call: false,
  user_avg_amount: 0,
  user_tx_count: 0,
  sms_text: '',
  call_transcript: ''
})

onMounted(async () => {
  try {
    const res = await api.get('/auth/me');
    if (res.data) {
      form.payer_account_age_days = res.data.account_age_days || 1;
      form.user_avg_amount = res.data.avg_amount || 0;
      form.user_tx_count = res.data.tx_count || 0;
    }
  } catch (err) {
    console.error('Failed to load personalized user stats:', err);
  }
})

const scoreColorClass = computed(() => {
  const score = result.value?.global_score ?? 0
  if (score > 75) return 'text-red'
  if (score > 40) return 'text-orange-9'
  return 'text-green'
})

// Voice Recording Logic
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []
    
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data)
    }
    
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
      const file = new File([audioBlob], 'memo.wav', { type: 'audio/wav' })
      audioFile.value = file
      void processAudio(file)
    }
    
    mediaRecorder.start()
    isRecording.value = true
  } catch {
    $q.notify({ color: 'negative', message: 'Microphone access denied' })
  }
}

const stopRecording = () => {
  if (mediaRecorder) {
    mediaRecorder.stop()
    isRecording.value = false
  }
}

const uploadAudio = () => {
  if (audioFile.value) {
    void processAudio(audioFile.value)
  }
}

const processAudio = async (file: File) => {
  transcriptionLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/audio/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    pollTranscriptionResult(response.data.task_id)
  } catch {
    $q.notify({ color: 'negative', message: 'Failed to upload audio' })
    transcriptionLoading.value = false
  }
}

const pollTranscriptionResult = (taskId: string) => {
  const poll = async () => {
    try {
      const response = await api.get(`/audio/result/${taskId}`)
      if (response.data.status === 'complete') {
        form.call_transcript = response.data.transcription
        transcriptionLoading.value = false
        $q.notify({ color: 'positive', message: 'Transcription complete', icon: 'mic' })
      } else if (response.data.status === 'failed') {
        throw new Error('Transcription failed')
      } else {
        setTimeout(() => { void poll() }, 2000)
      }
    } catch {
      $q.notify({ color: 'negative', message: 'Transcription failed' })
      transcriptionLoading.value = false
    }
  }
  void poll()
}

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

    const response = await api.post('/multi/verify', payload)
    result.value = response.data
    
    $q.notify({
      color: (result.value?.global_score ?? 0) > 40 ? 'negative' : 'positive',
      message: 'Analysis Complete',
      icon: 'done_all'
    })
  } catch {
    $q.notify({
      color: 'negative',
      message: 'Failed to run multimodal analysis. Ensure models and workers are running.',
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
.anim-pulse {
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>
