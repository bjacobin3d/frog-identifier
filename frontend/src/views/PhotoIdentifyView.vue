<script setup lang="ts">
import { ref, computed } from 'vue'
import { useIdentificationStore } from '@/stores/identification'
import { useSightingsStore } from '@/stores/sightings'
import PredictionResults from '@/components/identify/PredictionResults.vue'
import SaveSightingModal from '@/components/identify/SaveSightingModal.vue'

const identificationStore = useIdentificationStore()
const sightingsStore = useSightingsStore()

const selectedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const isDragging = ref(false)
const showSaveModal = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const canUpload = computed(() => selectedFile.value && !identificationStore.isProcessing)

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectFile(input.files[0])
  }
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  isDragging.value = false
  
  const file = event.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    selectFile(file)
  }
}

function selectFile(file: File) {
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  identificationStore.reset()
}

async function identifyImage() {
  if (!selectedFile.value) return
  await identificationStore.identifyImage(selectedFile.value)
}

function resetIdentification() {
  identificationStore.reset()
  selectedFile.value = null
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
}

function openSaveModal() {
  showSaveModal.value = true
}

async function handleSave(data: { notes: string; locationName: string }) {
  if (!identificationStore.selectedPrediction || !selectedFile.value) return
  
  await sightingsStore.create({
    species_id: identificationStore.selectedPrediction.species_id,
    detection_type: 'image',
    confidence_score: identificationStore.selectedPrediction.confidence,
    notes: data.notes || undefined,
    location_name: data.locationName || undefined,
    image: selectedFile.value,
  })
  
  showSaveModal.value = false
  resetIdentification()
}

function triggerFileInput() {
  fileInput.value?.click()
}
</script>

<template>
  <div class="min-h-screen py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-pond-400 to-pond-600 shadow-xl shadow-pond-500/25 mb-6">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <h1 class="text-3xl sm:text-4xl font-display font-bold text-white mb-4">Photo Identify</h1>
        <p class="text-lg text-frog-400 max-w-xl mx-auto">
          Upload a photo of a frog and our AI will identify the species
        </p>
      </div>

      <!-- Upload Area -->
      <div class="card p-8 mb-8">
        <!-- Image Preview / Drop Zone -->
        <div
          class="relative border-2 border-dashed rounded-2xl transition-all overflow-hidden"
          :class="isDragging 
            ? 'border-pond-500 bg-pond-500/10' 
            : previewUrl 
              ? 'border-frog-700/50' 
              : 'border-frog-800/50 hover:border-frog-700/50'"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop="handleDrop"
        >
          <!-- Preview -->
          <div v-if="previewUrl" class="aspect-video relative">
            <img
              :src="previewUrl"
              alt="Selected image"
              class="w-full h-full object-contain bg-frog-950"
            />
            <button
              @click="resetIdentification"
              class="absolute top-4 right-4 p-2 rounded-lg bg-frog-950/80 text-frog-400 hover:text-white transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Drop Zone -->
          <div v-else class="aspect-video flex flex-col items-center justify-center p-8 cursor-pointer" @click="triggerFileInput">
            <div class="w-20 h-20 rounded-2xl bg-frog-800/30 flex items-center justify-center mb-6">
              <svg class="w-10 h-10 text-frog-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <p class="text-lg font-medium text-white mb-2">
              {{ isDragging ? 'Drop your image here' : 'Drag & drop an image' }}
            </p>
            <p class="text-frog-500 mb-4">or click to browse</p>
            <p class="text-sm text-frog-600">Supports JPEG, PNG, WebP</p>
          </div>
        </div>

        <!-- Hidden File Input -->
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="hidden"
          @change="handleFileSelect"
        />

        <!-- Identify Button -->
        <div class="mt-6 flex justify-center gap-4">
          <button
            v-if="!previewUrl"
            @click="triggerFileInput"
            class="btn btn-secondary"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            Upload Image
          </button>

          <button
            v-if="previewUrl && !identificationStore.result"
            @click="identifyImage"
            :disabled="!canUpload"
            class="btn btn-primary btn-lg"
          >
            <svg v-if="identificationStore.isProcessing" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            {{ identificationStore.isProcessing ? 'Analyzing...' : 'Identify Frog' }}
          </button>

          <button
            v-if="identificationStore.result"
            @click="resetIdentification"
            class="btn btn-secondary"
          >
            Try Another Photo
          </button>
        </div>
      </div>

      <!-- Results -->
      <PredictionResults
        v-if="identificationStore.result"
        :result="identificationStore.result"
        :selected-prediction="identificationStore.selectedPrediction"
        @select="identificationStore.selectPrediction"
        @save="openSaveModal"
      />

      <!-- Error -->
      <div v-if="identificationStore.error" class="card p-6 border-red-500/30 bg-red-500/10">
        <p class="text-red-400 text-center">{{ identificationStore.error }}</p>
      </div>

      <!-- Tips -->
      <div class="mt-12 card p-6">
        <h3 class="font-display font-semibold text-white mb-4">Photo Tips</h3>
        <ul class="space-y-2 text-frog-400">
          <li class="flex items-start gap-2">
            <svg class="w-5 h-5 text-frog-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Get as close as safely possible to the frog
          </li>
          <li class="flex items-start gap-2">
            <svg class="w-5 h-5 text-frog-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Ensure the frog is in focus and well-lit
          </li>
          <li class="flex items-start gap-2">
            <svg class="w-5 h-5 text-frog-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Side or top-down angles work best
          </li>
          <li class="flex items-start gap-2">
            <svg class="w-5 h-5 text-frog-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Include distinguishing features like patterns or coloration
          </li>
        </ul>
      </div>
    </div>

    <!-- Save Modal -->
    <SaveSightingModal
      v-if="showSaveModal"
      :prediction="identificationStore.selectedPrediction!"
      detection-type="image"
      @save="handleSave"
      @close="showSaveModal = false"
    />
  </div>
</template>
