import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Home' }
  },
  {
    path: '/identify/audio',
    name: 'identify-audio',
    component: () => import('@/views/AudioIdentifyView.vue'),
    meta: { title: 'Listen & Identify' }
  },
  {
    path: '/identify/photo',
    name: 'identify-photo',
    component: () => import('@/views/PhotoIdentifyView.vue'),
    meta: { title: 'Photo Identify' }
  },
  {
    path: '/species',
    name: 'species',
    component: () => import('@/views/SpeciesGuideView.vue'),
    meta: { title: 'Species Guide' }
  },
  {
    path: '/species/:id',
    name: 'species-detail',
    component: () => import('@/views/SpeciesDetailView.vue'),
    meta: { title: 'Species Detail' }
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('@/views/LibraryView.vue'),
    meta: { title: 'My Library' }
  },
  {
    path: '/library/:id',
    name: 'sighting-detail',
    component: () => import('@/views/SightingDetailView.vue'),
    meta: { title: 'Sighting Detail' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0, behavior: 'smooth' }
  }
})

// Update document title
router.beforeEach((to, from, next) => {
  const title = to.meta.title as string
  document.title = title ? `${title} | Frog Identifier` : 'Frog Identifier'
  next()
})

export default router
