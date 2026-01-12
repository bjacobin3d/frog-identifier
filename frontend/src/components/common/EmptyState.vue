<script setup lang="ts">
defineProps<{
  icon?: 'search' | 'collection' | 'audio' | 'camera'
  title: string
  description?: string
}>()

const iconPaths = {
  search: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
  collection: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
  audio: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z',
  camera: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M15 13a3 3 0 11-6 0 3 3 0 016 0z',
}
</script>

<template>
  <div class="card p-12 text-center">
    <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-frog-800/30 flex items-center justify-center">
      <svg class="w-8 h-8 text-frog-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPaths[icon || 'collection']"/>
      </svg>
    </div>
    <h3 class="text-xl font-display font-semibold text-white mb-2">{{ title }}</h3>
    <p v-if="description" class="text-frog-500 mb-6">{{ description }}</p>
    <slot />
  </div>
</template>
