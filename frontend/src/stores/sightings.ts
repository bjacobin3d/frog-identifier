import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Sighting, SightingStats, SightingFilters, CreateSightingData } from '@/types'
import { sightingsApi } from '@/services/api'

export const useSightingsStore = defineStore('sightings', () => {
  const sightings = ref<Sighting[]>([])
  const currentSighting = ref<Sighting | null>(null)
  const stats = ref<SightingStats | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const filters = ref<SightingFilters>({})

  const recentSightings = computed(() => 
    [...sightings.value].sort((a, b) => 
      new Date(b.sighted_at).getTime() - new Date(a.sighted_at).getTime()
    ).slice(0, 5)
  )

  async function fetchAll(newFilters?: SightingFilters, skip = 0, limit = 50) {
    isLoading.value = true
    error.value = null
    if (newFilters) filters.value = newFilters
    try {
      const response = await sightingsApi.list(filters.value, skip, limit)
      sightings.value = response.items
      total.value = response.total
    } catch (e) {
      error.value = 'Failed to load sightings'
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchById(id: number) {
    isLoading.value = true
    error.value = null
    try {
      currentSighting.value = await sightingsApi.get(id)
    } catch (e) {
      error.value = 'Failed to load sighting details'
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchStats() {
    try {
      stats.value = await sightingsApi.getStats()
    } catch (e) {
      console.error('Failed to load stats:', e)
    }
  }

  async function create(data: CreateSightingData): Promise<Sighting | null> {
    isLoading.value = true
    error.value = null
    try {
      const newSighting = await sightingsApi.create(data)
      sightings.value.unshift(newSighting)
      total.value++
      return newSighting
    } catch (e) {
      error.value = 'Failed to save sighting'
      console.error(e)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function update(id: number, data: { notes?: string; location_name?: string }) {
    isLoading.value = true
    error.value = null
    try {
      const updated = await sightingsApi.update(id, data)
      const index = sightings.value.findIndex(s => s.id === id)
      if (index !== -1) sightings.value[index] = updated
      if (currentSighting.value?.id === id) currentSighting.value = updated
      return updated
    } catch (e) {
      error.value = 'Failed to update sighting'
      console.error(e)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function remove(id: number) {
    isLoading.value = true
    error.value = null
    try {
      await sightingsApi.delete(id)
      sightings.value = sightings.value.filter(s => s.id !== id)
      total.value--
      if (currentSighting.value?.id === id) currentSighting.value = null
    } catch (e) {
      error.value = 'Failed to delete sighting'
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  function setFilters(newFilters: SightingFilters) {
    filters.value = newFilters
  }

  function clearFilters() {
    filters.value = {}
  }

  return {
    sightings,
    currentSighting,
    stats,
    isLoading,
    error,
    total,
    filters,
    recentSightings,
    fetchAll,
    fetchById,
    fetchStats,
    create,
    update,
    remove,
    setFilters,
    clearFilters,
  }
})
