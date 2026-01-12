import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Species } from '@/types'
import { speciesApi } from '@/services/api'

export const useSpeciesStore = defineStore('species', () => {
  const species = ref<Species[]>([])
  const currentSpecies = ref<Species | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  const filteredSpecies = computed(() => {
    if (!searchQuery.value) return species.value
    const query = searchQuery.value.toLowerCase()
    return species.value.filter(
      s =>
        s.common_name.toLowerCase().includes(query) ||
        s.scientific_name.toLowerCase().includes(query)
    )
  })

  async function fetchAll() {
    isLoading.value = true
    error.value = null
    try {
      const response = await speciesApi.list(0, 500)
      species.value = response.items
    } catch (e) {
      error.value = 'Failed to load species'
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchById(id: number) {
    isLoading.value = true
    error.value = null
    try {
      currentSpecies.value = await speciesApi.get(id)
    } catch (e) {
      error.value = 'Failed to load species details'
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  function getById(id: number): Species | undefined {
    return species.value.find(s => s.id === id)
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  return {
    species,
    currentSpecies,
    isLoading,
    error,
    searchQuery,
    filteredSpecies,
    fetchAll,
    fetchById,
    getById,
    setSearchQuery,
  }
})
