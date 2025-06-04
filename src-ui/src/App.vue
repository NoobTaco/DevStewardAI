<template>
  <div class="h-screen bg-ctp-base text-ctp-text flex flex-col overflow-hidden">
    <!-- Header -->
    <AppHeader />
    
    <!-- Main Content Area -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Navigation -->
      <AppSidebar />
      
      <!-- Main Content -->
      <main class="flex-1 overflow-hidden">
        <router-view />
      </main>
    </div>
    
    <!-- Global Loading Overlay -->
    <LoadingOverlay v-if="appStore.isLoading" />
    
    <!-- Notifications -->
    <NotificationContainer />
    
    <!-- Error Modal -->
    <ErrorModal 
      v-if="appStore.error" 
      :error="appStore.error" 
      @close="appStore.clearError" 
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from './stores/appStore'
import AppHeader from './components/layout/AppHeader.vue'
import AppSidebar from './components/layout/AppSidebar.vue'
import LoadingOverlay from './components/ui/LoadingOverlay.vue'
import NotificationContainer from './components/ui/NotificationContainer.vue'
import ErrorModal from './components/ui/ErrorModal.vue'

const appStore = useAppStore()

onMounted(async () => {
  await appStore.initializeApp()
})
</script>

<style>
/* Catppuccin Mocha Theme CSS Custom Properties */
:root {
  --ctp-rosewater: #f5e0dc;
  --ctp-flamingo: #f2cdcd;
  --ctp-pink: #f5c2e7;
  --ctp-mauve: #cba6f7;
  --ctp-red: #f38ba8;
  --ctp-maroon: #eba0ac;
  --ctp-peach: #fab387;
  --ctp-yellow: #f9e2af;
  --ctp-green: #a6e3a1;
  --ctp-teal: #94e2d5;
  --ctp-sky: #89dceb;
  --ctp-sapphire: #74c7ec;
  --ctp-blue: #89b4fa;
  --ctp-lavender: #b4befe;
  --ctp-text: #cdd6f4;
  --ctp-subtext1: #bac2de;
  --ctp-subtext0: #a6adc8;
  --ctp-overlay2: #9399b2;
  --ctp-overlay1: #7f849c;
  --ctp-overlay0: #6c7086;
  --ctp-surface2: #585b70;
  --ctp-surface1: #45475a;
  --ctp-surface0: #313244;
  --ctp-base: #1e1e2e;
  --ctp-mantle: #181825;
  --ctp-crust: #11111b;
}

/* Apply smooth transitions globally */
* {
  transition: all 0.2s ease-in-out;
}

/* Custom scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--ctp-surface0);
}

::-webkit-scrollbar-thumb {
  background: var(--ctp-overlay0);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--ctp-overlay1);
}

/* Focus styles for accessibility */
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 2px solid var(--ctp-blue);
  outline-offset: 2px;
}

/* Ensure proper text contrast */
.text-ctp-text {
  color: var(--ctp-text);
}

.bg-ctp-base {
  background-color: var(--ctp-base);
}

.bg-ctp-surface0 {
  background-color: var(--ctp-surface0);
}

.bg-ctp-surface1 {
  background-color: var(--ctp-surface1);
}

.border-ctp-surface2 {
  border-color: var(--ctp-surface2);
}

/* Animation keyframes */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>