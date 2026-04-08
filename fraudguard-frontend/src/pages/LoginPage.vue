<template>
  <q-page class="login-page">

    <!-- Background mesh -->
    <div class="login-bg">
      <div class="mesh-orb orb-1" />
      <div class="mesh-orb orb-2" />
      <div class="mesh-grid" />
    </div>

    <!-- Content -->
    <div class="login-container">

      <!-- Brand -->
      <div class="brand-block fade-up fade-up-1">
        <div class="brand-icon">
          <q-icon name="shield" size="26px" class="text-blue-light" />
        </div>
        <div class="brand-name sora">FraudGuard</div>
        <div class="brand-tagline">Advanced UPI Fraud Detection</div>
      </div>

      <!-- Card -->
      <div class="login-card fg-card fade-up fade-up-2">

        <!-- Tabs -->
        <div class="auth-tabs">
          <button
            class="auth-tab"
            :class="{ active: !isRegister }"
            @click="isRegister = false"
          >
            Sign In
          </button>
          <button
            class="auth-tab"
            :class="{ active: isRegister }"
            @click="isRegister = true"
          >
            Register
          </button>
          <div class="tab-indicator" :class="{ right: isRegister }" />
        </div>

        <div class="auth-body">
          <transition name="form-fade" mode="out-in">
            <div :key="isRegister ? 'register' : 'login'">
              <div class="auth-title sora">
                {{ isRegister ? 'Create Account' : 'Welcome back' }}
              </div>
              <div class="auth-sub">
                {{ isRegister
                  ? 'Join FraudGuard to protect your transactions'
                  : 'Sign in to your security dashboard' }}
              </div>

              <div class="form-fields">
                <div class="field-group">
                  <label class="field-label mono">EMAIL ADDRESS</label>
                  <div class="field-wrap" :class="{ focused: emailFocused }">
                    <q-icon name="alternate_email" size="16px" class="field-icon" />
                    <input
                      v-model="form.email"
                      type="email"
                      class="field-input"
                      placeholder="you@example.com"
                      autocomplete="email"
                      @focus="emailFocused = true"
                      @blur="emailFocused = false"
                      @keyup.enter="handleSubmit"
                    />
                  </div>
                </div>

                <div class="field-group">
                  <label class="field-label mono">PASSWORD</label>
                  <div class="field-wrap" :class="{ focused: passFocused }">
                    <q-icon name="lock_outline" size="16px" class="field-icon" />
                    <input
                      v-model="form.password"
                      :type="showPass ? 'text' : 'password'"
                      class="field-input"
                      placeholder="••••••••"
                      autocomplete="current-password"
                      @focus="passFocused = true"
                      @blur="passFocused = false"
                      @keyup.enter="handleSubmit"
                    />
                    <button class="field-toggle" @click="showPass = !showPass" type="button">
                      <q-icon :name="showPass ? 'visibility_off' : 'visibility'" size="16px" />
                    </button>
                  </div>
                </div>
              </div>

              <button
                class="submit-btn"
                @click="handleSubmit"
                :disabled="loading"
              >
                <span v-if="!loading">
                  {{ isRegister ? 'Create Account' : 'Sign In' }}
                  <q-icon name="arrow_forward" size="16px" />
                </span>
                <span v-else class="btn-loading">
                  <q-spinner-dots size="20px" color="white" />
                </span>
              </button>

              <div v-if="errorMsg" class="error-banner">
                <q-icon name="error_outline" size="16px" />
                {{ errorMsg }}
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Security badge -->
      <div class="security-badge fade-up fade-up-3">
        <q-icon name="lock" size="12px" />
        <span>End-to-end encrypted &nbsp;·&nbsp; RBI Compliant</span>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/authStore'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const isRegister = ref(false)
const loading = ref(false)
const showPass = ref(false)
const emailFocused = ref(false)
const passFocused = ref(false)
const errorMsg = ref('')

const form = reactive({ email: '', password: '' })

async function handleSubmit() {
  if (!form.email || !form.password) {
    errorMsg.value = 'Please fill in all fields'
    return
  }
  errorMsg.value = ''
  loading.value = true

  try {
    if (isRegister.value) {
      await authStore.register(form.email, form.password)
      isRegister.value = false
      form.password = ''
      errorMsg.value = ''
    } else {
      await authStore.login(form.email, form.password)
      await router.push('/')
    }
  } catch (err: unknown) {
    let detail = 'Operation failed. Check your credentials.'
    if (axios.isAxiosError(err) && err.response?.data?.detail) {
      detail = err.response.data.detail as string
    }
    errorMsg.value = detail
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--fg-navy);
  overflow: hidden;
  position: relative;
}

// Background effects
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.mesh-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;

  &.orb-1 {
    width: 500px; height: 500px;
    background: var(--fg-blue);
    top: -200px; left: -150px;
  }

  &.orb-2 {
    width: 400px; height: 400px;
    background: var(--fg-cyan);
    bottom: -150px; right: -100px;
    opacity: 0.08;
  }
}

.mesh-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
  background-size: 40px 40px;
}

// Container
.login-container {
  width: 100%;
  max-width: 420px;
  padding: 24px;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

// Brand
.brand-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.brand-icon {
  width: 52px; height: 52px;
  border-radius: 14px;
  background: rgba(59,130,246,0.12);
  border: 1px solid rgba(59,130,246,0.2);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 30px rgba(59,130,246,0.15);
}

.brand-name {
  font-size: 24px;
  font-weight: 800;
  color: var(--fg-text-primary);
  letter-spacing: -0.5px;
}

.brand-tagline {
  font-size: 13px;
  color: var(--fg-text-muted);
}

// Card
.login-card {
  width: 100%;
  border-radius: 20px !important;
  overflow: hidden;
}

// Auth tabs
.auth-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  position: relative;
  background: var(--fg-surface);
  border-bottom: 1px solid var(--fg-border);
}

.auth-tab {
  padding: 14px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: var(--fg-text-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  position: relative;
  z-index: 1;

  &.active { color: var(--fg-text-primary); }
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50%;
  height: 2px;
  background: var(--fg-blue);
  transition: transform 0.25s ease;
  box-shadow: 0 0 8px rgba(59,130,246,0.5);

  &.right { transform: translateX(100%); }
}

.auth-body { padding: 28px; }

.auth-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--fg-text-primary);
  margin-bottom: 4px;
}

.auth-sub {
  font-size: 13px;
  color: var(--fg-text-muted);
  margin-bottom: 24px;
}

// Form
.form-fields { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }

.field-group { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 1.2px;
  color: var(--fg-text-muted);
  text-transform: uppercase;
}

.field-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--fg-surface);
  border: 1px solid var(--fg-border);
  border-radius: 10px;
  padding: 0 14px;
  transition: all 0.2s ease;

  &.focused {
    border-color: var(--fg-blue);
    box-shadow: 0 0 0 3px var(--fg-blue-glow);
  }
}

.field-icon { color: var(--fg-text-muted); flex-shrink: 0; }

.field-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--fg-text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  padding: 13px 0;

  &::placeholder { color: var(--fg-text-muted); }
}

.field-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--fg-text-muted);
  display: flex;
  padding: 0;

  &:hover { color: var(--fg-text-primary); }
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: var(--fg-blue);
  border: none;
  border-radius: 10px;
  color: white;
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 16px rgba(59,130,246,0.35);
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #2563EB;
    box-shadow: 0 6px 22px rgba(59,130,246,0.5);
    transform: translateY(-1px);
  }

  &:disabled { opacity: 0.7; cursor: not-allowed; }
}

.btn-loading { display: flex; align-items: center; justify-content: center; }

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  padding: 10px 14px;
  border-radius: 8px;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.2);
  color: var(--fg-red);
  font-size: 13px;
}

// Security badge
.security-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--fg-text-muted);
  font-family: 'DM Mono', monospace;
}

// Transitions
.form-fade-enter-active, .form-fade-leave-active { transition: all 0.2s ease; }
.form-fade-enter-from  { opacity: 0; transform: translateY(6px); }
.form-fade-leave-to    { opacity: 0; transform: translateY(-6px); }
</style>
