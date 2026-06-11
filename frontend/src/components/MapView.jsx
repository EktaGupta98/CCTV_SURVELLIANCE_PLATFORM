import React, { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'

// Reset Leaflet icon path config to prevent missing icon crashes
delete L.Icon.Default.prototype._getIconUrl;

// Custom HTML/Tailwind icon renderer for targets
const createCustomIcon = (className, text) => {
  const isPerson = className === 'person';
  const colorClass = isPerson 
    ? 'border-violet-500 bg-violet-600 text-white' 
    : 'border-emerald-500 bg-emerald-600 text-white';
    
  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="h-8 w-8 rounded-full border-2 ${colorClass} flex items-center justify-center font-bold text-[10px] shadow-lg animate-pulse">
        ${text.substring(0, 3).toUpperCase()}
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

// Sub-component to auto-fit bounds based on paths
function MapAutoCenter({ path }) {
  const map = useMap()

  useEffect(() => {
    if (path && path.length > 0) {
      const coordinates = path.map(p => [p.latitude, p.longitude])
      // Set view to focus on coordinates
      if (coordinates.length === 1) {
        map.setView(coordinates[0], 14)
      } else {
        map.fitBounds(coordinates, { padding: [50, 50] })
      }
    }
  }, [path, map])

  return null
}

export default function MapView({ path = [] }) {
  const polylineCoords = path.map(p => [p.latitude, p.longitude]);
  
  // Set default center if empty (San Francisco template coords)
  const defaultCenter = path.length > 0 
    ? [path[0].latitude, path[0].longitude] 
    : [37.7749, -122.4194];

  return (
    <div className="h-[460px] w-full rounded-2xl overflow-hidden border border-slate-800 shadow-xl relative z-10">
      <MapContainer 
        center={defaultCenter} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        {/* OpenStreetMap Tile Layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Draw tracking lines connecting camera detections */}
        {polylineCoords.length > 1 && (
          <Polyline 
            positions={polylineCoords} 
            color="#6366f1" 
            weight={4} 
            opacity={0.8}
            dashArray="10, 8"
          />
        )}

        {/* Draw camera markers */}
        {path.map((point, index) => {
          const customIcon = createCustomIcon(point.class_name, `${index + 1}`);
          return (
            <Marker 
              key={`${point.camera_id}-${index}`} 
              position={[point.latitude, point.longitude]}
              icon={customIcon}
            >
              <Popup>
                <div className="text-slate-100 p-1 font-sans space-y-2 min-w-[150px]">
                  <p className="font-extrabold text-sm border-b border-slate-700 pb-1 text-slate-100">
                    {point.camera_name}
                  </p>
                  
                  {point.thumbnail_path && (
                    <div className="h-20 w-full bg-slate-900 rounded overflow-hidden flex items-center justify-center">
                      <img 
                        src={point.thumbnail_path} 
                        alt="Target crop" 
                        className="h-full w-full object-cover"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%23020617%22/><text x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23475569%22 font-size=%2210%22>Broken Image</text></svg>";
                        }}
                      />
                    </div>
                  )}

                  <div className="text-[10px] space-y-1 text-slate-400">
                    <p><span className="font-bold text-slate-300">Target:</span> {point.class_name}</p>
                    <p><span className="font-bold text-slate-300">Step:</span> #{index + 1} in path</p>
                    <p><span className="font-bold text-slate-300">Time:</span> {new Date(point.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              </Popup>
            </Marker>
          )
        })}

        {/* Auto fit center based on coords */}
        <MapAutoCenter path={path} />

      </MapContainer>
    </div>
  )
}
