<template>
  <div class="bg-ctp-surface0 rounded-lg p-6">
    <div class="flex items-center space-x-3 mb-6">
      <div class="w-10 h-10 bg-ctp-mauve rounded-lg flex items-center justify-center">
        <Settings class="w-5 h-5 text-ctp-base" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-ctp-text">Organization Settings</h3>
        <p class="text-sm text-ctp-subtext1">Configure how your project will be organized</p>
      </div>
    </div>

    <form @submit.prevent="generatePreview" class="space-y-4">
      <!-- Target Category Override -->
      <div>
        <label class="block text-sm font-medium text-ctp-text mb-2">
          Target Category (Optional)
        </label>
        <select
          v-model="targetCategory"
          class="w-full px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text focus:outline-none focus:ring-2 focus:ring-ctp-blue"
        >
          <option value="">Use AI Classification: {{ scan.final_classification.category }}</option>
          <option value="Web/Frontend">Web/Frontend</option>
          <option value="Web/Backend">Web/Backend</option>
          <option value="Web/FullStack">Web/FullStack</option>
          <option value="Mobile/CrossPlatform">Mobile/CrossPlatform</option>
          <option value="SystemUtilities/Python">SystemUtilities/Python</option>
          <option value="SystemUtilities/Rust">SystemUtilities/Rust</option>
          <option value="SystemUtilities/Go">SystemUtilities/Go</option>
          <option value="Games/Unity">Games/Unity</option>
          <option value="Games/Godot">Games/Godot</option>
          <option value="Libraries/Python">Libraries/Python</option>
          <option value="Libraries/JavaScript">Libraries/JavaScript</option>
          <option value="DataScience">DataScience</option>
          <option value="Misc">Misc</option>
        </select>
      </div>

      <!-- Custom Project Name -->
      <div>
        <label class="block text-sm font-medium text-ctp-text mb-2">
          Custom Project Name (Optional)
        </label>
        <input
          v-model="customName"
          type="text"
          :placeholder="scan.final_classification.suggested_name || 'Leave empty to use suggested name'"
          class="w-full px-3 py-2 bg-ctp-surface1 border border-ctp-surface2 rounded-lg text-ctp-text placeholder-ctp-subtext0 focus:outline-none focus:ring-2 focus:ring-ctp-blue"
        />
      </div>

      <!-- Conflict Resolution -->
      <div>
        <label class="block text-sm font-medium text-ctp-text mb-2">
          Conflict Resolution
        </label>
        <div class="grid grid-cols-3 gap-2">
          <label
            v-for="option in conflictOptions"
            :key="option.value"
            :class="[
              'flex flex-col items-center p-3 border-2 rounded-lg cursor-pointer transition-colors',
              conflictResolution === option.value 
                ? 'border-ctp-blue bg-ctp-blue/10' 
                : 'border-ctp-surface2 hover:border-ctp-overlay0'
            ]"
          >
            <input
              v-model="conflictResolution"
              :value="option.value"
              type="radio"
              class="sr-only"
            />
            <component :is="option.icon" class="w-5 h-5 mb-1" />
            <span class="text-sm font-medium text-ctp-text">{{ option.label }}</span>
            <span class="text-xs text-ctp-subtext1 text-center">{{ option.description }}</span>
          </label>
        </div>
      </div>

      <!-- Create Backup -->
      <div class="flex items-center justify-between p-3 bg-ctp-surface1 rounded-lg">
        <div>
          <div class="font-medium text-ctp-text">Create Backup</div>
          <div class="text-sm text-ctp-subtext1">Create a backup before organizing (Recommended)</div>
        </div>
        <label class="relative inline-flex items-center cursor-pointer">
          <input
            v-model="createBackup"
            type="checkbox"
            class="sr-only peer"
          />
          <div class="w-11 h-6 bg-ctp-surface2 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-ctp-blue/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-ctp-blue"></div>
        </label>
      </div>

      <!-- Generate Preview Button -->
      <button
        type="submit"
        :disabled="isGenerating"
        class="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-ctp-mauve hover:bg-opacity-80 disabled:bg-ctp-surface2 disabled:text-ctp-subtext0 text-ctp-base font-medium rounded-lg transition-colors"
      >
        <component :is="isGenerating ? LoaderIcon : Eye" :class="['w-5 h-5', isGenerating && 'animate-spin']" />
        <span>{{ isGenerating ? 'Generating Preview...' : 'Generate Preview' }}</span>
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  Settings, 
  Eye, 
  Loader2 as LoaderIcon,
  SkipForward,
  Edit3,
  AlertTriangle
} from 'lucide-vue-next'
import type { ScanResponse } from '../../stores/appStore'

interface Props {
  scan: ScanResponse
}

const props = defineProps<Props>()
const emit = defineEmits<{
  preview: [options: {
    targetCategory?: string
    conflictResolution?: string
    createBackup?: boolean
    customName?: string
  }]
}>()

// Form state
const targetCategory = ref('')
const customName = ref('')
const conflictResolution = ref('rename')
const createBackup = ref(true)
const isGenerating = ref(false)

const conflictOptions = [
  {
    value: 'skip',
    label: 'Skip',
    description: 'Skip if exists',
    icon: SkipForward
  },
  {
    value: 'rename',
    label: 'Rename',
    description: 'Add suffix',
    icon: Edit3
  },
  {
    value: 'overwrite',
    label: 'Overwrite',
    description: 'Replace existing',
    icon: AlertTriangle
  }
]

const generatePreview = async () => {
  try {
    isGenerating.value = true
    
    emit('preview', {
      targetCategory: targetCategory.value || undefined,
      conflictResolution: conflictResolution.value,
      createBackup: createBackup.value,
      customName: customName.value || undefined
    })
    
  } catch (error) {
    console.error('Failed to generate preview:', error)
  } finally {
    isGenerating.value = false
  }
}
</script>