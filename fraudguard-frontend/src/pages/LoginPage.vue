<template>
  <q-page class="flex flex-center bg-grey-1">
    <q-card square bordered class="q-pa-lg shadow-2" style="width: 400px; border-radius: 12px;">
      <q-card-section class="bg-primary text-white text-center q-mb-md" style="border-top-left-radius: 12px; border-top-right-radius: 12px;">
        <div class="text-h6 text-weight-bold">{{ isRegister ? 'Register' : 'Login' }}</div>
      </q-card-section>
      
      <q-card-section class="q-gutter-y-md">
        <q-input 
          filled 
          v-model="form.email" 
          label="Email" 
          type="email" 
          lazy-rules
          :rules="[ val => val && val.length > 0 || 'Email is required']"
        />
        <q-input 
          filled 
          v-model="form.password" 
          label="Password" 
          type="password" 
          lazy-rules
          :rules="[ val => val && val.length > 0 || 'Password is required']"
        />
      </q-card-section>
      
      <q-card-actions class="q-px-md q-pb-lg">
        <q-btn
          unelevated
          color="primary"
          size="lg"
          class="full-width rounded-borders"
          :label="isRegister ? 'Register' : 'Login'"
          @click="handleSubmit"
          :loading="loading"
        />
      </q-card-actions>
      
      <q-card-section class="text-center q-pa-none">
        <q-btn flat class="text-primary text-weight-bold" @click="isRegister = !isRegister">
          {{ isRegister ? 'Back to Login' : 'Need an account? Register' }}
        </q-btn>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/authStore'
import { useQuasar } from 'quasar'
import axios from 'axios'

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()

const isRegister = ref(false)
const loading = ref(false)

const form = reactive({
  email: '',
  password: ''
})

async function handleSubmit() {
  if (!form.email || !form.password) {
    $q.notify({ type: 'warning', message: 'Please fill in all fields' })
    return
  }
  
  loading.value = true
  try {
    if (isRegister.value) {
      await authStore.register(form.email, form.password)
      $q.notify({ 
        type: 'positive', 
        message: 'Registered successfully! Please login with your credentials.', 
        position: 'top' 
      })
      isRegister.value = false
      form.password = '' // Clear password for login
    } else {
      await authStore.login(form.email, form.password)
      $q.notify({ 
        type: 'positive', 
        message: 'Logged in successfully!', 
        position: 'top' 
      })
      await router.push('/')
    }
  } catch (err: unknown) {
    console.error('Auth error:', err)
    let detail = 'Operation failed. Check your credentials.'
    if (axios.isAxiosError(err) && err.response?.data?.detail) {
      detail = err.response.data.detail as string
    }
    $q.notify({ 
      type: 'negative', 
      message: detail, 
      position: 'top' 
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.rounded-borders {
  border-radius: 8px;
}
</style>
