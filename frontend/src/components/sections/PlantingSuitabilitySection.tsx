'use client'

import { useState, useEffect } from 'react'
import { Calendar, Sprout, AlertTriangle, CheckCircle, Info, TrendingUp } from 'lucide-react'
import { API_BASE } from '@/lib/config'

interface PlantingSuitabilityProps {
  farm: any
}

export default function PlantingSuitabilitySection({ farm }: PlantingSuitabilityProps) {
  const [selectedCrop, setSelectedCrop] = useState<string>('')
  const [plantingDate, setPlantingDate] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [availableCrops, setAvailableCrops] = useState<any[]>([])

  useEffect(() => {
    // Load available crops from backend
    loadCrops()
  }, [])

  const loadCrops = async () => {
    try {
      const response = await fetch(`${API_BASE}/crops/list`)
      if (response.ok) {
        const crops = await response.json()
        setAvailableCrops(crops)
      }
    } catch (err) {
      console.error('Failed to load crops:', err)
    }
  }

  const handleCheckSuitability = async () => {
    if (!farm) {
      setError('Please select a farm first')
      return
    }

    if (!selectedCrop) {
      setError('Please select a crop to plant')
      return
    }

    if (!plantingDate) {
      setError('Please select a planting date')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/planting/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farm_id: farm.id,
          latitude: farm.latitude,
          longitude: farm.longitude,
          crop_name: selectedCrop,
          planting_date: plantingDate
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Assessment failed: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
      
      // Store result in localStorage for scientific export
      if (farm?.id) {
        localStorage.setItem(`planting_result_${farm.id}`, JSON.stringify(data))
      }
    } catch (err: any) {
      setError(err.message || 'Failed to assess planting suitability')
    } finally {
      setLoading(false)
    }
  }

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'recommended':
        return 'bg-green-50 border-green-500 text-green-900'
      case 'recommended_with_caution':
        return 'bg-yellow-50 border-yellow-500 text-yellow-900'
      case 'not_recommended':
        return 'bg-red-50 border-red-500 text-red-900'
      default:
        return 'bg-gray-50 border-gray-500 text-gray-900'
    }
  }

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case 'recommended':
        return <CheckCircle className="w-8 h-8 text-green-600" />
      case 'recommended_with_caution':
        return <AlertTriangle className="w-8 h-8 text-yellow-600" />
      case 'not_recommended':
        return <AlertTriangle className="w-8 h-8 text-red-600" />
      default:
        return <Info className="w-8 h-8 text-gray-600" />
    }
  }

  const getRecommendationLabel = (recommendation: string) => {
    switch (recommendation) {
      case 'recommended':
        return 'Recommended'
      case 'recommended_with_caution':
        return 'Recommended with Caution'
      case 'not_recommended':
        return 'Not Recommended'
      default:
        return 'Insufficient Data'
    }
  }

  if (!farm) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-charcoal-900 flex items-center gap-2 mb-4">
          <Sprout className="w-6 h-6 text-forest-600" />
          Check Planting Suitability
        </h2>
        <p className="text-charcoal-600">
          Please select a farm from the map above to check planting suitability.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-charcoal-900 flex items-center gap-2">
          <Sprout className="w-6 h-6 text-forest-600" />
          Check Planting Suitability
        </h2>
        <p className="text-charcoal-600 mt-1">
          Get science-based recommendations using NASA climate data
        </p>
      </div>

      {/* Input Form */}
      <div className="grid md:grid-cols-3 gap-4 mb-6">
        {/* Crop Selection */}
        <div>
          <label className="block text-sm font-medium text-charcoal-700 mb-2">
            What do you want to plant?
          </label>
          <select
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="w-full px-4 py-3 border border-charcoal-300 rounded-lg focus:ring-2 focus:ring-forest-500 focus:border-transparent"
            disabled={loading}
          >
            <option value="">Select a crop...</option>
            {availableCrops.map((crop) => (
              <option key={crop.key} value={crop.key}>
                {crop.name}
              </option>
            ))}
          </select>
        </div>

        {/* Planting Date */}
        <div>
          <label className="block text-sm font-medium text-charcoal-700 mb-2">
            When do you want to plant?
          </label>
          <div className="relative">
            <input
              type="date"
              value={plantingDate}
              onChange={(e) => setPlantingDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-3 border border-charcoal-300 rounded-lg focus:ring-2 focus:ring-forest-500 focus:border-transparent"
              disabled={loading}
            />
            <Calendar className="absolute right-3 top-3 w-5 h-5 text-charcoal-400 pointer-events-none" />
          </div>
        </div>

        {/* Check Button */}
        <div className="flex items-end">
          <button
            onClick={handleCheckSuitability}
            disabled={loading || !selectedCrop || !plantingDate}
            className={`w-full py-3 rounded-lg font-semibold transition-colors ${
              loading || !selectedCrop || !plantingDate
                ? 'bg-charcoal-300 text-charcoal-600 cursor-not-allowed'
                : 'bg-forest-600 text-white hover:bg-forest-700'
            }`}
          >
            {loading ? 'Analyzing...' : 'Check Planting Suitability'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-2 border-red-300 text-red-900 px-4 py-3 rounded-lg mb-6">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
            <div className="flex-1">
              <div className="font-semibold">Error</div>
              <div className="text-sm mt-1">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Main Recommendation */}
          <div className={`border-2 rounded-lg p-6 ${getRecommendationColor(result.recommendation)}`}>
            <div className="flex items-start gap-4">
              {getRecommendationIcon(result.recommendation)}
              <div className="flex-1">
                <h3 className="text-2xl font-bold mb-2">
                  {getRecommendationLabel(result.recommendation)}
                </h3>
                <p className="text-lg mb-4">{result.main_reason}</p>
                
                {/* Farm Context */}
                <div className="text-sm opacity-90">
                  <strong>Farm:</strong> {farm.name} ({farm.latitude.toFixed(4)}°, {farm.longitude.toFixed(4)}°)
                  <br />
                  <strong>Crop:</strong> {result.crop_name}
                  <br />
                  <strong>Planting Date:</strong> {new Date(plantingDate).toLocaleDateString()}
                </div>
              </div>
            </div>
          </div>

          {/* Climate Evidence */}
          {result.climate_evidence && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-charcoal-900 mb-2 flex items-center gap-2">
                <Info className="w-5 h-5 text-blue-600" />
                Climate & Water Evidence
              </h4>
              <div className="text-sm text-charcoal-700 space-y-1">
                {result.climate_evidence.map((item: string, idx: number) => (
                  <div key={idx}>• {item}</div>
                ))}
              </div>
            </div>
          )}

          {/* Soil Constraints */}
          {result.soil_constraints && result.soil_constraints.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h4 className="font-semibold text-charcoal-900 mb-2">Soil Considerations</h4>
              <div className="text-sm text-charcoal-700 space-y-1">
                {result.soil_constraints.map((item: string, idx: number) => (
                  <div key={idx}>• {item}</div>
                ))}
              </div>
            </div>
          )}

          {/* Current Monitoring */}
          {result.monitoring_status && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h4 className="font-semibold text-charcoal-900 mb-2">Current Monitoring</h4>
              <p className="text-sm text-charcoal-700">{result.monitoring_status}</p>
            </div>
          )}

          {/* Risks */}
          {result.risks && result.risks.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="font-semibold text-charcoal-900 mb-2 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                Risks & Uncertainties
              </h4>
              <div className="text-sm text-charcoal-700 space-y-1">
                {result.risks.map((item: string, idx: number) => (
                  <div key={idx}>• {item}</div>
                ))}
              </div>
            </div>
          )}

          {/* Farmer Actions */}
          {result.farmer_actions && result.farmer_actions.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-charcoal-900 mb-2">Recommended Actions</h4>
              <div className="text-sm text-charcoal-700 space-y-1">
                {result.farmer_actions.map((item: string, idx: number) => (
                  <div key={idx}>• {item}</div>
                ))}
              </div>
            </div>
          )}

          {/* Data Sources */}
          {result.data_sources && result.data_sources.length > 0 && (
            <div className="bg-charcoal-50 border border-charcoal-200 rounded-lg p-4">
              <h4 className="font-semibold text-charcoal-900 mb-2 text-sm">Data Sources Used</h4>
              <div className="text-xs text-charcoal-600 space-y-1">
                {result.data_sources.map((source: string, idx: number) => (
                  <div key={idx}>• {source}</div>
                ))}
              </div>
            </div>
          )}

          {/* Compare Rotations Button */}
          <div className="border-t-2 border-charcoal-200 pt-6">
            <button
              onClick={() => {
                const rotationSection = document.getElementById('rotation-lab')
                if (rotationSection) {
                  rotationSection.scrollIntoView({ behavior: 'smooth' })
                }
              }}
              className="w-full py-3 px-6 bg-forest-600 text-white rounded-lg hover:bg-forest-700 transition-colors font-semibold flex items-center justify-center gap-2"
            >
              <TrendingUp className="w-5 h-5" />
              Compare Other Planting Plans
            </button>
            <p className="text-sm text-charcoal-600 text-center mt-2">
              See how different crop rotations perform under various climate scenarios
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
