<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useSightingsStore } from '@/stores/sightings'
import { useSpeciesStore } from '@/stores/species'
import type { SightingFilters } from '@/types'
import SightingCard from '@/components/library/SightingCard.vue'
import FilterPanel from '@/components/library/FilterPanel.vue'

const sightingsStore = useSightingsStore()
const speciesStore = useSpeciesStore()

const showFilters = ref(false)
const filters = ref<SightingFilters>({})

onMounted(async () => {
  await Promise.all([
    sightingsStore.fetchAll(),
    sightingsStore.fetchStats(),
    speciesStore.fetchAll()
  ])
})

async function applyFilters(newFilters: SightingFilters) {
  filters.value = newFilters
  await sightingsStore.fetchAll(newFilters)
  showFilters.value = false
}

function clearFilters() {
  filters.value = {}
  sightingsStore.fetchAll()
}

const hasActiveFilters = computed(() => {
  return filters.value.species_id || filters.value.detection_type || filters.value.start_date || filters.value.end_date
})
</script>

<template>
  <div class="min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 class="text-3xl sm:text-4xl font-display font-bold text-white mb-2">My Library</h1>
          <p class="text-frog-400">
            {{ sightingsStore.total }} sighting{{ sightingsStore.total !== 1 ? 's' : '' }} recorded
          </p>
        </div>
        
        <div class="flex gap-3">
          <button
            @click="showFilters = !showFilters"
            class="btn btn-secondary"
            :class="{ 'ring-2 ring-frog-500': hasActiveFilters }"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
            </svg>
            Filters
            <span v-if="hasActiveFilters" class="w-2 h-2 rounded-full bg-frog-500"></span>
          </button>
          
          <RouterLink to="/identify/audio" class="btn btn-primary">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Add Sighting
          </RouterLink>
        </div>
      </div>

      <!-- Filter Panel -->
      <FilterPanel
        v-if="showFilters"
        :filters="filters"
        :species="speciesStore.species"
        @apply="applyFilters"
        @clear="clearFilters"
        @close="showFilters = false"
        class="mb-8"
      />

      <!-- Stats Cards -->
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8" v-if="sightingsStore.stats">
        <div class="card p-4">
          <p class="text-2xl font-display font-bold text-white">{{ sightingsStore.stats.total_sightings }}</p>
          <p class="text-sm text-frog-500">Total Sightings</p>
        </div>
        <div class="card p-4">
          <p class="text-2xl font-display font-bold text-white">{{ sightingsStore.stats.unique_species }}</p>
          <p class="text-sm text-frog-500">Unique Species</p>
        </div>
        <div class="card p-4">
          <p class="text-2xl font-display font-bold text-white">{{ sightingsStore.stats.audio_identifications }}</p>
          <p class="text-sm text-frog-500">Audio IDs</p>
        </div>
        <div class="card p-4">
          <p class="text-2xl font-display font-bold text-white">{{ sightingsStore.stats.image_identifications }}</p>
          <p class="text-sm text-frog-500">Photo IDs</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="sightingsStore.isLoading" class="flex items-center justify-center py-24">
        <div class="w-8 h-8 border-2 border-frog-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Sightings Grid -->
      <div v-else-if="sightingsStore.sightings.length > 0" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <SightingCard
          v-for="sighting in sightingsStore.sightings"
          :key="sighting.id"
          :sighting="sighting"
          :species="speciesStore.getById(sighting.species_id)"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="card p-12 text-center">
        <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-frog-800/30 flex items-center justify-center">
          <svg class="w-10 h-10 text-frog-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
          </svg>
        </div>
        <h2 class="text-2xl font-display font-semibold text-white mb-2">
          {{ hasActiveFilters ? 'No matching sightings' : 'No sightings yet' }}
        </h2>
        <p class="text-frog-500 mb-8 max-w-md mx-auto">
          {{ hasActiveFilters 
            ? 'Try adjusting your filters to see more results.' 
            : 'Start identifying frogs to build your personal library of discoveries.' 
          }}
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button v-if="hasActiveFilters" @click="clearFilters" class="btn btn-secondary">
            Clear Filters
          </button>
          <RouterLink to="/identify/audio" class="btn btn-primary">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
            </svg>
            Start Identifying
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
