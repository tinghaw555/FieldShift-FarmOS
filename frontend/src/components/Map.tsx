'use client'

import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix default marker icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Custom blue marker for device location
const deviceLocationIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

// MapController: Handles programmatic map movements when center prop changes
function MapController({ center, zoom }: { center: [number, number], zoom?: number }) {
  const map = useMap()
  
  useEffect(() => {
    if (center && center[0] !== 0 && center[1] !== 0) {
      // Smoothly fly to the new center position
      map.flyTo(center, zoom || 13, {
        animate: true,
        duration: 1.5
      })
    }
  }, [center, zoom, map])
  
  return null
}

export default function Map({ center, farms, onMapClick, onFarmClick, selectedFarm, deviceLocation, accuracy }: any) {
  return (
    <MapContainer
      center={[39.8283, -98.5795]} // Initial center (USA), will be overridden by MapController
      zoom={4}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {/* Programmatically move map when center changes */}
      <MapController center={center} zoom={deviceLocation ? 13 : undefined} />
      
      <MapClickHandler onMapClick={onMapClick} />
      
      {/* Device location marker (blue) */}
      {deviceLocation && (
        <Marker position={deviceLocation} icon={deviceLocationIcon}>
          <Popup>
            <div className="p-2">
              <div className="font-semibold text-blue-600">📍 Your Device Location</div>
              <div className="text-xs text-gray-600">
                {deviceLocation[0].toFixed(4)}°, {deviceLocation[1].toFixed(4)}°
              </div>
              {accuracy && (
                <div className="text-xs text-gray-500 mt-1">
                  Accuracy: ±{Math.round(accuracy)}m
                </div>
              )}
              <div className="text-xs text-gray-500 mt-1">
                Click on map to set farm location
              </div>
            </div>
          </Popup>
        </Marker>
      )}
      
      {/* Farm markers (green/red) */}
      {farms.map((farm: any) => (
        <Marker
          key={farm.id}
          position={[farm.latitude, farm.longitude]}
          eventHandlers={{
            click: () => onFarmClick(farm)
          }}
        >
          <Popup>
            <div className="p-2">
              <div className="font-semibold">🌾 {farm.name}</div>
              <div className="text-xs text-gray-600">
                {farm.latitude.toFixed(4)}°, {farm.longitude.toFixed(4)}°
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
