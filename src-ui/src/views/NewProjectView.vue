<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-ctp-surface2">
      <h2 class="text-2xl font-bold text-ctp-text mb-2">New Project</h2>
      <p class="text-ctp-subtext1">Create new projects from pre-configured templates</p>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto p-6">
      <div class="max-w-4xl mx-auto">
        <!-- Coming Soon Message -->
        <div class="bg-ctp-surface0 rounded-lg p-8 text-center">
          <div class="w-16 h-16 mx-auto bg-ctp-yellow rounded-full flex items-center justify-center mb-4">
            <Plus class="w-8 h-8 text-ctp-base" />
          </div>
          
          <h3 class="text-xl font-bold text-ctp-text mb-2">Project Templates</h3>
          <p class="text-ctp-subtext1 mb-6">
            This feature will allow you to create new projects from curated templates.
          </p>
          
          <div class="bg-ctp-surface1 rounded-lg p-4 text-left max-w-md mx-auto">
            <h4 class="font-medium text-ctp-text mb-2">Planned Templates:</h4>
            <ul class="text-sm text-ctp-subtext1 space-y-1">
              <li>• Python CLI Utility</li>
              <li>• Static Website</li>
              <li>• Vue.js Application</li>
              <li>• Rust CLI Tool</li>
              <li>• Go Microservice</li>
              <li>• React Component Library</li>
            </ul>
          </div>
          
          <div class="mt-6 text-sm text-ctp-subtext0">
            This feature will be implemented in a future release.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Plus } from 'lucide-vue-next'
</script>