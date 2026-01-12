<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useSightingsStore } from '@/stores/sightings'
import { useSpeciesStore } from '@/stores/species'
import ConfidenceMeter from '@/components/identify/ConfidenceMeter.vue'

const route = useRoute()
const router = useRouter()
const sightingsStore = useSightingsStore()
const speciesStore = useSpeciesStore()

const isEditing = ref(false)
const editNotes = ref('')
const editLocation = ref('')
const showDeleteConfirm = ref(false)

const sightingId = computed(() => Number(route.params.id))

onMounted(async () => {
  await Promise.all([
    sightingsStore.fetchById(sightingId.value),
    speciesStore.fetchAll()
  ])
  
  if (sightingsStore.currentSighting) {
    editNotes.value = sightingsStore.currentSighting.notes || ''
    editLocation.value = sightingsStore.currentSighting.location_name || ''
  }
})

const sighting = computed(() => sightingsStore.currentSighting)
const species = computed(() => 
  sighting.value ? speciesStore.getById(sighting.value.species_id) : undefined
)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`
}

async function saveChanges() {
  if (!sighting.value) return
  
  await sightingsStore.update(sighting.value.id, {
    notes: editNotes.value || undefined,
    location_name: editLocation.value || undefined,
  })
  
  isEditing.value = false
}

function cancelEdit() {
  if (sighting.value) {
    editNotes.value = sighting.value.notes || ''
    editLocation.value = sighting.value.location_name || ''
  }
  isEditing.value = false
}

async function deleteSighting() {
  if (!sighting.value) return
  
  await sightingsStore.remove(sighting.value.id)
  router.push('/library')
}
</script>

<template>
  <div class="min-h-screen py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Back Link -->
      <RouterLink 
        to="/library"
        class="inline-flex items-center gap-2 text-frog-500 hover:text-frog-300 transition-colors mb-8"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Back to Library
      </RouterLink>

      <!-- Loading State -->
      <div v-if="sightingsStore.isLoading" class="flex items-center justify-center py-24">
        <div class="w-8 h-8 border-2 border-frog-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="sightingsStore.error" class="card p-12 text-center">
        <p class="text-red-400">{{ sightingsStore.error }}</p>
      </div>

      <!-- Content -->
      <div v-else-if="sighting" class="space-y-8">
        <!-- Main Card -->
        <div class="card overflow-hidden">
          <!-- Image/Audio Visual -->
          <div class="aspect-video relative overflow-hidden bg-frog-900/50">
            <img
              v-if="sighting.image_path"
              :src="sighting.image_path"
              :alt="species?.common_name || 'Frog sighting'"
              class="w-full h-full object-contain"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <div class="text-center">
                <svg 
                  class="w-24 h-24 text-frog-700 mx-auto mb-4" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                </svg>
                <p class="text-frog-600">Audio Recording</p>
              </div>
            </div>
            
            <!-- Detection Type Badge -->
            <div class="absolute top-4 left-4">
              <span 
                class="badge"
                :class="sighting.detection_type === 'audio' ? 'badge-success' : 'badge-info'"
              >
                {{ sighting.detection_type === 'audio' ? 'Audio Identification' : 'Photo Identification' }}
              </span>
            </div>
          </div>

          <!-- Audio Player -->
          <div v-if="sighting.audio_path" class="p-6 border-b border-frog-800/30">
            <h3 class="text-sm font-medium text-frog-500 mb-3">Recording</h3>
            <audio :src="sighting.audio_path" controls class="w-full" />
          </div>

          <!-- Content -->
          <div class="p-6">
            <!-- Species Info -->
            <div class="flex items-start justify-between gap-4 mb-6">
              <div>
                <h1 class="text-3xl font-display font-bold text-white mb-2">
                  {{ species?.common_name || 'Unknown Species' }}
                </h1>
                <p v-if="species" class="text-lg text-frog-400 italic">{{ species.scientific_name }}</p>
              </div>
              <RouterLink
                v-if="species"
                :to="`/species/${species.id}`"
                class="btn btn-secondary btn-sm shrink-0"
              >
                View Species
              </RouterLink>
            </div>

            <!-- Confidence -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm text-frog-500">Confidence</span>
                <span class="text-lg font-semibold text-frog-300">
                  {{ formatConfidence(sighting.confidence_score) }}
                </span>
              </div>
              <ConfidenceMeter :confidence="sighting.confidence_score" size="md" />
            </div>

            <!-- Date & Location -->
            <div class="grid sm:grid-cols-2 gap-4 mb-6">
              <div class="p-4 rounded-xl bg-frog-900/30">
                <div class="flex items-center gap-2 text-frog-500 mb-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  <span class="text-sm">Date & Time</span>
                </div>
                <p class="text-white">{{ formatDate(sighting.sighted_at) }}</p>
              </div>
              
              <div class="p-4 rounded-xl bg-frog-900/30">
                <div class="flex items-center gap-2 text-frog-500 mb-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <span class="text-sm">Location</span>
                </div>
                <p v-if="!isEditing" class="text-white">{{ sighting.location_name || 'Not specified' }}</p>
                <input
                  v-else
                  v-model="editLocation"
                  type="text"
                  class="input mt-1"
                  placeholder="Enter location"
                />
              </div>
            </div>

            <!-- Notes -->
            <div class="mb-6">
              <div class="flex items-center gap-2 text-frog-500 mb-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
                <span class="text-sm">Notes</span>
              </div>
              <p v-if="!isEditing" class="text-frog-300">{{ sighting.notes || 'No notes added' }}</p>
              <textarea
                v-else
                v-model="editNotes"
                class="input min-h-[100px] resize-none"
                placeholder="Add notes about this sighting..."
              />
            </div>

            <!-- Actions -->
            <div class="flex flex-wrap gap-3 pt-4 border-t border-frog-800/30">
              <template v-if="!isEditing">
                <button @click="isEditing = true" class="btn btn-secondary">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                  Edit
                </button>
                <button @click="showDeleteConfirm = true" class="btn btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/10">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                  Delete
                </button>
              </template>
              <template v-else>
                <button @click="saveChanges" class="btn btn-primary">
                  Save Changes
                </button>
                <button @click="cancelEdit" class="btn btn-ghost">
                  Cancel
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-frog-950/80 backdrop-blur-sm" @click="showDeleteConfirm = false" />
        <div class="relative card p-6 w-full max-w-md animate-bounce-in">
          <h3 class="text-xl font-display font-semibold text-white mb-4">Delete Sighting?</h3>
          <p class="text-frog-400 mb-6">This action cannot be undone. The sighting and any associated files will be permanently removed.</p>
          <div class="flex gap-3">
            <button @click="showDeleteConfirm = false" class="btn btn-secondary flex-1">
              Cancel
            </button>
            <button @click="deleteSighting" class="btn bg-red-500 hover:bg-red-400 text-white flex-1">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
