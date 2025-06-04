<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-ctp-surface2">
      <h2 class="text-2xl font-bold text-ctp-text mb-2">Project Organizer</h2>
      <p class="text-ctp-subtext1">Scan and organize your development projects using AI-powered classification</p>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-hidden">
      <div class="h-full grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
        
        <!-- Left Panel: Project Scanner -->
        <div class="space-y-6">
          <ProjectScanner 
            @scan-complete="onScanComplete"
            :disabled="!appStore.isBackendHealthy"
          />
          
          <!-- Scan Results -->
          <ScanResults 
            v-if="appStore.currentScan"
            :scan="appStore.currentScan"
            @organize="onOrganizeRequest"
          />
        </div>

        <!-- Right Panel: Organization -->
        <div class="space-y-6">
          <!-- Organization Preview -->
          <OrganizationPreview
            v-if="appStore.currentOrganizationPlan"
            :plan="appStore.currentOrganizationPlan"
            @execute="onExecuteOrganization"
            @modify="onModifyPlan"
          />
          
          <!-- Organization Settings -->
          <OrganizationSettings
            v-else-if="appStore.currentScan"
            :scan="appStore.currentScan"
            @preview="onPreviewOrganization"
          />
          
          <!-- Getting Started -->
          <GettingStarted
            v-else
            :backend-healthy="appStore.isBackendHealthy"
            :ollama-available="appStore.isOllamaAvailable"
            @start-backend="appStore.startBackend"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '../stores/appStore'
import type { ScanResponse, OrganizePreviewResponse } from '../stores/appStore'

// Components
import ProjectScanner from '../components/organizer/ProjectScanner.vue'
import ScanResults from '../components/organizer/ScanResults.vue'
import OrganizationPreview from '../components/organizer/OrganizationPreview.vue'
import OrganizationSettings from '../components/organizer/OrganizationSettings.vue'
import GettingStarted from '../components/organizer/GettingStarted.vue'

const appStore = useAppStore()

const onScanComplete = (scan: ScanResponse) => {
  // Scan is automatically stored in the app store
  console.log('Scan completed:', scan)
}

const onOrganizeRequest = () => {
  // Scroll to organization settings
  // Could add smooth scrolling behavior here
}

const onPreviewOrganization = async (options: {
  targetCategory?: string
  conflictResolution?: string
  createBackup?: boolean
  customName?: string
}) => {
  if (!appStore.currentScan) return
  
  try {
    await appStore.previewOrganization(
      appStore.currentScan.scan_id,
      options.targetCategory,
      options.conflictResolution,
      options.createBackup,
      options.customName
    )
  } catch (error) {
    console.error('Failed to preview organization:', error)
  }
}

const onModifyPlan = () => {
  // Clear current plan to go back to settings
  appStore.currentOrganizationPlan = null
}

const onExecuteOrganization = async (planId: string) => {
  try {
    const result = await appStore.executeOrganization(planId)
    console.log('Organization executed:', result)
  } catch (error) {
    console.error('Failed to execute organization:', error)
  }
}
</script>