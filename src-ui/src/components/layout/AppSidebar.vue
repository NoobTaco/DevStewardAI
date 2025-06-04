<template>
  <aside class="w-64 bg-ctp-surface0 border-r border-ctp-surface2 flex flex-col">
    <!-- Navigation -->
    <nav class="flex-1 p-4 space-y-2">
      <router-link
        v-for="item in navigationItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center space-x-3 px-4 py-3 rounded-lg text-ctp-subtext1 hover:text-ctp-text hover:bg-ctp-surface1 transition-all group"
        :class="{ 
          'bg-ctp-surface1 text-ctp-text': $route.path === item.path,
          'opacity-50': item.disabled
        }"
      >
        <component :is="item.icon" class="w-5 h-5 group-hover:scale-110 transition-transform" />
        <div>
          <div class="font-medium">{{ item.title }}</div>
          <div class="text-xs text-ctp-subtext0">{{ item.description }}</div>
        </div>
      </router-link>
    </nav>

    <!-- System Info -->
    <div class="p-4 border-t border-ctp-surface2 space-y-3">
      <!-- Health Summary -->
      <div class="text-sm">
        <div class="flex items-center justify-between mb-2">
          <span class="text-ctp-subtext1">System Status</span>
          <span 
            :class="[
              'text-xs px-2 py-1 rounded-full',
              appStore.isBackendHealthy ? 'bg-ctp-green text-ctp-base' : 'bg-ctp-red text-ctp-base'
            ]"
          >
            {{ appStore.isBackendHealthy ? 'Healthy' : 'Unhealthy' }}
          </span>
        </div>
        
        <div class="space-y-1 text-xs text-ctp-subtext0">
          <div class="flex justify-between">
            <span>Backend:</span>
            <span :class="appStore.backendStatus?.is_running ? 'text-ctp-green' : 'text-ctp-red'">
              {{ appStore.backendStatus?.is_running ? 'Running' : 'Stopped' }}
            </span>
          </div>
          
          <div class="flex justify-between">
            <span>AI Models:</span>
            <span :class="appStore.availableModels.length > 0 ? 'text-ctp-green' : 'text-ctp-yellow'">
              {{ appStore.availableModels.length }} available
            </span>
          </div>
          
          <div v-if="appStore.backendStatus?.uptime_seconds" class="flex justify-between">
            <span>Uptime:</span>
            <span class="text-ctp-text">{{ formatUptime(appStore.backendStatus.uptime_seconds) }}</span>
          </div>
        </div>
      </div>

      <!-- Current Project Info -->
      <div v-if="appStore.currentScan" class="text-sm">
        <div class="text-ctp-subtext1 mb-2">Current Project</div>
        <div class="bg-ctp-surface1 rounded-lg p-3 space-y-1">
          <div class="font-medium text-ctp-text truncate" :title="appStore.currentScan.path">
            {{ getProjectName(appStore.currentScan.path) }}
          </div>
          <div class="text-xs text-ctp-subtext0">
            {{ appStore.currentScan.final_classification.category }}
          </div>
          <div class="text-xs text-ctp-subtext0">
            {{ appStore.currentScan.total_files }} files
          </div>
        </div>
      </div>

      <!-- Version Info -->
      <div class="text-xs text-ctp-subtext0 text-center">
        DevSteward AI v1.0.0
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  FolderOpen, 
  Plus, 
  Settings,
  Sparkles
} from 'lucide-vue-next'
import { useAppStore } from '../../stores/appStore'

const route = useRoute()
const appStore = useAppStore()

const navigationItems = computed(() => [
  {
    path: '/organizer',
    title: 'Project Organizer',
    description: 'Scan & organize projects',
    icon: FolderOpen,
    disabled: false
  },
  {
    path: '/new-project',
    title: 'New Project',
    description: 'Create from templates',
    icon: Plus,
    disabled: false
  },
  {
    path: '/settings',
    title: 'Settings',
    description: 'Configure preferences',
    icon: Settings,
    disabled: false
  }
])

const formatUptime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes}m`
  }
}

const getProjectName = (path: string): string => {
  return path.split('/').pop() || path
}
</script>