import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Clock, Camera, MapPin, RefreshCw, Layers } from 'lucide-react'
import { api } from '../services/api'
import MapView from '../components/MapView'

export default function EntityDetail() {
  const { id } = useParams()

  // Fetch entity basic info
  const { data: entity = null, isLoading: isLoadingEntity } = useQuery({
    queryKey: ['entity', id],
    queryFn: () => api.getEntityDetails(id),
  })

  // Fetch entity history path (contains lat/lon and details)
  const { data: history = [], isLoading: isLoadingHistory } = useQuery({
    queryKey: ['entityHistory', id],
    queryFn: () => api.getEntityHistory(id),
  })

  // Format path points specifically for Leaflet map polylines
  const mapPath = history.map(item => ({
    latitude: item.latitude,
    longitude: item.longitude,
    camera_id: item.camera_id,
    camera_name: item.camera_name,
    timestamp: item.timestamp,
    thumbnail_path: item.thumbnail_path,
    class_name: item.class_name
  }))

  const isLoading = isLoadingEntity || isLoadingHistory

  if (isLoading) {
    return (
      <div className="py-24 text-center text-slate-500 flex flex-col justify-center items-center gap-4">
        <RefreshCw className="animate-spin h-8 w-8 text-indigo-500" />
        <p className="text-sm font-semibold">Retrieving intelligence dossier logs...</p>
      </div>
    )
  }

  if (!entity) {
    return (
      <div className="py-24 text-center text-slate-500 space-y-4">
        <p className="text-lg font-bold text-slate-400">Entity Dossier Not Found</p>
        <Link to="/" className="text-indigo-400 hover:underline flex items-center justify-center gap-1">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Back navigation & Page Header */}
      <div className="space-y-4">
        <Link 
          to="/" 
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm font-medium w-fit"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <span className={`text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-md border ${
              entity.class_name === 'person' 
                ? 'bg-violet-500/10 border-violet-500/20 text-violet-400' 
                : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
            }`}>
              {entity.class_name} Target
            </span>
            <h1 className="text-3xl font-extrabold text-white mt-3 font-mono">
              Target ID: {entity.id}
            </h1>
            <p className="text-slate-400 mt-2">
              Cross-Camera identification tracks mapping chronological route coordinates.
            </p>
          </div>
        </div>
      </div>

      {/* Map Path Visualization Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Leaflet Map Card */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="h-5 w-5 text-indigo-400" />
            Geospatial Trajectory Path
          </h2>
          <MapView path={mapPath} />
        </div>

        {/* Target Dossier details */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between">
          <div className="space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="h-5 w-5 text-indigo-400" />
              Target Chronology Log
            </h2>
            
            {history.length === 0 ? (
              <p className="text-slate-500 text-sm">No historical tracking records logged yet.</p>
            ) : (
              <div className="space-y-4 max-h-[360px] overflow-y-auto pr-1">
                {history.map((record, index) => (
                  <div 
                    key={record.id} 
                    className="flex gap-4 p-3 rounded-xl border border-slate-800 bg-slate-900/35 hover:bg-slate-900/50 transition-colors"
                  >
                    {/* Index Badge */}
                    <div className="flex-shrink-0 h-8 w-8 rounded-lg bg-indigo-500/10 border border-indigo-500/25 flex items-center justify-center font-bold text-indigo-400 text-xs">
                      #{index + 1}
                    </div>

                    {/* Details */}
                    <div className="flex-1 min-w-0 space-y-1 text-xs">
                      <p className="font-bold text-slate-200 truncate flex items-center gap-1">
                        <Camera className="h-3.5 w-3.5 text-slate-500" />
                        {record.camera_name}
                      </p>
                      <p className="text-slate-400 flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5 text-slate-500" />
                        {new Date(record.timestamp).toLocaleString()}
                      </p>
                      <p className="text-slate-500 font-mono text-[10px] flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-slate-500" />
                        {record.latitude.toFixed(5)}, {record.longitude.toFixed(5)}
                      </p>
                    </div>

                    {/* Crop Thumbnail */}
                    {record.thumbnail_path && (
                      <div className="flex-shrink-0 h-12 w-12 bg-slate-950 rounded overflow-hidden flex items-center justify-center border border-slate-800">
                        <img 
                          src={record.thumbnail_path} 
                          alt="Crop" 
                          className="h-full w-full object-cover"
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%23020617%22/><text x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23475569%22 font-size=%228%22>Broken</text></svg>";
                          }}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-6 p-4 bg-slate-900/40 border border-slate-800 text-slate-400 rounded-xl text-xs">
            <span className="font-bold text-slate-300 block mb-1">Target Intelligence Report</span>
            Successfully re-identified target across {new Set(history.map(h => h.camera_id)).size} unique CCTV nodes. Total distance coordinates logged: {history.length}.
          </div>
        </div>

      </div>
    </div>
  )
}
