'use client'

import { useState, useEffect } from 'react'
import { Sliders, TrendingUp, AlertTriangle, Sun, Droplets, HelpCircle, Calculator, Loader2 } from 'lucide-react'
import { API_BASE } from '@/lib/config'

type WateringMethod = 'rainwater' | 'bucket' | 'pump' | 'not_sure' | 'advanced'

interface FlipPointResult {
  success: boolean
  current_preferred_rotation: string | null
  flippoint_threshold_mm_week: number | null
  flippoint_from: string | null
  flippoint_to: string | null
  has_flippoint: boolean
  rotations_analyzed: number
  explanation: string
  error?: string
}

export default function FlipPointSection({ farm }: any) {
  const [parameter, setParameter] = useState<'irrigation' | 'soil_taw' | 'stress_weight'>('irrigation')
  
  // Farmer-friendly irrigation inputs
  const [wateringMethod, setWateringMethod] = useState<WateringMethod>('not_sure')
  const [plotArea, setPlotArea] = useState<number>(1000) // m²
  const [plotAreaUnit, setPlotAreaUnit] = useState<'m2' | 'hectares'>('m2')
  const [bucketSize, setBucketSize] = useState<number>(10) // litres
  const [bucketsPerDay, setBucketsPerDay] = useState<number>(5)
  const [wateringDaysPerWeek, setWateringDaysPerWeek] = useState<number>(3)
  const [pumpFlowRate, setPumpFlowRate] = useState<number>(20) // litres/minute
  const [pumpMinutesPerDay, setPumpMinutesPerDay] = useState<number>(30)
  const [irrigationMethod, setIrrigationMethod] = useState<string>('surface') // Method type
  const [irrigationEfficiency, setIrrigationEfficiency] = useState<number>(55) // % (calculated from method)
  const [customEfficiency, setCustomEfficiency] = useState<number>(70) // % (for custom mode)
  
  // Advanced mode
  const [advancedIrrigationMm, setAdvancedIrrigationMm] = useState<number>(50)
  
  // Update irrigation efficiency when method changes
  useEffect(() => {
    if (irrigationMethod === 'surface') {
      setIrrigationEfficiency(55) // Manual/Surface: 50-60% typical
    } else if (irrigationMethod === 'sprinkler') {
      setIrrigationEfficiency(70) // Sprinkler: 65-75% typical
    } else if (irrigationMethod === 'drip') {
      setIrrigationEfficiency(90) // Drip: 85-95% typical
    } else if (irrigationMethod === 'custom') {
      setIrrigationEfficiency(customEfficiency)
    }
  }, [irrigationMethod, customEfficiency])
  
  // Calculated values
  const [calculatedIrrigationMm, setCalculatedIrrigationMm] = useState<number>(0)
  const [weeklyLitres, setWeeklyLitres] = useState<number>(0)
  
  // Other parameters
  const [soilTaw, setSoilTaw] = useState<number>(150) // mm
  const [stressWeight, setStressWeight] = useState<number>(50) // %
  
  // Show help modal
  const [showFlowMeasureHelp, setShowFlowMeasureHelp] = useState(false)
  
  // Backend integration state
  const [isUpdatingIrrigation, setIsUpdatingIrrigation] = useState(false)
  const [isCalculatingFlipPoint, setIsCalculatingFlipPoint] = useState(false)
  const [flipPointResult, setFlipPointResult] = useState<FlipPointResult | null>(null)
  const [lastCalculatedMm, setLastCalculatedMm] = useState<number | null>(null)
  const [flipPointError, setFlipPointError] = useState<string | null>(null)

  // Calculate irrigation capacity in mm/week from farmer inputs
  useEffect(() => {
    let weeklyLitresGross = 0
    let areaM2 = plotAreaUnit === 'hectares' ? plotArea * 10000 : plotArea

    if (wateringMethod === 'bucket') {
      // Weekly litres = bucket size × buckets/day × days/week
      weeklyLitresGross = bucketSize * bucketsPerDay * wateringDaysPerWeek
    } else if (wateringMethod === 'pump') {
      // Weekly litres = flow rate × minutes/day × days/week
      weeklyLitresGross = pumpFlowRate * pumpMinutesPerDay * wateringDaysPerWeek
    } else if (wateringMethod === 'advanced') {
      // Use advanced mm/week directly
      setCalculatedIrrigationMm(advancedIrrigationMm)
      setWeeklyLitres(advancedIrrigationMm * areaM2)
      return
    } else {
      // Rainwater only or not sure - 0 irrigation
      setCalculatedIrrigationMm(0)
      setWeeklyLitres(0)
      return
    }

    setWeeklyLitres(weeklyLitresGross)

    // Convert to mm/week applied to soil
    // Gross depth (mm) = litres / area (m²)
    const grossDepthMm = weeklyLitresGross / areaM2

    // Effective depth accounting for irrigation efficiency
    // Effective irrigation = gross × (efficiency / 100)
    const effectiveDepthMm = grossDepthMm * (irrigationEfficiency / 100)

    setCalculatedIrrigationMm(effectiveDepthMm)
  }, [wateringMethod, plotArea, plotAreaUnit, bucketSize, bucketsPerDay, 
      wateringDaysPerWeek, pumpFlowRate, pumpMinutesPerDay, irrigationEfficiency, advancedIrrigationMm])
  
  // Update backend when irrigation capacity changes
  useEffect(() => {
    if (!farm?.id) return
    
    // Only update if value actually changed
    if (lastCalculatedMm !== null && Math.abs(calculatedIrrigationMm - lastCalculatedMm) < 0.01) {
      return
    }
    
    const updateBackend = async () => {
      setIsUpdatingIrrigation(true)
      setFlipPointError(null)
      
      try {
        const areaM2 = plotAreaUnit === 'hectares' ? plotArea * 10000 : plotArea
        const irrigationMmDay = calculatedIrrigationMm / 7
        
        const response = await fetch(`${API_BASE}/farms/${farm.id}/irrigation`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            irrigation_mm_week: calculatedIrrigationMm,
            irrigation_mm_day: irrigationMmDay,
            source: wateringMethod === 'advanced' ? 'advanced' : 'calculated',
            method: wateringMethod,
            weekly_litres: weeklyLitres,
            plot_area_m2: areaM2,
            efficiency_percent: wateringMethod === 'bucket' || wateringMethod === 'pump' ? irrigationEfficiency : null
          })
        })
        
        if (!response.ok) {
          throw new Error('Failed to update irrigation capacity')
        }
        
        setLastCalculatedMm(calculatedIrrigationMm)
        
        // Mark FlipPoint results as stale
        if (flipPointResult && flipPointResult.success) {
          setFlipPointResult(null) // Clear stale results
        }
      } catch (error) {
        console.error('Error updating irrigation capacity:', error)
        setFlipPointError('Failed to update irrigation capacity')
      } finally {
        setIsUpdatingIrrigation(false)
      }
    }
    
    // Debounce updates
    const timer = setTimeout(updateBackend, 1000)
    return () => clearTimeout(timer)
  }, [calculatedIrrigationMm, farm?.id])
  
  // Function to calculate FlipPoint
  const calculateFlipPoint = async () => {
    if (!farm?.id || !farm?.latitude || !farm?.longitude) {
      setFlipPointError('Farm location required for FlipPoint analysis')
      return
    }
    
    if (wateringMethod === 'not_sure') {
      setFlipPointError('Please measure your water supply first')
      return
    }
    
    setIsCalculatingFlipPoint(true)
    setFlipPointError(null)
    
    try {
      // First, fetch rotations for this farm
      const rotationsResponse = await fetch(`${API_BASE}/rotations/farm/${farm.id}`)
      
      if (!rotationsResponse.ok) {
        throw new Error('Failed to fetch rotations')
      }
      
      const rotations = await rotationsResponse.json()
      
      if (!rotations || rotations.length < 2) {
        setFlipPointError(`${rotations?.length || 0} of 2 rotation plans configured. Create and save at least 2 rotations in the "Compare Crop Rotations" section above.`)
        setIsCalculatingFlipPoint(false)
        return
      }
      
      // Build rotation configs for FlipPoint API
      const rotationConfigs: any = {}
      
      for (const rotation of rotations) {
        const crops = rotation.crops.map((c: any) => ({
          crop: c.crop_name,
          planting: c.planting_date,
          harvest: c.harvest_date
        }))
        
        rotationConfigs[rotation.rotation_type] = crops
      }
      
      // Call FlipPoint endpoint
      const flipPointResponse = await fetch(`${API_BASE}/rotations/flippoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farm_id: farm.id,
          latitude: farm.latitude,
          longitude: farm.longitude,
          year: 2023,
          rotations: rotationConfigs,
          parameter: 'irrigation_capacity',
          current_value: calculatedIrrigationMm,
          min_value: 0,
          max_value: Math.max(100, calculatedIrrigationMm * 2),
          steps: 20
        })
      })
      
      if (!flipPointResponse.ok) {
        throw new Error('FlipPoint calculation failed')
      }
      
      const result = await flipPointResponse.json()
      setFlipPointResult(result)
      
      // Store result in localStorage for scientific export
      if (farm?.id) {
        localStorage.setItem(`flippoint_result_${farm.id}`, JSON.stringify(result))
      }
      
    } catch (error) {
      console.error('Error calculating FlipPoint:', error)
      setFlipPointError('Failed to calculate FlipPoint. Please try again.')
    } finally {
      setIsCalculatingFlipPoint(false)
    }
  }

  if (!farm) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <Sliders className="w-12 h-12 text-charcoal-400 mx-auto mb-3" />
        <p className="text-charcoal-600">Select a farm to perform FlipPoint analysis</p>
      </div>
    )
  }

  const getParameterInfo = () => {
    switch (parameter) {
      case 'irrigation':
        return {
          label: 'Water Supply',
          unit: 'mm/week',
          description: 'How much water reaches your crops each week',
          value: calculatedIrrigationMm
        }
      case 'soil_taw':
        return {
          label: 'Soil Water Capacity (TAW)',
          unit: 'mm',
          description: 'Total available water in soil profile',
          value: soilTaw
        }
      case 'stress_weight':
        return {
          label: 'Stress Minimization Priority',
          unit: '%',
          description: 'How much you prioritize avoiding water stress vs. other factors',
          value: stressWeight
        }
    }
  }

  const getWateringMethodLabel = (method: WateringMethod) => {
    switch (method) {
      case 'rainwater': return 'Rainwater Only'
      case 'bucket': return 'Bucket or Watering Can'
      case 'pump': return 'Pump or Irrigation System'
      case 'not_sure': return 'Not Sure / Not Measured'
      case 'advanced': return 'Advanced (mm/week)'
    }
  }

  const formatAreaDisplay = () => {
    if (plotAreaUnit === 'hectares') {
      return `${plotArea} hectares (${(plotArea * 10000).toLocaleString()} m²)`
    }
    return `${plotArea.toLocaleString()} m²`
  }

  const info = getParameterInfo()

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-charcoal-900 flex items-center gap-2">
          <Sliders className="w-6 h-6 text-forest-600" />
          What If Conditions Change?
        </h2>
        <p className="text-charcoal-600 mt-1">
          Understand how your water supply, soil, and priorities affect crop rotation decisions
        </p>
      </div>

      {parameter === 'irrigation' ? (
        /* FARMER-FRIENDLY IRRIGATION SETUP */
        <div className="space-y-6">
          {/* Plot Area */}
          <div className="p-5 bg-gradient-to-br from-emerald-50 to-green-50 rounded-lg border border-emerald-200">
            <h3 className="font-semibold text-charcoal-900 mb-4 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-emerald-600" />
              Your Field Area
            </h3>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-2">
                  Field Size
                </label>
                <input
                  type="number"
                  value={plotArea}
                  onChange={(e) => setPlotArea(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  min="0"
                  step="0.1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-charcoal-700 mb-2">
                  Unit
                </label>
                <select
                  value={plotAreaUnit}
                  onChange={(e) => setPlotAreaUnit(e.target.value as 'm2' | 'hectares')}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                >
                  <option value="m2">Square Meters (m²)</option>
                  <option value="hectares">Hectares (ha)</option>
                </select>
              </div>
            </div>
            
            <div className="mt-3 text-sm text-charcoal-600 bg-white p-3 rounded">
              <strong>Your field:</strong> {formatAreaDisplay()}
            </div>
          </div>

          {/* Watering Method Selection */}
          <div className="p-5 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-charcoal-900 mb-4 flex items-center gap-2">
              <Droplets className="w-5 h-5 text-blue-600" />
              How Do You Water Your Crops?
            </h3>
            
            <div className="grid md:grid-cols-2 gap-3">
              {(['rainwater', 'bucket', 'pump', 'not_sure', 'advanced'] as WateringMethod[]).map((method) => (
                <button
                  key={method}
                  onClick={() => setWateringMethod(method)}
                  className={`p-4 rounded-lg border-2 text-left transition-colors ${
                    wateringMethod === method
                      ? 'border-blue-500 bg-blue-50 text-blue-900'
                      : 'border-charcoal-200 bg-white hover:border-blue-300'
                  }`}
                >
                  <div className="font-medium">{getWateringMethodLabel(method)}</div>
                  <div className="text-xs text-charcoal-600 mt-1">
                    {method === 'rainwater' && 'Depend only on natural rainfall'}
                    {method === 'bucket' && 'Manual watering with buckets or cans'}
                    {method === 'pump' && 'Motorized pump or drip irrigation'}
                    {method === 'not_sure' && 'Haven\'t measured water supply yet'}
                    {method === 'advanced' && 'Enter scientific value (mm/week)'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Bucket/Can Inputs */}
          {wateringMethod === 'bucket' && (
            <div className="p-5 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-lg border border-cyan-200">
              <h3 className="font-semibold text-charcoal-900 mb-4">Bucket/Watering Can Details</h3>
              
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-charcoal-700 mb-2">
                    Bucket/Can Size (litres)
                  </label>
                  <input
                    type="number"
                    value={bucketSize}
                    onChange={(e) => setBucketSize(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                    min="0"
                    step="1"
                  />
                  <div className="text-xs text-charcoal-500 mt-1">Common: 10-20 litres</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-charcoal-700 mb-2">
                    Buckets Per Day
                  </label>
                  <input
                    type="number"
                    value={bucketsPerDay}
                    onChange={(e) => setBucketsPerDay(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                    min="0"
                    step="1"
                  />
                  <div className="text-xs text-charcoal-500 mt-1">Average per day</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-charcoal-700 mb-2">
                    Watering Days/Week
                  </label>
                  <input
                    type="number"
                    value={wateringDaysPerWeek}
                    onChange={(e) => setWateringDaysPerWeek(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                    min="0"
                    max="7"
                    step="1"
                  />
                  <div className="text-xs text-charcoal-500 mt-1">0-7 days</div>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-white rounded-lg border border-cyan-300">
                <div className="text-sm">
                  <strong>Weekly water:</strong> {(bucketSize * bucketsPerDay * wateringDaysPerWeek).toLocaleString()} litres
                </div>
              </div>
            </div>
          )}

          {/* Pump Inputs */}
          {wateringMethod === 'pump' && (
            <div className="p-5 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-charcoal-900">Pump System Details</h3>
                <button
                  onClick={() => setShowFlowMeasureHelp(true)}
                  className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                >
                  <HelpCircle className="w-4 h-4" />
                  How to measure flow?
                </button>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-charcoal-700 mb-2">
                    Flow Rate (litres/minute)
                  </label>
                  <input
                    type="number"
                    value={pumpFlowRate}
                    onChange={(e) => setPumpFlowRate(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                    min="0"
                    step="0.5"
                  />
                  <div className="text-xs text-charcoal-500 mt-1">Actual measured flow</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-charcoal-700 mb-2">
                    Minutes Per Day
                  </label>
                  <input
                    type="number"
                    value={pumpMinutesPerDay}
                    onChange={(e) => setPumpMinutesPerDay(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                    min="0"
                    step="5"
                  />
                  <div className="text-xs text-charcoal-500 mt-1">Daily runtime</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-charcoal-700 mb-2">
                    Watering Days/Week
                  </label>
                  <input
                    type="number"
                    value={wateringDaysPerWeek}
                    onChange={(e) => setWateringDaysPerWeek(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                    min="0"
                    max="7"
                    step="1"
                  />
                  <div className="text-xs text-charcoal-500 mt-1">0-7 days</div>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-white rounded-lg border border-purple-300">
                <div className="text-sm">
                  <strong>Weekly water:</strong> {(pumpFlowRate * pumpMinutesPerDay * wateringDaysPerWeek).toLocaleString()} litres
                </div>
              </div>
            </div>
          )}

          {/* Advanced Mode */}
          {wateringMethod === 'advanced' && (
            <div className="p-5 bg-gradient-to-br from-charcoal-50 to-slate-50 rounded-lg border border-charcoal-300">
              <h3 className="font-semibold text-charcoal-900 mb-4">Advanced: Scientific Value</h3>
              
              <div className="max-w-md">
                <label className="block text-sm font-medium text-charcoal-700 mb-2">
                  Effective Irrigation Depth (mm/week)
                </label>
                <input
                  type="number"
                  value={advancedIrrigationMm}
                  onChange={(e) => setAdvancedIrrigationMm(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  min="0"
                  step="1"
                />
                <div className="text-xs text-charcoal-500 mt-1">
                  This is the effective water reaching the root zone
                </div>
              </div>
            </div>
          )}

          {/* Irrigation Method */}
          {(wateringMethod === 'bucket' || wateringMethod === 'pump') && (
            <div className="p-5 bg-gradient-to-br from-amber-50 to-yellow-50 rounded-lg border border-amber-200">
              <h3 className="font-semibold text-charcoal-900 mb-3">Irrigation Method</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-charcoal-700 mb-2">
                  Select your irrigation method
                </label>
                <select
                  value={irrigationMethod}
                  onChange={(e) => setIrrigationMethod(e.target.value)}
                  className="w-full px-3 py-2 border border-charcoal-300 rounded-lg focus:ring-2 focus:ring-forest-500"
                >
                  <option value="surface">Manual / Surface Irrigation</option>
                  <option value="sprinkler">Sprinkler Irrigation</option>
                  <option value="drip">Drip Irrigation</option>
                  <option value="custom">Custom Efficiency</option>
                </select>
              </div>
              
              {irrigationMethod === 'custom' ? (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-charcoal-700 mb-2">
                    Custom Efficiency (%)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="98"
                    value={customEfficiency}
                    onChange={(e) => setCustomEfficiency(parseInt(e.target.value) || 70)}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                  />
                </div>
              ) : (
                <div className="p-3 bg-white rounded-lg border border-amber-300">
                  <div className="text-sm text-charcoal-700">
                    <strong>Assumed Efficiency:</strong> {irrigationEfficiency}%
                  </div>
                  <div className="text-xs text-charcoal-600 mt-1">
                    This is a model input assumption based on typical {
                      irrigationMethod === 'surface' ? 'manual/surface' :
                      irrigationMethod === 'sprinkler' ? 'sprinkler' :
                      'drip'
                    } irrigation performance (FAO guidelines).
                  </div>
                </div>
              )}
              
              <div className="text-xs text-charcoal-600 mt-3 space-y-1">
                <div><strong>Typical irrigation efficiencies:</strong></div>
                <div>• Manual/Surface: 50-60% (assumes runoff and evaporation)</div>
                <div>• Sprinkler: 65-75% (moderate control, some wind drift)</div>
                <div>• Drip: 85-95% (precise delivery, minimal loss)</div>
                <div className="pt-2 text-amber-800">
                  <strong>Note:</strong> Efficiency is estimated, not measured. Actual performance varies with soil, weather, and management practices.
                </div>
              </div>
            </div>
          )}

          {/* Calculated Result */}
          <div className="p-6 bg-gradient-to-r from-emerald-500 to-green-500 rounded-lg text-white">
            <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
              <Calculator className="w-6 h-6" />
              Your Water Supply
            </h3>
            
            {wateringMethod === 'not_sure' || wateringMethod === 'rainwater' ? (
              <div>
                <div className="text-3xl font-bold mb-2">
                  {wateringMethod === 'rainwater' ? 'Rainwater Only' : 'Not Yet Measured'}
                </div>
                <div className="text-sm text-emerald-50">
                  {wateringMethod === 'rainwater' 
                    ? 'Your crop rotation will depend entirely on rainfall'
                    : 'Enter your watering details above to see how much water you can provide'}
                </div>
              </div>
            ) : (
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <div className="text-emerald-100 text-sm">Weekly Water Volume</div>
                  <div className="text-3xl font-bold">{weeklyLitres.toLocaleString()}</div>
                  <div className="text-sm">litres/week</div>
                </div>
                
                <div>
                  <div className="text-emerald-100 text-sm">Effective Irrigation Depth</div>
                  <div className="text-3xl font-bold">{calculatedIrrigationMm.toFixed(1)}</div>
                  <div className="text-sm">mm/week</div>
                </div>
                
                <div>
                  <div className="text-emerald-100 text-sm">Water Per m²</div>
                  <div className="text-3xl font-bold">
                    {(weeklyLitres / (plotAreaUnit === 'hectares' ? plotArea * 10000 : plotArea)).toFixed(1)}
                  </div>
                  <div className="text-sm">litres/m²/week</div>
                </div>
              </div>
            )}
            
            {wateringMethod !== 'not_sure' && wateringMethod !== 'rainwater' && (
              <div className="mt-4 pt-4 border-t border-emerald-400 text-sm text-emerald-50">
                <div className="mb-2"><strong>What this means:</strong></div>
                <div>
                  Your current water supply can provide {calculatedIrrigationMm.toFixed(1)} mm of effective irrigation per week 
                  across your {formatAreaDisplay()}. This is {weeklyLitres.toLocaleString()} litres total per week.
                </div>
              </div>
            )}
          </div>

          {/* FlipPoint Result - Backend Connected */}
          <div className="p-6 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-300">
            {flipPointResult ? (
              /* Show calculated FlipPoint results */
              <div>
                <div className="flex items-start gap-4 mb-4">
                  <TrendingUp className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-semibold text-charcoal-900 text-lg mb-2">FlipPoint Analysis Results</div>
                    <div className="text-sm text-charcoal-700">
                      Based on NASA POWER climate data and FAO-56 crop water model
                    </div>
                  </div>
                </div>
                
                {flipPointResult.success ? (
                  <div className="space-y-4">
                    {/* Current Preferred Rotation */}
                    <div className="p-4 bg-white rounded-lg border border-blue-200">
                      <div className="font-medium text-charcoal-900 mb-1">At Your Current Water Supply:</div>
                      <div className="text-lg font-bold text-forest-700">
                        {flipPointResult.current_preferred_rotation ? 
                          flipPointResult.current_preferred_rotation.replace('_', ' ').toUpperCase() : 
                          'Unknown'}
                      </div>
                      <div className="text-sm text-charcoal-600 mt-1">
                        With {calculatedIrrigationMm.toFixed(1)} mm/week irrigation capacity
                      </div>
                    </div>
                    
                    {/* FlipPoint Threshold */}
                    {flipPointResult.has_flippoint && flipPointResult.flippoint_threshold_mm_week ? (
                      <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border-2 border-amber-400">
                        <div className="flex items-start gap-3">
                          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                          <div>
                            <div className="font-semibold text-charcoal-900 mb-2">FlipPoint Detected!</div>
                            <div className="text-sm text-charcoal-700 space-y-2">
                              <div>
                                <strong>Threshold:</strong> {flipPointResult.flippoint_threshold_mm_week.toFixed(1)} mm/week
                              </div>
                              <div>
                                When your irrigation capacity {calculatedIrrigationMm < (flipPointResult.flippoint_threshold_mm_week || 0) ? 'increases above' : 'decreases below'} this 
                                threshold, the optimal rotation switches from <strong>{flipPointResult.flippoint_from?.replace('_', ' ')}</strong> to{' '}
                                <strong>{flipPointResult.flippoint_to?.replace('_', ' ')}</strong>.
                              </div>
                              {wateringMethod === 'bucket' || wateringMethod === 'pump' ? (
                                <div className="mt-3 pt-3 border-t border-amber-300">
                                  <div className="font-medium mb-1">To reach this threshold, you would need:</div>
                                  <div className="font-bold text-lg text-amber-900">
                                    {((flipPointResult.flippoint_threshold_mm_week || 0) * (plotAreaUnit === 'hectares' ? plotArea * 10000 : plotArea)).toLocaleString()} litres/week
                                  </div>
                                  <div className="text-xs text-charcoal-600 mt-1">
                                    Across your {formatAreaDisplay()} at {irrigationEfficiency}% efficiency
                                  </div>
                                </div>
                              ) : null}
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-300">
                        <div className="font-medium text-charcoal-900 mb-1">No FlipPoint Detected</div>
                        <div className="text-sm text-charcoal-700">
                          Your preferred rotation (<strong>{flipPointResult.current_preferred_rotation?.replace('_', ' ')}</strong>) remains 
                          optimal across the tested irrigation range (0-{Math.max(100, calculatedIrrigationMm * 2).toFixed(0)} mm/week).
                          This means your rotation choice is stable and won't change with reasonable irrigation variations.
                        </div>
                      </div>
                    )}
                    
                    {/* Last Updated */}
                    <div className="text-xs text-charcoal-500 text-right">
                      Calculated just now • Based on {flipPointResult.rotations_analyzed || 0} rotations
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-red-50 rounded-lg border border-red-300">
                    <div className="font-medium text-red-900 mb-1">Calculation Error</div>
                    <div className="text-sm text-red-700">
                      {flipPointResult.error || 'Unable to calculate FlipPoint. Please check your rotation configurations.'}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* Show call-to-action to calculate */
              <div>
                <div className="flex items-start gap-4 mb-4">
                  <AlertTriangle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-semibold text-charcoal-900 mb-2">Ready to Calculate FlipPoint</div>
                    <div className="text-sm text-charcoal-700 space-y-2">
                      <p>
                        FlipPoint analysis will show you the water supply threshold where your optimal crop rotation changes.
                        This helps you understand how irrigation capacity affects your farming decisions.
                      </p>
                      {wateringMethod === 'not_sure' ? (
                        <div className="p-3 bg-amber-50 rounded border border-amber-300 text-amber-900">
                          Please measure your water supply first by selecting a watering method above.
                        </div>
                      ) : (
                        <div className="p-3 bg-blue-100 rounded text-sm">
                          <div className="font-medium mb-1">Requirements:</div>
                          <ul className="list-disc ml-5 space-y-1">
                            <li>At least 2 crop rotations configured (use "Compare Crop Rotations" section)</li>
                            <li>Farm location (GPS coordinates)</li>
                            <li>Water supply information (already provided: {calculatedIrrigationMm.toFixed(1)} mm/week)</li>
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-center mt-4">
                  <button
                    onClick={calculateFlipPoint}
                    disabled={isCalculatingFlipPoint || wateringMethod === 'not_sure'}
                    className="px-6 py-3 bg-forest-600 text-white rounded-lg hover:bg-forest-700 disabled:bg-charcoal-300 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
                  >
                    {isCalculatingFlipPoint ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Calculating FlipPoint...
                      </>
                    ) : (
                      <>
                        <Calculator className="w-5 h-5" />
                        Calculate FlipPoint Threshold
                      </>
                    )}
                  </button>
                </div>
                
                {flipPointError && (
                  <div className="mt-3 p-3 bg-red-50 rounded border border-red-300 text-sm text-red-700">
                    {flipPointError}
                  </div>
                )}
              </div>
            )}
            
            {/* Updating indicator */}
            {isUpdatingIrrigation && (
              <div className="mt-4 pt-4 border-t border-blue-200 flex items-center gap-2 text-sm text-blue-700">
                <Loader2 className="w-4 h-4 animate-spin" />
                Updating irrigation capacity in backend...
              </div>
            )}
          </div>
        </div>
      ) : (
        /* OTHER PARAMETERS (Soil TAW, Stress Weight) - Simplified */
        <div className="space-y-6">
          <div className="p-5 bg-gradient-to-br from-charcoal-50 to-forest-50 rounded-lg border border-charcoal-200">
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="font-medium text-charcoal-900">{info.label}</label>
                <span className="text-2xl font-bold text-forest-700">
                  {info.value.toFixed(0)} {info.unit}
                </span>
              </div>
              
              {parameter === 'soil_taw' ? (
                <div>
                  <input
                    type="range"
                    min="50"
                    max="250"
                    value={soilTaw}
                    onChange={(e) => setSoilTaw(parseInt(e.target.value))}
                    className="w-full h-2 bg-charcoal-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-charcoal-600 mt-1">
                    <span>50 mm (sandy soil)</span>
                    <span>250 mm (clay/loam)</span>
                  </div>
                  <div className="mt-3 text-sm text-charcoal-600">
                    <strong>Typical values:</strong> Sandy soil: 50-100 mm | Loam: 100-175 mm | Clay: 150-250 mm
                  </div>
                </div>
              ) : (
                <div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={stressWeight}
                    onChange={(e) => setStressWeight(parseInt(e.target.value))}
                    className="w-full h-2 bg-charcoal-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-charcoal-600 mt-1">
                    <span>0% (prioritize other factors)</span>
                    <span>100% (stress-avoidance only)</span>
                  </div>
                  <div className="mt-3 text-sm text-charcoal-600">
                    Higher values mean you prioritize avoiding water stress over crop diversity, market value, or other considerations.
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Placeholder */}
          <div className="p-6 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-300">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <div className="font-semibold text-charcoal-900 mb-2">Compare Crop Plans First</div>
                <div className="text-sm text-charcoal-700">
                  To see how {info.label.toLowerCase()} affects your rotation choice, first use the "Compare Crop Rotations" 
                  section to analyze different strategies with your current assumptions.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Flow Measurement Help Modal */}
      {showFlowMeasureHelp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
             onClick={() => setShowFlowMeasureHelp(false)}>
          <div className="bg-white rounded-lg max-w-2xl w-full p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-charcoal-900">How to Measure Pump Flow Rate</h3>
              <button
                onClick={() => setShowFlowMeasureHelp(false)}
                className="text-charcoal-500 hover:text-charcoal-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4 text-sm text-charcoal-700">
              <div>
                <strong className="text-charcoal-900">You'll need:</strong>
                <ul className="list-disc ml-5 mt-2">
                  <li>A large container or bucket (10-20 litres)</li>
                  <li>A stopwatch or phone timer</li>
                  <li>Measuring jug or marked container</li>
                </ul>
              </div>
              
              <div>
                <strong className="text-charcoal-900">Steps:</strong>
                <ol className="list-decimal ml-5 mt-2 space-y-2">
                  <li>Place your container under the pump discharge</li>
                  <li>Start the pump and timer simultaneously</li>
                  <li>Fill the container for exactly 1 minute</li>
                  <li>Stop the pump and measure the water volume</li>
                  <li>The volume in litres = your flow rate in litres/minute</li>
                </ol>
              </div>
              
              <div className="p-3 bg-amber-50 rounded border border-amber-200">
                <strong className="text-amber-900">Example:</strong>
                <div className="mt-1">
                  If you collect 15 litres in 1 minute, your flow rate is <strong>15 litres/minute</strong>.
                </div>
              </div>
              
              <div className="p-3 bg-blue-50 rounded border border-blue-200">
                <strong className="text-blue-900">Tips:</strong>
                <ul className="mt-1 space-y-1">
                  <li>• Repeat 2-3 times and average the results</li>
                  <li>• Use the actual measured flow, not the pump's rated capacity</li>
                  <li>• Account for any restrictions in your hoses or pipes</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-6 text-right">
              <button
                onClick={() => setShowFlowMeasureHelp(false)}
                className="px-4 py-2 bg-forest-600 text-white rounded-lg hover:bg-forest-700"
              >
                Got It
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
