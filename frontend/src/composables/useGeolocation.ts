import { ref } from 'vue'

export interface GeolocationState {
  latitude: number | null
  longitude: number | null
  accuracy: number | null
  isLoading: boolean
  error: string | null
}

export function useGeolocation() {
  const latitude = ref<number | null>(null)
  const longitude = ref<number | null>(null)
  const accuracy = ref<number | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function getCurrentPosition(): Promise<{ latitude: number; longitude: number } | null> {
    if (!navigator.geolocation) {
      error.value = 'Geolocation is not supported by your browser'
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        })
      })

      latitude.value = position.coords.latitude
      longitude.value = position.coords.longitude
      accuracy.value = position.coords.accuracy

      return {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      }
    } catch (err: any) {
      switch (err.code) {
        case err.PERMISSION_DENIED:
          error.value = 'Location permission denied'
          break
        case err.POSITION_UNAVAILABLE:
          error.value = 'Location information unavailable'
          break
        case err.TIMEOUT:
          error.value = 'Location request timed out'
          break
        default:
          error.value = 'An error occurred while getting location'
      }
      return null
    } finally {
      isLoading.value = false
    }
  }

  function formatCoordinates(): string {
    if (latitude.value === null || longitude.value === null) return ''
    return `${latitude.value.toFixed(6)}, ${longitude.value.toFixed(6)}`
  }

  function reset(): void {
    latitude.value = null
    longitude.value = null
    accuracy.value = null
    error.value = null
  }

  return {
    latitude,
    longitude,
    accuracy,
    isLoading,
    error,
    getCurrentPosition,
    formatCoordinates,
    reset,
  }
}
