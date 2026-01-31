<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api, { getErrorMessage } from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

// Auth flow states
type AuthStep = 'email' | 'login' | 'register'
const step = ref<AuthStep>('email')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref('')
let errorTimeout: ReturnType<typeof setTimeout> | null = null

// Auto-dismiss error after 5 seconds
watch(error, (newError) => {
    if (errorTimeout) {
        clearTimeout(errorTimeout)
        errorTimeout = null
    }
    if (newError) {
        errorTimeout = setTimeout(() => {
            error.value = ''
        }, 5000)
    }
})

onUnmounted(() => {
    if (errorTimeout) clearTimeout(errorTimeout)
})

function dismissError() {
    error.value = ''
    if (errorTimeout) {
        clearTimeout(errorTimeout)
        errorTimeout = null
    }
}

// Password strength calculation
const passwordStrength = computed(() => {
    const pwd = password.value
    if (!pwd) return { score: 0, label: '', color: '' }

    let score = 0
    const checks = {
        length: pwd.length >= 8,
        lowercase: /[a-z]/.test(pwd),
        uppercase: /[A-Z]/.test(pwd),
        number: /\d/.test(pwd),
        symbol: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
    }

    if (checks.length) score++
    if (checks.lowercase) score++
    if (checks.uppercase) score++
    if (checks.number) score++
    if (checks.symbol) score++

    const labels = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong']
    const colors = ['', 'bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-emerald-500']

    return {
        score,
        label: labels[score],
        color: colors[score],
        checks,
    }
})

const authSubtitle = computed(() => {
    if (step.value === 'email') return 'Sign in to continue'
    if (step.value === 'login') return 'Welcome back!'
    return 'Create your account'
})

// Step 1: Check if email exists
async function handleEmailSubmit() {
    if (!email.value) {
        error.value = 'Please enter your email address'
        return
    }

    isLoading.value = true
    error.value = ''

    try {
        const response = await api.post('/auth/check-user', { email: email.value })
        const { exists } = response.data.data
        step.value = exists ? 'login' : 'register'
    } catch (err) {
        error.value = getErrorMessage(err, 'Failed to check email. Please try again.')
    } finally {
        isLoading.value = false
    }
}

// Step 2a: Login
async function handleLogin() {
    if (!password.value) {
        error.value = 'Please enter your password'
        return
    }

    isLoading.value = true
    error.value = ''

    try {
        const response = await api.post('/auth/login', {
            email: email.value,
            password: password.value,
        })
        const user = response.data.data
        authStore.setUser(user.user_id, user.email)
        router.push({ name: 'chat' })
    } catch (err) {
        error.value = getErrorMessage(err, 'Login failed. Please try again.')
    } finally {
        isLoading.value = false
    }
}

// Step 2b: Register
async function handleRegister() {
    if (!password.value || !confirmPassword.value) {
        error.value = 'Please fill in all fields'
        return
    }

    if (password.value !== confirmPassword.value) {
        error.value = 'Passwords do not match'
        return
    }

    if (passwordStrength.value.score < 4) {
        error.value = 'Password must include uppercase, lowercase, number, and be at least 8 characters'
        return
    }

    isLoading.value = true
    error.value = ''

    try {
        const response = await api.post('/auth/register', {
            email: email.value,
            password: password.value,
        })
        const user = response.data.data
        authStore.setUser(user.user_id, user.email)
        router.push({ name: 'chat' })
    } catch (err) {
        error.value = getErrorMessage(err, 'Registration failed. Please try again.')
    } finally {
        isLoading.value = false
    }
}

function goBack() {
    step.value = 'email'
    password.value = ''
    confirmPassword.value = ''
    error.value = ''
}
</script>

<template>
    <div class="min-h-screen bg-[var(--background)] flex items-center justify-center p-6">
        <div class="w-full max-w-lg">
            <!-- Logo & Header -->
            <div class="text-center mb-10">
                <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-[var(--primary)]/10 mb-6">
                    <span class="text-5xl">🎙️</span>
                </div>
                <h1 class="text-4xl font-bold text-[var(--text-primary)] mb-3">WikiVoice</h1>
                <p class="text-lg text-[var(--text-secondary)]">
                    {{ authSubtitle }}
                </p>
            </div>

            <!-- Auth Card -->
            <div class="bg-[var(--surface)] rounded-2xl p-8 shadow-xl">
                <!-- Error Alert -->
                <Transition name="fade">
                    <div v-if="error"
                        class="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-start gap-3">
                        <span class="text-lg">⚠️</span>
                        <span class="flex-1 text-sm">{{ error }}</span>
                        <button @click="dismissError"
                            class="text-red-400 hover:text-red-300 transition-colors text-lg leading-none">
                            ×
                        </button>
                    </div>
                </Transition>

                <!-- Step 1: Email -->
                <form v-if="step === 'email'" @submit.prevent="handleEmailSubmit" class="space-y-6">
                    <div>
                        <label class="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                            Email Address
                        </label>
                        <input v-model="email" type="email" placeholder="you@example.com" autofocus
                            class="w-full px-5 py-4 rounded-xl bg-[var(--background)] border-2 border-[var(--border)] text-[var(--text-primary)] text-lg placeholder-[var(--text-secondary)]/50 focus:outline-none focus:border-[var(--primary)] transition-colors" />
                    </div>

                    <button type="submit" :disabled="isLoading"
                        class="w-full py-4 rounded-xl bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-semibold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                        {{ isLoading ? 'Checking...' : 'Continue' }}
                    </button>
                </form>

                <!-- Step 2a: Login -->
                <form v-else-if="step === 'login'" @submit.prevent="handleLogin" class="space-y-6">
                    <div
                        class="flex items-center gap-3 p-4 rounded-xl bg-[var(--background)] border border-[var(--border)]">
                        <span class="text-2xl">👤</span>
                        <div class="flex-1">
                            <p class="text-sm text-[var(--text-secondary)]">Signing in as</p>
                            <p class="text-[var(--text-primary)] font-medium">{{ email }}</p>
                        </div>
                        <button type="button" @click="goBack" class="text-[var(--primary)] hover:underline text-sm">
                            Change
                        </button>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                            Password
                        </label>
                        <input v-model="password" type="password" placeholder="Enter your password" autofocus
                            class="w-full px-5 py-4 rounded-xl bg-[var(--background)] border-2 border-[var(--border)] text-[var(--text-primary)] text-lg placeholder-[var(--text-secondary)]/50 focus:outline-none focus:border-[var(--primary)] transition-colors" />
                    </div>

                    <button type="submit" :disabled="isLoading"
                        class="w-full py-4 rounded-xl bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-semibold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                        {{ isLoading ? 'Signing in...' : 'Sign In' }}
                    </button>
                </form>

                <!-- Step 2b: Register -->
                <form v-else @submit.prevent="handleRegister" class="space-y-6">
                    <div
                        class="flex items-center gap-3 p-4 rounded-xl bg-[var(--background)] border border-[var(--border)]">
                        <span class="text-2xl">✨</span>
                        <div class="flex-1">
                            <p class="text-sm text-[var(--text-secondary)]">Creating account for</p>
                            <p class="text-[var(--text-primary)] font-medium">{{ email }}</p>
                        </div>
                        <button type="button" @click="goBack" class="text-[var(--primary)] hover:underline text-sm">
                            Change
                        </button>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                            Password
                        </label>
                        <input v-model="password" type="password" placeholder="Create a strong password" autofocus
                            class="w-full px-5 py-4 rounded-xl bg-[var(--background)] border-2 border-[var(--border)] text-[var(--text-primary)] text-lg placeholder-[var(--text-secondary)]/50 focus:outline-none focus:border-[var(--primary)] transition-colors" />

                        <!-- Password Strength Indicator -->
                        <div v-if="password" class="mt-4 space-y-3">
                            <div class="flex gap-1.5">
                                <div v-for="i in 5" :key="i" :class="[
                                    'h-2 flex-1 rounded-full transition-all',
                                    i <= passwordStrength.score ? passwordStrength.color : 'bg-[var(--border)]'
                                ]" />
                            </div>
                            <p :class="[
                                'text-sm font-medium',
                                passwordStrength.score >= 4 ? 'text-green-400' :
                                    passwordStrength.score >= 3 ? 'text-yellow-400' : 'text-red-400'
                            ]">
                                {{ passwordStrength.label }}
                            </p>
                            <div class="grid grid-cols-2 gap-2 text-xs">
                                <div
                                    :class="passwordStrength.checks?.length ? 'text-green-400' : 'text-[var(--text-secondary)]'">
                                    {{ passwordStrength.checks?.length ? '✓' : '○' }} 8+ characters
                                </div>
                                <div
                                    :class="passwordStrength.checks?.uppercase ? 'text-green-400' : 'text-[var(--text-secondary)]'">
                                    {{ passwordStrength.checks?.uppercase ? '✓' : '○' }} Uppercase letter
                                </div>
                                <div
                                    :class="passwordStrength.checks?.lowercase ? 'text-green-400' : 'text-[var(--text-secondary)]'">
                                    {{ passwordStrength.checks?.lowercase ? '✓' : '○' }} Lowercase letter
                                </div>
                                <div
                                    :class="passwordStrength.checks?.number ? 'text-green-400' : 'text-[var(--text-secondary)]'">
                                    {{ passwordStrength.checks?.number ? '✓' : '○' }} Number
                                </div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                            Confirm Password
                        </label>
                        <input v-model="confirmPassword" type="password" placeholder="Confirm your password"
                            class="w-full px-5 py-4 rounded-xl bg-[var(--background)] border-2 border-[var(--border)] text-[var(--text-primary)] text-lg placeholder-[var(--text-secondary)]/50 focus:outline-none focus:border-[var(--primary)] transition-colors" />
                        <p v-if="confirmPassword && password !== confirmPassword" class="mt-2 text-sm text-red-400">
                            Passwords don't match
                        </p>
                    </div>

                    <button type="submit"
                        :disabled="isLoading || passwordStrength.score < 4 || password !== confirmPassword"
                        class="w-full py-4 rounded-xl bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-semibold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                        {{ isLoading ? 'Creating account...' : 'Create Account' }}
                    </button>
                </form>
            </div>

            <!-- Footer -->
            <p class="mt-8 text-center text-[var(--text-secondary)] text-sm">
                By continuing, you agree to our Terms of Service and Privacy Policy.
            </p>
        </div>
    </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}
</style>
