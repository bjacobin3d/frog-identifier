import axios from 'axios'
import type {
  Species,
  SpeciesListResponse,
  Sighting,
  SightingListResponse,
  SightingStats,
  CreateSightingData,
  IdentificationResult,
  SightingFilters
} from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Species API
export const speciesApi = {
  async list(skip = 0, limit = 100, search?: string): Promise<SpeciesListResponse> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (search) params.append('search', search)
    const response = await api.get<SpeciesListResponse>(`/species?${params}`)
    return response.data
  },

  async get(id: number): Promise<Species> {
    const response = await api.get<Species>(`/species/${id}`)
    return response.data
  },

  async getCalls(id: number): Promise<{ species_id: number; common_name: string; audio_samples: string[] }> {
    const response = await api.get(`/species/${id}/calls`)
    return response.data
  },
}

// Sightings API
export const sightingsApi = {
  async list(filters?: SightingFilters, skip = 0, limit = 50): Promise<SightingListResponse> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (filters?.species_id) params.append('species_id', filters.species_id.toString())
    if (filters?.detection_type) params.append('detection_type', filters.detection_type)
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)
    const response = await api.get<SightingListResponse>(`/sightings?${params}`)
    return response.data
  },

  async get(id: number): Promise<Sighting> {
    const response = await api.get<Sighting>(`/sightings/${id}`)
    return response.data
  },

  async getStats(): Promise<SightingStats> {
    const response = await api.get<SightingStats>('/sightings/stats')
    return response.data
  },

  async create(data: CreateSightingData): Promise<Sighting> {
    const formData = new FormData()
    formData.append('species_id', data.species_id.toString())
    formData.append('detection_type', data.detection_type)
    formData.append('confidence_score', data.confidence_score.toString())
    if (data.notes) formData.append('notes', data.notes)
    if (data.latitude) formData.append('latitude', data.latitude.toString())
    if (data.longitude) formData.append('longitude', data.longitude.toString())
    if (data.location_name) formData.append('location_name', data.location_name)
    if (data.image) formData.append('image', data.image)
    if (data.audio) formData.append('audio', data.audio)

    const response = await api.post<Sighting>('/sightings', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async update(id: number, data: { notes?: string; location_name?: string }): Promise<Sighting> {
    const response = await api.put<Sighting>(`/sightings/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/sightings/${id}`)
  },
}

// Identification API
export const identifyApi = {
  async audio(audioBlob: Blob): Promise<IdentificationResult> {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    const response = await api.post<IdentificationResult>('/identify/audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async audioStream(audioData: string): Promise<IdentificationResult> {
    const response = await api.post<IdentificationResult>('/identify/audio/stream', {
      audio_data: audioData,
      sample_rate: 44100,
      format: 'webm',
    })
    return response.data
  },

  async image(imageFile: File): Promise<IdentificationResult> {
    const formData = new FormData()
    formData.append('image', imageFile)
    const response = await api.post<IdentificationResult>('/identify/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

export default api
