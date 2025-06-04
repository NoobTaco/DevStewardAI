<template>
  <div class="bg-ctp-surface0 rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-ctp-green rounded-lg flex items-center justify-center">
          <CheckCircle class="w-5 h-5 text-ctp-base" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-ctp-text">Scan Results</h3>
          <p class="text-sm text-ctp-subtext1">Project analysis completed</p>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="flex space-x-2">
        <button
          @click="$emit('organize')"
          class="px-4 py-2 bg-ctp-blue hover:bg-opacity-80 text-ctp-base text-sm font-medium rounded-lg transition-colors"
        >
          Organize
        </button>
      </div>
    </div>

    <!-- Project Info -->
    <div class="space-y-4">
      <!-- Basic Info -->
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-ctp-surface1 rounded-lg p-4">
          <div class="text-2xl font-bold text-ctp-text">{{ scan.total_files.toLocaleString() }}</div>
          <div class="text-sm text-ctp-subtext1">Files</div>
        </div>
        <div class="bg-ctp-surface1 rounded-lg p-4">
          <div class="text-2xl font-bold text-ctp-text">{{ scan.total_directories.toLocaleString() }}</div>
          <div class="text-sm text-ctp-subtext1">Directories</div>
        </div>
      </div>

      <!-- Classification Result -->
      <div class="bg-ctp-surface1 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <h4 class="font-medium text-ctp-text">Project Classification</h4>
          <span 
            :class="[
              'px-2 py-1 text-xs rounded-full',
              getConfidenceColor(scan.final_classification.confidence)
            ]"
          >
            {{ Math.round(scan.final_classification.confidence * 100) }}% confident
          </span>
        </div>
        
        <div class="space-y-2">
          <div class="flex items-center space-x-2">
            <FolderTree class="w-4 h-4 text-ctp-blue" />
            <span class="font-medium text-ctp-text">{{ scan.final_classification.category }}</span>
          </div>
          
          <div class="text-sm text-ctp-subtext1">
            <strong>Method:</strong> {{ scan.final_classification.method }}
          </div>
          
          <div class="text-sm text-ctp-subtext1">
            <strong>Reasoning:</strong> {{ scan.final_classification.reasoning }}
          </div>
          
          <div v-if="scan.final_classification.suggested_name" class="text-sm text-ctp-subtext1">
            <strong>Suggested Name:</strong> {{ scan.final_classification.suggested_name }}
          </div>
        </div>
      </div>

      <!-- Key Files -->
      <div v-if="scan.key_files.length > 0" class="bg-ctp-surface1 rounded-lg p-4">
        <h4 class="font-medium text-ctp-text mb-3">Key Files Detected</h4>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="file in scan.key_files"
            :key="file"
            class="px-2 py-1 bg-ctp-surface2 text-ctp-text text-xs rounded-md"
          >
            {{ file }}
          </span>
        </div>
      </div>

      <!-- File Extensions -->
      <div class="bg-ctp-surface1 rounded-lg p-4">
        <h4 class="font-medium text-ctp-text mb-3">File Extensions</h4>
        <div class="space-y-2">
          <div
            v-for="[ext, count] in topExtensions"
            :key="ext"
            class="flex items-center justify-between"
          >
            <span class="text-sm text-ctp-subtext1">{{ ext || 'No extension' }}</span>
            <div class="flex items-center space-x-2">
              <div class="w-20 bg-ctp-surface2 rounded-full h-2">
                <div 
                  class="bg-ctp-blue h-2 rounded-full"
                  :style="{ width: `${(count / maxExtensionCount) * 100}%` }"
                ></div>
              </div>
              <span class="text-sm text-ctp-text w-8 text-right">{{ count }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="remainingExtensions > 0" class="text-xs text-ctp-subtext0 mt-2">
          And {{ remainingExtensions }} more...
        </div>
      </div>

      <!-- Scan Metadata -->
      <div class="text-xs text-ctp-subtext0 space-y-1">
        <div><strong>Scan ID:</strong> {{ scan.scan_id }}</div>
        <div><strong>Duration:</strong> {{ scan.scan_duration_ms }}ms</div>
        <div><strong>Path:</strong> {{ scan.path }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircle, FolderTree } from 'lucide-vue-next'
import type { ScanResponse } from '../../stores/appStore'

interface Props {
  scan: ScanResponse
}

const props = defineProps<Props>()
const emit = defineEmits<{
  organize: []
}>()

const topExtensions = computed(() => {
  const entries = Object.entries(props.scan.file_extensions)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
  return entries
})

const maxExtensionCount = computed(() => {
  return Math.max(...Object.values(props.scan.file_extensions))
})

const remainingExtensions = computed(() => {
  return Math.max(0, Object.keys(props.scan.file_extensions).length - 10)
})

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return 'bg-ctp-green text-ctp-base'
  if (confidence >= 0.6) return 'bg-ctp-yellow text-ctp-base'
  return 'bg-ctp-red text-ctp-base'
}
</script>