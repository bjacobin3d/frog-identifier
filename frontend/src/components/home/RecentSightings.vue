<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { Sighting, Species } from '@/types'

const props = defineProps<{
  sightings: Sighting[]
  species: Species[]
}>()

function getSpeciesName(speciesId: number): string {
  const found = props.species.find(s => s.id === speciesId)
  return found?.common_name ?? 'Unknown Species'
}

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

const hasSightings = computed(() => props.sightings.length > 0)
</script>

<template>
  <div v-if="hasSightings" class="grid gap-4">
    <RouterLink
      v-for="(sighting, index) in sightings"
      :key="sighting.id"
      :to="`/library/${sighting.id}`"
      class="card p-4 card-hover animate-slide-up"
      :style="{ animationDelay: `${index * 100}ms` }"
    >
      <div class="flex items-center gap-4">
        <!-- Detection Type Icon -->
        <div 
          class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
          :class="sighting.detection_type === 'audio' ? 'bg-frog-500/20' : 'bg-pond-500/20'"
        >
          <svg 
            v-if="sighting.detection_type === 'audio'"
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
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <h4 class="font-semibold text-white truncate">{{ getSpeciesName(sighting.species_id) }}</h4>
          <div class="flex items-center gap-3 text-sm text-frog-500">
            <span>{{ formatDate(sighting.sighted_at) }}</span>
            <span v-if="sighting.location_name" class="truncate">• {{ sighting.location_name }}</span>
          </div>
        </div>

        <!-- Confidence -->
        <div class="text-right shrink-0">
          <span class="text-lg font-semibold text-frog-300">{{ formatConfidence(sighting.confidence_score) }}</span>
          <p class="text-xs text-frog-600">confidence</p>
        </div>

        <!-- Arrow -->
        <svg class="w-5 h-5 text-frog-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </div>
    </RouterLink>
  </div>

  <!-- Empty State -->
  <div v-else class="card p-12 text-center">
    <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-frog-800/30 flex items-center justify-center">
      <svg class="w-8 h-8 text-frog-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
      </svg>
    </div>
    <h3 class="text-xl font-display font-semibold text-white mb-2">No Sightings Yet</h3>
    <p class="text-frog-500 mb-6">Start identifying frogs to build your library!</p>
    <RouterLink to="/identify/audio" class="btn btn-primary">
      Start Identifying
    </RouterLink>
  </div>
</template>
