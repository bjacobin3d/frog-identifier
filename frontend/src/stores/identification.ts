import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { IdentificationResult, PredictionItem } from '@/types'
import { identifyApi } from '@/services/api'

export const useIdentificationStore = defineStore('identification', () => {
  const result = ref<IdentificationResult | null>(null)
  const isProcessing = ref(false)
  const error = ref<string | null>(null)
  const selectedPrediction = ref<PredictionItem | null>(null)

  async function identifyAudio(audioBlob: Blob) {
    isProcessing.value = true
    error.value = null
    result.value = null
    try {
      result.value = await identifyApi.audio(audioBlob)
      if (result.value.top_prediction) {
        selectedPrediction.value = result.value.top_prediction
      }
    } catch (e) {
      error.value = 'Failed to identify audio'
      console.error(e)
    } finally {
      isProcessing.value = false
    }
  }

  async function identifyAudioStream(audioData: string) {
    isProcessing.value = true
    error.value = null
    try {
      result.value = await identifyApi.audioStream(audioData)
      if (result.value.top_prediction) {
        selectedPrediction.value = result.value.top_prediction
      }
    } catch (e) {
      error.value = 'Failed to identify audio stream'
      console.error(e)
    } finally {
      isProcessing.value = false
    }
  }

  async function identifyImage(imageFile: File) {
    isProcessing.value = true
    error.value = null
    result.value = null
    try {
      result.value = await identifyApi.image(imageFile)
      if (result.value.top_prediction) {
        selectedPrediction.value = result.value.top_prediction
      }
    } catch (e) {
      error.value = 'Failed to identify image'
      console.error(e)
    } finally {
      isProcessing.value = false
    }
  }

  function selectPrediction(prediction: PredictionItem) {
    selectedPrediction.value = prediction
  }

  function reset() {
    result.value = null
    error.value = null
    selectedPrediction.value = null
  }

  return {
    result,
    isProcessing,
    error,
    selectedPrediction,
    identifyAudio,
    identifyAudioStream,
    identifyImage,
    selectPrediction,
    reset,
  }
})
