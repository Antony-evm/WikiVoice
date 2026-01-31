<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function navigateTo(route: string) {
  router.push({ name: route })
}
</script>

<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 border-b border-[var(--border)] bg-[var(--background)] backdrop-blur-sm transition-all duration-300">
    <div class="px-4 md:px-8 lg:px-12 py-3 md:py-4 flex justify-between items-center">
      <button @click="navigateTo('home')" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
        <div
          class="w-9 h-9 md:w-10 md:h-10 flex items-center justify-center border-2 border-[var(--primary)] rounded-lg text-[var(--primary)] font-serif font-bold text-xl md:text-2xl">
          W
        </div>
        <span
          class="text-xl md:text-2xl font-bold text-[var(--text-primary)] tracking-tight font-serif">WikiVoice</span>
      </button>
      <div class="flex gap-4 md:gap-6 items-center">
        <template v-if="authStore.isAuthenticated">
          <button @click="navigateTo('chat')"
            class="text-[var(--text-primary)] hover:text-[var(--primary)] font-medium transition-colors uppercase text-sm tracking-wider hidden md:block">
            Research
          </button>
          <button @click="authStore.logout()"
            class="text-[var(--text-secondary)] hover:text-[var(--text-primary)] font-normal transition-colors uppercase text-sm tracking-wider">
            Logout
          </button>
        </template>
        <template v-else>
          <button @click="navigateTo('auth')"
            class="px-4 md:px-6 py-2 md:py-2.5 border-2 border-[var(--primary)] rounded-lg text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white transition-all duration-300 uppercase text-sm tracking-wider font-semibold">
            Sign In
          </button>
        </template>
      </div>
    </div>
  </header>
</template>
