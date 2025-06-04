<template>
  <div class="fixed inset-0 bg-ctp-base bg-opacity-80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-ctp-surface0 rounded-lg shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-ctp-surface2">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-ctp-red rounded-full flex items-center justify-center">
            <AlertCircle class="w-6 h-6 text-ctp-base" />
          </div>
          <div>
            <h3 class="text-lg font-semibold text-ctp-text">Error Occurred</h3>
            <p class="text-sm text-ctp-subtext1">Something went wrong</p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="p-1 rounded-lg hover:bg-ctp-surface1 transition-colors"
        >
          <X class="w-5 h-5 text-ctp-subtext1" />
        </button>
      </div>
      
      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-60">
        <div class="space-y-4">
          <!-- Error Message -->
          <div class="bg-ctp-surface1 rounded-lg p-4">
            <p class="text-sm text-ctp-text leading-relaxed">
              {{ error }}
            </p>
          </div>
          
          <!-- Suggestions -->
          <div class="space-y-2">
            <h4 class="text-sm font-medium text-ctp-text">Suggested Actions:</h4>
            <ul class="text-sm text-ctp-subtext1 space-y-1">
              <li class="flex items-start space-x-2">
                <span class="text-ctp-blue">•</span>
                <span>Check that the Python backend is running</span>
              </li>
              <li class="flex items-start space-x-2">
                <span class="text-ctp-blue">•</span>
                <span>Verify your network connection</span>
              </li>
              <li class="flex items-start space-x-2">
                <span class="text-ctp-blue">•</span>
                <span>Try refreshing the application</span>
              </li>
              <li class="flex items-start space-x-2">
                <span class="text-ctp-blue">•</span>
                <span>Check application logs for more details</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="flex items-center justify-end space-x-3 p-6 border-t border-ctp-surface2">
        <button
          @click="copyError"
          class="px-4 py-2 text-sm bg-ctp-surface1 hover:bg-ctp-surface2 text-ctp-text rounded-lg transition-colors"
        >
          Copy Error
        </button>
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm bg-ctp-blue hover:bg-opacity-80 text-ctp-base rounded-lg transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AlertCircle, X } from 'lucide-vue-next'

interface Props {
  error: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const copyError = async () => {
  try {
    await navigator.clipboard.writeText(props.error)
    // Could add a notification here that it was copied
  } catch (err) {
    console.warn('Failed to copy error to clipboard:', err)
  }
}
</script>