<script setup lang="ts">
import type { IdentificationResult, PredictionItem } from '@/types'
import ConfidenceMeter from './ConfidenceMeter.vue'

defineProps<{
  result: IdentificationResult
  selectedPrediction: PredictionItem | null
}>()

const emit = defineEmits<{
  select: [prediction: PredictionItem]
  save: []
}>()

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`
}
</script>

<template>
  <div class="card p-6 animate-fade-in">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-display font-semibold text-cream-100">Identification Results</h2>
      <span class="badge badge-success">
        {{ result.predictions.length }} matches found
      </span>
    </div>

    <!-- Top Prediction Highlight -->
    <div v-if="result.top_prediction" class="mb-6">
      <div 
        class="p-6 rounded-xl border-2 transition-all cursor-pointer"
        :class="selectedPrediction?.species_id === result.top_prediction.species_id 
          ? 'border-sage-500 bg-sage-900/30' 
          : 'border-slate-700/50 bg-slate-800/30 hover:border-slate-600/50'"
        @click="emit('select', result.top_prediction!)"
      >
        <div class="flex items-center gap-4 mb-4">
          <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-sage-500 to-sage-700 flex items-center justify-center shadow-lg">
            <span class="text-2xl font-bold text-cream-50">#1</span>
          </div>
          <div class="flex-1">
            <h3 class="text-2xl font-display font-bold text-cream-100">
              {{ result.top_prediction.common_name }}
            </h3>
            <p class="text-cream-400 italic">{{ result.top_prediction.scientific_name }}</p>
          </div>
          <div class="text-right">
            <p class="text-3xl font-bold text-sage-400">
              {{ formatConfidence(result.top_prediction.confidence) }}
            </p>
            <p class="text-sm text-cream-500">confidence</p>
          </div>
        </div>
        <ConfidenceMeter :confidence="result.top_prediction.confidence" size="lg" />
      </div>
    </div>

    <!-- Other Predictions -->
    <div v-if="result.predictions.length > 1" class="space-y-3">
      <h4 class="text-sm font-medium text-cream-500 uppercase tracking-wider mb-3">Other Possibilities</h4>
      
      <div
        v-for="(prediction, index) in result.predictions.slice(1)"
        :key="prediction.species_id"
        class="p-4 rounded-xl border transition-all cursor-pointer"
        :class="selectedPrediction?.species_id === prediction.species_id 
          ? 'border-sage-500 bg-sage-900/30' 
          : 'border-slate-800/50 bg-slate-900/40 hover:border-slate-700/50'"
        @click="emit('select', prediction)"
      >
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 rounded-lg bg-slate-800/70 flex items-center justify-center">
            <span class="text-sm font-bold text-cream-400">#{{ index + 2 }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="font-semibold text-cream-100 truncate">{{ prediction.common_name }}</h4>
            <p class="text-sm text-cream-500 italic truncate">{{ prediction.scientific_name }}</p>
          </div>
          <div class="text-right shrink-0">
            <p class="text-lg font-semibold text-cream-400">{{ formatConfidence(prediction.confidence) }}</p>
          </div>
        </div>
        <ConfidenceMeter :confidence="prediction.confidence" size="sm" class="mt-3" />
      </div>
    </div>

    <!-- Save Button -->
    <div class="mt-8 pt-6 border-t border-slate-800/50">
      <button
        @click="emit('save')"
        :disabled="!selectedPrediction"
        class="btn btn-primary w-full"
        :class="{ 'opacity-50 cursor-not-allowed': !selectedPrediction }"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        Save to Library
      </button>
      <p v-if="!selectedPrediction" class="text-center text-sm text-cream-500 mt-2">
        Select a prediction to save
      </p>
    </div>
  </div>
</template>
