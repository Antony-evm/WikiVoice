<script setup lang="ts">
import { RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[var(--background)]">
    <NavBar />
    <main class="flex-1 pt-16">
      <RouterView />
    </main>
  </div>
</template>
