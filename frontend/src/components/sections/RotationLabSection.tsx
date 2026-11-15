'use client'

import { useState, useEffect } from 'react'
import { Repeat, Droplets, AlertCircle, Plus, Loader2, CheckCircle, XCircle, TrendingUp } from 'lucide-react'
import { CROP_LIST } from '@/lib/config'
import { API_BASE } from '@/lib/config'

interface CropConfig {
  crop: string
  planting: string
  harvest: string
}

interface CalculationResult {
  success: boolean
  total_seasonal_water_demand_mm: number
  total_stress_days: number
  total_irrigation_need_mm: number
  crops_analyzed: number
  crop_results: any[]
  data_source: string
  assumptions: any
}

interface ComparisonResult {
  success: boolean
  results: {
    current?: any
    small_shift?: any
    alternative?: any
  }
  comparison: {
    preferred_rotation: string | null
    preferred_reason: string
  }
}

export default function RotationLabSection({ farm }: any) {
  const [rotationType, setRotationType] = useState<'current' | 'small_shift' | 'alternative'>('current')
  const [rotations, setRotations] = useState({
    current: [{ crop: 'corn', planting: '05-01', harvest: '10-15' }],
    small_shift: [{ crop: 'soybean', planting: '05-15', harvest: '10-01' }],
    alternative: [
      { crop: 'wheat', planting: '03-15', harvest: '07-30' },
      { crop: 'clover', planting: '08-01', harvest: '11-15' }
    ]
  })
  
  const [calculationResult, setCalculationResult] = useState<CalculationResult | null>(null)
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resultsStale, setResultsStale] = useState(false)
  const [savingRotations, setSavingRotations] = useState(false)
  const [savedRotationIds, setSavedRotationIds] = useState<{[key: string]: number}>({})
  const [loadingRotations, setLoadingRotations] = useState(false)

  // Mark results as stale when rotations change
  const handleRotationChange = (newRotations: typeof rotations) => {
    setRotations(newRotations)
    setResultsStale(true)
  }
  
  // Load existing rotations from backend on mount
  useEffect(() => {
    if (farm?.id) {
      loadSavedRotations()
    }
  }, [farm?.id])
  
  // Load saved rotations from backend
  const loadSavedRotations = async () => {
    if (!farm?.id) return
    
    setLoadingRotations(true)
    try {
      const response = await fetch(`${API_BASE}/rotations/farm/${farm.id}`)
      
      if (response.ok) {
        const savedRotations = await response.json()
        
        if (savedRotations && savedRotations.length > 0) {
          // Map backend rotations to frontend state
          const loadedRotations: any = {}
          const loadedIds: {[key: string]: number} = {}
          
          for (const rotation of savedRotations) {
            const rotType = rotation.rotation_type
            loadedIds[rotType] = rotation.id
            
            loadedRotations[rotType] = rotation.crops.map((c: any) => ({
              crop: c.crop_name,
              planting: c.planting_date,
              harvest: c.harvest_date
            }))
          }
          
          // Merge with defaults for missing rotation types
          setRotations({
            current: loadedRotations.current || [{ crop: 'corn', planting: '05-01', harvest: '10-15' }],
            small_shift: loadedRotations.small_shift || [{ crop: 'soybean', planting: '05-15', harvest: '10-01' }],
            alternative: loadedRotations.alternative || [
              { crop: 'wheat', planting: '03-15', harvest: '07-30' },
              { crop: 'clover', planting: '08-01', harvest: '11-15' }
            ]
          })
          setSavedRotationIds(loadedIds)
        }
      }
    } catch (err) {
      console.error('Failed to load rotations:', err)
    } finally {
      setLoadingRotations(false)
    }
  }
  
  // Save rotations to backend for FlipPoint to use
  const saveRotationsToBackend = async () => {
    if (!farm?.id) return
    
    setSavingRotations(true)
    try {
      const newSavedIds: {[key: string]: number} = {}
      
      for (const [rotType, crops] of Object.entries(rotations)) {
        // Delete existing rotation of this type for this farm
        if (savedRotationIds[rotType]) {
          try {
            await fetch(`${API_BASE}/rotations/${savedRotationIds[rotType]}`, {
              method: 'DELETE'
            })
          } catch (e) {
            console.log('Old rotation not found, creating new')
          }
        }
        
        // Create new rotation
        const rotationData = {
          farm_id: farm.id,
          rotation_type: rotType,
          name: `${rotType.replace('_', ' ').charAt(0).toUpperCase() + rotType.slice(1)} Rotation`,
          crops: crops.map((c, idx) => ({
            crop_name: c.crop,
            planting_date: c.planting,
            harvest_date: c.harvest,
            sequence_order: idx + 1
          }))
        }
        
        const response = await fetch(`${API_BASE}/rotations/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(rotationData)
        })
        
        if (response.ok) {
          const created = await response.json()
          newSavedIds[rotType] = created.id
        }
      }
      
      setSavedRotationIds(newSavedIds)
    } catch (err) {
      console.error('Failed to save rotations:', err)
      setError('Failed to save rotations to database')
    } finally {
      setSavingRotations(false)
    }
  }

  if (!farm) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <Repeat className="w-12 h-12 text-charcoal-400 mx-auto mb-3" />
        <p className="text-charcoal-600">Select a farm to analyze crop rotations</p>
      </div>
    )
  }

  const addCrop = (type: 'current' | 'small_shift' | 'alternative') => {
    const newRotations = {
      ...rotations,
      [type]: [...rotations[type], { crop: 'corn', planting: '05-01', harvest: '10-15' }]
    }
    handleRotationChange(newRotations)
  }

  const calculateWaterNeeds = async () => {
    setLoading(true)
    setError(null)
    setCalculationResult(null)
    
    try {
      const response = await fetch(`${API_BASE}/rotations/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farm_id: farm.id,
          latitude: farm.latitude,
          longitude: farm.longitude,
          year: 2023,
          crops: rotations[rotationType]
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Calculation failed: ${response.status}`)
      }
      
      const result = await response.json()
      setCalculationResult(result)
      setResultsStale(false)
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById('calculation-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
      
    } catch (err: any) {
      setError(err.message || 'Failed to calculate water needs')
    } finally {
      setLoading(false)
    }
  }

  const compareAllRotations = async () => {
    setLoading(true)
    setError(null)
    setComparisonResult(null)
    
    try {
      const response = await fetch(`${API_BASE}/rotations/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farm_id: farm.id,
          latitude: farm.latitude,
          longitude: farm.longitude,
          year: 2023,
          rotations: rotations
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Comparison failed: ${response.status}`)
      }
      
      const result = await response.json()
      setComparisonResult(result)
      setResultsStale(false)
      
      // Store result in localStorage for scientific export
      if (farm?.id) {
        localStorage.setItem(`rotation_result_${farm.id}`, JSON.stringify(result))
      }
      
      // Auto-save rotations to backend after successful comparison
      await saveRotationsToBackend()
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById('comparison-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
      
    } catch (err: any) {
      setError(err.message || 'Failed to compare rotations')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-charcoal-900 flex items-center gap-2">
          <Repeat className="w-6 h-6 text-forest-600" />
          Crop Rotation Planning
        </h2>
        <p className="text-charcoal-600 mt-1">
          Compare crop rotation strategies using historical climate data
        </p>
      </div>

      {/* Rotation Strategy Tabs */}
      <div className="flex gap-2 mb-6 border-b border-charcoal-200">
        {[
          { key: 'current', label: 'A: Current Rotation', color: 'blue' },
          { key: 'small_shift', label: 'B: Small Shift', color: 'emerald' },
          { key: 'alternative', label: 'C: Alternative', color: 'purple' }
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setRotationType(key as any)}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              rotationType === key
                ? 'border-forest-600 text-forest-700'
                : 'border-transparent text-charcoal-600 hover:text-charcoal-900'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Rotation Editor */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: Crop Configuration */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-charcoal-900">Configure Crops</h3>
            <button
              onClick={() => addCrop(rotationType)}
              className="flex items-center gap-1 text-sm text-forest-600 hover:text-forest-700"
            >
              <Plus className="w-4 h-4" />
              Add Crop
            </button>
          </div>
          
          {/* Saved Status Indicator */}
          {Object.keys(savedRotationIds).length > 0 && (
            <div className="p-2 bg-blue-50 border border-blue-200 rounded text-sm">
              <CheckCircle className="w-4 h-4 text-blue-600 inline mr-1" />
              <span className="text-blue-800 font-medium">
                {Object.keys(savedRotationIds).length} of 3 rotations saved to database
              </span>
            </div>
          )}

          <div className="space-y-3">
            {rotations[rotationType].map((crop, index) => (
              <div key={index} className="p-4 bg-charcoal-50 rounded-lg border border-charcoal-200">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-charcoal-700 mb-1">
                      Crop Type
                    </label>
                    <select
                      value={crop.crop}
                      onChange={(e) => {
                        const newRotations = { ...rotations }
                        newRotations[rotationType][index].crop = e.target.value
                        handleRotationChange(newRotations)
                      }}
                      className="w-full px-3 py-2 text-sm border border-charcoal-300 rounded-lg
                               focus:ring-2 focus:ring-forest-500 focus:border-transparent"
                    >
                      {CROP_LIST.map(cropName => (
                        <option key={cropName} value={cropName}>
                          {cropName.replace('_', ' ')}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs font-medium text-charcoal-700 mb-1">
                        Plant
                      </label>
                      <input
                        type="text"
                        value={crop.planting}
                        onChange={(e) => {
                          const newRotations = { ...rotations }
                          newRotations[rotationType][index].planting = e.target.value
                          handleRotationChange(newRotations)
                        }}
                        placeholder="MM-DD"
                        className="w-full px-2 py-2 text-sm border border-charcoal-300 rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-charcoal-700 mb-1">
                        Harvest
                      </label>
                      <input
                        type="text"
                        value={crop.harvest}
                        onChange={(e) => {
                          const newRotations = { ...rotations }
                          newRotations[rotationType][index].harvest = e.target.value
                          handleRotationChange(newRotations)
                        }}
                        placeholder="MM-DD"
                        className="w-full px-2 py-2 text-sm border border-charcoal-300 rounded-lg"
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-sm text-charcoal-600">
            {rotations[rotationType].length} crop(s) in rotation
          </div>
        </div>

        {/* Right: Analysis Status */}
        <div className="space-y-4">
          <h3 className="font-semibold text-charcoal-900">Analysis Status</h3>
          
          {!calculationResult && !comparisonResult && (
            <div className="p-6 bg-charcoal-50 rounded-lg border border-charcoal-200 text-center">
              <AlertCircle className="w-8 h-8 text-charcoal-400 mx-auto mb-2" />
              <p className="text-charcoal-600">Not calculated yet</p>
              <p className="text-xs text-charcoal-500 mt-1">
                Click "Calculate Water Needs" or "Compare 3 Crop Plans" below
              </p>
            </div>
          )}

          {calculationResult && (
            <div id="calculation-results" className="space-y-4">
              {resultsStale && (
                <div className="p-3 bg-amber-50 border border-amber-300 rounded-lg text-sm text-amber-800">
                  ⚠️ Results may be outdated - crops or dates have changed
                </div>
              )}
              
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start gap-3 mb-3">
                  <Droplets className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="font-medium text-charcoal-900 mb-1">
                      Estimated Seasonal Water Demand
                    </div>
                    <div className="text-3xl font-bold text-blue-700">
                      {calculationResult.total_seasonal_water_demand_mm.toFixed(0)} mm
                    </div>
                    <div className="text-xs text-charcoal-600 mt-1">
                      Data source: {calculationResult.data_source}
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-white rounded-lg border border-charcoal-200">
                  <div className="text-xs text-charcoal-600 mb-1">Estimated Water-Stress Days</div>
                  <div className="text-xl font-bold text-orange-600">
                    {calculationResult.total_stress_days} days
                  </div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-charcoal-200">
                  <div className="text-xs text-charcoal-600 mb-1">Possible Irrigation Need</div>
                  <div className="text-xl font-bold text-cyan-600">
                    {calculationResult.total_irrigation_need_mm.toFixed(0)} mm
                  </div>
                </div>
              </div>
            </div>
          )}

          {comparisonResult && (
            <div id="comparison-results" className="space-y-4">
              {resultsStale && (
                <div className="p-3 bg-amber-50 border border-amber-300 rounded-lg text-sm text-amber-800">
                  ⚠️ Results may be outdated - rotations have changed
                </div>
              )}
              
              <div className="p-4 bg-gradient-to-r from-forest-50 to-emerald-50 rounded-lg border-2 border-forest-300">
                <div className="flex items-start gap-3">
                  <TrendingUp className="w-6 h-6 text-forest-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="font-semibold text-forest-900 mb-2">Comparison Result</div>
                    <div className="text-lg font-bold text-forest-900 mb-1">
                      {comparisonResult.comparison.preferred_rotation 
                        ? `Preferred: ${comparisonResult.comparison.preferred_rotation.replace('_', ' ').toUpperCase()}`
                        : 'No clear preference'}
                    </div>
                    <div className="text-sm text-charcoal-700">
                      {comparisonResult.comparison.preferred_reason}
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                {['current', 'small_shift', 'alternative'].map(type => {
                  const result = comparisonResult.results[type as keyof typeof comparisonResult.results]
                  const isPreferred = comparisonResult.comparison.preferred_rotation === type
                  
                  return (
                    <div 
                      key={type}
                      className={`p-3 rounded-lg border ${
                        isPreferred 
                          ? 'bg-forest-50 border-forest-400 border-2' 
                          : 'bg-white border-charcoal-200'
                      }`}
                    >
                      <div className="text-xs font-semibold text-charcoal-900 mb-2 uppercase">
                        {type.replace('_', ' ')}
                      </div>
                      {result?.feasible ? (
                        <div className="space-y-1 text-xs">
                          <div className="text-charcoal-700">
                            Water: {result.total_seasonal_water_demand_mm?.toFixed(0) || 'N/A'} mm
                          </div>
                          <div className="text-charcoal-700">
                            Stress: {result.total_stress_days || 0} days
                          </div>
                          <div className="text-charcoal-700">
                            Irrigation: {result.total_irrigation_need_mm?.toFixed(0) || 0} mm
                          </div>
                        </div>
                      ) : (
                        <div className="text-xs text-red-600">Not feasible</div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border-2 border-red-300 rounded-lg">
          <div className="flex items-start gap-3">
            <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="font-semibold text-red-900">Error</div>
              <div className="text-sm text-red-800 mt-1">{error}</div>
            </div>
            <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">✕</button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-6 flex gap-3">
        <button
          onClick={calculateWaterNeeds}
          disabled={loading}
          className={`flex-1 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            loading
              ? 'bg-charcoal-300 text-charcoal-600 cursor-not-allowed'
              : 'bg-forest-600 text-white hover:bg-forest-700'
          }`}
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? 'Calculating...' : 'Calculate Water Needs'}
        </button>
        <button
          onClick={compareAllRotations}
          disabled={loading}
          className={`flex-1 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            loading
              ? 'bg-charcoal-300 text-charcoal-600 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          {loading ? 'Comparing...' : 'Compare 3 Crop Plans & Save'}
        </button>
        <button
          onClick={saveRotationsToBackend}
          disabled={savingRotations || loading}
          className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            savingRotations || loading
              ? 'bg-charcoal-300 text-charcoal-600 cursor-not-allowed'
              : 'bg-emerald-600 text-white hover:bg-emerald-700'
          }`}
        >
          {savingRotations && <Loader2 className="w-4 h-4 animate-spin" />}
          {savingRotations ? 'Saving...' : 'Save Rotations'}
        </button>
      </div>

      {/* Data Sources & Methodology */}
      <details className="mt-6">
        <summary className="cursor-pointer text-sm font-medium text-charcoal-700 hover:text-charcoal-900">
          Data Sources & Methodology
        </summary>
        <div className="mt-3 p-4 bg-charcoal-50 rounded-lg border border-charcoal-200 text-sm">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div className="font-semibold text-charcoal-900 mb-2">Climate Data</div>
              <ul className="space-y-1 text-charcoal-700 text-xs">
                <li><strong>NASA POWER</strong>: Daily meteorological data</li>
                <li>Coverage: Global (1981-present)</li>
                <li>Resolution: ~50 km gridded</li>
                <li>Variables: Temperature, precipitation, radiation, humidity, wind</li>
              </ul>
            </div>
            <div>
              <div className="font-semibold text-charcoal-900 mb-2">Crop Water Model</div>
              <ul className="space-y-1 text-charcoal-700 text-xs">
                <li><strong>FAO-56 Penman-Monteith</strong>: Reference ET₀</li>
                <li><strong>Crop coefficients</strong>: Kc values by growth stage</li>
                <li><strong>Water balance</strong>: Daily soil water accounting</li>
                <li><strong>Source</strong>: Allen et al. 1998, FAO Irrigation & Drainage Paper 56</li>
              </ul>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-charcoal-300 text-xs text-charcoal-600">
            <strong>Limitations:</strong> Values are estimates for comparative purposes only. 
            Actual water needs depend on local soil conditions, irrigation efficiency, crop varieties, 
            and management practices. See MODEL_LIMITATIONS.md for details.
          </div>
        </div>
      </details>
    </div>
  )
}
