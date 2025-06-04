import { createRouter, createWebHistory } from 'vue-router'
import OrganizerView from '../views/OrganizerView.vue'
import NewProjectView from '../views/NewProjectView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/organizer'
    },
    {
      path: '/organizer',
      name: 'Organizer',
      component: OrganizerView,
      meta: {
        title: 'Project Organizer',
        description: 'Scan and organize your development projects'
      }
    },
    {
      path: '/new-project',
      name: 'NewProject', 
      component: NewProjectView,
      meta: {
        title: 'New Project',
        description: 'Create new projects from templates'
      }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: SettingsView,
      meta: {
        title: 'Settings',
        description: 'Configure DevSteward AI preferences'
      }
    }
  ]
})

// Set page title based on route
router.beforeEach((to) => {
  const title = to.meta?.title ? `${to.meta.title} | DevSteward AI` : 'DevSteward AI'
  document.title = title
})

export default router