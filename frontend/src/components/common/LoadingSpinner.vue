<script setup lang="ts">
defineProps<{
  size?: 'sm' | 'md' | 'lg'
  text?: string
}>()

const sizeClasses = {
  sm: 'w-4 h-4 border-2',
  md: 'w-8 h-8 border-2',
  lg: 'w-12 h-12 border-3',
}
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3">
    <div
      :class="[
        'rounded-full border-frog-500 border-t-transparent animate-spin',
        sizeClasses[size || 'md']
      ]"
    />
    <p v-if="text" class="text-frog-400 text-sm">{{ text }}</p>
  </div>
</template>
