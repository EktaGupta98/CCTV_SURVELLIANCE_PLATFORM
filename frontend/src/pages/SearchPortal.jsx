import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Search, Camera, Users, Calendar, MapPin, RefreshCw, Eye, Tag } from 'lucide-react'
import { api } from '../services/api'

export default function SearchPortal() {
  const [classFilter, setClassFilter] = useState('')
  const [cameraIdFilter, setCameraIdFilter] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [radiusMeters, setRadiusMeters] = useState('')
  const [entityId, setEntityId] = useState('')

  // Search trigger query state
  const [searchParams, setSearchParams] = useState({
    class_name: null,
    camera_id: null,
    start_time: null,
    end_time: null,
    latitude: null,
    longitude: null,
    radius_meters: null,
    entity_id: null,
    skip: 0,
    limit: 100
  })

  // Queries
  const { data: cameras = [] } = useQuery({
    queryKey: ['cameras'],
    queryFn: api.getCameras,
  })

  const { data: results = [], isLoading, isRefetching, refetch } = useQuery({
    queryKey: ['search', searchParams],
    queryFn: () => api.searchHistory(searchParams),
    enabled: true,
  })

  const handleSearch = (e) => {
    e.preventDefault()
    
    // Clean filters to exclude empty values
    setSearchParams({
      class_name: classFilter || null,
      camera_id: cameraIdFilter || null,
      start_time: startTime ? new Date(startTime).toISOString() : null,
      end_time: endTime ? new Date(endTime).toISOString() : null,
      latitude: latitude !== '' ? parseFloat(latitude) : null,
      longitude: longitude !== '' ? parseFloat(longitude) : null,
      radius_meters: radiusMeters !== '' ? parseFloat(radiusMeters) : null,
      entity_id: entityId || null,
      skip: 0,
      limit: 100
    })
  }

  const handleClear = () => {
    setClassFilter('')
    setCameraIdFilter('')
    setStartTime('')
    setEndTime('')
    setLatitude('')
    setLongitude('')
    setRadiusMeters('')
    setEntityId('')
    setSearchParams({
      class_name: null,
      camera_id: null,
      start_time: null,
      end_time: null,
      latitude: null,
      longitude: null,
      radius_meters: null,
      entity_id: null,
      skip: 0,
      limit: 100
    })
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          <Search className="h-8 w-8 text-indigo-500" />
          Intelligence Search Portal
        </h1>
        <p className="text-slate-400 mt-2">Filter and query global entity re-identification history logs across camera networks.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Filter Settings Sidebar */}
        <div className="glass-panel p-6 rounded-2xl h-fit space-y-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">Search Filters</h2>
          <form onSubmit={handleSearch} className="space-y-4">
            
            {/* Class */}
            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                <Tag className="h-3 w-3" /> Target Class
              </label>
              <select
                value={classFilter}
                onChange={(e) => setClassFilter(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-sm text-slate-200 outline-none outline-0 transition-colors"
              >
                <option value="">All Classes</option>
                <option value="person">Person</option>
                <option value="vehicle">Vehicle (Car, Truck, Bus)</option>
              </select>
            </div>

            {/* Entity ID */}
            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                <Users className="h-3 w-3" /> Entity ID (UUID)
              </label>
              <input
                type="text"
                value={entityId}
                onChange={(e) => setEntityId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-sm text-slate-200 outline-none transition-colors"
                placeholder="Paste Target UUID..."
              />
            </div>

            {/* Camera */}
            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                <Camera className="h-3 w-3" /> Camera Node
              </label>
              <select
                value={cameraIdFilter}
                onChange={(e) => setCameraIdFilter(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-sm text-slate-200 outline-none transition-colors"
              >
                <option value="">All Cameras</option>
                {cameras.map((cam) => (
                  <option key={cam.id} value={cam.id}>{cam.name}</option>
                ))}
              </select>
            </div>

            {/* Date range */}
            <div className="space-y-2">
              <label className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                <Calendar className="h-3 w-3" /> Time Range Window
              </label>
              <div className="space-y-2">
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none transition-colors"
                  placeholder="Start date"
                />
                <input
                  type="datetime-local"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none transition-colors"
                  placeholder="End date"
                />
              </div>
            </div>

            {/* Geo Proximity Radius */}
            <div className="space-y-2 border-t border-slate-800 pt-4">
              <label className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                <MapPin className="h-3 w-3" /> Geo Proximity (Radius)
              </label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none transition-colors"
                  placeholder="Lat"
                />
                <input
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none transition-colors"
                  placeholder="Lon"
                />
              </div>
              <input
                type="number"
                value={radiusMeters}
                onChange={(e) => setRadiusMeters(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-300 outline-none transition-colors"
                placeholder="Radius in meters"
              />
            </div>

            {/* Form actions */}
            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={handleClear}
                className="w-1/2 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-xs font-bold text-slate-300 transition-colors cursor-pointer"
              >
                Clear
              </button>
              <button
                type="submit"
                className="w-1/2 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-colors shadow-lg shadow-indigo-600/10 cursor-pointer"
              >
                Apply
              </button>
            </div>

          </form>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-3 glass-panel p-6 rounded-2xl space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Eye className="h-5 w-5 text-indigo-400" />
              Tracking Log Query Results ({results.length})
            </h2>
            {(isLoading || isRefetching) && (
              <RefreshCw className="animate-spin h-5 w-5 text-indigo-400" />
            )}
          </div>

          {isLoading ? (
            <div className="py-24 text-center text-slate-500 flex justify-center items-center">
              <RefreshCw className="animate-spin h-6 w-6 mr-2" />
              Searching intelligence database...
            </div>
          ) : results.length === 0 ? (
            <div className="py-24 border border-dashed border-slate-800 rounded-2xl text-center text-slate-500 space-y-4">
              <Search className="h-12 w-12 mx-auto text-slate-700" />
              <p className="text-sm font-semibold">No historical tracks match the filter parameters.</p>
              <p className="text-xs text-slate-600">Try broadening your time range or selection fields.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 max-h-[680px] overflow-y-auto pr-2">
              {results.map((record) => (
                <div 
                  key={record.id} 
                  className="glass-card rounded-xl border border-slate-800/80 hover:border-slate-700 overflow-hidden transition-all hover:scale-[1.01]"
                >
                  {/* Visual Detection Thumbnail Crop */}
                  <div className="h-44 bg-slate-950 flex items-center justify-center relative overflow-hidden group">
                    {record.thumbnail_path ? (
                      <img 
                        src={record.thumbnail_path} 
                        alt="Crop target" 
                        className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%23020617%22/><text x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23475569%22 font-size=%2210%22>Broken Image</text></svg>";
                        }}
                      />
                    ) : (
                      <div className="text-slate-700 text-xs font-semibold uppercase">No Thumbnail</div>
                    )}
                    <span className={`absolute top-3 right-3 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-md border ${
                      record.class_name === 'person' 
                        ? 'bg-violet-500/10 border-violet-500/20 text-violet-400' 
                        : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    }`}>
                      {record.class_name}
                    </span>
                  </div>

                  {/* Card Body */}
                  <div className="p-4 space-y-3">
                    <div>
                      <span className="text-[10px] text-slate-500 font-semibold uppercase block">Global Entity ID</span>
                      <Link 
                        to={`/entity/${record.entity_id}`} 
                        className="text-xs font-mono font-bold text-indigo-400 hover:text-indigo-300 block truncate"
                      >
                        {record.entity_id}
                      </Link>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-xs border-t border-slate-800/60 pt-3">
                      <div>
                        <span className="text-[10px] text-slate-500 uppercase block">Camera Node</span>
                        <span className="font-semibold text-slate-300 truncate block mt-0.5">{record.camera_name}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 uppercase block">Timestamp</span>
                        <span className="text-[11px] text-slate-300 block mt-0.5">
                          {new Date(record.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center border-t border-slate-800/60 pt-3">
                      <span className="text-[10px] font-mono text-slate-600">
                        Lat: {record.latitude.toFixed(4)}, Lon: {record.longitude.toFixed(4)}
                      </span>
                      <Link 
                        to={`/entity/${record.entity_id}`} 
                        className="flex items-center gap-1 text-[11px] font-bold text-indigo-400 hover:text-white bg-indigo-500/5 hover:bg-indigo-600 border border-indigo-500/20 rounded-md px-2.5 py-1 transition-all"
                      >
                        Trace History
                        <Eye className="h-3 w-3" />
                      </Link>
                    </div>
                  </div>

                </div>
              ))}
            </div>
          )}

        </div>

      </div>
    </div>
  )
}
