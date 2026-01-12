import { ref, onUnmounted } from 'vue'

export interface AudioRecorderState {
  isRecording: boolean
  isPaused: boolean
  duration: number
  audioLevel: number
}

export function useAudioRecorder() {
  const isRecording = ref(false)
  const isPaused = ref(false)
  const duration = ref(0)
  const audioLevel = ref(0)
  const audioBlob = ref<Blob | null>(null)
  const error = ref<string | null>(null)

  let mediaRecorder: MediaRecorder | null = null
  let audioChunks: Blob[] = []
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let durationInterval: number | null = null
  let animationFrame: number | null = null

  async function startRecording(): Promise<void> {
    try {
      error.value = null
      audioBlob.value = null
      audioChunks = []

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // Set up audio analysis
      audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)

      // Start level monitoring
      updateAudioLevel()

      // Set up media recorder
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        audioBlob.value = new Blob(audioChunks, { type: 'audio/webm' })
        cleanup()
      }

      mediaRecorder.start(1000)
      isRecording.value = true
      duration.value = 0

      // Start duration counter
      durationInterval = window.setInterval(() => {
        if (!isPaused.value) {
          duration.value++
        }
      }, 1000)

    } catch (err) {
      error.value = 'Could not access microphone. Please check permissions.'
      console.error('Error starting recording:', err)
    }
  }

  function stopRecording(): Blob | null {
    if (mediaRecorder && isRecording.value) {
      mediaRecorder.stop()
      mediaRecorder.stream.getTracks().forEach(track => track.stop())
      isRecording.value = false
      isPaused.value = false
    }
    return audioBlob.value
  }

  function pauseRecording(): void {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.pause()
      isPaused.value = true
    }
  }

  function resumeRecording(): void {
    if (mediaRecorder && mediaRecorder.state === 'paused') {
      mediaRecorder.resume()
      isPaused.value = false
    }
  }

  function updateAudioLevel(): void {
    if (!analyser) return

    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    analyser.getByteFrequencyData(dataArray)

    const average = dataArray.reduce((a, b) => a + b) / dataArray.length
    audioLevel.value = average / 255

    if (isRecording.value) {
      animationFrame = requestAnimationFrame(updateAudioLevel)
    }
  }

  function cleanup(): void {
    if (durationInterval) {
      clearInterval(durationInterval)
      durationInterval = null
    }
    if (animationFrame) {
      cancelAnimationFrame(animationFrame)
      animationFrame = null
    }
    if (audioContext) {
      audioContext.close()
      audioContext = null
    }
    analyser = null
    audioLevel.value = 0
  }

  function reset(): void {
    stopRecording()
    audioBlob.value = null
    duration.value = 0
    error.value = null
  }

  onUnmounted(() => {
    stopRecording()
    cleanup()
  })

  return {
    isRecording,
    isPaused,
    duration,
    audioLevel,
    audioBlob,
    error,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    reset,
  }
}
