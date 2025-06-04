<template>
  <header class="bg-ctp-surface0 border-b border-ctp-surface2 px-6 py-4 flex items-center justify-between">
    <!-- Logo and Title -->
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 bg-gradient-to-br from-ctp-blue to-ctp-mauve rounded-lg flex items-center justify-center">
        <Bot class="w-5 h-5 text-ctp-base" />
      </div>
      <div>
        <h1 class="text-xl font-bold text-ctp-text">DevSteward AI</h1>
        <p class="text-sm text-ctp-subtext1">Project Organizer & Bootstrapper</p>
      </div>
    </div>

    <!-- Status Indicators -->
    <div class="flex items-center space-x-4">
      <!-- Backend Status -->
      <div class="flex items-center space-x-2">
        <div class="flex items-center space-x-1">
          <div 
            :class="[
              'w-2 h-2 rounded-full',
              appStore.isBackendHealthy ? 'bg-ctp-green' : 'bg-ctp-red'
            ]"
          ></div>
          <span class="text-sm text-ctp-subtext1">Backend</span>
        </div>
        
        <!-- Ollama Status -->
        <div class="flex items-center space-x-1">
          <div 
            :class="[
              'w-2 h-2 rounded-full',
              appStore.isOllamaAvailable ? 'bg-ctp-green' : 'bg-ctp-yellow'
            ]"
          ></div>
          <span class="text-sm text-ctp-subtext1">AI</span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center space-x-2">
        <!-- Refresh Status -->
        <button
          @click="refreshStatus"
          :disabled="appStore.isLoading"
          class="p-2 rounded-lg bg-ctp-surface1 hover:bg-ctp-surface2 transition-colors disabled:opacity-50"
          title="Refresh Status"
        >
          <RefreshCw :class="['w-4 h-4', appStore.isLoading && 'animate-spin']" />
        </button>

        <!-- Backend Controls -->
        <button
          v-if="!appStore.backendStatus?.is_running"
          @click="appStore.startBackend"
          :disabled="appStore.isLoading"
          class="px-3 py-1 text-sm bg-ctp-green text-ctp-base rounded-lg hover:bg-opacity-80 transition-colors disabled:opacity-50"
        >
          Start Backend
        </button>
        
        <button
          v-else
          @click="appStore.stopBackend"
          :disabled="appStore.isLoading"
          class="px-3 py-1 text-sm bg-ctp-red text-ctp-base rounded-lg hover:bg-opacity-80 transition-colors disabled:opacity-50"
        >
          Stop Backend
        </button>
      </div>

      <!-- Settings Button -->
      <router-link 
        to="/settings"
        class="p-2 rounded-lg bg-ctp-surface1 hover:bg-ctp-surface2 transition-colors"
        title="Settings"
      >
        <Settings class="w-4 h-4" />
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Bot, RefreshCw, Settings } from 'lucide-vue-next'
import { useAppStore } from '../../stores/appStore'

const appStore = useAppStore()

const refreshStatus = async () => {
  await appStore.checkBackendStatus()
  if (appStore.backendStatus?.is_running) {
    await appStore.checkHealth()
  }
  if (appStore.isOllamaAvailable) {
    await appStore.loadAvailableModels()
  }
}
</script>