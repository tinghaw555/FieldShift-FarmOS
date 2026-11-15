'use client'

import { useState, useEffect } from 'react'
import { Cpu, Thermometer, Droplets, Gauge, Power, AlertTriangle, CheckCircle, Activity, Wifi, WifiOff, Loader2, Info, ChevronDown, ChevronUp } from 'lucide-react'
import { API_BASE } from '@/lib/config'

type DataMode = 'hardware' | 'preview' | 'offline'
type PumpState = 'off' | 'on' | 'starting' | 'stopping' | 'fault' | 'unknown'
type SystemStatus = 'online' | 'offline' | 'checking'

interface BackendSensorReading {
  timestamp: string
  sensors: {
    temperature?: { value: number; unit: string }
    humidity?: { value: number; unit: string }
    soil_moisture?: { value: number; unit: string }
    water_level?: { value: number; unit: string }
  }
}

export default function SmartFarmSection({ farm }: any) {
  const [dataMode, setDataMode] = useState<DataMode>('offline')
  const [systemStatus, setSystemStatus] = useState<SystemStatus>('checking')
  const [backendReadings, setBackendReadings] = useState<BackendSensorReading[]>([])
  const [currentReadingIndex, setCurrentReadingIndex] = useState(0)
  const [currentReading, setCurrentReading] = useState<BackendSensorReading | null>(null)
  const [datasetError, setDatasetError] = useState<string | null>(null)
  const [devices, setDevices] = useState<any[]>([])
  const [pumpStatus, setPumpStatus] = useState<any>(null)
  const [pumpLoading, setPumpLoading] = useState(false)
  const [showConfirmStart, setShowConfirmStart] = useState(false)
  const [showConfirmStop, setShowConfirmStop] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showDataSourceDetails, setShowDataSourceDetails] = useState(false)
  const [dataSource, setDataSource] = useState<string>('none')
  
  // Preview mode pump state (software-only, never touches hardware)
  const [previewPumpOn, setPreviewPumpOn] = useState(false)

  useEffect(() => {
    // Check system health immediately on mount
    checkSystemHealth()
    
    // Poll system health every 30 seconds (reasonable interval)
    const healthInterval = setInterval(() => {
      checkSystemHealth()
    }, 30000)
    
    return () => clearInterval(healthInterval)
  }, [])
  
  useEffect(() => {
    if (farm) {
      loadDevices()
      loadDataFromBackend()
      loadPumpStatus()
      
      // Poll for sensor data and pump status every 5 seconds
      const dataInterval = setInterval(() => {
        // Only poll latest if not in preview playback mode
        if (dataMode !== 'preview') {
          loadDataFromBackend()
        }
        loadPumpStatus()
      }, 5000)
      
      return () => clearInterval(dataInterval)
    }
  }, [farm])

  // Load sensor data from backend on mount
  useEffect(() => {
    if (farm) {
      loadBackendDataset()
    }
  }, [farm])
  
  // Auto-advance preview readings every 5 seconds
  useEffect(() => {
    if (dataMode !== 'preview' || backendReadings.length === 0) return
    
    const playbackInterval = setInterval(() => {
      setCurrentReadingIndex(prevIndex => {
        const nextIndex = (prevIndex + 1) % backendReadings.length
        setCurrentReading(backendReadings[nextIndex])
        return nextIndex
      })
    }, 5000) // Advance every 5 seconds
    
    return () => clearInterval(playbackInterval)
  }, [dataMode, backendReadings])
  
  // Check system health (backend availability)
  const checkSystemHealth = async () => {
    try {
      // Use AbortController for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
      
      // Health endpoint is at root, not /api
      const healthUrl = API_BASE.replace('/api', '')
      const response = await fetch(healthUrl, { 
        method: 'GET',
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (response.ok) {
        const data = await response.json()
        // Backend returns { status: "operational" }
        if (data.status === 'operational') {
          setSystemStatus('online')
        } else {
          setSystemStatus('offline')
        }
      } else {
        setSystemStatus('offline')
      }
    } catch (error) {
      // Network error or timeout
      setSystemStatus('offline')
    }
  }

  const loadBackendDataset = async () => {
    if (!farm) return
    
    try {
      const response = await fetch(`${API_BASE}/hardware/farm/${farm.id}/csv-readings`)
      if (!response.ok) {
        throw new Error('Failed to load sensor readings from backend')
      }
      
      const data = await response.json()
      
      if (data.status === 'success' && data.readings && data.readings.length > 0) {
        setBackendReadings(data.readings)
        setCurrentReadingIndex(0)
        setCurrentReading(data.readings[0])
        setDataSource(data.data_source || 'csv_demonstration')
        
        // Auto-enable preview mode
        setDataMode('preview')
        setDatasetError(null)
      } else {
        throw new Error('No sensor readings found')
      }
    } catch (err: any) {
      console.error('Failed to load backend dataset:', err)
      setDatasetError(err.message || 'Failed to load sensor readings')
      setBackendReadings([])
      setDataMode('offline')
    }
  }

  const loadDataFromBackend = async () => {
    if (!farm) return
    
    try {
      const response = await fetch(`${API_BASE}/hardware/farm/${farm.id}/latest`)
      if (!response.ok) {
        throw new Error('Failed to fetch latest readings')
      }
      
      const data = await response.json()
      
      if (data.status === 'current' || data.status === 'stale') {
        // Real hardware data
        setDataMode('hardware')
        setDataSource('hardware')
        // Convert to our format
        const reading: BackendSensorReading = {
          timestamp: data.latest_timestamp,
          sensors: {
            temperature: data.readings.temperature,
            humidity: data.readings.humidity,
            soil_moisture: data.readings.soil_moisture,
            water_level: data.readings.water_level
          }
        }
        setCurrentReading(reading)
      } else if (data.status === 'csv_demo') {
        // CSV demonstration data - don't override preview playback
        if (dataMode !== 'preview') {
          setDataMode('preview')
          setDataSource('csv_demonstration')
          const reading: BackendSensorReading = {
            timestamp: data.latest_timestamp,
            sensors: {
              temperature: data.readings.temperature,
              humidity: data.readings.humidity,
              soil_moisture: data.readings.soil_moisture,
              water_level: data.readings.water_level
            }
          }
          setCurrentReading(reading)
        }
      } else {
        // No data
        setDataMode('offline')
        setDataSource('none')
      }
    } catch (error) {
      console.error('Failed to load sensor data:', error)
      // Only set to offline if currently in hardware mode, preserve preview mode
      if (dataMode === 'hardware') {
        setDataMode('offline')
      }
    }
  }

  const loadDevices = async () => {
    if (!farm) return
    
    try {
      const response = await fetch(`${API_BASE}/hardware/farm/${farm.id}/devices`)
      if (response.ok) {
        const data = await response.json()
        setDevices(data)
      }
    } catch (error) {
      console.error('Failed to load devices:', error)
    }
  }

  const loadPumpStatus = async () => {
    if (!farm || devices.length === 0) return
    
    try {
      const deviceId = devices[0].device_id
      const response = await fetch(`${API_BASE}/hardware/pump/status/${deviceId}`)
      if (response.ok) {
        const status = await response.json()
        setPumpStatus(status)
      }
    } catch (error) {
      console.error('Failed to load pump status:', error)
    }
  }

  const handlePhysicalPumpToggle = async (turnOn: boolean) => {
    if (!devices[0]) {
      setError('No device connected')
      return
    }

    setPumpLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/hardware/pump/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: devices[0].device_id,
          farm_id: farm.id,
          action: turnOn ? 'start' : 'stop',
          duration_seconds: turnOn ? 10 : undefined
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `Failed to ${turnOn ? 'start' : 'stop'} pump`)
      }

      const result = await response.json()
      console.log(`Pump ${turnOn ? 'start' : 'stop'} command sent:`, result)
      setShowConfirmStart(false)
      setShowConfirmStop(false)
      
      setTimeout(() => loadPumpStatus(), 1000)
    } catch (err: any) {
      setError(err.message)
      console.error(`Pump ${turnOn ? 'start' : 'stop'} failed:`, err)
    } finally {
      setPumpLoading(false)
    }
  }

  const getSensorValue = (sensorType: string) => {
    if (!currentReading || !currentReading.sensors) return null
    
    const sensor = currentReading.sensors[sensorType as keyof typeof currentReading.sensors]
    return sensor?.value ?? null
  }
  
  const getSensorTimestamp = () => {
    if (!currentReading) return null
    
    if (dataMode === 'hardware') {
      return 'Just now'
    } else if (dataMode === 'preview') {
      const time = currentReading.timestamp.split(' ')[1] || ''
      return `Sample: ${time}`
    }
    return null
  }

  const getSystemStatusBadge = () => {
    if (systemStatus === 'online') {
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-sm font-semibold border border-green-300">
          <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse"></div>
          System Online
        </div>
      )
    } else if (systemStatus === 'checking') {
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-charcoal-100 text-charcoal-600 rounded-full text-sm font-medium">
          <Loader2 className="w-3 h-3 animate-spin" />
          Checking...
        </div>
      )
    } else {
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-sm font-semibold border border-red-300">
          <WifiOff className="w-3 h-3" />
          System Offline
        </div>
      )
    }
  }
  
  const getDataSourceDescription = () => {
    if (dataMode === 'hardware') {
      return {
        label: 'Connected',
        description: 'Receiving authenticated ESP32 telemetry from database',
        color: 'green',
        icon: Wifi
      }
    } else if (dataMode === 'preview') {
      // Determine if using farm-specific or shared demonstration data
      const isFarmSpecific = dataSource === 'farm_specific'
      const isSharedDemo = dataSource === 'shared_demonstration'
      
      if (isFarmSpecific) {
        return {
          label: 'Preview Mode — Farm Data',
          description: `Displaying ${farm.name}'s imported readings (${backendReadings.length} readings)`,
          color: 'blue',
          icon: Activity
        }
      } else if (isSharedDemo) {
        return {
          label: 'Preview Mode — Example Readings',
          description: `Displaying shared demonstration data (${backendReadings.length} example readings)`,
          color: 'purple',
          icon: Activity
        }
      } else {
        return {
          label: 'Preview Mode',
          description: `Displaying CSV demonstration data from database (${backendReadings.length} readings)`,
          color: 'blue',
          icon: Activity
        }
      }
    } else {
      return {
        label: 'Offline',
        description: 'No sensor data available',
        color: 'charcoal',
        icon: WifiOff
      }
    }
  }

  const getPumpStateDisplay = (state: PumpState) => {
    switch (state) {
      case 'on':
        return { label: 'ON', color: 'text-green-700', bgColor: 'bg-green-100', icon: CheckCircle }
      case 'starting':
        return { label: 'Starting...', color: 'text-yellow-700', bgColor: 'bg-yellow-100', icon: Loader2 }
      case 'stopping':
        return { label: 'Stopping...', color: 'text-yellow-700', bgColor: 'bg-yellow-100', icon: Loader2 }
      case 'off':
        return { label: 'OFF', color: 'text-charcoal-600', bgColor: 'bg-charcoal-100', icon: Power }
      case 'fault':
        return { label: 'FAULT', color: 'text-red-700', bgColor: 'bg-red-100', icon: AlertTriangle }
      default:
        return { label: 'Unknown', color: 'text-charcoal-500', bgColor: 'bg-charcoal-50', icon: AlertTriangle }
    }
  }

  if (!farm) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <Cpu className="w-12 h-12 text-charcoal-400 mx-auto mb-3" />
        <p className="text-charcoal-600">Select a farm to access Smart Farm monitoring</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-charcoal-900 flex items-center gap-2">
              <Cpu className="w-6 h-6 text-forest-600" />
              Smart Farm Monitoring
            </h2>
            <p className="text-charcoal-600 mt-1 text-sm">
              Sensor readings and irrigation control
            </p>
          </div>
          {getSystemStatusBadge()}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Sensor Readings */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-charcoal-900">Sensor Readings</h3>
            <button
              onClick={() => setShowDataSourceDetails(!showDataSourceDetails)}
              className="flex items-center gap-1 text-sm text-forest-600 hover:text-forest-700 font-medium"
            >
              <Info className="w-4 h-4" />
              Data Source
              {showDataSourceDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          </div>

          {/* Data Source Details Panel */}
          {showDataSourceDetails && (
            <div className="mb-4 p-4 bg-charcoal-50 border border-charcoal-300 rounded-lg">
              <div className="flex items-start gap-3">
                {(() => {
                  const source = getDataSourceDescription()
                  const Icon = source.icon
                  return (
                    <>
                      <Icon className={`w-5 h-5 mt-0.5 ${
                        source.color === 'green' ? 'text-green-600' :
                        source.color === 'blue' ? 'text-blue-600' :
                        source.color === 'purple' ? 'text-purple-600' :
                        'text-charcoal-500'
                      }`} />
                      <div className="flex-1">
                        <div className="font-semibold text-charcoal-900 mb-1">{source.label}</div>
                        <div className="text-sm text-charcoal-700 mb-3">{source.description}</div>
                        
                        {dataMode === 'preview' && backendReadings.length > 0 && (
                          <div className="text-xs text-charcoal-600 space-y-1 bg-white p-3 rounded border border-charcoal-200">
                            <div><strong>Dataset:</strong> {backendReadings.length} readings from database</div>
                            <div><strong>Current Reading:</strong> {currentReadingIndex + 1} of {backendReadings.length}</div>
                            <div><strong>Sample Time:</strong> {currentReading?.timestamp || 'N/A'}</div>
                            <div><strong>Data Source:</strong> {
                              dataSource === 'farm_specific' ? `${farm.name}'s Imported Data` :
                              dataSource === 'shared_demonstration' ? 'Shared Example Readings' :
                              dataSource === 'csv_demonstration' ? 'CSV Import' : 'Backend'
                            }</div>
                            <div><strong>Update Interval:</strong> Every 5 seconds</div>
                            <div className="pt-2 border-t border-charcoal-200 mt-2">
                              <strong>Note:</strong> {
                                dataSource === 'farm_specific' 
                                  ? `Preview data shows ${farm.name}'s imported measurements stored in database.`
                                  : dataSource === 'shared_demonstration'
                                  ? 'Example readings from shared demonstration dataset, not specific to this farm.'
                                  : 'Preview data is from CSV import stored in database, not live sensor measurements.'
                              }
                            </div>
                          </div>
                        )}
                        
                        {dataMode === 'hardware' && currentReading && (
                          <div className="text-xs text-charcoal-600 space-y-1 bg-white p-3 rounded border border-charcoal-200">
                            <div><strong>Device Status:</strong> Connected</div>
                            <div><strong>Last Update:</strong> Just now</div>
                            <div><strong>Telemetry:</strong> Authenticated ESP32</div>
                            {devices.length > 0 && (
                              <div><strong>Device ID:</strong> <span className="font-mono">{devices[0].device_id}</span></div>
                            )}
                          </div>
                        )}
                        
                        {dataMode === 'offline' && (
                          <div className="text-xs text-charcoal-600 bg-white p-3 rounded border border-charcoal-200">
                            No sensor data currently available. Connect an ESP32 device or check system status.
                          </div>
                        )}
                      </div>
                    </>
                  )
                })()}
              </div>
            </div>
          )}

          {dataMode === 'offline' ? (
            <div className="p-8 bg-charcoal-50 rounded-lg border border-charcoal-200 text-center">
              <WifiOff className="w-12 h-12 text-charcoal-400 mx-auto mb-3" />
              <p className="text-charcoal-700 font-medium mb-2">No Sensor Data Available</p>
              <p className="text-sm text-charcoal-600">
                {datasetError || 'Waiting for sensor connection...'}
              </p>
            </div>
          ) : (
            <>
              
              <div className="grid md:grid-cols-2 gap-4">
                {/* Air Temperature */}
                <div className="p-4 bg-gradient-to-br from-orange-50 to-red-50 rounded-lg border border-orange-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Thermometer className="w-5 h-5 text-orange-600" />
                    <span className="font-medium text-charcoal-900">Temperature</span>
                  </div>
                  <div className="text-3xl font-bold text-orange-700 mb-1">
                    {getSensorValue('temperature')?.toFixed(1) ?? '--'}°C
                  </div>
                  {getSensorTimestamp() && (
                    <div className="text-xs text-charcoal-500">{getSensorTimestamp()}</div>
                  )}
                </div>

                {/* Air Humidity */}
                <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Droplets className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-charcoal-900">Humidity</span>
                  </div>
                  <div className="text-3xl font-bold text-blue-700 mb-1">
                    {getSensorValue('humidity')?.toFixed(0) ?? '--'}%
                  </div>
                  {getSensorTimestamp() && (
                    <div className="text-xs text-charcoal-500">{getSensorTimestamp()}</div>
                  )}
                </div>

                {/* Soil Moisture */}
                <div className="p-4 bg-gradient-to-br from-emerald-50 to-green-50 rounded-lg border border-emerald-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Gauge className="w-5 h-5 text-emerald-600" />
                    <span className="font-medium text-charcoal-900">Soil Moisture</span>
                  </div>
                  <div className="text-3xl font-bold text-emerald-700 mb-1">
                    {getSensorValue('soil_moisture')?.toFixed(0) ?? '--'}%
                  </div>
                  {getSensorTimestamp() && (
                    <div className="text-xs text-charcoal-500">{getSensorTimestamp()}</div>
                  )}
                </div>

                {/* Water Level */}
                <div className="p-4 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-lg border border-cyan-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Droplets className="w-5 h-5 text-cyan-600" />
                    <span className="font-medium text-charcoal-900">Reservoir Level</span>
                  </div>
                  <div className="text-3xl font-bold text-cyan-700 mb-1">
                    {getSensorValue('water_level')?.toFixed(0) ?? '--'}%
                  </div>
                  {getSensorTimestamp() && (
                    <div className="text-xs text-charcoal-500">{getSensorTimestamp()}</div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Pump Control */}
        <div className="space-y-4">
          <h3 className="font-semibold text-charcoal-900">Water Pump Control</h3>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-300 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-red-900">{error}</div>
              </div>
            </div>
          )}

          {/* PREVIEW MODE PUMP SWITCH */}
          {dataMode === 'preview' ? (
            <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-300">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-charcoal-700">Pump Control</span>
                <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-bold ${
                  previewPumpOn ? 'bg-green-200 text-green-800' : 'bg-charcoal-200 text-charcoal-700'
                }`}>
                  <Power className="w-3.5 h-3.5" />
                  {previewPumpOn ? 'ON' : 'OFF'}
                </div>
              </div>

              {/* ON/OFF Toggle Switch */}
              <div className="flex items-center justify-center py-4">
                <button
                  onClick={() => setPreviewPumpOn(!previewPumpOn)}
                  className={`relative w-20 h-10 rounded-full transition-colors ${
                    previewPumpOn ? 'bg-green-500' : 'bg-charcoal-300'
                  }`}
                  aria-label={previewPumpOn ? 'Turn pump off' : 'Turn pump on'}
                >
                  <div className={`absolute top-1 ${previewPumpOn ? 'right-1' : 'left-1'} w-8 h-8 bg-white rounded-full shadow-md transition-all`}></div>
                  <span className={`absolute top-2.5 text-xs font-bold ${previewPumpOn ? 'left-2 text-white' : 'right-2 text-charcoal-700'}`}>
                    {previewPumpOn ? 'ON' : 'OFF'}
                  </span>
                </button>
              </div>

              <div className="text-center text-sm text-charcoal-700">
                <div className="font-medium">
                  {previewPumpOn ? 'Pump ON — Preview' : 'Pump OFF — Preview'}
                </div>
                <p className="text-xs text-charcoal-600 mt-1">
                  Software preview only - no hardware commands sent
                </p>
              </div>
            </div>
          ) : (
            /* PHYSICAL PUMP CONTROLS */
            <>
              {pumpStatus && pumpStatus.device_status !== 'offline' && devices.length > 0 ? (
                <>
                  <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border-2 border-green-200">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium text-charcoal-700">Physical Pump Status</span>
                      {(() => {
                        const display = getPumpStateDisplay(pumpStatus.pump_state)
                        const StateIcon = display.icon
                        return (
                          <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-bold ${display.bgColor} ${display.color}`}>
                            <StateIcon className={`w-3.5 h-3.5 ${display.label.includes('...') ? 'animate-spin' : ''}`} />
                            {display.label}
                          </div>
                        )
                      })()}
                    </div>

                    {/* ON/OFF Toggle Switch for Physical Pump */}
                    {!showConfirmStart && !showConfirmStop ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-center py-4">
                          <button
                            onClick={() => {
                              if (!pumpStatus.commissioned) {
                                setError('Pump not commissioned. Enable commissioning in firmware first.')
                                return
                              }
                              if (!pumpStatus.water_level_ok) {
                                setError('Cannot start: Reservoir level is low')
                                return
                              }
                              if (pumpStatus.device_status === 'offline') {
                                setError('Cannot start: Device is offline')
                                return
                              }
                              
                              if (pumpStatus.pump_state === 'off') {
                                setShowConfirmStart(true)
                                setError(null)
                              } else if (pumpStatus.pump_state === 'on') {
                                setShowConfirmStop(true)
                                setError(null)
                              }
                            }}
                            disabled={pumpLoading || pumpStatus.pump_state === 'starting' || pumpStatus.pump_state === 'stopping'}
                            className={`relative w-20 h-10 rounded-full transition-colors ${
                              pumpStatus.pump_state === 'on' ? 'bg-green-500' : 'bg-charcoal-300'
                            } ${(pumpLoading || pumpStatus.pump_state === 'starting' || pumpStatus.pump_state === 'stopping') ? 'opacity-50 cursor-not-allowed' : ''}`}
                          >
                            <div className={`absolute top-1 ${pumpStatus.pump_state === 'on' ? 'right-1' : 'left-1'} w-8 h-8 bg-white rounded-full shadow-md transition-all`}></div>
                            <span className={`absolute top-2.5 text-xs font-bold ${pumpStatus.pump_state === 'on' ? 'left-2 text-white' : 'right-2 text-charcoal-700'}`}>
                              {pumpStatus.pump_state === 'on' ? 'ON' : 'OFF'}
                            </span>
                          </button>
                        </div>

                        <div className="space-y-2 text-xs">
                          <div className="flex justify-between">
                            <span className="text-charcoal-600">Device</span>
                            <span className={`font-medium ${
                              pumpStatus.device_status === 'online' ? 'text-green-700' : 'text-yellow-700'
                            }`}>
                              {pumpStatus.device_status === 'online' ? '🟢 Online' : '🟡 Stale'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-charcoal-600">Reservoir</span>
                            <span className={`font-medium ${
                              pumpStatus.water_level_ok ? 'text-green-700' : 'text-red-700'
                            }`}>
                              {pumpStatus.water_level_ok ? '✓ OK' : '⚠️ Low'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-charcoal-600">Commissioned</span>
                            <span className={`font-medium ${
                              pumpStatus.commissioned ? 'text-green-700' : 'text-charcoal-500'
                            }`}>
                              {pumpStatus.commissioned ? 'Yes' : 'No'}
                            </span>
                          </div>
                        </div>
                      </div>
                    ) : showConfirmStart ? (
                      <div className="p-4 bg-amber-50 border-2 border-amber-400 rounded-lg">
                        <div className="text-sm font-semibold text-amber-900 mb-2">⚠️ Confirm Physical Pump Start</div>
                        <p className="text-xs text-amber-800 mb-3">
                          This will activate the physical water pump for 10 seconds. Ensure pump is properly connected, reservoir has water, and discharge hose is positioned correctly.
                        </p>
                        <div className="grid grid-cols-2 gap-2">
                          <button
                            onClick={() => {
                              setShowConfirmStart(false)
                              setError(null)
                            }}
                            className="px-3 py-2 bg-white border border-charcoal-300 text-charcoal-700 rounded-lg hover:bg-charcoal-50 text-sm font-medium"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handlePhysicalPumpToggle(true)}
                            disabled={pumpLoading}
                            className="px-3 py-2 bg-forest-600 text-white rounded-lg hover:bg-forest-700 text-sm font-medium flex items-center justify-center gap-2"
                          >
                            {pumpLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Power className="w-4 h-4" />}
                            {pumpLoading ? 'Starting...' : 'Confirm Start'}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 bg-amber-50 border-2 border-amber-400 rounded-lg">
                        <div className="text-sm font-semibold text-amber-900 mb-2">⚠️ Confirm Physical Pump Stop</div>
                        <p className="text-xs text-amber-800 mb-3">
                          This will stop the physical water pump immediately.
                        </p>
                        <div className="grid grid-cols-2 gap-2">
                          <button
                            onClick={() => {
                              setShowConfirmStop(false)
                              setError(null)
                            }}
                            className="px-3 py-2 bg-white border border-charcoal-300 text-charcoal-700 rounded-lg hover:bg-charcoal-50 text-sm font-medium"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handlePhysicalPumpToggle(false)}
                            disabled={pumpLoading}
                            className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium flex items-center justify-center gap-2"
                          >
                            {pumpLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Power className="w-4 h-4" />}
                            {pumpLoading ? 'Stopping...' : 'Confirm Stop'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {pumpStatus.last_update && (
                    <div className="text-xs text-charcoal-500">
                      Last updated: {new Date(pumpStatus.last_update).toLocaleTimeString()}
                    </div>
                  )}
                </>
              ) : (
                <div className="p-4 bg-amber-50 border border-amber-300 rounded-lg">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-amber-900">
                      <div className="font-semibold mb-1">Physical Pump Unavailable</div>
                      <p className="text-xs text-amber-800 mb-2">
                        Physical pump control requires a connected and commissioned ESP32 device.
                      </p>
                      <p className="text-xs text-amber-700">
                        {devices.length === 0 
                          ? 'No devices registered for this farm.'
                          : 'ESP32 offline or not commissioned. Check power and Wi-Fi connection.'
                        }
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {devices.length > 0 && (
            <div className="p-4 bg-charcoal-50 rounded-lg border border-charcoal-200">
              <div className="font-medium text-charcoal-900 mb-2 text-sm">Registered Devices</div>
              <div className="space-y-2">
                {devices.map((device, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="text-charcoal-700">{device.device_id}</span>
                    <span className={`px-2 py-0.5 rounded ${
                      device.status === 'online' ? 'bg-green-100 text-green-700' :
                      device.status === 'stale' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-charcoal-100 text-charcoal-600'
                    }`}>
                      {device.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
