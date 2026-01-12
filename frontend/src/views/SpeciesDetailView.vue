<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useSpeciesStore } from '@/stores/species'

const route = useRoute()
const speciesStore = useSpeciesStore()

const speciesId = computed(() => Number(route.params.id))

onMounted(async () => {
  await speciesStore.fetchById(speciesId.value)
})

const species = computed(() => speciesStore.currentSpecies)
</script>

<template>
  <div class="min-h-screen py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Back Link -->
      <RouterLink 
        to="/species"
        class="inline-flex items-center gap-2 text-frog-500 hover:text-frog-300 transition-colors mb-8"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Back to Species Guide
      </RouterLink>

      <!-- Loading State -->
      <div v-if="speciesStore.isLoading" class="flex items-center justify-center py-24">
        <div class="w-8 h-8 border-2 border-frog-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="speciesStore.error" class="card p-12 text-center">
        <p class="text-red-400">{{ speciesStore.error }}</p>
      </div>

      <!-- Content -->
      <div v-else-if="species" class="space-y-8">
        <!-- Hero Card -->
        <div class="card overflow-hidden">
          <!-- Image -->
          <div class="aspect-video relative overflow-hidden bg-frog-900/50">
            <img
              v-if="species.image_url"
              :src="species.image_url"
              :alt="species.common_name"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-24 h-24 text-frog-800" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2z"/>
              </svg>
            </div>
            <div class="absolute inset-0 bg-gradient-to-t from-frog-950 via-frog-950/50 to-transparent" />
            
            <!-- Title Overlay -->
            <div class="absolute bottom-0 left-0 right-0 p-8">
              <h1 class="text-4xl font-display font-bold text-white mb-2">
                {{ species.common_name }}
              </h1>
              <p class="text-xl text-frog-300 italic">{{ species.scientific_name }}</p>
            </div>
          </div>
        </div>

        <!-- Info Grid -->
        <div class="grid md:grid-cols-2 gap-6">
          <!-- Description -->
          <div class="card p-6" v-if="species.description">
            <h2 class="text-lg font-display font-semibold text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-frog-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              About
            </h2>
            <p class="text-frog-400 leading-relaxed">{{ species.description }}</p>
          </div>

          <!-- Habitat -->
          <div class="card p-6" v-if="species.habitat">
            <h2 class="text-lg font-display font-semibold text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-pond-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"/>
              </svg>
              Habitat
            </h2>
            <p class="text-frog-400 leading-relaxed">{{ species.habitat }}</p>
          </div>

          <!-- Range -->
          <div class="card p-6 md:col-span-2" v-if="species.range">
            <h2 class="text-lg font-display font-semibold text-white mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-lilypad-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              Range
            </h2>
            <p class="text-frog-400 leading-relaxed">{{ species.range }}</p>
          </div>
        </div>

        <!-- Audio Sample -->
        <div class="card p-6" v-if="species.audio_sample_url">
          <h2 class="text-lg font-display font-semibold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-frog-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
            </svg>
            Call Sample
          </h2>
          <audio
            :src="species.audio_sample_url"
            controls
            class="w-full"
          />
        </div>

        <!-- Actions -->
        <div class="flex flex-wrap gap-4">
          <RouterLink to="/identify/audio" class="btn btn-primary">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
            </svg>
            Identify by Call
          </RouterLink>
          <RouterLink to="/identify/photo" class="btn btn-secondary">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
            </svg>
            Identify by Photo
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
