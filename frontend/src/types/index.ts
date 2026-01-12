// Species types
export interface Species {
  id: number
  common_name: string
  scientific_name: string
  description: string | null
  habitat: string | null
  range: string | null
  image_url: string | null
  audio_sample_url: string | null
  created_at: string
}

export interface SpeciesListResponse {
  items: Species[]
  total: number
  skip: number
  limit: number
}

// Sighting types
export interface Sighting {
  id: number
  species_id: number
  detection_type: 'audio' | 'image'
  confidence_score: number
  notes: string | null
  latitude: number | null
  longitude: number | null
  location_name: string | null
  image_path: string | null
  audio_path: string | null
  sighted_at: string
  created_at: string
}

export interface SightingListResponse {
  items: Sighting[]
  total: number
  skip: number
  limit: number
}

export interface SightingStats {
  total_sightings: number
  unique_species: number
  audio_identifications: number
  image_identifications: number
  recent_sightings: number
  top_species: Array<{ name: string; count: number }>
}

export interface CreateSightingData {
  species_id: number
  detection_type: 'audio' | 'image'
  confidence_score: number
  notes?: string
  latitude?: number
  longitude?: number
  location_name?: string
  image?: File
  audio?: File
}

// Identification types
export interface PredictionItem {
  species_id: number
  common_name: string
  scientific_name: string
  confidence: number
  image_url: string | null
}

export interface IdentificationResult {
  detection_type: 'audio' | 'image'
  predictions: PredictionItem[]
  top_prediction: PredictionItem | null
}

// Audio recording types
export interface AudioRecordingState {
  isRecording: boolean
  isProcessing: boolean
  audioLevel: number
  duration: number
}

// Filter types
export interface SightingFilters {
  species_id?: number
  detection_type?: 'audio' | 'image'
  start_date?: string
  end_date?: string
}

// Real-time identification types
export interface RealtimePrediction {
  species_id: number | null
  common_name: string
  scientific_name: string
  confidence: number
}

export interface RealtimeDetectionMessage {
  type: 'detection'
  predictions: RealtimePrediction[]
  aggregated: RealtimePrediction[]
  timestamp: string
}

