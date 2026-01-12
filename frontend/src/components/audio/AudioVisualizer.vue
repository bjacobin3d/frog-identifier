<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  level: number
  isRecording: boolean
}>()

const bars = computed(() => {
  const count = 32
  const arr = []
  for (let i = 0; i < count; i++) {
    // Create a wave effect based on position
    const position = i / count
    const wave = Math.sin(position * Math.PI * 2 + Date.now() / 300) * 0.3
    const baseHeight = props.isRecording ? 0.2 : 0.05
    const height = Math.min(1, baseHeight + props.level * (0.7 + wave))
    arr.push(height)
  }
  return arr
})
</script>

<template>
  <div class="relative h-32 flex items-end justify-center gap-1 px-4">
    <div
      v-for="(height, index) in bars"
      :key="index"
      class="audio-bar w-2 min-h-[4px] transition-all duration-75"
      :class="{ 'animate-pulse-soft': isRecording }"
      :style="{ 
        height: `${height * 100}%`,
        opacity: isRecording ? 0.8 + height * 0.2 : 0.3,
      }"
    />
    
    <!-- Pulse ring when recording -->
    <div
      v-if="isRecording"
      class="absolute inset-0 flex items-center justify-center pointer-events-none"
    >
      <div class="w-20 h-20 rounded-full border-2 border-sage-500/30 animate-ping" />
    </div>
  </div>
</template>
