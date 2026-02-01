<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

function navigateTo(route: string) {
  mobileMenuOpen.value = false
  router.push({ name: route })
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
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
        <!-- Desktop nav links -->
        <button @click="navigateTo('architecture')"
          class="text-[var(--text-secondary)] hover:text-[var(--primary)] font-normal transition-colors uppercase text-sm tracking-wider hidden md:block">
          Architecture
        </button>
        <button @click="navigateTo('roadmap')"
          class="text-[var(--text-secondary)] hover:text-[var(--primary)] font-normal transition-colors uppercase text-sm tracking-wider hidden md:block">
          Roadmap
        </button>
        <template v-if="authStore.isAuthenticated">
          <button @click="navigateTo('chat')"
            class="text-[var(--text-primary)] hover:text-[var(--primary)] font-medium transition-colors uppercase text-sm tracking-wider hidden md:block">
            Research
          </button>
          <button @click="authStore.logout()"
            class="text-[var(--text-secondary)] hover:text-[var(--text-primary)] font-normal transition-colors uppercase text-sm tracking-wider hidden md:block">
            Logout
          </button>
        </template>
        <template v-else>
          <button @click="navigateTo('auth')"
            class="px-4 md:px-6 py-2 md:py-2.5 border-2 border-[var(--primary)] rounded-lg text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white transition-all duration-300 uppercase text-sm tracking-wider font-semibold hidden md:block">
            Sign In
          </button>
        </template>

        <!-- Mobile hamburger menu button -->
        <button @click="toggleMobileMenu" class="md:hidden p-2 text-[var(--text-primary)]" aria-label="Toggle menu">
          <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile dropdown menu -->
    <Transition name="slide">
      <div v-if="mobileMenuOpen" class="md:hidden border-t border-[var(--border)] bg-[var(--background)]">
        <nav class="px-4 py-3 space-y-1">
          <button @click="navigateTo('architecture')"
            class="block w-full text-left px-3 py-2.5 rounded-lg text-[var(--text-secondary)] hover:text-[var(--primary)] hover:bg-[var(--surface)] font-normal transition-colors uppercase text-sm tracking-wider">
            Architecture
          </button>
          <button @click="navigateTo('roadmap')"
            class="block w-full text-left px-3 py-2.5 rounded-lg text-[var(--text-secondary)] hover:text-[var(--primary)] hover:bg-[var(--surface)] font-normal transition-colors uppercase text-sm tracking-wider">
            Roadmap
          </button>
          <template v-if="authStore.isAuthenticated">
            <button @click="navigateTo('chat')"
              class="block w-full text-left px-3 py-2.5 rounded-lg text-[var(--text-primary)] hover:text-[var(--primary)] hover:bg-[var(--surface)] font-medium transition-colors uppercase text-sm tracking-wider">
              Research
            </button>
            <button @click="authStore.logout(); mobileMenuOpen = false"
              class="block w-full text-left px-3 py-2.5 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface)] font-normal transition-colors uppercase text-sm tracking-wider">
              Logout
            </button>
          </template>
          <template v-else>
            <button @click="navigateTo('auth')"
              class="block w-full text-center mt-2 px-4 py-2.5 border-2 border-[var(--primary)] rounded-lg text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white transition-all duration-300 uppercase text-sm tracking-wider font-semibold">
              Sign In
            </button>
          </template>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
