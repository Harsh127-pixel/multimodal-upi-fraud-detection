<template>
  <q-page class="page-wrapper">
    <div class="header-section fade-up fade-up-1">
      <div class="row items-center justify-between">
        <div>
          <div class="page-title sora">Community Threat Watch</div>
          <div class="page-subtitle">Crowdsourced Threat Intelligence via GenAI OCR</div>
        </div>
        <q-chip color="purple" icon="workspace_premium" text-color="white" label="Your Contribution Points: 150" class="sora text-bold" />
      </div>
    </div>

    <div class="row q-col-gutter-xl q-mt-md">
      <!-- Submission Form -->
      <div class="col-12 col-md-6 fade-up fade-up-2">
         <div class="fg-card">
            <div class="section-label mono">REPORT SUSPICIOUS ACTIVITY</div>
            <div class="q-mt-none text-grey-5 q-mb-xl">Upload screenshots of WhatsApp scams, fake QRs, or suspicious SMS messages. Our AI will extract the data to protect others.</div>
            
            <q-file
               v-model="imageFile"
               label="Upload Screenshot (PNG/JPG)"
               filled
               dark
               class="fg-input q-mb-md"
               accept="image/*"
            >
               <template v-slot:prepend>
                  <q-icon name="cloud_upload" />
               </template>
            </q-file>
            
            <q-input
               v-model="description"
               type="textarea"
               dark
               filled
               class="fg-input q-mb-lg"
               placeholder="Optional: Provide any context (e.g., 'They claimed to be from Jio')"
            />
            
            <q-btn
               color="primary"
               label="Extract & Report to Global Matrix"
               icon="troubleshoot"
               class="full-width q-py-sm sora"
               @click="submitReport"
               :loading="loading"
               size="lg"
            />
         </div>
      </div>
      
      <!-- Processing Results -->
      <div class="col-12 col-md-6 fade-up fade-up-3">
         <div class="fg-card full-height" style="min-height: 400px; display: flex; flex-direction: column;">
            <div class="section-label mono">GEN-AI OCR EXTRACTION RESULTS</div>
            
            <div v-if="!reportResult && !loading" class="empty-state">
               <q-icon name="document_scanner" size="48px" color="blue-grey-8" />
               <div class="q-mt-md text-grey">Awaiting Image Upload</div>
            </div>
            
            <div v-if="loading" class="empty-state">
               <q-spinner-grid size="48px" color="purple" />
               <div class="q-mt-md text-purple text-bold sora">Running Vision Model...</div>
            </div>

            <div v-if="reportResult" class="results-fade">
               <div class="q-mb-md">
                  <div class="mono text-grey-5 q-mb-xs">EXTRACTED TEXT</div>
                  <div class="bg-dark q-pa-md rounded-borders text-italic" style="border: 1px solid var(--fg-border)">
                     "{{ reportResult.extracted_text }}"
                  </div>
               </div>
               
               <div>
                  <div class="mono text-grey-5 q-mb-xs">THREAT INDICATORS FOUND</div>
                  <q-list dark bordered separator class="rounded-borders">
                     <q-item v-for="(indicator, i) in reportResult.threat_indicators_found" :key="i">
                        <q-item-section avatar>
                           <q-icon :name="indicator.type === 'phone' ? 'phone_android' : 'link'" color="negative" />
                        </q-item-section>
                        <q-item-section>
                           <q-item-label class="mono text-bold text-red">{{ indicator.value }}</q-item-label>
                           <q-item-label caption class="text-capitalize">{{ indicator.type }} Profile</q-item-label>
                        </q-item-section>
                     </q-item>
                  </q-list>
               </div>
               
               <div class="action-box q-mt-xl bg-green-10 rounded-borders q-pa-md row items-center gap-md">
                  <q-icon name="military_tech" color="white" size="32px" />
                  <div>
                    <div class="text-white sora">{{ reportResult.action }}</div>
                    <div class="text-green-2 text-caption">You earned +{{ reportResult.reward_points }} Trust Points!</div>
                  </div>
               </div>
            </div>
         </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from 'src/boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const loading = ref(false)
const imageFile = ref<File | null>(null)
const description = ref('')

interface ExtractedIndicator {
   type: string;
   value: string;
}

interface ReportResult {
   status: string;
   extracted_text: string;
   threat_indicators_found: ExtractedIndicator[];
   action: string;
   reward_points: number;
}

const reportResult = ref<ReportResult | null>(null)

async function submitReport() {
  if (!imageFile.value) {
     $q.notify({color:'warning', message: 'Please attach a screenshot'})
     return
  }
  
  loading.value = true
  reportResult.value = null
  
  try {
     // Mocking base64 conversion delay
     await new Promise(r => setTimeout(r, 800))
     const res = await api.post('/community/report', {
        image_base64: "data:image/png;base64,mock...", 
        description: description.value
     })
     reportResult.value = res.data
     $q.notify({color: 'positive', icon: 'check_circle', message: 'Successfully crowdsourced!'})
  } catch {
     $q.notify({color: 'negative', message: 'Failed to process report'})
  } finally {
     loading.value = false
  }
}
</script>

<style scoped lang="scss">
.page-wrapper {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

.empty-state {
   flex: 1;
   display: flex;
   flex-direction: column;
   align-items: center;
   justify-content: center;
}

.results-fade {
   animation: fadeIn 0.4s ease-out;
}
</style>
