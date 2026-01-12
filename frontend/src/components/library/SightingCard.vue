<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Sighting, Species } from '@/types'

defineProps<{
  sighting: Sighting
  species?: Species
}>()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`
}
</script>

<template>
  <RouterLink
    :to="`/library/${sighting.id}`"
    class="card card-hover overflow-hidden group"
  >
    <!-- Image / Placeholder -->
    <div class="aspect-video relative overflow-hidden bg-frog-900/50">
      <img
        v-if="sighting.image_path"
        :src="sighting.image_path"
        :alt="species?.common_name || 'Frog sighting'"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <svg 
          v-if="sighting.detection_type === 'audio'"
          class="w-16 h-16 text-frog-700" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
        </svg>
        <svg v-else class="w-16 h-16 text-frog-700" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2z"/>
        </svg>
      </div>
      
      <!-- Detection Type Badge -->
      <div class="absolute top-3 left-3">
        <span 
          class="badge"
          :class="sighting.detection_type === 'audio' ? 'badge-success' : 'badge-info'"
        >
          <svg 
            v-if="sighting.detection_type === 'audio'"
            class="w-3 h-3" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
          </svg>
          <svg 
            v-else
            class="w-3 h-3" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
          </svg>
          {{ sighting.detection_type === 'audio' ? 'Audio' : 'Photo' }}
        </span>
      </div>

      <!-- Confidence Badge -->
      <div class="absolute top-3 right-3">
        <span class="badge bg-frog-950/80 text-frog-300 border-frog-700/50">
          {{ formatConfidence(sighting.confidence_score) }}
        </span>
      </div>

      <div class="absolute inset-0 bg-gradient-to-t from-frog-950 via-transparent to-transparent" />
    </div>

    <!-- Content -->
    <div class="p-5">
      <h3 class="text-lg font-display font-semibold text-white mb-1 group-hover:text-frog-300 transition-colors">
        {{ species?.common_name || 'Unknown Species' }}
      </h3>
      
      <div class="flex items-center gap-3 text-sm text-frog-500 mb-3">
        <span>{{ formatDate(sighting.sighted_at) }}</span>
        <span v-if="sighting.location_name" class="truncate">• {{ sighting.location_name }}</span>
      </div>

      <p v-if="sighting.notes" class="text-sm text-frog-400 line-clamp-2">
        {{ sighting.notes }}
      </p>
    </div>
  </RouterLink>
</template>
