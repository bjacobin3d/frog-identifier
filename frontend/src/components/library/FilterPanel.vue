<script setup lang="ts">
import { ref, watch } from 'vue'
import type { SightingFilters, Species } from '@/types'

const props = defineProps<{
  filters: SightingFilters
  species: Species[]
}>()

const emit = defineEmits<{
  apply: [filters: SightingFilters]
  clear: []
  close: []
}>()

const localFilters = ref<SightingFilters>({ ...props.filters })

watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

function apply() {
  emit('apply', { ...localFilters.value })
}

function clear() {
  localFilters.value = {}
  emit('clear')
}
</script>

<template>
  <div class="card p-6 animate-slide-up">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-display font-semibold text-white">Filter Sightings</h3>
      <button @click="emit('close')" class="text-frog-500 hover:text-frog-300 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <!-- Species Filter -->
      <div>
        <label class="label">Species</label>
        <select v-model="localFilters.species_id" class="input">
          <option :value="undefined">All Species</option>
          <option v-for="s in species" :key="s.id" :value="s.id">
            {{ s.common_name }}
          </option>
        </select>
      </div>

      <!-- Detection Type Filter -->
      <div>
        <label class="label">Detection Type</label>
        <select v-model="localFilters.detection_type" class="input">
          <option :value="undefined">All Types</option>
          <option value="audio">Audio</option>
          <option value="image">Photo</option>
        </select>
      </div>

      <!-- Start Date Filter -->
      <div>
        <label class="label">From Date</label>
        <input
          v-model="localFilters.start_date"
          type="date"
          class="input"
        />
      </div>

      <!-- End Date Filter -->
      <div>
        <label class="label">To Date</label>
        <input
          v-model="localFilters.end_date"
          type="date"
          class="input"
        />
      </div>
    </div>

    <div class="flex gap-3">
      <button @click="clear" class="btn btn-ghost">
        Clear All
      </button>
      <button @click="apply" class="btn btn-primary">
        Apply Filters
      </button>
    </div>
  </div>
</template>
