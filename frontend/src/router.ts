import { createRouter, createWebHistory } from 'vue-router'

import LibraryView from './views/LibraryView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', name: 'knowledge', component: LibraryView }],
})
