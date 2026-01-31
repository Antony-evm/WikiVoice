<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api, { getErrorMessage } from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref('')

const isFormValid = computed(() => {
  if (!email.value || !password.value || !confirmPassword.value) {
    return false
  }

  if (password.value !== confirmPassword.value) {
    return false
  }

  if (password.value.length < 8 || password.value.length > 32) {
    return false
  }

  const hasUppercase = /[A-Z]/.test(password.value)
  const hasLowercase = /[a-z]/.test(password.value)
  const hasNumber = /\d/.test(password.value)
  const hasSymbol = /[^a-zA-Z0-9\s]/.test(password.value)

  return hasUppercase && hasLowercase && hasNumber && hasSymbol
})

async function handleRegister() {
  if (!email.value || !password.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 8 || password.value.length > 32) {
    error.value = 'Password must be between 8 and 32 characters'
    return
  }

  const hasUppercase = /[A-Z]/.test(password.value)
  const hasLowercase = /[a-z]/.test(password.value)
  const hasNumber = /\d/.test(password.value)
  const hasSymbol = /[^a-zA-Z0-9\s]/.test(password.value)

  if (!hasUppercase || !hasLowercase || !hasNumber || !hasSymbol) {
    error.value = 'Password must include uppercase, lowercase, number, and symbol'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await api.post('/auth/register', {
      email: email.value,
      password: password.value,
    })

    const { user } = response.data.data
    authStore.setUser(user.user_id, user.email)

    router.push({ name: 'chat' })
  } catch (err: unknown) {
    error.value = getErrorMessage(err, 'Registration failed. Please try again.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-[var(--background)] flex items-center justify-center px-4 md:px-8 pt-20 pb-8 font-sans">
    <div class="w-full max-w-md mx-auto">
      <div class="text-center mb-8">
        <h1
          class="text-4xl font-serif font-bold text-[var(--text-primary)] mb-4 flex items-center justify-center">
          <div
            class="w-14 h-14 border-2 border-[var(--text-primary)] rounded-full flex items-center justify-center text-2xl">
            W</div>
        </h1>
        <h2 class="text-lg text-[var(--text-primary)] font-serif italic opacity-70">New Researcher
          Registration</h2>
      </div>

      <form @submit.prevent="handleRegister"
        class="bg-transparent border border-[var(--border)] rounded-lg p-6 md:p-8 relative">
        <div
          class="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[var(--background)] px-4 py-1 text-xs font-serif text-[var(--text-secondary)] tracking-wider uppercase">
          Application
        </div>

        <div v-if="error"
          class="mb-4 p-3 bg-red-50 border-l-4 border-red-500 rounded text-red-600 text-sm font-serif">
          {{ error }}
        </div>

        <div class="mb-4">
          <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-2 uppercase tracking-wider">
            Email
          </label>
          <input v-model="email" type="email" placeholder="researcher@university.edu"
            class="w-full px-4 py-3 bg-[var(--background)] border border-[var(--border)] rounded-lg text-base text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all" />
        </div>

        <div class="mb-4">
          <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-2 uppercase tracking-wider">
            Password
          </label>
          <input v-model="password" type="password" placeholder="••••••••"
            class="w-full px-4 py-3 bg-[var(--background)] border border-[var(--border)] rounded-lg text-base text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all" />
        </div>

        <div class="mb-6">
          <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-2 uppercase tracking-wider">
            Confirm Password
          </label>
          <input v-model="confirmPassword" type="password" placeholder="••••••••"
            class="w-full px-4 py-3 bg-[var(--background)] border border-[var(--border)] rounded-lg text-base text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all" />
        </div>

        <button type="submit" :disabled="isLoading || !isFormValid"
          class="w-full py-3 bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-semibold font-serif text-base rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider">
          {{ isLoading ? 'Registering...' : 'Create Credentials' }}
        </button>

        <p class="mt-6 text-center text-[var(--text-secondary)] font-serif italic text-sm">
          Already registered?
          <router-link to="/login" class="text-[var(--primary)] hover:underline ml-1 font-semibold">
            Log in
          </router-link>
        </p>
      </form>
    </div>
  </div>
</template>
