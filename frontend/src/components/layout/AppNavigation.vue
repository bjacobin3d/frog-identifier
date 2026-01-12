<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const isMobileMenuOpen = ref(false)

const navLinks = [
  { to: '/', label: 'Home', icon: 'home' },
  { to: '/identify/audio', label: 'Listen', icon: 'mic' },
  { to: '/identify/photo', label: 'Photo', icon: 'camera' },
  { to: '/species', label: 'Species', icon: 'book' },
  { to: '/library', label: 'Library', icon: 'collection' },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}
</script>

<template>
  <nav class="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-3 group">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-sage-600 to-sage-700 flex items-center justify-center shadow-lg shadow-sage-900/30 group-hover:shadow-sage-800/40 transition-shadow">
            <svg class="w-6 h-6 text-cream-50" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2zm-3 8a1.5 1.5 0 110 3 1.5 1.5 0 010-3zm6 0a1.5 1.5 0 110 3 1.5 1.5 0 010-3z"/>
            </svg>
          </div>
          <span class="font-display text-xl font-semibold text-cream-100 hidden sm:block">Frog Identifier</span>
        </RouterLink>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center gap-1">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            :class="isActive(link.to) 
              ? 'bg-slate-800/60 text-cream-100' 
              : 'text-cream-400 hover:text-cream-200 hover:bg-slate-800/40'"
          >
            {{ link.label }}
          </RouterLink>
        </div>

        <!-- Mobile Menu Button -->
        <button
          @click="toggleMobileMenu"
          class="md:hidden p-2 rounded-lg text-cream-400 hover:text-cream-200 hover:bg-slate-800/40"
        >
          <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
          <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="isMobileMenuOpen" class="md:hidden border-t border-slate-800/50 bg-slate-950/95 backdrop-blur-xl">
        <div class="px-4 py-3 space-y-1">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            @click="isMobileMenuOpen = false"
            class="block px-4 py-3 rounded-lg text-sm font-medium transition-all"
            :class="isActive(link.to) 
              ? 'bg-slate-800/60 text-cream-100' 
              : 'text-cream-400 hover:text-cream-200 hover:bg-slate-800/40'"
          >
            {{ link.label }}
          </RouterLink>
        </div>
      </div>
    </Transition>
  </nav>
</template>
