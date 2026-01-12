<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  confidence: number
  size?: 'sm' | 'md' | 'lg'
}>()

const heightClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'h-1.5'
    case 'lg': return 'h-3'
    default: return 'h-2'
  }
})

const percentage = computed(() => Math.round(props.confidence * 100))

const colorClass = computed(() => {
  if (props.confidence >= 0.8) return 'from-sage-500 to-sage-400'
  if (props.confidence >= 0.5) return 'from-amber-500 to-amber-400'
  return 'from-slate-500 to-slate-400'
})
</script>

<template>
  <div class="confidence-meter" :class="heightClass">
    <div 
      class="h-full rounded-full bg-gradient-to-r transition-all duration-700 ease-out"
      :class="colorClass"
      :style="{ width: `${percentage}%` }"
    />
  </div>
</template>
