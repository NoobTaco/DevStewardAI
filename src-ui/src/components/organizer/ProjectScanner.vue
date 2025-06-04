<template>
  <div class="bg-ctp-surface0 rounded-lg p-6">
    <div class="flex items-center space-x-3 mb-6">
      <div class="w-10 h-10 bg-ctp-blue rounded-lg flex items-center justify-center">
        <Search class="w-5 h-5 text-ctp-base" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-ctp-text">Project Scanner</h3>
        <p class="text-sm text-ctp-subtext1">Select and analyze a project directory</p>
      </div>
    </div>

    <form @submit.prevent="scanProject" class="space-y-4">
      <!-- Directory Selection -->
      <div>
        <label class="block text-sm font-medium text-ctp-text mb-2">
          Project Directory
        </label>
        <div class="flex space-x-2">
          <input
            v-model="projectPath"
            type="text"
            placeholder="Select a project directory..."
            class="flex-1 px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text placeholder-ctp-subtext0 focus:outline-none focus:ring-2 focus:ring-ctp-blue focus:border-transparent"
            :disabled="isScanning"
          />
          <button
            type="button"
            @click="selectDirectory"
            :disabled="isScanning || disabled"
            class="px-4 py-2 bg-ctp-surface1 hover:bg-ctp-surface2 border border-ctp-surface2 rounded-lg text-ctp-text transition-colors disabled:opacity-50"
          >
            <FolderOpen class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Scan Options -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- AI Analysis Toggle -->
        <div class="flex items-center justify-between p-3 bg-ctp-surface1 rounded-lg">
          <div>
            <div class="text-sm font-medium text-ctp-text">AI Analysis</div>
            <div class="text-xs text-ctp-subtext1">
              {{ appStore.canUseAI ? 'Enhanced classification' : 'Requires Ollama' }}
            </div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              v-model="useAI"
              type="checkbox"
              class="sr-only peer"
              :disabled="!appStore.canUseAI || isScanning"
            />
            <div class="w-11 h-6 bg-ctp-surface2 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-ctp-blue/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-ctp-blue"></div>
          </label>
        </div>

        <!-- AI Model Selection -->
        <div v-if="useAI && appStore.canUseAI">
          <label class="block text-sm font-medium text-ctp-text mb-2">
            AI Model
          </label>
          <select
            v-model="selectedModel"
            :disabled="isScanning"
            class="w-full px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text focus:outline-none focus:ring-2 focus:ring-ctp-blue focus:border-transparent"
          >
            <option
              v-for="model in appStore.availableModels"
              :key="model"
              :value="model"
            >
              {{ model }}
            </option>
          </select>
        </div>
      </div>

      <!-- Scan Button -->
      <button
        type="submit"
        :disabled="!projectPath || isScanning || disabled"
        class="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-ctp-blue hover:bg-opacity-80 disabled:bg-ctp-surface2 disabled:text-ctp-subtext0 text-ctp-base font-medium rounded-lg transition-colors"
      >
        <component :is="isScanning ? LoaderIcon : Search" :class="['w-5 h-5', isScanning && 'animate-spin']" />
        <span>{{ isScanning ? 'Scanning...' : 'Scan Project' }}</span>
      </button>
    </form>

    <!-- Backend Status Warning -->
    <div v-if="!appStore.isBackendHealthy" class="mt-4 p-3 bg-ctp-yellow/10 border border-ctp-yellow rounded-lg">
      <div class="flex items-center space-x-2">
        <AlertTriangle class="w-4 h-4 text-ctp-yellow" />
        <span class="text-sm text-ctp-text">Backend is not running. Start it to scan projects.</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  Search, 
  FolderOpen, 
  Loader2 as LoaderIcon,
  AlertTriangle 
} from 'lucide-vue-next'
import { useAppStore } from '../../stores/appStore'
import type { ScanResponse } from '../../stores/appStore'

interface Props {
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  scanComplete: [scan: ScanResponse]
}>()

const appStore = useAppStore()

// Form state
const projectPath = ref('')
const useAI = ref(true)
const selectedModel = ref('')
const isScanning = ref(false)

// Initialize with default model
onMounted(() => {
  if (appStore.availableModels.length > 0) {
    selectedModel.value = appStore.settings?.default_ai_model || appStore.availableModels[0]
  }
})

const selectDirectory = async () => {
  const selected = await appStore.selectDirectory()
  if (selected) {
    projectPath.value = selected
  }
}

const scanProject = async () => {
  if (!projectPath.value) return

  try {
    isScanning.value = true
    
    const scan = await appStore.scanProject(
      projectPath.value,
      useAI.value && appStore.canUseAI,
      selectedModel.value
    )
    
    emit('scanComplete', scan)
    
  } catch (error) {
    console.error('Scan failed:', error)
  } finally {
    isScanning.value = false
  }
}
</script>