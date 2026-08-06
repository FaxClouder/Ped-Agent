import { createRouter, createWebHistory } from 'vue-router'

import LibraryView from './views/LibraryView.vue'
import AnswerView from './views/AnswerView.vue'
import VisionWorkbenchView from './views/VisionWorkbenchView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'knowledge', component: LibraryView },
    { path: '/qa', name: 'answer', component: AnswerView },
    { path: '/vision', name: 'vision', component: VisionWorkbenchView },
  ],
})
