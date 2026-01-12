<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="relative z-10 border-t border-slate-800/50 bg-slate-950/80 backdrop-blur-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col md:flex-row items-center justify-between gap-4">
        <!-- Logo & Copyright -->
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-sage-600 to-sage-700 flex items-center justify-center">
            <svg class="w-5 h-5 text-cream-50" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C9.5 2 7.5 4 7.5 6.5c0 .5.1 1 .3 1.5C5.5 8.5 4 10.5 4 13c0 3.3 2.7 6 6 6h4c3.3 0 6-2.7 6-6 0-2.5-1.5-4.5-3.8-5-.2-.5-.3-1-.3-1.5C16.5 4 14.5 2 12 2z"/>
            </svg>
          </div>
          <span class="text-cream-500 text-sm">
            © {{ currentYear }} Frog Identifier
          </span>
        </div>

        <!-- Info -->
        <p class="text-slate-500 text-sm text-center">
          Discover and catalog the frogs around you
        </p>

        <!-- Links -->
        <div class="flex items-center gap-6">
          <a href="#" class="text-cream-500 hover:text-cream-300 text-sm transition-colors">
            About
          </a>
          <a href="#" class="text-cream-500 hover:text-cream-300 text-sm transition-colors">
            Privacy
          </a>
          <a href="#" class="text-cream-500 hover:text-cream-300 text-sm transition-colors">
            Help
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>
