<template>
  <q-page class="q-pa-md flex flex-center">
    <div class="report-container">
      <div class="text-h4 text-weight-bold q-mb-lg text-primary text-center">Report Fraud</div>
      
      <q-stepper
        v-model="step"
        ref="stepperRef"
        color="primary"
        animated
        class="bg-blur"
      >
        <q-step
          :name="1"
          title="Fraud Type"
          icon="settings"
          :done="step > 1"
        >
          <div class="text-subtitle1 q-mb-md">Select the type of fraud you encountered:</div>
          <div class="q-gutter-sm column">
            <q-radio v-model="form.fraud_type" val="fake_qr" label="Fake QR Code" color="primary" />
            <q-radio v-model="form.fraud_type" val="impersonation" label="Impersonation" color="primary" />
            <q-radio v-model="form.fraud_type" val="lottery" label="Lottery Scam" color="primary" />
            <q-radio v-model="form.fraud_type" val="investment" label="Investment Fraud" color="primary" />
            <q-radio v-model="form.fraud_type" val="other" label="Other" color="primary" />
          </div>
        </q-step>

        <q-step
          :name="2"
          title="Details"
          icon="assignment"
          :done="step > 2"
        >
          <div class="q-gutter-y-md">
            <q-input
              filled
              v-model="form.upi_id"
              label="Fraudulent UPI ID"
              placeholder="e.g. suspect@bank"
              hint="The UPI ID that requested or received money"
            />
            <q-input
              filled
              v-model.number="form.amount_lost"
              type="number"
              label="Amount Lost (₹)"
              prefix="₹"
            />
            <q-input
              filled
              v-model="form.utr_number"
              label="UTR / Transaction Number"
              hint="Check your transaction history for the 12-digit number"
            />
            <q-input
              filled
              v-model="form.description"
              type="textarea"
              label="Description"
              placeholder="Describe what happened..."
            />
          </div>
        </q-step>

        <q-step
          :name="3"
          title="Confirmation"
          icon="check_circle"
        >
          <div v-if="caseId" class="text-center">
            <q-icon name="verified" color="positive" size="100px" />
            <div class="text-h5 q-mt-md">Report Submitted!</div>
            <div class="text-subtitle1 q-mb-md">Case ID: <span class="text-weight-bold">{{ caseId }}</span></div>
            <q-banner dense class="bg-positive text-white rounded-borders">
              Your report helps protect the community. Our team will investigate this UPI ID.
            </q-banner>
          </div>
          <div v-else class="text-center">
            <div class="text-subtitle1 q-mb-lg">Please review your details before submitting.</div>
            <div class="q-pa-md bg-grey-2 rounded-borders text-left q-mb-md">
              <div><strong>Type:</strong> {{ form.fraud_type }}</div>
              <div><strong>UPI ID:</strong> {{ form.upi_id }}</div>
              <div><strong>Amount:</strong> ₹{{ form.amount_lost }}</div>
              <div><strong>UTR:</strong> {{ form.utr_number }}</div>
            </div>
            <q-btn
              color="primary"
              label="Submit Report"
              @click="submitReport"
              :loading="loading"
              class="full-width"
              size="lg"
            />
          </div>
        </q-step>

        <template v-slot:navigation>
          <q-stepper-navigation class="flex justify-between q-mt-md">
            <q-btn
              v-if="step > 1 && !caseId"
              flat
              color="primary"
              @click="stepperRef?.previous()"
              label="Back"
            />
            <q-btn
              v-if="step < 3"
              @click="stepperRef?.next()"
              color="primary"
              label="Continue"
              :disable="isNextDisabled"
            />
            <q-btn
              v-if="caseId"
              @click="goToDashboard"
              color="primary"
              label="Go to Dashboard"
            />
          </q-stepper-navigation>
        </template>
      </q-stepper>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar, QStepper } from 'quasar'
import { api } from 'boot/axios'

const $q = useQuasar()
const router = useRouter()
const step = ref(1)
const loading = ref(false)
const caseId = ref<string | null>(null)
const stepperRef = ref<InstanceType<typeof QStepper> | null>(null)

const form = reactive({
  upi_id: '',
  fraud_type: 'fake_qr',
  amount_lost: null as number | null,
  utr_number: '',
  description: '',
  evidence_url: null
})

const isNextDisabled = computed(() => {
  if (step.value === 1) return !form.fraud_type
  if (step.value === 2) return !form.upi_id || !form.amount_lost || !form.utr_number
  return false
})

async function submitReport() {
  loading.value = true
  try {
    const response = await api.post('/reports/submit', form)
    caseId.value = response.data.case_id
    $q.notify({
      type: 'positive',
      message: `Report submitted. Case ID: ${caseId.value}`,
      position: 'top'
    })
    await router.push('/')
  } catch (error: unknown) {
    console.error('Submission error:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to submit report. Please try again.',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

async function goToDashboard() {
  await router.push('/')
}
</script>

<style scoped>
.report-container {
  width: 100%;
  max-width: 600px;
}
.bg-blur {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
}
</style>
