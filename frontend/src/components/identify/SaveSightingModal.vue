<script setup lang="ts">
import { ref } from 'vue'
import type { PredictionItem } from '@/types'

const props = defineProps<{
  prediction: PredictionItem
  detectionType: 'audio' | 'image'
}>()

const emit = defineEmits<{
  save: [data: { notes: string; locationName: string }]
  close: []
}>()

const notes = ref('')
const locationName = ref('')
const isGettingLocation = ref(false)

async function getLocation() {
  if (!navigator.geolocation) {
    alert('Geolocation is not supported by your browser')
    return
  }
  
  isGettingLocation.value = true
  try {
    const position = await new Promise<GeolocationPosition>((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject)
    })
    
    // For now, just show coordinates. In production, you'd use a reverse geocoding service.
    locationName.value = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`
  } catch (error) {
    console.error('Error getting location:', error)
    alert('Could not get your location')
  } finally {
    isGettingLocation.value = false
  }
}

function handleSave() {
  emit('save', {
    notes: notes.value,
    locationName: locationName.value,
  })
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div 
      class="absolute inset-0 bg-frog-950/80 backdrop-blur-sm"
      @click="emit('close')"
    />
    
    <!-- Modal -->
    <div class="relative card p-6 w-full max-w-md animate-bounce-in">
      <!-- Close Button -->
      <button
        @click="emit('close')"
        class="absolute top-4 right-4 p-2 text-frog-500 hover:text-frog-300 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>

      <!-- Header -->
      <div class="mb-6">
        <h2 class="text-xl font-display font-semibold text-white mb-2">Save to Library</h2>
        <p class="text-frog-400">Add this sighting to your personal collection</p>
      </div>

      <!-- Species Info -->
      <div class="flex items-center gap-4 p-4 rounded-xl bg-frog-900/30 border border-frog-800/30 mb-6">
        <div 
          class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
          :class="detectionType === 'audio' ? 'bg-frog-500/20' : 'bg-pond-500/20'"
        >
          <svg 
            v-if="detectionType === 'audio'"
            class="w-6 h-6 text-frog-400" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
          </svg>
          <svg 
            v-else
            class="w-6 h-6 text-pond-400" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
          </svg>
        </div>
        <div class="min-w-0">
          <h3 class="font-semibold text-white truncate">{{ prediction.common_name }}</h3>
          <p class="text-sm text-frog-500">{{ Math.round(prediction.confidence * 100) }}% confidence</p>
        </div>
      </div>

      <!-- Form -->
      <div class="space-y-4">
        <!-- Location -->
        <div>
          <label class="label">Location</label>
          <div class="flex gap-2">
            <input
              v-model="locationName"
              type="text"
              class="input flex-1"
              placeholder="e.g., Backyard pond"
            />
            <button
              @click="getLocation"
              :disabled="isGettingLocation"
              class="btn btn-secondary px-3"
              title="Get current location"
            >
              <svg 
                class="w-5 h-5" 
                :class="{ 'animate-spin': isGettingLocation }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Notes -->
        <div>
          <label class="label">Notes (optional)</label>
          <textarea
            v-model="notes"
            class="input min-h-[100px] resize-none"
            placeholder="Add any observations about this sighting..."
          />
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 mt-6">
        <button @click="emit('close')" class="btn btn-secondary flex-1">
          Cancel
        </button>
        <button @click="handleSave" class="btn btn-primary flex-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          Save
        </button>
      </div>
    </div>
  </div>
</template>
