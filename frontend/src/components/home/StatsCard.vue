<script setup lang="ts">
defineProps<{
  title: string
  value: number
  icon: 'eye' | 'collection' | 'mic' | 'camera'
  color: 'sage' | 'amber' | 'slate' | 'forest'
}>()

const iconPaths = {
  eye: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
  collection: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
  mic: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z',
  camera: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M15 13a3 3 0 11-6 0 3 3 0 016 0z',
}

const colorClasses = {
  sage: 'bg-sage-900/50 text-sage-400',
  amber: 'bg-amber-900/30 text-amber-400',
  slate: 'bg-slate-800/60 text-cream-400',
  forest: 'bg-forest-900/40 text-forest-400',
}
</script>

<template>
  <div class="card p-6">
    <div class="flex items-center gap-4">
      <div :class="['w-12 h-12 rounded-xl flex items-center justify-center', colorClasses[color]]">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPaths[icon]"/>
        </svg>
      </div>
      <div>
        <p class="text-3xl font-display font-bold text-cream-100">{{ value }}</p>
        <p class="text-sm text-cream-500">{{ title }}</p>
      </div>
    </div>
  </div>
</template>
