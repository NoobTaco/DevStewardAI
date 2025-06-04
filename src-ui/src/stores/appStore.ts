import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { invoke } from '@tauri-apps/api/tauri'

// Types matching our Tauri/Rust backend
export interface HealthResponse {
  status: string
  timestamp: string
  version: string
  python_backend: boolean
  ollama_available: boolean
}

export interface ScanResponse {
  scan_id: string
  path: string
  total_files: number
  total_directories: number
  file_extensions: Record<string, number>
  key_files: string[]
  heuristic_classification: ClassificationResult
  ai_classification?: ClassificationResult
  final_classification: ClassificationResult
  scan_duration_ms: number
  timestamp: string
}

export interface ClassificationResult {
  category: string
  confidence: number
  reasoning: string
  method: string
  suggested_name?: string
}

export interface OrganizePreviewResponse {
  plan_id: string
  scan_id: string
  source_path: string
  target_path: string
  operations: OperationStep[]
  total_operations: number
  estimated_time_seconds: number
  total_files: number
  total_size_bytes: number
  conflicts_found: number
  safety_warnings: string[]
  timestamp: string
}

export interface OperationStep {
  operation_id: string
  operation_type: string
  source_path: string
  target_path: string
  estimated_time_seconds: number
  file_count: number
  total_size_bytes: number
  conflicts: string[]
  resolution: string
}

export interface ProcessStatus {
  is_running: boolean
  pid?: number
  port: number
  uptime_seconds?: number
  health_status?: string
}

export interface AppSettings {
  organization_root: string
  default_ai_model: string
  create_backup_by_default: boolean
  use_ai_by_default: boolean
  conflict_resolution_strategy: string
  ollama_base_url: string
  python_backend_port: number
  auto_start_backend: boolean
}

export interface OrganizeExecuteResponse {
  operation_id: string
  plan_id: string
  status: string
  message: string
  progress_url?: string
  rollback_manifest?: string
  timestamp: string
}

export const useAppStore = defineStore('app', () => {
  // State
  const isInitialized = ref(false)
  const backendStatus = ref<ProcessStatus | null>(null)
  const health = ref<HealthResponse | null>(null)
  const settings = ref<AppSettings | null>(null)
  const availableModels = ref<string[]>([])
  const currentScan = ref<ScanResponse | null>(null)
  const currentOrganizationPlan = ref<OrganizePreviewResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const notifications = ref<Array<{ id: string; type: 'info' | 'success' | 'warning' | 'error'; message: string; timestamp: Date }>>([])

  // Navigation state
  const currentView = ref<'organizer' | 'newProject' | 'settings'>('organizer')

  // Computed
  const isBackendHealthy = computed(() => {
    return health.value?.status === 'healthy' && health.value?.python_backend === true
  })

  const isOllamaAvailable = computed(() => {
    return health.value?.ollama_available === true
  })

  const canUseAI = computed(() => {
    return isBackendHealthy.value && isOllamaAvailable.value && availableModels.value.length > 0
  })

  // Actions
  const addNotification = (type: 'info' | 'success' | 'warning' | 'error', message: string) => {
    const notification = {
      id: Date.now().toString(),
      type,
      message,
      timestamp: new Date()
    }
    notifications.value.unshift(notification)
    
    // Auto-remove after 5 seconds for non-error notifications
    if (type !== 'error') {
      setTimeout(() => {
        removeNotification(notification.id)
      }, 5000)
    }
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearError = () => {
    error.value = null
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setCurrentView = (view: 'organizer' | 'newProject' | 'settings') => {
    currentView.value = view
    clearError()
  }

  // Backend interaction methods
  const initializeApp = async () => {
    if (isInitialized.value) return

    try {
      setLoading(true)
      
      // Load settings first
      await loadSettings()
      
      // Check backend status
      await checkBackendStatus()
      
      // If backend is not running and auto-start is enabled, try to start it
      if (!backendStatus.value?.is_running && settings.value?.auto_start_backend) {
        await startBackend()
      }
      
      // Check health
      await checkHealth()
      
      // Load available models if Ollama is available
      if (isOllamaAvailable.value) {
        await loadAvailableModels()
      }
      
      isInitialized.value = true
      addNotification('success', 'DevSteward AI initialized successfully')
      
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to initialize application'
      error.value = message
      addNotification('error', message)
    } finally {
      setLoading(false)
    }
  }

  const checkBackendStatus = async () => {
    try {
      const status = await invoke<ProcessStatus>('get_backend_status')
      backendStatus.value = status
    } catch (err) {
      console.warn('Failed to check backend status:', err)
      backendStatus.value = null
    }
  }

  const startBackend = async () => {
    try {
      setLoading(true)
      await invoke<string>('start_python_backend')
      await checkBackendStatus()
      addNotification('success', 'Python backend started successfully')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start backend'
      addNotification('error', message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const stopBackend = async () => {
    try {
      setLoading(true)
      await invoke<string>('stop_python_backend')
      await checkBackendStatus()
      health.value = null
      addNotification('info', 'Python backend stopped')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop backend'
      addNotification('error', message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const checkHealth = async () => {
    try {
      const healthResponse = await invoke<HealthResponse>('check_health')
      health.value = healthResponse
    } catch (err) {
      console.warn('Health check failed:', err)
      health.value = null
    }
  }

  const loadAvailableModels = async () => {
    try {
      const models = await invoke<string[]>('get_ollama_models')
      availableModels.value = models
    } catch (err) {
      console.warn('Failed to load Ollama models:', err)
      availableModels.value = []
    }
  }

  const loadSettings = async () => {
    try {
      const appSettings = await invoke<AppSettings>('get_app_settings')
      settings.value = appSettings
    } catch (err) {
      console.warn('Failed to load settings:', err)
      // Use default settings
      settings.value = {
        organization_root: '~/OrganizedProjects',
        default_ai_model: 'llama2',
        create_backup_by_default: true,
        use_ai_by_default: true,
        conflict_resolution_strategy: 'rename',
        ollama_base_url: 'http://localhost:11434',
        python_backend_port: 8008,
        auto_start_backend: true
      }
    }
  }

  const saveSettings = async (newSettings: AppSettings) => {
    try {
      setLoading(true)
      await invoke<string>('save_app_settings', { settings: newSettings })
      settings.value = newSettings
      addNotification('success', 'Settings saved successfully')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save settings'
      addNotification('error', message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const scanProject = async (path: string, useAI: boolean = true, aiModel?: string) => {
    try {
      setLoading(true)
      clearError()
      
      const scanResult = await invoke<ScanResponse>('scan_project_directory', {
        path,
        useAi: useAI,
        aiModel: aiModel || settings.value?.default_ai_model || 'llama2'
      })
      
      currentScan.value = scanResult
      addNotification('success', `Project scanned successfully: ${scanResult.final_classification.category}`)
      return scanResult
      
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to scan project'
      error.value = message
      addNotification('error', message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const previewOrganization = async (
    scanId: string,
    targetCategory?: string,
    conflictResolution?: string,
    createBackup?: boolean,
    customName?: string
  ) => {
    try {
      setLoading(true)
      clearError()
      
      const preview = await invoke<OrganizePreviewResponse>('preview_organization', {
        scanId,
        targetCategory,
        conflictResolution: conflictResolution || settings.value?.conflict_resolution_strategy || 'rename',
        createBackup: createBackup ?? settings.value?.create_backup_by_default ?? true,
        customName
      })
      
      currentOrganizationPlan.value = preview
      addNotification('success', `Organization plan generated: ${preview.total_operations} operations`)
      return preview
      
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate organization preview'
      error.value = message
      addNotification('error', message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const executeOrganization = async (planId: string) => {
    try {
      setLoading(true)
      clearError()
      
      const result = await invoke<OrganizeExecuteResponse>('execute_organization', {
        planId,
        confirmExecution: true
      })
      
      if (result.status === 'completed') {
        addNotification('success', 'Organization completed successfully!')
        // Clear current scan and plan after successful execution
        currentScan.value = null
        currentOrganizationPlan.value = null
      } else if (result.status === 'failed') {
        addNotification('error', `Organization failed: ${result.message}`)
      }
      
      return result
      
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to execute organization'
      error.value = message
      addNotification('error', message)
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const selectDirectory = async (): Promise<string | null> => {
    try {
      const result = await invoke<string | null>('select_directory')
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to select directory'
      addNotification('error', message)
      return null
    }
  }

  const getHomeDirectory = async (): Promise<string> => {
    try {
      const homeDir = await invoke<string>('get_home_directory')
      return homeDir
    } catch (err) {
      return '~'
    }
  }

  // Auto-refresh backend status and health
  const startAutoRefresh = () => {
    setInterval(async () => {
      if (isInitialized.value) {
        await checkBackendStatus()
        if (backendStatus.value?.is_running) {
          await checkHealth()
        }
      }
    }, 10000) // Every 10 seconds
  }

  // Watchers for reactive updates
  watch(isInitialized, (initialized) => {
    if (initialized) {
      startAutoRefresh()
    }
  })

  return {
    // State
    isInitialized,
    backendStatus,
    health,
    settings,
    availableModels,
    currentScan,
    currentOrganizationPlan,
    isLoading,
    error,
    notifications,
    currentView,
    
    // Computed
    isBackendHealthy,
    isOllamaAvailable,
    canUseAI,
    
    // Actions
    addNotification,
    removeNotification,
    clearError,
    setLoading,
    setCurrentView,
    initializeApp,
    checkBackendStatus,
    startBackend,
    stopBackend,
    checkHealth,
    loadAvailableModels,
    loadSettings,
    saveSettings,
    scanProject,
    previewOrganization,
    executeOrganization,
    selectDirectory,
    getHomeDirectory
  }
})