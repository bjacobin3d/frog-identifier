<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Species } from '@/types'

defineProps<{
  species: Species
}>()
</script>

<template>
  <RouterLink
    :to="`/species/${species.id}`"
    class="card card-hover overflow-hidden group"
  >
    <!-- Image -->
    <div class="aspect-[4/3] relative overflow-hidden bg-frog-900/50">
      <img
        v-if="species.image_url"
        :src="species.image_url"
        :alt="species.common_name"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <svg class="w-16 h-16 text-frog-800" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2z"/>
        </svg>
      </div>
      
      <!-- Gradient overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-frog-950 via-transparent to-transparent" />
    </div>

    <!-- Content -->
    <div class="p-5">
      <h3 class="text-lg font-display font-semibold text-white mb-1 group-hover:text-frog-300 transition-colors">
        {{ species.common_name }}
      </h3>
      <p class="text-sm text-frog-500 italic mb-3">{{ species.scientific_name }}</p>
      
      <p v-if="species.description" class="text-sm text-frog-400 line-clamp-2">
        {{ species.description }}
      </p>

      <!-- View Details -->
      <div class="flex items-center gap-1 mt-4 text-frog-500 group-hover:text-frog-300 transition-colors">
        <span class="text-sm font-medium">View Details</span>
        <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </div>
    </div>
  </RouterLink>
</template>
