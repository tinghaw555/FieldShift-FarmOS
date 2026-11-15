'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Plus, MapPin, Star, Search, MoreVertical, Edit2, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { API_BASE } from '@/lib/config'

// Dynamic import for Leaflet (client-side only)
const MapComponent = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => <div className="h-96 bg-charcoal-100 animate-pulse rounded-lg" />
})

export default function FarmSection({ onFarmSelected, selectedFarm }: any) {
  const [farms, setFarms] = useState<any[]>([])
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newFarm, setNewFarm] = useState({ name: '', latitude: 0, longitude: 0 })
  const [mapCenter, setMapCenter] = useState<[number, number]>([39.8283, -98.5795]) // Center of USA
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [geolocating, setGeolocating] = useState(false)
  const [deviceLocation, setDeviceLocation] = useState<[number, number] | null>(null)
  const [locationAccuracy, setLocationAccuracy] = useState<number | null>(null)
  
  // Phase 1: Farm management features
  const [searchQuery, setSearchQuery] = useState('')
  const [showAllFarms, setShowAllFarms] = useState(false)
  const [openMenuId, setOpenMenuId] = useState<number | null>(null)
  const [renameDialogOpen, setRenameDialogOpen] = useState<number | null>(null)
  const [renameName, setRenameName] = useState('')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<number | null>(null)
  const [deleteImpact, setDeleteImpact] = useState<any>(null)

  useEffect(() => {
    loadFarms()
  }, [])

  const loadFarms = async () => {
    try {
      setError(null)
      console.log('Loading farms from:', `${API_BASE}/farms/`)
      const response = await fetch(`${API_BASE}/farms/`)
      console.log('Load farms response:', response.status, response.statusText)
      
      if (!response.ok) {
        throw new Error(`Failed to load farms: ${response.status} ${response.statusText}`)
      }
      const data = await response.json()
      console.log('Loaded farms:', data)
      setFarms(data)
    } catch (error: any) {
      console.error('Failed to load farms:', error)
      setError(`Failed to load farms: ${error.message}`)
    }
  }

  const handleMapClick = (lat: number, lng: number) => {
    setNewFarm(prev => ({ ...prev, latitude: lat, longitude: lng }))
    setShowCreateForm(true)
    setError(null)
    setSuccess(null)
  }

  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser')
      return
    }

    setGeolocating(true)
    setError(null)
    setSuccess(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude
        const accuracy = position.coords.accuracy
        
        console.log('Geolocation success:', { lat, lng, accuracy })
        
        setDeviceLocation([lat, lng])
        setLocationAccuracy(accuracy)
        setNewFarm(prev => ({ ...prev, latitude: lat, longitude: lng }))
        setMapCenter([lat, lng])
        setShowCreateForm(true)
        setGeolocating(false)
        
        const accuracyText = accuracy < 100 ? 'Good' : accuracy < 500 ? 'Fair' : 'Low'
        setSuccess(`Location detected: ${lat.toFixed(4)}°, ${lng.toFixed(4)}° (${accuracyText} accuracy: ±${Math.round(accuracy)}m)`)
        
        // Clear success message after 5 seconds
        setTimeout(() => setSuccess(null), 5000)
      },
      (err) => {
        setGeolocating(false)
        console.error('Geolocation error:', err)
        
        let errorMessage = 'Failed to get your location. '
        
        switch (err.code) {
          case err.PERMISSION_DENIED:
            errorMessage = '❌ Location access denied. Please allow location access in your browser settings and try again.'
            break
          case err.POSITION_UNAVAILABLE:
            errorMessage = '❌ Location information is unavailable. Please check your device GPS settings or try again.'
            break
          case err.TIMEOUT:
            errorMessage = '⏱️ Location request timed out. Please try again or enter coordinates manually.'
            break
          default:
            errorMessage = '❌ An unknown error occurred while getting your location.'
        }
        
        setError(errorMessage)
      },
      {
        enableHighAccuracy: false,  // Use network/WiFi for faster results
        timeout: 20000,              // 20 seconds timeout
        maximumAge: 60000           // Accept cached position up to 1 minute old
      }
    )
  }

  const handleCreateFarm = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!newFarm.name || newFarm.name.trim() === '') {
      setError('Farm name is required')
      return
    }
    
    if (newFarm.latitude === 0 && newFarm.longitude === 0) {
      setError('Please select a location on the map or enter coordinates')
      return
    }
    
    setLoading(true)
    setError(null)
    setSuccess(null)
    
    try {
      console.log('Creating farm with data:', newFarm)
      console.log('API endpoint:', `${API_BASE}/farms/`)
      
      const response = await fetch(`${API_BASE}/farms/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newFarm.name.trim(),
          latitude: newFarm.latitude,
          longitude: newFarm.longitude
        })
      })
      
      console.log('Create farm response:', response.status, response.statusText)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('Error data:', errorData)
        throw new Error(errorData.detail || `Failed to create farm: ${response.status} ${response.statusText}`)
      }
      
      const farm = await response.json()
      console.log('Created farm:', farm)
      
      // Reload farms list
      await loadFarms()
      
      // Select the new farm
      handleFarmSelect(farm)
      
      // Show success message
      setSuccess(`Farm "${farm.name}" created successfully!`)
      
      // Reset form
      setShowCreateForm(false)
      setNewFarm({ name: '', latitude: 0, longitude: 0 })
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000)
      
    } catch (error: any) {
      console.error('Failed to create farm:', error)
      setError(error.message || 'Failed to create farm. Please check your connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  // Phase 1: Handle farm selection with last_selected_at update
  const handleFarmSelect = async (farm: any) => {
    onFarmSelected(farm)
    setMapCenter([farm.latitude, farm.longitude])
    
    // Update last_selected_at on backend
    try {
      await fetch(`${API_BASE}/farms/${farm.id}/select`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      })
      // Reload farms to update sorting
      loadFarms()
    } catch (error) {
      console.error('Failed to update last_selected_at:', error)
    }
  }

  // Phase 1: Toggle favorite
  const handleToggleFavorite = async (farmId: number, currentFavorite: boolean, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent farm selection
    
    try {
      const response = await fetch(`${API_BASE}/farms/${farmId}/favorite`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_favorite: !currentFavorite })
      })
      
      if (!response.ok) throw new Error('Failed to update favorite')
      
      // Reload farms to update sorting
      await loadFarms()
      setSuccess(currentFavorite ? 'Removed from favorites' : 'Added to favorites')
      setTimeout(() => setSuccess(null), 2000)
    } catch (error: any) {
      setError(error.message)
      setTimeout(() => setError(null), 3000)
    }
  }

  // Phase 1: Open rename dialog
  const handleRenameClick = (farm: any, e: React.MouseEvent) => {
    e.stopPropagation()
    setRenameDialogOpen(farm.id)
    setRenameName(farm.name)
    setOpenMenuId(null)
  }

  // Phase 1: Submit rename
  const handleRenameSubmit = async (farmId: number) => {
    if (!renameName.trim()) {
      setError('Farm name cannot be empty')
      return
    }
    
    try {
      const response = await fetch(`${API_BASE}/farms/${farmId}/rename`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: renameName.trim() })
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to rename farm')
      }
      
      await loadFarms()
      setSuccess('Farm renamed successfully')
      setTimeout(() => setSuccess(null), 2000)
      setRenameDialogOpen(null)
    } catch (error: any) {
      setError(error.message)
      setTimeout(() => setError(null), 3000)
    }
  }

  // Phase 1: Open delete dialog with impact check
  const handleDeleteClick = async (farmId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setOpenMenuId(null)
    
    try {
      const response = await fetch(`${API_BASE}/farms/${farmId}/delete-impact`)
      const impact = await response.json()
      setDeleteImpact(impact)
      setDeleteDialogOpen(farmId)
    } catch (error: any) {
      setError('Failed to check delete impact')
      setTimeout(() => setError(null), 3000)
    }
  }

  // Phase 1: Confirm delete
  const handleDeleteConfirm = async (farmId: number) => {
    try {
      const response = await fetch(`${API_BASE}/farms/${farmId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Failed to delete farm')
      
      const result = await response.json()
      
      // If deleted farm was selected, clear selection
      if (selectedFarm?.id === farmId) {
        onFarmSelected(null)
      }
      
      await loadFarms()
      setSuccess(result.message)
      setTimeout(() => setSuccess(null), 3000)
      setDeleteDialogOpen(null)
      setDeleteImpact(null)
    } catch (error: any) {
      setError(error.message)
      setTimeout(() => setError(null), 3000)
    }
  }

  // Phase 1: Filter farms by search
  const filteredFarms = farms.filter(farm =>
    farm.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Phase 1: Show only 3 farms by default
  const displayedFarms = showAllFarms ? filteredFarms : filteredFarms.slice(0, 3)

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-charcoal-900 flex items-center gap-2">
            <MapPin className="w-6 h-6 text-forest-600" />
            Farm Location
          </h2>
          <p className="text-charcoal-600 mt-1">
            Use your device location or click anywhere on the map
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleUseMyLocation}
            disabled={geolocating}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              geolocating
                ? 'bg-charcoal-300 text-charcoal-600 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <MapPin className="w-4 h-4" />
            {geolocating ? 'Detecting Location...' : 'Use My Location'}
          </button>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 px-4 py-2 bg-forest-600 text-white rounded-lg
                     hover:bg-forest-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Farm
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2">
          <div className="h-96 rounded-lg overflow-hidden border border-charcoal-200">
            <MapComponent
              center={mapCenter}
              farms={farms}
              onMapClick={handleMapClick}
              onFarmClick={(farm: any) => handleFarmSelect(farm)}
              selectedFarm={selectedFarm}
              deviceLocation={deviceLocation}
              accuracy={locationAccuracy}
            />
          </div>
          <p className="text-xs text-charcoal-500 mt-2">
            © OpenStreetMap contributors | 📍 Blue marker: your device location | 🌾 Green markers: saved farms
          </p>
        </div>

        {/* Farm List / Create Form */}
        <div className="space-y-4">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-2 border-red-300 text-red-900 px-4 py-3 rounded-lg">
              <div className="flex items-start gap-2">
                <span className="text-red-600 font-bold">⚠️</span>
                <div className="flex-1">
                  <div className="font-semibold">Error</div>
                  <div className="text-sm mt-1">{error}</div>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="text-red-600 hover:text-red-800"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border-2 border-green-300 text-green-900 px-4 py-3 rounded-lg">
              <div className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <div className="flex-1">
                  <div className="text-sm">{success}</div>
                </div>
                <button
                  onClick={() => setSuccess(null)}
                  className="text-green-600 hover:text-green-800"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {showCreateForm ? (
            <div className="bg-forest-50 p-4 rounded-lg border border-forest-200">
              <h3 className="font-semibold text-charcoal-900 mb-3">Create New Farm</h3>
              <form onSubmit={handleCreateFarm} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-charcoal-700 mb-1">
                    Farm Name
                  </label>
                  <input
                    type="text"
                    value={newFarm.name}
                    onChange={(e) => setNewFarm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-charcoal-300 rounded-lg focus:ring-2 
                             focus:ring-forest-500 focus:border-transparent"
                    placeholder="My Farm"
                    required
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-sm font-medium text-charcoal-700 mb-1">
                      Latitude
                    </label>
                    <input
                      type="number"
                      step="0.0001"
                      value={newFarm.latitude}
                      onChange={(e) => setNewFarm(prev => ({ ...prev, latitude: parseFloat(e.target.value) }))}
                      className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-charcoal-700 mb-1">
                      Longitude
                    </label>
                    <input
                      type="number"
                      step="0.0001"
                      value={newFarm.longitude}
                      onChange={(e) => setNewFarm(prev => ({ ...prev, longitude: parseFloat(e.target.value) }))}
                      className="w-full px-3 py-2 border border-charcoal-300 rounded-lg"
                      required
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
                      loading
                        ? 'bg-charcoal-300 text-charcoal-600 cursor-not-allowed'
                        : 'bg-forest-600 text-white hover:bg-forest-700'
                    }`}
                  >
                    {loading ? 'Creating...' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateForm(false)
                      setError(null)
                    }}
                    disabled={loading}
                    className="flex-1 bg-charcoal-200 text-charcoal-700 py-2 rounded-lg hover:bg-charcoal-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : null}

          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-charcoal-900">
                Your Farms {farms.length > 0 && `(${farms.length})`}
              </h3>
            </div>

            {/* Phase 1: Search Box */}
            {farms.length > 0 && (
              <div className="mb-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-charcoal-400" />
                  <input
                    type="text"
                    placeholder="Search farms..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-charcoal-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-forest-500 focus:border-transparent"
                  />
                </div>
              </div>
            )}

            {/* Phase 1: Farm List with 3-item preview */}
            <div className={`space-y-2 ${showAllFarms && farms.length > 3 ? 'max-h-96 overflow-y-auto' : ''}`}>
              {filteredFarms.length === 0 ? (
                <p className="text-sm text-charcoal-500 text-center py-8">
                  {searchQuery ? 'No matching farms found' : 'No farms yet. Click on the map to create one!'}
                </p>
              ) : (
                <>
                  {displayedFarms.map((farm) => (
                    <div
                      key={farm.id}
                      className={`relative p-3 rounded-lg border transition-colors ${
                        selectedFarm?.id === farm.id
                          ? 'bg-forest-50 border-forest-500'
                          : 'bg-white border-charcoal-200 hover:border-forest-300'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {/* Favorite Star */}
                        <button
                          onClick={(e) => handleToggleFavorite(farm.id, farm.is_favorite, e)}
                          className="mt-1 p-1 hover:bg-charcoal-100 rounded transition-colors"
                          title={farm.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                        >
                          <Star 
                            className={`w-4 h-4 ${
                              farm.is_favorite 
                                ? 'fill-yellow-400 text-yellow-400' 
                                : 'text-charcoal-400'
                            }`}
                          />
                        </button>

                        {/* Farm Info */}
                        <button
                          onClick={() => handleFarmSelect(farm)}
                          className="flex-1 text-left"
                        >
                          <div className="font-medium text-charcoal-900">{farm.name}</div>
                          <div className="text-xs text-charcoal-600 mt-1">
                            {farm.latitude.toFixed(4)}°, {farm.longitude.toFixed(4)}°
                          </div>
                        </button>

                        {/* Actions Menu */}
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setOpenMenuId(openMenuId === farm.id ? null : farm.id)
                            }}
                            className="p-1 hover:bg-charcoal-100 rounded transition-colors"
                          >
                            <MoreVertical className="w-4 h-4 text-charcoal-600" />
                          </button>

                          {openMenuId === farm.id && (
                            <div className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border border-charcoal-200 py-1 z-10">
                              <button
                                onClick={(e) => handleRenameClick(farm, e)}
                                className="w-full px-4 py-2 text-left text-sm hover:bg-charcoal-50 flex items-center gap-2"
                              >
                                <Edit2 className="w-3 h-3" />
                                Rename
                              </button>
                              <button
                                onClick={(e) => handleDeleteClick(farm.id, e)}
                                className="w-full px-4 py-2 text-left text-sm hover:bg-red-50 text-red-600 flex items-center gap-2"
                              >
                                <Trash2 className="w-3 h-3" />
                                Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Phase 1: View All / Show Less Button */}
                  {filteredFarms.length > 3 && (
                    <button
                      onClick={() => setShowAllFarms(!showAllFarms)}
                      className="w-full py-2 px-3 text-sm text-forest-600 hover:bg-forest-50 rounded-lg
                               border border-forest-200 flex items-center justify-center gap-2 transition-colors"
                    >
                      {showAllFarms ? (
                        <>
                          <ChevronUp className="w-4 h-4" />
                          Show Less
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-4 h-4" />
                          View All Farms ({filteredFarms.length})
                        </>
                      )}
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Phase 1: Rename Dialog */}
      {renameDialogOpen !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-charcoal-900 mb-4">Rename Farm</h3>
            <input
              type="text"
              value={renameName}
              onChange={(e) => setRenameName(e.target.value)}
              className="w-full px-3 py-2 border border-charcoal-300 rounded-lg mb-4
                       focus:ring-2 focus:ring-forest-500 focus:border-transparent"
              placeholder="Farm name"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRenameSubmit(renameDialogOpen)
                if (e.key === 'Escape') setRenameDialogOpen(null)
              }}
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setRenameDialogOpen(null)}
                className="px-4 py-2 text-charcoal-700 hover:bg-charcoal-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => handleRenameSubmit(renameDialogOpen)}
                className="px-4 py-2 bg-forest-600 text-white rounded-lg hover:bg-forest-700"
              >
                Rename
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Phase 1: Delete Confirmation Dialog */}
      {deleteDialogOpen !== null && deleteImpact && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-start gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-charcoal-900">Delete Farm</h3>
                <p className="text-sm text-charcoal-600 mt-1">
                  Are you sure you want to delete <strong>"{deleteImpact.farm_name}"</strong>?
                </p>
              </div>
            </div>

            {/* Impact Warning */}
            {(deleteImpact.impact.rotations > 0 || 
              deleteImpact.impact.sensor_readings > 0 ||
              deleteImpact.impact.irrigation_experiments > 0 ||
              deleteImpact.impact.connected_devices > 0) && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <p className="text-sm font-medium text-yellow-900 mb-2">This will also delete:</p>
                <ul className="text-sm text-yellow-800 space-y-1">
                  {deleteImpact.impact.rotations > 0 && (
                    <li>• {deleteImpact.impact.rotations} crop rotation{deleteImpact.impact.rotations !== 1 ? 's' : ''}</li>
                  )}
                  {deleteImpact.impact.sensor_readings > 0 && (
                    <li>• {deleteImpact.impact.sensor_readings} sensor reading{deleteImpact.impact.sensor_readings !== 1 ? 's' : ''}</li>
                  )}
                  {deleteImpact.impact.irrigation_experiments > 0 && (
                    <li>• {deleteImpact.impact.irrigation_experiments} irrigation experiment{deleteImpact.impact.irrigation_experiments !== 1 ? 's' : ''}</li>
                  )}
                  {deleteImpact.impact.connected_devices > 0 && (
                    <li>• {deleteImpact.impact.connected_devices} connected device{deleteImpact.impact.connected_devices !== 1 ? 's' : ''} (will be unlinked)</li>
                  )}
                </ul>
              </div>
            )}

            <p className="text-sm text-red-600 font-medium mb-4">{deleteImpact.warning}</p>

            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setDeleteDialogOpen(null)
                  setDeleteImpact(null)
                }}
                className="px-4 py-2 text-charcoal-700 hover:bg-charcoal-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteConfirm(deleteDialogOpen)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Delete Farm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close menu */}
      {openMenuId !== null && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={() => setOpenMenuId(null)}
        />
      )}
    </div>
  )
}
