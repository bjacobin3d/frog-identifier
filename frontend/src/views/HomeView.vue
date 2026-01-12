<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSightingsStore } from '@/stores/sightings'
import { useSpeciesStore } from '@/stores/species'
import StatsCard from '@/components/home/StatsCard.vue'
import RecentSightings from '@/components/home/RecentSightings.vue'

const sightingsStore = useSightingsStore()
const speciesStore = useSpeciesStore()

onMounted(async () => {
  await Promise.all([
    sightingsStore.fetchStats(),
    sightingsStore.fetchAll({}, 0, 5),
    speciesStore.fetchAll()
  ])
})
</script>

<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="relative py-20 lg:py-32 overflow-hidden">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <!-- Animated Frog Icon -->
          <div class="mb-8 animate-float">
            <div class="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-to-br from-sage-500 to-sage-700 shadow-2xl shadow-sage-900/40">
              <svg class="w-14 h-14 text-cream-50" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2zm-3 8a1.5 1.5 0 110 3 1.5 1.5 0 010-3zm6 0a1.5 1.5 0 110 3 1.5 1.5 0 010-3z"/>
              </svg>
            </div>
          </div>

          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-display font-bold mb-6 tracking-tight">
            <span class="text-cream-50">Discover the </span>
            <span class="text-sage-400">Frogs</span>
            <span class="text-cream-50"> Around You</span>
          </h1>

          <p class="text-lg sm:text-xl text-cream-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Identify frog species by their unique calls or photos. Build your personal library
            of amphibian encounters and become a citizen scientist.
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <RouterLink to="/identify/audio" class="btn btn-primary btn-lg group">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
              </svg>
              <span>Start Listening</span>
              <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </RouterLink>

            <RouterLink to="/identify/photo" class="btn btn-secondary btn-lg group">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              <span>Upload Photo</span>
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Decorative elements -->
      <div class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-700/50 to-transparent"></div>
    </section>

    <!-- Features Section -->
    <section class="py-16 lg:py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-3 gap-8">
          <!-- Feature 1: Audio ID -->
          <div class="card p-8 card-hover group">
            <div class="w-14 h-14 rounded-2xl bg-sage-900/50 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-sage-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
              </svg>
            </div>
            <h3 class="text-xl font-display font-semibold text-cream-100 mb-3">Real-time Audio ID</h3>
            <p class="text-cream-500 leading-relaxed">
              Record frog calls with your device's microphone and get instant species identification powered by AI.
            </p>
          </div>

          <!-- Feature 2: Photo ID -->
          <div class="card p-8 card-hover group">
            <div class="w-14 h-14 rounded-2xl bg-amber-900/30 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <h3 class="text-xl font-display font-semibold text-cream-100 mb-3">Photo Recognition</h3>
            <p class="text-cream-500 leading-relaxed">
              Snap or upload a photo of a frog and our image classifier will identify the species.
            </p>
          </div>

          <!-- Feature 3: Library -->
          <div class="card p-8 card-hover group">
            <div class="w-14 h-14 rounded-2xl bg-slate-800/80 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg class="w-7 h-7 text-cream-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
            </div>
            <h3 class="text-xl font-display font-semibold text-cream-100 mb-3">Personal Library</h3>
            <p class="text-cream-500 leading-relaxed">
              Keep track of all your frog encounters with notes, locations, and photos in your personal library.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-16 lg:py-24 border-t border-slate-800/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-display font-bold text-cream-50 mb-4">Your Frog Journey</h2>
          <p class="text-cream-500">Track your discoveries and build your collection</p>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Sightings"
            :value="sightingsStore.stats?.total_sightings ?? 0"
            icon="eye"
            color="sage"
          />
          <StatsCard
            title="Species Found"
            :value="sightingsStore.stats?.unique_species ?? 0"
            icon="collection"
            color="amber"
          />
          <StatsCard
            title="Audio IDs"
            :value="sightingsStore.stats?.audio_identifications ?? 0"
            icon="mic"
            color="sage"
          />
          <StatsCard
            title="Photo IDs"
            :value="sightingsStore.stats?.image_identifications ?? 0"
            icon="camera"
            color="amber"
          />
        </div>
      </div>
    </section>

    <!-- Recent Sightings -->
    <section class="py-16 lg:py-24 border-t border-slate-800/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-8">
          <div>
            <h2 class="text-3xl font-display font-bold text-cream-50 mb-2">Recent Sightings</h2>
            <p class="text-cream-500">Your latest frog discoveries</p>
          </div>
          <RouterLink to="/library" class="btn btn-secondary btn-sm">
            View All
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </RouterLink>
        </div>

        <RecentSightings :sightings="sightingsStore.recentSightings" :species="speciesStore.species" />
      </div>
    </section>

    <!-- Species Preview -->
    <section class="py-16 lg:py-24 border-t border-slate-800/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-display font-bold text-cream-50 mb-4">Species Guide</h2>
          <p class="text-cream-500 max-w-2xl mx-auto">
            Explore {{ speciesStore.species.length }} frog species in our database. Learn about their calls, habitats, and ranges.
          </p>
        </div>

        <div class="text-center">
          <RouterLink to="/species" class="btn btn-primary">
            Explore All Species
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
