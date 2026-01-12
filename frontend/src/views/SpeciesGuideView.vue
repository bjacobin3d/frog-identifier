<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useSpeciesStore } from '@/stores/species'
import SpeciesCard from '@/components/species/SpeciesCard.vue'
import SearchInput from '@/components/common/SearchInput.vue'

const speciesStore = useSpeciesStore()

onMounted(() => {
  speciesStore.fetchAll()
})

const alphabetGroups = computed(() => {
  const groups: Record<string, typeof speciesStore.filteredSpecies> = {}
  
  speciesStore.filteredSpecies.forEach(species => {
    const letter = species.common_name[0].toUpperCase()
    if (!groups[letter]) groups[letter] = []
    groups[letter].push(species)
  })
  
  return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b))
})
</script>

<template>
  <div class="min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-lilypad-400 to-lilypad-600 shadow-xl shadow-lilypad-500/25 mb-6">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
        </div>
        <h1 class="text-3xl sm:text-4xl font-display font-bold text-white mb-4">Species Guide</h1>
        <p class="text-lg text-frog-400 max-w-xl mx-auto">
          Explore {{ speciesStore.species.length }} frog species in our database
        </p>
      </div>

      <!-- Search -->
      <div class="max-w-xl mx-auto mb-12">
        <SearchInput
          :model-value="speciesStore.searchQuery"
          @update:model-value="speciesStore.setSearchQuery"
          placeholder="Search by common or scientific name..."
        />
      </div>

      <!-- Loading State -->
      <div v-if="speciesStore.isLoading" class="flex items-center justify-center py-12">
        <div class="w-8 h-8 border-2 border-frog-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Species Grid -->
      <div v-else-if="alphabetGroups.length > 0">
        <div v-for="[letter, species] in alphabetGroups" :key="letter" class="mb-12">
          <h2 class="text-2xl font-display font-bold text-frog-300 mb-6 sticky top-20 bg-frog-950/80 backdrop-blur-sm py-2 -mx-4 px-4 z-10">
            {{ letter }}
          </h2>
          <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <SpeciesCard
              v-for="s in species"
              :key="s.id"
              :species="s"
            />
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-else class="card p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-frog-800/30 flex items-center justify-center">
          <svg class="w-8 h-8 text-frog-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <h3 class="text-xl font-display font-semibold text-white mb-2">No species found</h3>
        <p class="text-frog-500">Try adjusting your search terms</p>
      </div>
    </div>
  </div>
</template>
