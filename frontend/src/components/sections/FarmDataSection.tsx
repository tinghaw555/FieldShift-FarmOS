'use client'

import { useState, useEffect } from 'react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api'

interface FarmerObservation {
  id: number
  farm_id: number
  observation_date: string
  observation_time?: string
  temperature?: number
  humidity?: number
  rainfall?: number
  soil_moisture_raw?: number
  soil_moisture_percent?: number
  water_level?: string
  notes?: string
  data_source: string
  uploaded_at: string
  upload_method: string
  validation_status: string
}

interface CSVPreviewRow {
  row_number: number
  observation_date: string
  observation_time?: string
  temperature?: number
  humidity?: number
  rainfall?: number
  soil_moisture_raw?: number
  soil_moisture_percent?: number
  water_level?: string
  notes?: string
  validation_status: string
  validation_message?: string
}

interface CSVPreview {
  filename: string
  total_rows: number
  valid_rows: number
  warning_rows: number
  error_rows: number
  preview_rows: CSVPreviewRow[]
  columns_found: string[]
  columns_expected: string[]
}

export default function FarmDataSection({ farm }: { farm: any }) {
  const [observations, setObservations] = useState<FarmerObservation[]>([])
  const [observationCount, setObservationCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info', text: string } | null>(null)
  
  // Phase 3: Refresh state
  const [refreshing, setRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<any>(null)
  
  // Phase 3: Export state
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([])
  const [exportFormat, setExportFormat] = useState<'csv' | 'json'>('csv')
  const [exportMetadata, setExportMetadata] = useState<any>(null)
  
  // Phase 3.5: Scientific Results Export state
  const [showScientificExportDialog, setShowScientificExportDialog] = useState(false)
  const [scientificExportNote, setScientificExportNote] = useState<string>('')
  const [exportingScientific, setExportingScientific] = useState(false)
  
  // CSV Upload
  const [uploadingFile, setUploadingFile] = useState(false)
  const [csvPreview, setCsvPreview] = useState<CSVPreview | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  
  // Manual Entry
  const [showManualEntry, setShowManualEntry] = useState(false)
  const [manualForm, setManualForm] = useState({
    observation_date: new Date().toISOString().split('T')[0],
    observation_time: '',
    temperature: '',
    humidity: '',
    rainfall: '',
    soil_moisture_raw: '',
    soil_moisture_percent: '',
    water_level: '',
    notes: ''
  })
  
  // View Data
  const [showViewData, setShowViewData] = useState(false)

  useEffect(() => {
    if (farm?.id) {
      loadObservationCount()
    }
  }, [farm])

  const loadObservationCount = async () => {
    if (!farm?.id) return
    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/observations/count`)
      if (res.ok) {
        const data = await res.json()
        setObservationCount(data.observation_count)
      }
    } catch (error) {
      console.error('Error loading observation count:', error)
    }
  }

  const loadObservations = async () => {
    if (!farm?.id) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/observations?limit=100`)
      if (res.ok) {
        const data = await res.json()
        setObservations(data)
      } else {
        setMessage({ type: 'error', text: 'Failed to load observations' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error loading observations' })
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadTemplate = async () => {
    if (!farm?.id) {
      setMessage({ type: 'error', text: 'Please select a farm first' })
      return
    }

    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/template`)
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `fieldshift_observations_${farm.name.replace(/\s/g, '_')}.csv`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        setMessage({ type: 'success', text: 'CSV template downloaded successfully' })
      } else {
        setMessage({ type: 'error', text: 'Failed to download template' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error downloading template' })
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!farm?.id) {
      setMessage({ type: 'error', text: 'Please select a farm first' })
      return
    }

    setUploadingFile(true)
    setMessage(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/upload-preview`, {
        method: 'POST',
        body: formData
      })

      if (res.ok) {
        const preview = await res.json()
        setCsvPreview(preview)
        setShowPreview(true)
        setMessage({ type: 'info', text: `Preview: ${preview.valid_rows} valid, ${preview.warning_rows} warnings, ${preview.error_rows} errors` })
      } else {
        const error = await res.json()
        setMessage({ type: 'error', text: error.detail || 'Failed to preview CSV' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error uploading file' })
    } finally {
      setUploadingFile(false)
      event.target.value = ''
    }
  }

  const handleConfirmImport = async () => {
    if (!csvPreview || !farm?.id) return

    setLoading(true)
    setMessage(null)

    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farm_id: farm.id,
          rows: csvPreview.preview_rows
        })
      })

      if (res.ok) {
        const result = await res.json()
        setMessage({ type: 'success', text: result.import_summary })
        setShowPreview(false)
        setCsvPreview(null)
        loadObservationCount()
      } else {
        const error = await res.json()
        setMessage({ type: 'error', text: error.detail || 'Failed to import data' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error importing data' })
    } finally {
      setLoading(false)
    }
  }

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!farm?.id) return

    setLoading(true)
    setMessage(null)

    const payload = {
      farm_id: farm.id,
      observation_date: manualForm.observation_date,
      observation_time: manualForm.observation_time || null,
      temperature: manualForm.temperature ? parseFloat(manualForm.temperature) : null,
      humidity: manualForm.humidity ? parseFloat(manualForm.humidity) : null,
      rainfall: manualForm.rainfall ? parseFloat(manualForm.rainfall) : null,
      soil_moisture_raw: manualForm.soil_moisture_raw ? parseInt(manualForm.soil_moisture_raw) : null,
      soil_moisture_percent: manualForm.soil_moisture_percent ? parseFloat(manualForm.soil_moisture_percent) : null,
      water_level: manualForm.water_level || null,
      notes: manualForm.notes || null
    }

    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (res.ok) {
        setMessage({ type: 'success', text: 'Observation added successfully' })
        setShowManualEntry(false)
        setManualForm({
          observation_date: new Date().toISOString().split('T')[0],
          observation_time: '',
          temperature: '',
          humidity: '',
          rainfall: '',
          soil_moisture_raw: '',
          soil_moisture_percent: '',
          water_level: '',
          notes: ''
        })
        loadObservationCount()
      } else {
        const error = await res.json()
        setMessage({ type: 'error', text: error.detail || 'Failed to add observation' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error adding observation' })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteObservation = async (observationId: number) => {
    if (!farm?.id) return
    if (!confirm('Delete this observation? This cannot be undone.')) return

    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/observations/${observationId}`, {
        method: 'DELETE'
      })

      if (res.ok) {
        setMessage({ type: 'success', text: 'Observation deleted' })
        loadObservations()
        loadObservationCount()
      } else {
        setMessage({ type: 'error', text: 'Failed to delete observation' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error deleting observation' })
    }
  }

  // Phase 3: Refresh available data
  const handleRefreshData = async () => {
    if (!farm?.id) {
      setMessage({ type: 'error', text: 'Please select a farm first' })
      return
    }

    setRefreshing(true)
    setMessage(null)

    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/refresh`, {
        method: 'POST'
      })

      if (res.ok) {
        const result = await res.json()
        setLastRefresh(result)
        
        const messages = []
        if (result.nasa_power.status === 'success') {
          messages.push(`✅ NASA POWER: ${result.nasa_power.message}`)
        } else if (result.nasa_power.status === 'cached') {
          messages.push(`⚠️ NASA POWER: Using cached data`)
        } else {
          messages.push(`❌ NASA POWER: ${result.nasa_power.message}`)
        }
        
        if (result.open_meteo.status === 'success') {
          messages.push(`✅ Open-Meteo: ${result.open_meteo.message}`)
        } else {
          messages.push(`❌ Open-Meteo: ${result.open_meteo.message}`)
        }
        
        setMessage({ type: 'success', text: messages.join(' | ') })
      } else {
        const error = await res.json()
        setMessage({ type: 'error', text: error.detail || 'Failed to refresh data' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error refreshing data' })
    } finally {
      setRefreshing(false)
    }
  }

  // Phase 3: Load export metadata
  const handleOpenExport = async () => {
    if (!farm?.id) {
      setMessage({ type: 'error', text: 'Please select a farm first' })
      return
    }

    try {
      const res = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/export/metadata`)
      if (res.ok) {
        const metadata = await res.json()
        setExportMetadata(metadata)
        setShowExportDialog(true)
        
        // Auto-select available datasets
        const available = []
        if (metadata.datasets.nasa_power?.available) available.push('nasa_power')
        if (metadata.datasets.open_meteo?.available) available.push('open_meteo')
        if (metadata.datasets.farmer_observations?.available) available.push('farmer_observations')
        if (metadata.datasets.sensor_readings?.available) available.push('sensor_readings')
        if (metadata.datasets.rotations?.available) available.push('rotations')
        setSelectedDatasets(available)
      } else {
        setMessage({ type: 'error', text: 'Failed to load export metadata' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error loading export metadata' })
    }
  }

  // Phase 3: Export data
  const handleExport = async () => {
    if (!farm?.id || selectedDatasets.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one dataset' })
      return
    }

    try {
      const datasetsParam = selectedDatasets.join(',')
      const url = `${API_BASE_URL}/farm-data/${farm.id}/export/${exportFormat}?datasets=${datasetsParam}`
      
      const res = await fetch(url)
      if (res.ok) {
        const blob = await res.blob()
        const downloadUrl = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        
        if (exportFormat === 'csv' && selectedDatasets.length > 1) {
          a.download = `fieldshift_export_${farm.name.replace(/\s/g, '_')}.zip`
        } else if (exportFormat === 'csv') {
          a.download = `fieldshift_${selectedDatasets[0]}_${farm.name.replace(/\s/g, '_')}.csv`
        } else {
          a.download = `fieldshift_export_${farm.name.replace(/\s/g, '_')}.json`
        }
        
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(downloadUrl)
        
        setMessage({ type: 'success', text: `Exported ${selectedDatasets.length} dataset(s) successfully` })
        setShowExportDialog(false)
      } else {
        const error = await res.json()
        setMessage({ type: 'error', text: error.detail || 'Failed to export data' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error exporting data' })
    }
  }

  // Phase 3.5: Export Scientific Results
  const handleExportScientificResults = async () => {
    if (!farm?.id) {
      setMessage({ type: 'error', text: 'Please select a farm first' })
      return
    }

    setExportingScientific(true)
    setMessage(null)

    try {
      // Check localStorage for stored calculation results
      const plantingResult = localStorage.getItem(`planting_result_${farm.id}`)
      const rotationResult = localStorage.getItem(`rotation_result_${farm.id}`)
      const flippointResult = localStorage.getItem(`flippoint_result_${farm.id}`)
      const groundTruthResult = localStorage.getItem(`groundtruth_result_${farm.id}`)

      const hasAnyResults = plantingResult || rotationResult || flippointResult || groundTruthResult

      if (!hasAnyResults) {
        setMessage({ 
          type: 'error', 
          text: 'No calculated results found. Please run calculations in the dashboard sections first (Planting Suitability, Rotation Lab, FlipPoint, or Ground Truth).' 
        })
        setExportingScientific(false)
        return
      }

      // Prepare calculation parameters from stored results
      const calculations: any = {}

      if (plantingResult) {
        try {
          const result = JSON.parse(plantingResult)
          calculations.planting_suitability = {
            crop_name: result.crop_name,
            planting_date: result.planting_date,
            latitude: result.latitude,
            longitude: result.longitude
          }
        } catch (e) {
          console.error('Failed to parse planting result:', e)
        }
      }

      if (rotationResult) {
        try {
          const result = JSON.parse(rotationResult)
          if (result.results) {
            // This is a comparison result
            const rotations: any = {}
            for (const [rotType, rotData] of Object.entries(result.results)) {
              if (rotData && typeof rotData === 'object' && 'crop_results' in rotData) {
                rotations[rotType] = (rotData as any).crop_results?.map((c: any) => ({
                  crop: c.crop,
                  planting: c.planting_date?.substring(5) || '05-01',
                  harvest: c.harvest_date?.substring(5) || '10-15'
                })) || []
              }
            }
            if (Object.keys(rotations).length > 0) {
              calculations.rotation_comparison = {
                rotations,
                year: result.year || 2023,
                latitude: result.latitude,
                longitude: result.longitude
              }
            }
          } else if (result.crop_results) {
            // This is a single rotation calculation
            calculations.crop_water_balance = {
              crops: result.crop_results.map((c: any) => ({
                crop: c.crop,
                planting: c.planting_date?.substring(5) || '05-01',
                harvest: c.harvest_date?.substring(5) || '10-15'
              })),
              year: result.year || 2023,
              latitude: result.latitude,
              longitude: result.longitude
            }
          }
        } catch (e) {
          console.error('Failed to parse rotation result:', e)
        }
      }

      if (flippointResult) {
        try {
          const result = JSON.parse(flippointResult)
          if (result.data_points && result.data_points.length > 0) {
            // Extract rotations from the first data point
            const rotations: any = {}
            const firstPoint = result.data_points[0]
            if (firstPoint.stress_scores) {
              for (const rotType of Object.keys(firstPoint.stress_scores)) {
                rotations[rotType] = [] // We don't have the crop details, but the calculation will work
              }
            }
            
            calculations.flippoint = {
              rotations: rotations,
              parameter: result.parameter || 'irrigation_capacity',
              current_value: result.current_value_mm_week || 10,
              min_value: result.test_range?.min_mm_week || 0,
              max_value: result.test_range?.max_mm_week || 50,
              steps: result.test_range?.steps || 20,
              year: 2023,
              latitude: result.latitude,
              longitude: result.longitude
            }
          }
        } catch (e) {
          console.error('Failed to parse flippoint result:', e)
        }
      }

      if (Object.keys(calculations).length === 0) {
        setMessage({ 
          type: 'error', 
          text: 'Could not parse stored calculation results. Please re-run calculations and try again.' 
        })
        setExportingScientific(false)
        return
      }

      // Call backend export endpoint
      const response = await fetch(`${API_BASE_URL}/farm-data/${farm.id}/export/scientific-results`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          calculations,
          format: 'csv'
        })
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || 'Failed to export scientific results')
      }

      // Download the file
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `fieldshift_scientific_results_${farm.name.replace(/\s/g, '_')}_${new Date().toISOString().split('T')[0]}.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(downloadUrl)

      const calcTypes = Object.keys(calculations).join(', ')
      setMessage({ 
        type: 'success', 
        text: `Scientific results exported successfully! Included: ${calcTypes}` 
      })
      setShowScientificExportDialog(false)
    } catch (error: any) {
      console.error('Export error:', error)
      setMessage({ 
        type: 'error', 
        text: error.message || 'Failed to export scientific results. Please try again.' 
      })
    } finally {
      setExportingScientific(false)
    }
  }

  if (!farm) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-charcoal-900 mb-2">📊 My Farm Data & Analysis</h2>
        <p className="text-charcoal-600">Please select a farm to upload and manage your data.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-charcoal-900">📊 My Farm Data & Analysis</h2>
          <p className="text-sm text-charcoal-600 mt-1">
            Farm: <span className="font-semibold text-forest-700">{farm.name}</span>
            {observationCount > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-forest-100 text-forest-800 rounded text-xs">
                {observationCount} observations
              </span>
            )}
          </p>
        </div>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' :
          message.type === 'error' ? 'bg-red-50 text-red-800 border border-red-200' :
          'bg-blue-50 text-blue-800 border border-blue-200'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-sm">{message.text}</span>
            <button onClick={() => setMessage(null)} className="text-lg leading-none">&times;</button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <button
          onClick={handleDownloadTemplate}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-forest-600 text-white rounded-lg hover:bg-forest-700 transition-colors"
        >
          <span>⬇️</span>
          <span className="font-medium text-sm">Download CSV Template</span>
        </button>

        <label className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors cursor-pointer">
          <span>📤</span>
          <span className="font-medium text-sm">
            {uploadingFile ? 'Uploading...' : 'Upload My Data'}
          </span>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={uploadingFile}
            className="hidden"
          />
        </label>

        <button
          onClick={() => setShowManualEntry(!showManualEntry)}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
        >
          <span>✏️</span>
          <span className="font-medium text-sm">Add Measurement Manually</span>
        </button>

        <button
          onClick={() => {
            if (!showViewData) loadObservations()
            setShowViewData(!showViewData)
          }}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <span>👁️</span>
          <span className="font-medium text-sm">
            View My Data ({observationCount})
          </span>
        </button>
      </div>

      {/* Phase 3: Refresh and Export Buttons */}
      <div className="space-y-3 mb-6">
        <div className="grid md:grid-cols-3 gap-3">
          <button
            onClick={handleRefreshData}
            disabled={refreshing}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:bg-charcoal-300 disabled:cursor-not-allowed transition-colors"
          >
            <span>{refreshing ? '🔄' : '🔃'}</span>
            <span className="font-medium text-sm">
              {refreshing ? 'Refreshing...' : 'Refresh Available Data'}
            </span>
          </button>

          <button
            onClick={handleOpenExport}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <span>📦</span>
            <span className="font-medium text-sm">Export Raw Data</span>
          </button>

          <button
            onClick={handleExportScientificResults}
            disabled={exportingScientific}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-charcoal-300 disabled:cursor-not-allowed transition-colors"
          >
            <span>🔬</span>
            <span className="font-medium text-sm">
              {exportingScientific ? 'Exporting...' : 'Export Scientific Results'}
            </span>
          </button>
        </div>
        
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setShowScientificExportDialog(true)}
            className="text-sm text-emerald-600 hover:text-emerald-700 underline flex items-center gap-1"
          >
            <span>ℹ️</span>
            <span>Need help? Click here for guidance on scientific exports</span>
          </button>
        </div>
      </div>

      {/* Last Refresh Status */}
      {lastRefresh && (
        <div className="mb-6 p-4 bg-teal-50 border border-teal-200 rounded-lg text-sm">
          <div className="font-semibold text-teal-900 mb-2">Last Refresh: {new Date(lastRefresh.refreshed_at).toLocaleString()}</div>
          <div className="space-y-1 text-teal-800">
            {lastRefresh.nasa_power.status === 'success' && (
              <div>✅ <strong>NASA POWER</strong>: {lastRefresh.nasa_power.message} ({lastRefresh.nasa_power.date_range})</div>
            )}
            {lastRefresh.nasa_power.status === 'cached' && (
              <div>⚠️ <strong>NASA POWER</strong>: {lastRefresh.nasa_power.message}</div>
            )}
            {lastRefresh.nasa_power.status === 'error' && (
              <div>❌ <strong>NASA POWER</strong>: {lastRefresh.nasa_power.message}</div>
            )}
            
            {lastRefresh.open_meteo.status === 'success' && (
              <div>✅ <strong>Open-Meteo</strong>: {lastRefresh.open_meteo.message}</div>
            )}
            {lastRefresh.open_meteo.status === 'error' && (
              <div>❌ <strong>Open-Meteo</strong>: {lastRefresh.open_meteo.message}</div>
            )}
          </div>
        </div>
      )}

      {/* CSV Preview Modal */}
      {showPreview && csvPreview && (
        <div className="mb-6 border-2 border-blue-500 rounded-lg p-4 bg-blue-50">
          <h3 className="text-lg font-bold text-charcoal-900 mb-3">Preview: {csvPreview.filename}</h3>
          
          <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
            <div className="bg-green-100 border border-green-300 rounded p-2 text-center">
              <div className="font-bold text-green-800">{csvPreview.valid_rows}</div>
              <div className="text-green-700">Valid Rows</div>
            </div>
            <div className="bg-yellow-100 border border-yellow-300 rounded p-2 text-center">
              <div className="font-bold text-yellow-800">{csvPreview.warning_rows}</div>
              <div className="text-yellow-700">Warnings</div>
            </div>
            <div className="bg-red-100 border border-red-300 rounded p-2 text-center">
              <div className="font-bold text-red-800">{csvPreview.error_rows}</div>
              <div className="text-red-700">Errors</div>
            </div>
          </div>

          <div className="max-h-64 overflow-auto bg-white rounded border border-charcoal-200 mb-4">
            <table className="w-full text-xs">
              <thead className="bg-charcoal-100 sticky top-0">
                <tr>
                  <th className="px-2 py-1 text-left">#</th>
                  <th className="px-2 py-1 text-left">Date</th>
                  <th className="px-2 py-1 text-left">Temp</th>
                  <th className="px-2 py-1 text-left">Humid</th>
                  <th className="px-2 py-1 text-left">Rain</th>
                  <th className="px-2 py-1 text-left">Status</th>
                  <th className="px-2 py-1 text-left">Message</th>
                </tr>
              </thead>
              <tbody>
                {csvPreview.preview_rows.slice(0, 20).map((row) => (
                  <tr key={row.row_number} className={
                    row.validation_status === 'error' ? 'bg-red-50' :
                    row.validation_status === 'warning' ? 'bg-yellow-50' : ''
                  }>
                    <td className="px-2 py-1">{row.row_number}</td>
                    <td className="px-2 py-1">{row.observation_date}</td>
                    <td className="px-2 py-1">{row.temperature ?? '-'}</td>
                    <td className="px-2 py-1">{row.humidity ?? '-'}</td>
                    <td className="px-2 py-1">{row.rainfall ?? '-'}</td>
                    <td className="px-2 py-1">
                      <span className={`px-1 rounded text-xs ${
                        row.validation_status === 'valid' ? 'bg-green-200 text-green-800' :
                        row.validation_status === 'warning' ? 'bg-yellow-200 text-yellow-800' :
                        'bg-red-200 text-red-800'
                      }`}>
                        {row.validation_status}
                      </span>
                    </td>
                    <td className="px-2 py-1 text-xs">{row.validation_message || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleConfirmImport}
              disabled={loading || csvPreview.valid_rows === 0}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-charcoal-300 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Importing...' : `Import ${csvPreview.valid_rows} Valid Rows`}
            </button>
            <button
              onClick={() => {
                setShowPreview(false)
                setCsvPreview(null)
              }}
              className="px-4 py-2 bg-charcoal-500 text-white rounded-lg hover:bg-charcoal-600"
            >
              Cancel
            </button>
          </div>

          {csvPreview.error_rows > 0 && (
            <p className="text-xs text-red-700 mt-2">
              ⚠️ Rows with errors will be skipped during import
            </p>
          )}
        </div>
      )}

      {/* Manual Entry Form */}
      {showManualEntry && (
        <div className="mb-6 border-2 border-amber-500 rounded-lg p-4 bg-amber-50">
          <h3 className="text-lg font-bold text-charcoal-900 mb-3">Add Observation Manually</h3>
          <form onSubmit={handleManualSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Date (Required)
                </label>
                <input
                  type="date"
                  value={manualForm.observation_date}
                  onChange={(e) => setManualForm({ ...manualForm, observation_date: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Time (Optional)
                </label>
                <input
                  type="time"
                  value={manualForm.observation_time}
                  onChange={(e) => setManualForm({ ...manualForm, observation_time: e.target.value })}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Temperature (°C)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={manualForm.temperature}
                  onChange={(e) => setManualForm({ ...manualForm, temperature: e.target.value })}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  placeholder="22.5"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Humidity (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  value={manualForm.humidity}
                  onChange={(e) => setManualForm({ ...manualForm, humidity: e.target.value })}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  placeholder="65"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Rainfall (mm)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={manualForm.rainfall}
                  onChange={(e) => setManualForm({ ...manualForm, rainfall: e.target.value })}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  placeholder="5.2"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Soil Moisture (Raw ADC 0-4095)
                </label>
                <input
                  type="number"
                  min="0"
                  max="4095"
                  value={manualForm.soil_moisture_raw}
                  onChange={(e) => setManualForm({ ...manualForm, soil_moisture_raw: e.target.value })}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  placeholder="2450"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Soil Moisture (% Calibrated)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  value={manualForm.soil_moisture_percent}
                  onChange={(e) => setManualForm({ ...manualForm, soil_moisture_percent: e.target.value })}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  placeholder="45"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-1">
                  Water Level
                </label>
                <select
                  value={manualForm.water_level}
                  onChange={(e) => setManualForm({ ...manualForm, water_level: e.target.value })}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                >
                  <option value="">Select...</option>
                  <option value="OK">OK</option>
                  <option value="Low">Low</option>
                  <option value="Unknown">Unknown</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-charcoal-700 mb-1">
                Notes (Optional, max 1000 characters)
              </label>
              <textarea
                value={manualForm.notes}
                onChange={(e) => setManualForm({ ...manualForm, notes: e.target.value })}
                maxLength={1000}
                rows={3}
                className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                placeholder="Any observations, weather conditions, or notes..."
              />
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-charcoal-300 disabled:cursor-not-allowed font-medium"
              >
                {loading ? 'Saving...' : 'Save Observation'}
              </button>
              <button
                type="button"
                onClick={() => setShowManualEntry(false)}
                className="px-4 py-2 bg-charcoal-500 text-white rounded-lg hover:bg-charcoal-600"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* View Data Table */}
      {showViewData && (
        <div className="border-2 border-purple-500 rounded-lg p-4 bg-purple-50">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold text-charcoal-900">My Observations</h3>
            <button
              onClick={() => setShowViewData(false)}
              className="text-charcoal-600 hover:text-charcoal-800"
            >
              ✕ Close
            </button>
          </div>

          {loading ? (
            <p className="text-center py-8 text-charcoal-600">Loading observations...</p>
          ) : observations.length === 0 ? (
            <p className="text-center py-8 text-charcoal-600">
              No observations yet. Upload CSV or add manually.
            </p>
          ) : (
            <div className="max-h-96 overflow-auto bg-white rounded border border-charcoal-200">
              <table className="w-full text-sm">
                <thead className="bg-charcoal-100 sticky top-0">
                  <tr>
                    <th className="px-3 py-2 text-left">Date</th>
                    <th className="px-3 py-2 text-left">Time</th>
                    <th className="px-3 py-2 text-left">Temp (°C)</th>
                    <th className="px-3 py-2 text-left">Humid (%)</th>
                    <th className="px-3 py-2 text-left">Rain (mm)</th>
                    <th className="px-3 py-2 text-left">Soil Moisture</th>
                    <th className="px-3 py-2 text-left">Water</th>
                    <th className="px-3 py-2 text-left">Source</th>
                    <th className="px-3 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {observations.map((obs) => (
                    <tr key={obs.id} className="border-t border-charcoal-200 hover:bg-charcoal-50">
                      <td className="px-3 py-2">{obs.observation_date}</td>
                      <td className="px-3 py-2">{obs.observation_time || '-'}</td>
                      <td className="px-3 py-2">{obs.temperature?.toFixed(1) ?? '-'}</td>
                      <td className="px-3 py-2">{obs.humidity?.toFixed(0) ?? '-'}</td>
                      <td className="px-3 py-2">{obs.rainfall?.toFixed(1) ?? '-'}</td>
                      <td className="px-3 py-2">
                        {obs.soil_moisture_raw ? `${obs.soil_moisture_raw} (raw)` :
                         obs.soil_moisture_percent ? `${obs.soil_moisture_percent}%` : '-'}
                      </td>
                      <td className="px-3 py-2">{obs.water_level || '-'}</td>
                      <td className="px-3 py-2">
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs">
                          {obs.upload_method === 'csv' ? '📤 CSV' : '✏️ Manual'}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <button
                          onClick={() => handleDeleteObservation(obs.id)}
                          className="text-red-600 hover:text-red-800 text-xs"
                          title="Delete observation"
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {observations.length > 0 && (
            <p className="text-xs text-charcoal-600 mt-3">
              ℹ️ All data labeled as <span className="font-semibold text-blue-700">Farmer-Provided</span>. 
              Not claimed as NASA POWER or Real Sensor measurements.
            </p>
          )}
        </div>
      )}

      {/* Information Box */}
      <div className="mt-6 p-4 bg-forest-50 border border-forest-200 rounded-lg text-sm text-charcoal-700">
        <p className="font-semibold text-forest-800 mb-2">📌 About Your Data</p>
        <ul className="space-y-1 text-xs">
          <li>• All uploaded data is labeled as <strong>Farmer-Provided</strong> and kept separate from NASA POWER and real sensor data</li>
          <li>• Use the CSV template to ensure correct format and units</li>
          <li>• Leave measurements blank if not available (don't use 0 unless actually zero)</li>
          <li>• Your data remains private to your farm and is stored locally</li>
          <li>• Delete individual observations anytime if needed</li>
          <li>• <strong>Phase 3</strong>: Refresh data to get latest NASA POWER and Open-Meteo information</li>
          <li>• <strong>Phase 3</strong>: Export your analysis including all available datasets with clear source labels</li>
        </ul>
      </div>

      {/* Export Dialog */}
      {showExportDialog && exportMetadata && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-charcoal-900">Export Latest Analysis</h3>
                <button
                  onClick={() => setShowExportDialog(false)}
                  className="text-charcoal-600 hover:text-charcoal-800 text-2xl leading-none"
                >
                  &times;
                </button>
              </div>

              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
                <div><strong>Farm:</strong> {exportMetadata.farm_name}</div>
                <div><strong>Location:</strong> {exportMetadata.latitude}, {exportMetadata.longitude}</div>
                <div><strong>Export Time:</strong> {new Date(exportMetadata.export_generated_at).toLocaleString()}</div>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold text-charcoal-900 mb-2">Available Datasets</h4>
                <div className="space-y-2">
                  {Object.entries(exportMetadata.datasets).map(([key, data]: [string, any]) => (
                    <label
                      key={key}
                      className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                        data.available
                          ? selectedDatasets.includes(key)
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-charcoal-300 hover:border-indigo-300'
                          : 'border-charcoal-200 bg-charcoal-50 cursor-not-allowed opacity-60'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedDatasets.includes(key)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedDatasets([...selectedDatasets, key])
                          } else {
                            setSelectedDatasets(selectedDatasets.filter(d => d !== key))
                          }
                        }}
                        disabled={!data.available}
                        className="w-4 h-4"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-charcoal-900">
                          {key === 'nasa_power' && '🛰️ NASA POWER Climate Data'}
                          {key === 'open_meteo' && '🌦️ Open-Meteo Weather Forecast'}
                          {key === 'farmer_observations' && '👨‍🌾 Farmer-Provided Observations'}
                          {key === 'sensor_readings' && '📡 Sensor Readings'}
                          {key === 'rotations' && '🔄 Crop Rotations'}
                        </div>
                        {data.available ? (
                          <div className="text-xs text-charcoal-600">
                            {data.count} records
                            {data.date_range && ` • ${data.date_range}`}
                          </div>
                        ) : (
                          <div className="text-xs text-red-600">Not Available - Calculate or import data first</div>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold text-charcoal-900 mb-2">Export Format</h4>
                <div className="flex gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      value="csv"
                      checked={exportFormat === 'csv'}
                      onChange={() => setExportFormat('csv')}
                      className="w-4 h-4"
                    />
                    <span>CSV (Excel/Sheets)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      value="json"
                      checked={exportFormat === 'json'}
                      onChange={() => setExportFormat('json')}
                      className="w-4 h-4"
                    />
                    <span>JSON (Advanced)</span>
                  </label>
                </div>
                <p className="text-xs text-charcoal-600 mt-2">
                  {exportFormat === 'csv' && selectedDatasets.length > 1
                    ? '📦 Multiple CSVs will be bundled into a ZIP file with README'
                    : exportFormat === 'csv'
                    ? '📄 Single CSV file'
                    : '📋 JSON file with all selected datasets'}
                </p>
              </div>

              <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-xs">
                <strong className="text-yellow-900">Data Provenance & Scientific Results:</strong>
                <p className="text-yellow-800 mt-1">
                  All exports clearly label data sources (NASA POWER, Open-Meteo, Farmer-Provided, Real Sensor, Demo Mode, Calculated).
                  No API keys, passwords, or credentials are included. Farmer observations are never claimed as verified NASA or sensor data.
                </p>
                <p className="text-yellow-800 mt-2">
                  <strong>Note:</strong> Exports include raw data and rotation PLANS only. Scientific calculations (planting suitability,
                  crop water balance, FlipPoint thresholds) are calculated on-demand in the dashboard and not persisted/exported.
                  Run analyses in the dashboard sections to view results.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleExport}
                  disabled={selectedDatasets.length === 0}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-charcoal-300 disabled:cursor-not-allowed font-medium"
                >
                  Export {selectedDatasets.length} Dataset(s)
                </button>
                <button
                  onClick={() => setShowExportDialog(false)}
                  className="px-4 py-2 bg-charcoal-500 text-white rounded-lg hover:bg-charcoal-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scientific Results Export Help Dialog */}
      {showScientificExportDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-charcoal-900">ℹ️ Scientific Export - Help & Guidance</h3>
                <button
                  onClick={() => setShowScientificExportDialog(false)}
                  className="text-charcoal-400 hover:text-charcoal-600 text-2xl leading-none"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4 mb-6">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-bold text-blue-900 mb-2">🔬 How Scientific Export Works</h4>
                  <p className="text-sm text-blue-800 mb-3">
                    The <strong>"Export Scientific Results"</strong> button downloads calculated results that you've 
                    already run in the dashboard sections. It exports actual numerical values, not just guidance.
                  </p>
                  <div className="text-sm text-blue-900 space-y-2">
                    <div className="font-semibold">What Gets Exported:</div>
                    <ul className="list-disc list-inside space-y-1 ml-2">
                      <li>Planting suitability scores and recommendations</li>
                      <li>Crop water balance (ET0, ETc, irrigation needs)</li>
                      <li>Rotation comparison results and rankings</li>
                      <li>FlipPoint threshold calculations</li>
                      <li>Ground Truth accuracy metrics (when available)</li>
                    </ul>
                  </div>
                </div>

                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                  <h4 className="font-bold text-emerald-900 mb-2">📋 Workflow</h4>
                  <ol className="text-sm text-emerald-800 list-decimal list-inside space-y-2">
                    <li><strong>Run calculations</strong> in dashboard sections (Planting Suitability, Rotation Lab, FlipPoint, Ground Truth)</li>
                    <li><strong>View results</strong> on screen to verify they're correct</li>
                    <li><strong>Click "Export Scientific Results"</strong> button (🔬 emerald button above)</li>
                    <li><strong>Download ZIP file</strong> containing CSV files with your calculated results</li>
                    <li><strong>Open in Excel/Google Sheets</strong> to view numerical data</li>
                  </ol>
                </div>

                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                  <h4 className="font-bold text-amber-900 mb-2">⚠️ Important Notes</h4>
                  <ul className="text-sm text-amber-800 list-disc list-inside space-y-1">
                    <li>Export only includes calculations you've actually run in the current session</li>
                    <li>If you haven't run any calculations, you'll get an error message</li>
                    <li>Results are labeled as "MODEL CALCULATION" (not observed measurements)</li>
                    <li>Data sources (NASA POWER, FAO-56) are documented in exports</li>
                    <li>Each export includes calculation timestamp and input parameters</li>
                  </ul>
                </div>

                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <h4 className="font-bold text-purple-900 mb-2">📍 Where to Run Calculations</h4>
                  <ul className="text-sm text-purple-800 list-disc list-inside space-y-1">
                    <li><strong>Planting Suitability</strong> → "Check Planting Suitability" section → Select crop & date → Click "Check Suitability"</li>
                    <li><strong>Crop Water Balance</strong> → "Crop Rotation Lab" section → Create rotations → Click "Compare Rotations"</li>
                    <li><strong>FlipPoint Threshold</strong> → "FlipPoint & Agricultural Risk" section → Configure → Click "Calculate FlipPoint"</li>
                    <li><strong>Ground Truth Metrics</strong> → "Ground Truth & Evidence" section → Automatically calculated from observations</li>
                  </ul>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowScientificExportDialog(false)
                    setMessage({ 
                      type: 'info', 
                      text: 'Click the 🔬 "Export Scientific Results" button to download your calculated results.' 
                    })
                  }}
                  className="flex-1 px-4 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                >
                  ✓ Got It - Ready to Export
                </button>
                <button
                  onClick={() => setShowScientificExportDialog(false)}
                  className="px-4 py-3 bg-charcoal-500 text-white rounded-lg hover:bg-charcoal-600"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
