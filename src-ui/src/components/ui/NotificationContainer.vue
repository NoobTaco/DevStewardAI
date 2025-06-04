<template>
  <div class="fixed top-4 right-4 z-40 space-y-3 max-w-sm">
    <TransitionGroup name="notification" tag="div">
      <div
        v-for="notification in appStore.notifications"
        :key="notification.id"
        :class="[
          'p-4 rounded-lg shadow-lg border-l-4 animate-slide-in',
          notificationClasses[notification.type]
        ]"
      >
        <div class="flex items-start space-x-3">
          <!-- Icon -->
          <component 
            :is="notificationIcons[notification.type]" 
            class="w-5 h-5 mt-0.5 flex-shrink-0"
          />
          
          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium">
              {{ notification.message }}
            </p>
            <p class="text-xs opacity-75 mt-1">
              {{ formatTime(notification.timestamp) }}
            </p>
          </div>
          
          <!-- Close Button -->
          <button
            @click="appStore.removeNotification(notification.id)"
            class="flex-shrink-0 opacity-75 hover:opacity-100 transition-opacity"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { 
  CheckCircle, 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  X 
} from 'lucide-vue-next'
import { useAppStore } from '../../stores/appStore'

const appStore = useAppStore()

const notificationIcons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info
}

const notificationClasses = {
  success: 'bg-ctp-surface0 border-ctp-green text-ctp-text',
  error: 'bg-ctp-surface0 border-ctp-red text-ctp-text',
  warning: 'bg-ctp-surface0 border-ctp-yellow text-ctp-text',
  info: 'bg-ctp-surface0 border-ctp-blue text-ctp-text'
}

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}
</script>

<style scoped>
.notification-enter-active {
  transition: all 0.3s ease-out;
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>