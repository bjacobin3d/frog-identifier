<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppNavigation from '@/components/layout/AppNavigation.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-950 relative">
    <!-- Subtle gradient background -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <!-- Top corner glow -->
      <div class="absolute -top-32 -right-32 w-[500px] h-[500px] bg-slate-800/30 rounded-full blur-[100px]"></div>
      <!-- Bottom accent -->
      <div class="absolute bottom-0 left-1/4 w-[600px] h-[300px] bg-sage-950/20 rounded-full blur-[120px]"></div>
      <!-- Subtle center glow -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-slate-900/50 rounded-full blur-[150px]"></div>
    </div>

    <!-- Noise texture overlay -->
    <div class="fixed inset-0 pointer-events-none opacity-[0.02]" 
         style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%270 0 256 256%27 xmlns=%27http://www.w3.org/2000/svg%27%3E%3Cfilter id=%27n%27%3E%3CfeTurbulence type=%27fractalNoise%27 baseFrequency=%270.7%27 numOctaves=%274%27 stitchTiles=%27stitch%27/%3E%3C/filter%3E%3Crect width=%27100%25%27 height=%27100%25%27 filter=%27url(%23n)%27/%3E%3C/svg%3E');">
    </div>

    <AppNavigation />
    
    <main class="flex-1 relative z-10">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
