<template>
  <div class="fixed inset-0 bg-ctp-base bg-opacity-80 backdrop-blur-sm z-50 flex items-center justify-center">
    <div class="bg-ctp-surface0 rounded-lg p-8 max-w-sm w-full mx-4 text-center shadow-2xl">
      <!-- Animated Logo -->
      <div class="relative mb-6">
        <div class="w-16 h-16 mx-auto bg-gradient-to-br from-ctp-blue to-ctp-mauve rounded-full flex items-center justify-center animate-pulse">
          <Bot class="w-8 h-8 text-ctp-base" />
        </div>
        <!-- Spinning Ring -->
        <div class="absolute inset-0 w-16 h-16 mx-auto border-4 border-transparent border-t-ctp-blue rounded-full animate-spin"></div>
      </div>
      
      <!-- Loading Text -->
      <div class="space-y-2">
        <h3 class="text-lg font-semibold text-ctp-text">Processing...</h3>
        <p class="text-sm text-ctp-subtext1">
          {{ loadingMessage }}
        </p>
      </div>
      
      <!-- Progress Dots -->
      <div class="flex justify-center space-x-1 mt-4">
        <div 
          v-for="i in 3" 
          :key="i"
          class="w-2 h-2 bg-ctp-blue rounded-full animate-pulse"
          :style="{ animationDelay: `${(i - 1) * 0.2}s` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Bot } from 'lucide-vue-next'

const loadingMessages = [
  'Initializing DevSteward AI...',
  'Connecting to backend...',
  'Scanning project structure...',
  'Analyzing project files...',
  'Running AI classification...',
  'Generating organization plan...',
  'Preparing file operations...',
  'Almost ready...'
]

const loadingMessage = ref(loadingMessages[0])
let messageInterval: number | null = null

onMounted(() => {
  let index = 0
  messageInterval = setInterval(() => {
    index = (index + 1) % loadingMessages.length
    loadingMessage.value = loadingMessages[index]
  }, 2000)
})

onUnmounted(() => {
  if (messageInterval) {
    clearInterval(messageInterval)
  }
})
</script>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%, 100% { 
    opacity: 1;
    transform: scale(1);
  }
  50% { 
    opacity: 0.5;
    transform: scale(0.95);
  }
}

.animate-pulse {
  animation: pulse 2s ease-in-out infinite;
}
</style>