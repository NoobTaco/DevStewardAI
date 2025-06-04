<template>
  <div class="bg-ctp-surface0 rounded-lg p-6">
    <div class="text-center space-y-6">
      <!-- Icon -->
      <div class="w-16 h-16 mx-auto bg-gradient-to-br from-ctp-blue to-ctp-mauve rounded-full flex items-center justify-center">
        <Sparkles class="w-8 h-8 text-ctp-base" />
      </div>
      
      <!-- Welcome Text -->
      <div>
        <h3 class="text-xl font-bold text-ctp-text mb-2">Welcome to DevSteward AI</h3>
        <p class="text-ctp-subtext1">
          Your AI-powered project organizer is ready to help you manage your development projects.
        </p>
      </div>

      <!-- Status Checks -->
      <div class="space-y-3">
        <!-- Backend Status -->
        <div class="flex items-center justify-between p-3 bg-ctp-surface1 rounded-lg">
          <div class="flex items-center space-x-3">
            <div :class="['w-3 h-3 rounded-full', backendHealthy ? 'bg-ctp-green' : 'bg-ctp-red']"></div>
            <span class="text-sm text-ctp-text">Python Backend</span>
          </div>
          <div class="text-sm">
            <span v-if="backendHealthy" class="text-ctp-green">Running</span>
            <button
              v-else
              @click="$emit('startBackend')"
              class="text-ctp-blue hover:text-ctp-sky"
            >
              Start Backend
            </button>
          </div>
        </div>

        <!-- AI Status -->
        <div class="flex items-center justify-between p-3 bg-ctp-surface1 rounded-lg">
          <div class="flex items-center space-x-3">
            <div :class="['w-3 h-3 rounded-full', ollamaAvailable ? 'bg-ctp-green' : 'bg-ctp-yellow']"></div>
            <span class="text-sm text-ctp-text">AI Models (Ollama)</span>
          </div>
          <span class="text-sm" :class="ollamaAvailable ? 'text-ctp-green' : 'text-ctp-yellow'">
            {{ ollamaAvailable ? 'Available' : 'Optional' }}
          </span>
        </div>
      </div>

      <!-- Getting Started Steps -->
      <div class="text-left space-y-4">
        <h4 class="font-medium text-ctp-text">How to get started:</h4>
        
        <div class="space-y-3">
          <div class="flex items-start space-x-3">
            <div class="w-6 h-6 bg-ctp-blue text-ctp-base rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              1
            </div>
            <div>
              <div class="text-sm font-medium text-ctp-text">Select a Project Directory</div>
              <div class="text-xs text-ctp-subtext1">Use the scanner on the left to choose a project folder</div>
            </div>
          </div>
          
          <div class="flex items-start space-x-3">
            <div class="w-6 h-6 bg-ctp-blue text-ctp-base rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              2
            </div>
            <div>
              <div class="text-sm font-medium text-ctp-text">AI Analysis & Classification</div>
              <div class="text-xs text-ctp-subtext1">Let AI determine the project type and best organization strategy</div>
            </div>
          </div>
          
          <div class="flex items-start space-x-3">
            <div class="w-6 h-6 bg-ctp-blue text-ctp-base rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              3
            </div>
            <div>
              <div class="text-sm font-medium text-ctp-text">Preview & Execute</div>
              <div class="text-xs text-ctp-subtext1">Review the organization plan and execute when ready</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Tips -->
      <div class="bg-ctp-surface1 rounded-lg p-4 text-left">
        <h4 class="font-medium text-ctp-text mb-2 flex items-center space-x-2">
          <Lightbulb class="w-4 h-4" />
          <span>Quick Tips</span>
        </h4>
        <ul class="text-sm text-ctp-subtext1 space-y-1">
          <li>• All operations are safe with automatic backup creation</li>
          <li>• You can preview organization plans before executing</li>
          <li>• AI classification works best with complete project structures</li>
          <li>• Rollback manifests are created for easy recovery</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sparkles, Lightbulb } from 'lucide-vue-next'

interface Props {
  backendHealthy: boolean
  ollamaAvailable: boolean
}

defineProps<Props>()
defineEmits<{
  startBackend: []
}>()
</script>