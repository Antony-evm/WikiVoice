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
  <div class="min-h-screen flex flex-col font-serif">
    <!-- Hero -->
    <main class="flex-1 flex flex-col items-center justify-center px-4 md:px-8 lg:px-16 pt-12 md:pt-16 pb-8 md:pb-10">
      <div class="max-w-4xl w-full text-center mx-auto">
        <div
          class="w-16 h-16 mx-auto mb-6 text-3xl border-2 border-[var(--border)] rounded-full flex items-center justify-center bg-[var(--surface)] text-[var(--primary)] font-serif shadow-sm">
          W
        </div>

        <h2
          class="text-3xl sm:text-4xl md:text-5xl font-normal text-[var(--text-primary)] mb-4 md:mb-6 leading-tight tracking-tight">
          The Free Encyclopedia
        </h2>

        <p
          class="text-xl sm:text-2xl md:text-3xl italic text-[var(--text-secondary)] mb-8 md:mb-12 font-light opacity-80">
          Voice Interface
        </p>

        <p
          class="text-base md:text-lg text-[var(--text-secondary)] mb-8 md:mb-12 max-w-2xl mx-auto leading-relaxed font-sans font-light">
          WikiVoice is a minimalist research tool. Ask questions, receive cited answers from Wikipedia, all through a
          natural voice interface.
        </p>

        <div class="flex justify-center gap-4 mb-8">
          <button @click="navigateTo(authStore.isAuthenticated ? 'chat' : 'auth')"
            class="px-8 md:px-12 py-3 md:py-4 border-2 border-[var(--primary)] rounded-lg bg-transparent hover:bg-[var(--primary)] hover:text-white text-[var(--primary)] font-serif text-base md:text-lg transition-all duration-300 tracking-wider uppercase">
            Start Research
          </button>
        </div>

        <!-- Features -->
        <div class="mt-10 md:mt-14 grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 font-sans text-left">
          <div
            class="pt-6 border-t border-[var(--border)] hover:border-[var(--primary)] transition-colors duration-500 group">
            <div
              class="text-3xl md:text-4xl mb-4 opacity-40 font-serif group-hover:text-[var(--primary)] transition-colors">
              01.</div>
            <h3 class="text-lg md:text-xl font-bold text-[var(--text-primary)] mb-3 uppercase tracking-wide">
              Voice Input
            </h3>
            <p class="text-[var(--text-secondary)] text-sm md:text-base leading-relaxed font-light">
              Dictate your queries naturally. The system transcribes and processes your voice with high fidelity.
            </p>
          </div>
          <div
            class="pt-6 border-t border-[var(--border)] hover:border-[var(--primary)] transition-colors duration-500 group">
            <div
              class="text-3xl md:text-4xl mb-4 opacity-40 font-serif group-hover:text-[var(--primary)] transition-colors">
              02.</div>
            <h3 class="text-lg md:text-xl font-bold text-[var(--text-primary)] mb-3 uppercase tracking-wide">
              Sourced Knowledge
            </h3>
            <p class="text-[var(--text-secondary)] text-sm md:text-base leading-relaxed font-light">
              Answers are synthesized directly from Wikipedia, ensuring every claim is backed by the world's knowledge.
            </p>
          </div>
          <div
            class="pt-6 border-t border-[var(--border)] hover:border-[var(--primary)] transition-colors duration-500 group">
            <div
              class="text-3xl md:text-4xl mb-4 opacity-40 font-serif group-hover:text-[var(--primary)] transition-colors">
              03.</div>
            <h3 class="text-lg md:text-xl font-bold text-[var(--text-primary)] mb-3 uppercase tracking-wide">
              Audio Synthesis
            </h3>
            <p class="text-[var(--text-secondary)] text-sm md:text-base leading-relaxed font-light">
              Listen to your results. Perfect for accessibility and research on the go.
            </p>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-[var(--border)] px-4 py-6 font-sans mt-auto">
      <div
        class="max-w-4xl mx-auto text-center text-[var(--text-secondary)] text-xs uppercase tracking-wider opacity-60">
        <p>&copy; {{ new Date().getFullYear() }} WikiVoice. A research interface for the open web.</p>
      </div>
    </footer>
  </div>
</template>
