<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{
  message: string
  type?: 'success' | 'error' | 'info' | 'warning'
  duration?: number
}>()

const emit = defineEmits<{
  close: []
}>()

const isVisible = ref(false)

const typeStyles = {
  success: 'bg-frog-500/20 border-frog-500/50 text-frog-300',
  error: 'bg-red-500/20 border-red-500/50 text-red-300',
  info: 'bg-pond-500/20 border-pond-500/50 text-pond-300',
  warning: 'bg-lilypad-500/20 border-lilypad-500/50 text-lilypad-300',
}

const icons = {
  success: 'M5 13l4 4L19 7',
  error: 'M6 18L18 6M6 6l12 12',
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
}

onMounted(() => {
  isVisible.value = true
  
  if (props.duration !== 0) {
    setTimeout(() => {
      isVisible.value = false
      setTimeout(() => emit('close'), 300)
    }, props.duration || 3000)
  }
})
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-2 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100"
    leave-to-class="transform translate-y-2 opacity-0"
  >
    <div
      v-if="isVisible"
      :class="[
        'flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-sm shadow-lg',
        typeStyles[type || 'info']
      ]"
    >
      <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons[type || 'info']"/>
      </svg>
      <p class="text-sm font-medium">{{ message }}</p>
      <button
        @click="isVisible = false; emit('close')"
        class="ml-auto p-1 rounded hover:bg-white/10 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
  </Transition>
</template>
