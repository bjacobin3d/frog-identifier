<script setup lang="ts">
import { ref, onUnmounted, computed, watch } from 'vue'
import { useIdentificationStore } from '@/stores/identification'
import { useSightingsStore } from '@/stores/sightings'
import type { RealtimePrediction } from '@/types'
import AudioVisualizer from '@/components/audio/AudioVisualizer.vue'
import PredictionResults from '@/components/identify/PredictionResults.vue'
import SaveSightingModal from '@/components/identify/SaveSightingModal.vue'

const identificationStore = useIdentificationStore()
const sightingsStore = useSightingsStore()

const mode = ref<'record' | 'realtime'>('realtime')

// Recording mode state
const isRecording = ref(false)
const recordingDuration = ref(0)
const audioLevel = ref(0)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])
const recordingInterval = ref<number | null>(null)
const analyser = ref<AnalyserNode | null>(null)
const animationFrame = ref<number | null>(null)
const showSaveModal = ref(false)
const recordedBlob = ref<Blob | null>(null)

// Real-time mode state
const isListening = ref(false)
const websocket = ref<WebSocket | null>(null)
const realtimePredictions = ref<RealtimePrediction[]>([])
const aggregatedPredictions = ref<RealtimePrediction[]>([])
const audioContext = ref<AudioContext | null>(null)
const realtimeStream = ref<MediaStream | null>(null)
const sessionDuration = ref(0)
const sessionTimer = ref<number | null>(null)

const topPrediction = computed(() => {
  return aggregatedPredictions.value[0] ?? null
})

watch(mode, () => {
  stopRecording()
  stopRealtime()
})

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    // Set up audio context for visualization
    audioContext.value = new AudioContext()
    const source = audioContext.value.createMediaStreamSource(stream)
    analyser.value = audioContext.value.createAnalyser()
    analyser.value.fftSize = 256
    source.connect(analyser.value)
    
    // Start visualizing
    updateAudioLevel()
    
    // Set up media recorder
    mediaRecorder.value = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }
    
    mediaRecorder.value.onstop = async () => {
      const blob = new Blob(audioChunks.value, { type: 'audio/webm' })
      recordedBlob.value = blob
      await identificationStore.identifyAudio(blob)
    }
    
    mediaRecorder.value.start(1000) // Collect data every second
    isRecording.value = true
    recordingDuration.value = 0
    
    // Start duration timer
    recordingInterval.value = window.setInterval(() => {
      recordingDuration.value++
    }, 1000)
    
  } catch {
    alert('Could not access microphone. Please check permissions.')
  }
}

function stopRecording() {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
    isRecording.value = false
    
    if (recordingInterval.value) {
      clearInterval(recordingInterval.value)
      recordingInterval.value = null
    }
    
    if (animationFrame.value) {
      cancelAnimationFrame(animationFrame.value)
      animationFrame.value = null
    }
  }
}

function updateAudioLevel() {
  if (!analyser.value) return
  
  const dataArray = new Uint8Array(analyser.value.frequencyBinCount)
  analyser.value.getByteFrequencyData(dataArray)
  
  // Calculate average level
  const average = dataArray.reduce((a, b) => a + b) / dataArray.length
  audioLevel.value = average / 255
  
  if (isRecording.value || isListening.value) {
    animationFrame.value = requestAnimationFrame(updateAudioLevel)
  }
}

async function startRealtime() {
  try {
    // Get microphone access
    realtimeStream.value = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    // Set up audio context for visualization
    audioContext.value = new AudioContext()
    const source = audioContext.value.createMediaStreamSource(realtimeStream.value)
    analyser.value = audioContext.value.createAnalyser()
    analyser.value.fftSize = 256
    source.connect(analyser.value)
    
    // Start visualizing
    updateAudioLevel()
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.hostname
    const wsPort = import.meta.env.DEV ? '8000' : window.location.port
    const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/api/v1/realtime/ws/identify/audio`
    
    websocket.value = new WebSocket(wsUrl)
    
    websocket.value.onopen = () => {
      isListening.value = true
      realtimePredictions.value = []
      aggregatedPredictions.value = []
      sessionDuration.value = 0
      
      sessionTimer.value = window.setInterval(() => {
        sessionDuration.value++
      }, 1000)
      
      startChunkRecording()
    }
    
    websocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'detection') {
          realtimePredictions.value = data.predictions || []
          aggregatedPredictions.value = data.aggregated || []
        } else if (data.type === 'session_end') {
          aggregatedPredictions.value = data.aggregated || []
        }
      } catch {
        // Ignore malformed messages
      }
    }
    
    websocket.value.onerror = () => {
      stopRealtime()
    }
    
    websocket.value.onclose = () => {
      stopRealtime()
    }
    
  } catch {
    alert('Could not start real-time identification. Please check microphone permissions.')
  }
}

function startChunkRecording() {
  if (!realtimeStream.value) return
  
  // Create a new recorder for each chunk
  const startNewChunk = () => {
    if (!realtimeStream.value || !isListening.value) return
    
    const recorder = new MediaRecorder(realtimeStream.value, { mimeType: 'audio/webm' })
    const chunks: Blob[] = []
    
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data)
      }
    }
    
    recorder.onstop = () => {
      if (chunks.length > 0 && websocket.value?.readyState === WebSocket.OPEN) {
        const blob = new Blob(chunks, { type: 'audio/webm' })
        
        // Convert to base64 and send
        const reader = new FileReader()
        reader.onload = () => {
          const base64 = (reader.result as string).split(',')[1]
          websocket.value?.send(JSON.stringify({
            type: 'audio_chunk',
            data: base64,
          }))
        }
        reader.readAsDataURL(blob)
      }
      
      // Start next chunk if still listening
      if (isListening.value) {
        startNewChunk()
      }
    }
    
    recorder.start()
    
    // Stop after 3 seconds (BirdNET's window size)
    setTimeout(() => {
      if (recorder.state === 'recording') {
        recorder.stop()
      }
    }, 3000)
  }
  
  startNewChunk()
}

function stopRealtime() {
  isListening.value = false
  
  // Stop session timer
  if (sessionTimer.value) {
    clearInterval(sessionTimer.value)
    sessionTimer.value = null
  }
  
  // Stop animation
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
    animationFrame.value = null
  }
  
  // Close WebSocket
  if (websocket.value) {
    websocket.value.send(JSON.stringify({ type: 'stop' }))
    websocket.value.close()
    websocket.value = null
  }
  
  // Stop stream
  if (realtimeStream.value) {
    realtimeStream.value.getTracks().forEach(track => track.stop())
    realtimeStream.value = null
  }
  
  // Close audio context
  if (audioContext.value) {
    audioContext.value.close()
    audioContext.value = null
  }
}

function resetRealtime() {
  stopRealtime()
  realtimePredictions.value = []
  aggregatedPredictions.value = []
  sessionDuration.value = 0
  audioLevel.value = 0
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function formatConfidence(confidence: number): string {
  return `${(confidence * 100).toFixed(1)}%`
}

function resetIdentification() {
  identificationStore.reset()
  recordingDuration.value = 0
  audioLevel.value = 0
  recordedBlob.value = null
}

function openSaveModal() {
  showSaveModal.value = true
}

async function handleSave(data: { notes: string; locationName: string }) {
  if (!identificationStore.selectedPrediction || !recordedBlob.value) return
  
  // Convert blob to file
  const audioFile = new File([recordedBlob.value], 'recording.webm', { type: 'audio/webm' })
  
  await sightingsStore.create({
    species_id: identificationStore.selectedPrediction.species_id,
    detection_type: 'audio',
    confidence_score: identificationStore.selectedPrediction.confidence,
    notes: data.notes || undefined,
    location_name: data.locationName || undefined,
    audio: audioFile,
  })
  
  showSaveModal.value = false
  resetIdentification()
}

onUnmounted(() => {
  stopRecording()
  stopRealtime()
})
</script>

<template>
  <div class="min-h-screen py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-sage-500 to-sage-700 shadow-xl shadow-sage-900/30 mb-6">
          <svg class="w-8 h-8 text-cream-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 01-3 3z"/>
          </svg>
        </div>
        <h1 class="text-3xl sm:text-4xl font-display font-bold text-cream-50 mb-4">Listen & Identify</h1>
        <p class="text-lg text-cream-400 max-w-xl mx-auto">
          {{ mode === 'realtime' ? 'Real-time frog call identification - like Merlin!' : 'Record frog calls and our AI will identify the species' }}
        </p>
      </div>

      <!-- Mode Toggle -->
      <div class="flex justify-center mb-8">
        <div class="inline-flex rounded-xl bg-slate-800/60 p-1">
          <button
            @click="mode = 'realtime'"
            :class="[
              'px-6 py-3 rounded-lg font-medium transition-all duration-200',
              mode === 'realtime' 
                ? 'bg-sage-600 text-cream-50 shadow-lg' 
                : 'text-cream-400 hover:text-cream-100'
            ]"
          >
            <div class="flex items-center gap-2">
              <div class="relative">
                <div v-if="mode === 'realtime' && isListening" class="absolute -top-1 -right-1 w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              Real-time
            </div>
          </button>
          <button
            @click="mode = 'record'"
            :class="[
              'px-6 py-3 rounded-lg font-medium transition-all duration-200',
              mode === 'record' 
                ? 'bg-sage-600 text-cream-50 shadow-lg' 
                : 'text-cream-400 hover:text-cream-100'
            ]"
          >
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="3" stroke-width="2"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
              </svg>
              Record
            </div>
          </button>
        </div>
      </div>

      <template v-if="mode === 'realtime'">
        <!-- Listening Card -->
        <div class="card p-8 mb-8">
          <!-- Audio Visualizer -->
          <AudioVisualizer :level="audioLevel" :is-recording="isListening" class="mb-8" />

          <!-- Status -->
          <div class="text-center mb-8">
            <p class="text-4xl font-mono font-bold text-cream-100 mb-2">
              {{ formatDuration(sessionDuration) }}
            </p>
            <p :class="isListening ? 'text-cream-400' : 'text-cream-500'">
              {{ isListening ? '🎤 Listening for frog calls...' : 'Ready to start' }}
            </p>
          </div>

          <!-- Controls -->
          <div class="flex justify-center gap-4">
            <button
              v-if="!isListening"
              @click="startRealtime"
              class="btn btn-primary btn-lg"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              Start Listening
            </button>

            <button
              v-if="isListening"
              @click="stopRealtime"
              class="btn bg-red-500 hover:bg-red-400 text-cream-100 btn-lg"
            >
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="2"/>
              </svg>
              Stop
            </button>

            <button
              v-if="!isListening && aggregatedPredictions.length > 0"
              @click="resetRealtime"
              class="btn btn-secondary"
            >
              Clear Results
            </button>
          </div>
        </div>

        <!-- Live Detections -->
        <div v-if="isListening || aggregatedPredictions.length > 0" class="space-y-6">
          <!-- Current Detection -->
          <div v-if="realtimePredictions.length > 0 && isListening" class="card p-6 border-sage-600/50 bg-sage-900/30 animate-fade-in">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-3 h-3 bg-sage-500 rounded-full animate-pulse"></div>
              <h3 class="font-display font-semibold text-cream-100">Just Detected</h3>
            </div>
            <div class="flex items-center gap-6">
              <!-- Species Image -->
              <div class="w-24 h-24 rounded-xl overflow-hidden bg-slate-800 shrink-0 shadow-lg ring-2 ring-sage-500/50">
                <img 
                  v-if="realtimePredictions[0].species_id"
                  :src="`/uploads/species/${realtimePredictions[0].species_id}.jpg`"
                  :alt="realtimePredictions[0].common_name"
                  class="w-full h-full object-cover"
                  @error="($event.target as HTMLImageElement).src = '/uploads/species/' + realtimePredictions[0].species_id + '.png'"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-sage-500">
                  <svg class="w-10 h-10" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2z"/>
                  </svg>
                </div>
              </div>
              <!-- Species Info -->
              <div class="flex-1 min-w-0">
                <p class="text-2xl font-bold text-cream-100 truncate">{{ realtimePredictions[0].common_name }}</p>
                <p class="text-sm text-cream-400 italic">{{ realtimePredictions[0].scientific_name }}</p>
              </div>
              <!-- Confidence -->
              <div class="text-right shrink-0">
                <p class="text-3xl font-bold text-sage-400">{{ formatConfidence(realtimePredictions[0].confidence) }}</p>
                <p class="text-xs text-cream-500">confidence</p>
              </div>
            </div>
          </div>

          <!-- Aggregated Results -->
          <div v-if="aggregatedPredictions.length > 0" class="card p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="font-display font-semibold text-cream-100">Session Detections</h3>
              <span class="px-3 py-1 rounded-full bg-sage-500/20 text-cream-400 text-sm">
                {{ aggregatedPredictions.length }} species found
              </span>
            </div>

            <div class="space-y-4">
              <div
                v-for="(pred, index) in aggregatedPredictions"
                :key="pred.common_name"
                class="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 hover:bg-slate-800/70 transition-colors"
              >
                <!-- Species Image -->
                <div class="relative shrink-0">
                  <div class="w-16 h-16 rounded-xl overflow-hidden bg-slate-700 shadow-md">
                    <img 
                      v-if="pred.species_id"
                      :src="`/uploads/species/${pred.species_id}.jpg`"
                      :alt="pred.common_name"
                      class="w-full h-full object-cover"
                      @error="($event.target as HTMLImageElement).src = '/uploads/species/' + pred.species_id + '.png'"
                    />
                    <div v-else class="w-full h-full flex items-center justify-center text-slate-500">
                      <svg class="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2z"/>
                      </svg>
                    </div>
                  </div>
                  <!-- Rank Badge -->
                  <div :class="[
                    'absolute -top-2 -left-2 w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shadow-lg',
                    index === 0 ? 'bg-sage-500 text-cream-100' : 'bg-slate-600 text-cream-400'
                  ]">
                    {{ index + 1 }}
                  </div>
                </div>

                <!-- Species Info -->
                <div class="flex-1">
                  <p class="font-semibold text-cream-100">{{ pred.common_name }}</p>
                  <p class="text-sm text-cream-500 italic">{{ pred.scientific_name || '—' }}</p>
                </div>

                <!-- Confidence Bar -->
                <div class="w-32">
                  <div class="flex items-center justify-between text-sm mb-1">
                    <span class="text-cream-400">{{ formatConfidence(pred.confidence) }}</span>
                  </div>
                  <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      class="h-full bg-gradient-to-r from-sage-600 to-sage-500 rounded-full transition-all duration-500"
                      :style="{ width: `${pred.confidence * 100}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- No Detections Yet -->
          <div v-else-if="isListening" class="card p-8 text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-800 flex items-center justify-center">
              <svg class="w-8 h-8 text-cream-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
              </svg>
            </div>
            <p class="text-cream-400">Waiting for frog calls...</p>
            <p class="text-sm text-cream-500 mt-2">Point your device towards the sound source</p>
          </div>
        </div>
      </template>

      <template v-else>
        <!-- Recording Card -->
        <div class="card p-8 mb-8">
          <!-- Audio Visualizer -->
          <AudioVisualizer :level="audioLevel" :is-recording="isRecording" class="mb-8" />

          <!-- Recording Info -->
          <div class="text-center mb-8">
            <p class="text-4xl font-mono font-bold text-cream-100 mb-2">
              {{ formatDuration(recordingDuration) }}
            </p>
            <p class="text-cream-500">
              {{ isRecording ? 'Recording...' : identificationStore.isProcessing ? 'Processing...' : 'Ready to record' }}
            </p>
          </div>

          <!-- Controls -->
          <div class="flex justify-center gap-4">
            <button
              v-if="!isRecording && !identificationStore.result"
              @click="startRecording"
              :disabled="identificationStore.isProcessing"
              class="btn btn-primary btn-lg"
            >
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="6"/>
              </svg>
              Start Recording
            </button>

            <button
              v-if="isRecording"
              @click="stopRecording"
              class="btn bg-red-500 hover:bg-red-400 text-cream-100 btn-lg"
            >
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="2"/>
              </svg>
              Stop Recording
            </button>

            <button
              v-if="identificationStore.result"
              @click="resetIdentification"
              class="btn btn-secondary"
            >
              Record Again
            </button>
          </div>

          <!-- Processing Indicator -->
          <div v-if="identificationStore.isProcessing" class="mt-8 flex items-center justify-center gap-3">
            <div class="w-6 h-6 border-2 border-sage-500 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-cream-400">Analyzing audio...</span>
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
      </template>

      <!-- Tips -->
      <div class="mt-12 card p-6">
        <h3 class="font-display font-semibold text-cream-100 mb-4">
          {{ mode === 'realtime' ? 'Real-time Tips' : 'Recording Tips' }}
        </h3>
        <ul class="space-y-2 text-cream-400">
          <template v-if="mode === 'realtime'">
            <li class="flex items-start gap-2">
              <svg class="w-5 h-5 text-cream-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Detections update every 3 seconds as the AI analyzes
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-5 h-5 text-cream-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Works best in quieter environments
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-5 h-5 text-cream-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Multiple species can be detected in a single session
            </li>
          </template>
          <template v-else>
            <li class="flex items-start gap-2">
              <svg class="w-5 h-5 text-cream-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Record for at least 3-5 seconds for best results
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-5 h-5 text-cream-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Try to minimize background noise
            </li>
          </template>
          <li class="flex items-start gap-2">
            <svg class="w-5 h-5 text-cream-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Point your device towards the sound source
          </li>
          <li class="flex items-start gap-2">
            <svg class="w-5 h-5 text-cream-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Frogs are most vocal at dusk and dawn
          </li>
        </ul>
      </div>
    </div>

    <!-- Save Modal -->
    <SaveSightingModal
      v-if="showSaveModal"
      :prediction="identificationStore.selectedPrediction!"
      detection-type="audio"
      @save="handleSave"
      @close="showSaveModal = false"
    />
  </div>
</template>
