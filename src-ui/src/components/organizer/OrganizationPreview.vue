<template>
  <div class="bg-ctp-surface0 rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-ctp-green rounded-lg flex items-center justify-center">
          <Eye class="w-5 h-5 text-ctp-base" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-ctp-text">Organization Preview</h3>
          <p class="text-sm text-ctp-subtext1">Review the organization plan before execution</p>
        </div>
      </div>
      
      <button
        @click="$emit('modify')"
        class="px-3 py-2 bg-ctp-surface1 hover:bg-ctp-surface2 text-ctp-text text-sm rounded-lg transition-colors"
      >
        Modify
      </button>
    </div>

    <!-- Plan Summary -->
    <div class="space-y-4 mb-6">
      <!-- Overview Cards -->
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-ctp-surface1 rounded-lg p-4">
          <div class="text-2xl font-bold text-ctp-text">{{ plan.total_operations }}</div>
          <div class="text-sm text-ctp-subtext1">Operations</div>
        </div>
        <div class="bg-ctp-surface1 rounded-lg p-4">
          <div class="text-2xl font-bold text-ctp-text">{{ formatTime(plan.estimated_time_seconds) }}</div>
          <div class="text-sm text-ctp-subtext1">Estimated Time</div>
        </div>
      </div>

      <!-- Target Information -->
      <div class="bg-ctp-surface1 rounded-lg p-4">
        <h4 class="font-medium text-ctp-text mb-2">Target Location</h4>
        <div class="space-y-1">
          <div class="text-sm text-ctp-subtext1">
            <strong>From:</strong> {{ plan.source_path }}
          </div>
          <div class="text-sm text-ctp-subtext1">
            <strong>To:</strong> {{ plan.target_path }}
          </div>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="plan.safety_warnings.length > 0" class="bg-ctp-yellow/10 border border-ctp-yellow rounded-lg p-4">
        <h4 class="font-medium text-ctp-text mb-2 flex items-center space-x-2">
          <AlertTriangle class="w-4 h-4 text-ctp-yellow" />
          <span>Safety Warnings</span>
        </h4>
        <ul class="text-sm text-ctp-text space-y-1">
          <li v-for="warning in plan.safety_warnings" :key="warning" class="flex items-start space-x-2">
            <span class="text-ctp-yellow">•</span>
            <span>{{ warning }}</span>
          </li>
        </ul>
      </div>

      <!-- Conflicts -->
      <div v-if="plan.conflicts_found > 0" class="bg-ctp-red/10 border border-ctp-red rounded-lg p-4">
        <h4 class="font-medium text-ctp-text mb-2 flex items-center space-x-2">
          <AlertCircle class="w-4 h-4 text-ctp-red" />
          <span>Conflicts Found</span>
        </h4>
        <p class="text-sm text-ctp-text">
          {{ plan.conflicts_found }} naming conflicts detected. These will be resolved according to your settings.
        </p>
      </div>
    </div>

    <!-- Operations List -->
    <div class="space-y-4 mb-6">
      <h4 class="font-medium text-ctp-text">Operations</h4>
      <div class="max-h-60 overflow-y-auto space-y-2">
        <div
          v-for="operation in plan.operations"
          :key="operation.operation_id"
          class="bg-ctp-surface1 rounded-lg p-3"
        >
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm font-medium text-ctp-text capitalize">
              {{ operation.operation_type.replace('_', ' ') }}
            </span>
            <span class="text-xs text-ctp-subtext1">
              {{ operation.file_count }} files • {{ formatBytes(operation.total_size_bytes) }}
            </span>
          </div>
          
          <div class="text-xs text-ctp-subtext1 space-y-1">
            <div><strong>From:</strong> {{ operation.source_path }}</div>
            <div><strong>To:</strong> {{ operation.target_path }}</div>
            
            <div v-if="operation.conflicts.length > 0" class="text-ctp-yellow">
              <strong>Conflicts:</strong> {{ operation.conflicts.join(', ') }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Execute Button -->
    <div class="space-y-3">
      <div class="flex items-center space-x-2 text-sm text-ctp-subtext1">
        <Shield class="w-4 h-4" />
        <span>This operation is safe and can be rolled back if needed</span>
      </div>
      
      <button
        @click="executeOrganization"
        :disabled="isExecuting"
        class="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-ctp-green hover:bg-opacity-80 disabled:bg-ctp-surface2 disabled:text-ctp-subtext0 text-ctp-base font-medium rounded-lg transition-colors"
      >
        <component :is="isExecuting ? LoaderIcon : Play" :class="['w-5 h-5', isExecuting && 'animate-spin']" />
        <span>{{ isExecuting ? 'Executing...' : 'Execute Organization' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  Eye, 
  Play, 
  Shield, 
  AlertTriangle, 
  AlertCircle,
  Loader2 as LoaderIcon
} from 'lucide-vue-next'
import type { OrganizePreviewResponse } from '../../stores/appStore'

interface Props {
  plan: OrganizePreviewResponse
}

const props = defineProps<Props>()
const emit = defineEmits<{
  execute: [planId: string]
  modify: []
}>()

const isExecuting = ref(false)

const formatTime = (seconds: number): string => {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`
  } else {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const executeOrganization = async () => {
  try {
    isExecuting.value = true
    emit('execute', props.plan.plan_id)
  } catch (error) {
    console.error('Failed to execute organization:', error)
  } finally {
    isExecuting.value = false
  }
}
</script>