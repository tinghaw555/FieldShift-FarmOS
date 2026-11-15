'use client'

import { useEffect, useState } from 'react'
import { Satellite, Cloud, AlertTriangle } from 'lucide-react'
import { API_BASE } from '@/lib/config'

export default function EarthObservationSection({ farm, refreshTrigger }: any) {
  const [climateData, setClimateData] = useState<any>(null)
  const [weatherForecast, setWeatherForecast] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (farm) {
      loadData()
    }
  }, [farm, refreshTrigger])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load climate summary
      const climateRes = await fetch(
        `${API_BASE}/climate/summary/${farm.latitude}/${farm.longitude}?year=2023`
      )
      if (climateRes.ok) {
        const data = await climateRes.json()
        setClimateData(data)
      }

      // Load weather forecast
      const weatherRes = await fetch(
        `${API_BASE}/weather/forecast/${farm.latitude}/${farm.longitude}`
      )
      if (weatherRes.ok) {
        const data = await weatherRes.json()
        setWeatherForecast(data)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!farm) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <Satellite className="w-12 h-12 text-charcoal-400 mx-auto mb-3" />
        <p className="text-charcoal-600">Select a farm to view Earth observation data</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-charcoal-900 flex items-center gap-2 mb-6">
        <Satellite className="w-6 h-6 text-forest-600" />
        Climate & Land Conditions
      </h2>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Historical Weather Analysis */}
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-charcoal-900 mb-2 flex items-center gap-2">
              <Satellite className="w-5 h-5" />
              Historical Weather Analysis
            </h3>
            {loading ? (
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-blue-200 rounded w-3/4"></div>
                <div className="h-4 bg-blue-200 rounded w-1/2"></div>
              </div>
            ) : climateData ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-charcoal-700">Year:</span>
                  <span className="font-medium">{climateData.year}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-charcoal-700">Mean Temperature:</span>
                  <span className="font-medium">
                    {climateData.temperature?.mean_annual?.toFixed(1) || 'N/A'}°C
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-charcoal-700">Total Precipitation:</span>
                  <span className="font-medium">
                    {climateData.precipitation?.total_annual?.toFixed(0) || 'N/A'} mm
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-charcoal-700">Rainy Days:</span>
                  <span className="font-medium">
                    {climateData.precipitation?.days_with_rain || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-charcoal-700">Data Points:</span>
                  <span className="font-medium">{climateData.data_points || 0}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-charcoal-600">No data available</p>
            )}
            <p className="text-xs text-charcoal-500 mt-3">
              Source: NASA POWER (NASA Langley Research Center)
            </p>
          </div>
        </div>

        {/* Open-Meteo Weather Forecast */}
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-sky-50 to-sky-100 p-4 rounded-lg border border-sky-200">
            <h3 className="font-semibold text-charcoal-900 mb-2 flex items-center gap-2">
              <Cloud className="w-5 h-5" />
              7-Day Weather Forecast
            </h3>
            {loading ? (
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-sky-200 rounded w-3/4"></div>
                <div className="h-4 bg-sky-200 rounded w-1/2"></div>
              </div>
            ) : weatherForecast?.forecast ? (
              <div className="space-y-2">
                {weatherForecast.forecast.slice(0, 3).map((day: any, i: number) => (
                  <div key={i} className="flex justify-between items-center text-sm">
                    <span className="text-charcoal-700">{day.date}</span>
                    <div className="flex items-center gap-3">
                      <span className="font-medium">
                        {day.temperature_max.toFixed(0)}° / {day.temperature_min.toFixed(0)}°
                      </span>
                      <span className="text-blue-600">
                        {day.precipitation.toFixed(0)}mm
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-charcoal-600">No forecast available</p>
            )}
            <p className="text-xs text-charcoal-500 mt-3">
              Source: Open-Meteo (CC BY 4.0)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
