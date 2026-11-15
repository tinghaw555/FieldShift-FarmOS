'use client'

import { useState, useEffect } from 'react'
import { AlertCircle, Cloud, Droplets, Wifi, WifiOff, Activity } from 'lucide-react'
import { API_BASE } from '@/lib/config'

export default function StatusBar({ farm }: { farm: any }) {
  const [deviceStatus, setDeviceStatus] = useState<string>('offline')

  useEffect(() => {
    if (farm) {
      checkDeviceStatus()
      const interval = setInterval(checkDeviceStatus, 15000)
      return () => clearInterval(interval)
    }
  }, [farm])

  const checkDeviceStatus = async () => {
    if (!farm) return
    
    try {
      const response = await fetch(`${API_BASE}/hardware/farm/${farm.id}/latest`)
      if (response.ok) {
        const data = await response.json()
        setDeviceStatus(data.status === 'current' ? 'online' : data.status === 'stale' ? 'stale' : 'offline')
      } else {
        setDeviceStatus('offline')
      }
    } catch (error) {
      setDeviceStatus('offline')
    }
  }

  if (!farm) return null

  const getDeviceStatusIndicator = () => {
    switch(deviceStatus) {
      case 'online':
        return (
          <div className="flex items-center gap-2">
            <Wifi className="w-4 h-4 text-green-500" />
            <span className="text-charcoal-700">Hardware: Connected</span>
          </div>
        )
      case 'stale':
        return (
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-yellow-500" />
            <span className="text-charcoal-700">Hardware: Data Stale</span>
          </div>
        )
      default:
        return (
          <div className="flex items-center gap-2">
            <WifiOff className="w-4 h-4 text-charcoal-400" />
            <span className="text-charcoal-700">Hardware: Offline</span>
          </div>
        )
    }
  }

  return (
    <div className="bg-white border-b border-charcoal-200 shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="font-semibold text-charcoal-800">
              📍 {farm.name}
            </div>
            <div className="text-sm text-charcoal-600">
              {farm.latitude.toFixed(4)}°, {farm.longitude.toFixed(4)}°
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Cloud className="w-4 h-4 text-blue-500" />
              <span className="text-charcoal-700">Climate: Active</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Droplets className="w-4 h-4 text-forest-600" />
              <span className="text-charcoal-700">Models: Ready</span>
            </div>
            
            {getDeviceStatusIndicator()}
          </div>
        </div>
      </div>
    </div>
  )
}
