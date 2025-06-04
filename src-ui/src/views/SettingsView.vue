<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-ctp-surface2">
      <h2 class="text-2xl font-bold text-ctp-text mb-2">Settings</h2>
      <p class="text-ctp-subtext1">Configure DevSteward AI preferences and behavior</p>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto p-6">
      <div class="max-w-2xl mx-auto space-y-6">
        
        <!-- Organization Settings -->
        <div class="bg-ctp-surface0 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-ctp-text mb-4 flex items-center space-x-2">
            <FolderOpen class="w-5 h-5" />
            <span>Organization Settings</span>
          </h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-ctp-text mb-2">
                Organization Root Directory
              </label>
              <div class="flex space-x-2">
                <input
                  v-model="localSettings.organization_root"
                  type="text"
                  class="flex-1 px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text focus:outline-none focus:ring-2 focus:ring-ctp-blue"
                />
                <button
                  @click="selectOrganizationRoot"
                  class="px-4 py-2 bg-ctp-surface1 hover:bg-ctp-surface2 border border-ctp-surface2 rounded-lg text-ctp-text"
                >
                  Browse
                </button>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ctp-text mb-2">
                Default Conflict Resolution
              </label>
              <select
                v-model="localSettings.conflict_resolution_strategy"
                class="w-full px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text focus:outline-none focus:ring-2 focus:ring-ctp-blue"
              >
                <option value="rename">Rename (Recommended)</option>
                <option value="skip">Skip</option>
                <option value="overwrite">Overwrite (Dangerous)</option>
              </select>
            </div>
            
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-ctp-text">Create Backups by Default</div>
                <div class="text-sm text-ctp-subtext1">Automatically create backups before organizing</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="localSettings.create_backup_by_default"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-ctp-surface2 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-ctp-blue/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-ctp-blue"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- AI Settings -->
        <div class="bg-ctp-surface0 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-ctp-text mb-4 flex items-center space-x-2">
            <Bot class="w-5 h-5" />
            <span>AI Settings</span>
          </h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-ctp-text mb-2">
                Ollama Base URL
              </label>
              <input
                v-model="localSettings.ollama_base_url"
                type="text"
                class="w-full px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text focus:outline-none focus:ring-2 focus:ring-ctp-blue"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ctp-text mb-2">
                Default AI Model
              </label>
              <select
                v-model="localSettings.default_ai_model"
                class="w-full px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text focus:outline-none focus:ring-2 focus:ring-ctp-blue"
              >
                <option
                  v-for="model in appStore.availableModels"
                  :key="model"
                  :value="model"
                >
                  {{ model }}
                </option>
                <option v-if="appStore.availableModels.length === 0" value="llama2">
                  llama2 (default)
                </option>
              </select>
            </div>
            
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-ctp-text">Use AI by Default</div>
                <div class="text-sm text-ctp-subtext1">Enable AI analysis for new scans</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="localSettings.use_ai_by_default"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-ctp-surface2 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-ctp-blue/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-ctp-blue"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- System Settings -->
        <div class="bg-ctp-surface0 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-ctp-text mb-4 flex items-center space-x-2">
            <Settings class="w-5 h-5" />
            <span>System Settings</span>
          </h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-ctp-text mb-2">
                Python Backend Port
              </label>
              <input
                v-model.number="localSettings.python_backend_port"
                type="number"
                min="1024"
                max="65535"
                class="w-full px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text focus:outline-none focus:ring-2 focus:ring-ctp-blue"
              />
            </div>
            
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-ctp-text">Auto-start Backend</div>
                <div class="text-sm text-ctp-subtext1">Start Python backend automatically on app launch</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="localSettings.auto_start_backend"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-ctp-surface2 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-ctp-blue/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-ctp-blue"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3">
          <button
            @click="resetSettings"
            class="px-4 py-2 bg-ctp-surface1 hover:bg-ctp-surface2 text-ctp-text rounded-lg transition-colors"
          >
            Reset to Defaults
          </button>
          <button
            @click="saveSettings"
            :disabled="!hasChanges || isSaving"
            class="px-4 py-2 bg-ctp-blue hover:bg-opacity-80 disabled:bg-ctp-surface2 disabled:text-ctp-subtext0 text-ctp-base rounded-lg transition-colors"
          >
            {{ isSaving ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { FolderOpen, Bot, Settings } from 'lucide-vue-next'
import { useAppStore } from '../stores/appStore'
import type { AppSettings } from '../stores/appStore'

const appStore = useAppStore()

const localSettings = ref<AppSettings>({
  organization_root: '~/OrganizedProjects',
  default_ai_model: 'llama2',
  create_backup_by_default: true,
  use_ai_by_default: true,
  conflict_resolution_strategy: 'rename',
  ollama_base_url: 'http://localhost:11434',
  python_backend_port: 8008,
  auto_start_backend: true
})

const originalSettings = ref<AppSettings | null>(null)
const isSaving = ref(false)

const hasChanges = computed(() => {
  if (!originalSettings.value) return false
  return JSON.stringify(localSettings.value) !== JSON.stringify(originalSettings.value)
})

onMounted(async () => {
  if (appStore.settings) {
    localSettings.value = { ...appStore.settings }
    originalSettings.value = { ...appStore.settings }
  }
})

// Watch for settings changes from the store
watch(() => appStore.settings, (newSettings) => {
  if (newSettings && !hasChanges.value) {
    localSettings.value = { ...newSettings }
    originalSettings.value = { ...newSettings }
  }
})

const selectOrganizationRoot = async () => {
  const selected = await appStore.selectDirectory()
  if (selected) {
    localSettings.value.organization_root = selected
  }
}

const resetSettings = () => {
  localSettings.value = {
    organization_root: '~/OrganizedProjects',
    default_ai_model: 'llama2',
    create_backup_by_default: true,
    use_ai_by_default: true,
    conflict_resolution_strategy: 'rename',
    ollama_base_url: 'http://localhost:11434',
    python_backend_port: 8008,
    auto_start_backend: true
  }
}

const saveSettings = async () => {
  try {
    isSaving.value = true
    await appStore.saveSettings(localSettings.value)
    originalSettings.value = { ...localSettings.value }
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    isSaving.value = false
  }
}
</script>