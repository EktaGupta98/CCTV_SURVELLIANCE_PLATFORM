import React, { useState, useEffect } from 'react'
import { Upload, Camera, MapPin, Calendar, Clock, RefreshCw, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react'
import { api } from '../services/api'

export default function UploadVideo() {
  const [file, setFile] = useState(null)
  const [cameraName, setCameraName] = useState('Front Entrance Main Gate')
  const [latitude, setLatitude] = useState(37.7749)
  const [longitude, setLongitude] = useState(-122.4194)
  const [timestamp, setTimestamp] = useState(new Date().toISOString().substring(0, 16))
  
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  
  // Job polling states
  const [activeJob, setActiveJob] = useState(null)
  const [jobProgress, setJobProgress] = useState(0)
  const [jobStatus, setJobStatus] = useState(null)

  // Preset location coordinate templates for ease of use
  const presetLocations = [
    { name: 'Main Gate Entrance', lat: 37.7749, lon: -122.4194 },
    { name: 'North Parking Lot', lat: 37.7760, lon: -122.4180 },
    { name: 'East Elevator Lobby', lat: 37.7735, lon: -122.4210 },
    { name: 'West Loading Dock', lat: 37.7755, lon: -122.4200 }
  ]

  const handlePresetSelect = (preset) => {
    setCameraName(preset.name)
    setLatitude(preset.lat)
    setLongitude(preset.lon)
  }

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setUploadError('Please select a video file.')
      return
    }

    setIsUploading(true)
    setUploadError(null)
    setActiveJob(null)
    setJobProgress(0)
    setJobStatus(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('camera_name', cameraName)
    formData.append('latitude', latitude)
    formData.append('longitude', longitude)
    
    // Format timestamp correctly for backend parser
    const formattedTimestamp = new Date(timestamp).toISOString()
    formData.append('video_timestamp', formattedTimestamp)

    try {
      const response = await api.uploadVideo(formData)
      setActiveJob(response.job_id)
      setJobStatus('PENDING')
      setIsUploading(false)
    } catch (err) {
      console.error(err)
      setUploadError(err.response?.data?.detail || 'An error occurred during footage upload.')
      setIsUploading(false)
    }
  }

  // Poll processing progress if an activeJob exists
  useEffect(() => {
    if (!activeJob) return

    let intervalId

    const checkStatus = async () => {
      try {
        const job = await api.getProcessingStatus(activeJob)
        setJobProgress(job.progress)
        setJobStatus(job.status)
        
        if (job.status === 'COMPLETED' || job.status === 'FAILED') {
          clearInterval(intervalId)
        }
      } catch (err) {
        console.error('Error fetching job status:', err)
      }
    }

    // Check immediately and then every 2 seconds
    checkStatus()
    intervalId = setInterval(checkStatus, 2000)

    return () => clearInterval(intervalId)
  }, [activeJob])

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white">Ingest CCTV Stream</h1>
        <p className="text-slate-400 mt-2">Upload footage to the YOLO tracking & CLIP cross-camera re-identification engine.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Form Panel */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* File Dropzone */}
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">Footage Video File</label>
              <div className="border border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-8 flex flex-col items-center justify-center bg-slate-900/20 hover:bg-indigo-500/5 transition-all relative">
                <input 
                  type="file" 
                  accept=".mp4,.avi,.mkv,.mov" 
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <Upload className="h-10 w-10 text-slate-500 mb-3" />
                <p className="text-sm font-bold text-slate-200">
                  {file ? file.name : 'Choose file or drag & drop'}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  MP4, AVI, MKV, or MOV up to 500MB
                </p>
              </div>
            </div>

            {/* Quick Presets */}
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">Quick Camera Presets</label>
              <div className="flex flex-wrap gap-2">
                {presetLocations.map((preset) => (
                  <button
                    key={preset.name}
                    type="button"
                    onClick={() => handlePresetSelect(preset)}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 rounded-lg text-xs transition-all"
                  >
                    {preset.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Metadata Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Camera className="h-3.5 w-3.5" />
                  Camera Name
                </label>
                <input 
                  type="text" 
                  value={cameraName}
                  onChange={(e) => setCameraName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
                  placeholder="e.g. Main Entrance Cam"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5" />
                  Video Start Date-Time
                </label>
                <input 
                  type="datetime-local" 
                  value={timestamp}
                  onChange={(e) => setTimestamp(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5" />
                  Camera Latitude
                </label>
                <input 
                  type="number" 
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5" />
                  Camera Longitude
                </label>
                <input 
                  type="number" 
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 outline-none transition-colors"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isUploading}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/40 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/15 cursor-pointer"
            >
              {isUploading ? (
                <>
                  <RefreshCw className="animate-spin h-5 w-5" />
                  Uploading Video Data...
                </>
              ) : (
                <>
                  <Upload className="h-5 w-5" />
                  Ingest Stream
                </>
              )}
            </button>
          </form>

          {uploadError && (
            <div className="mt-4 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 flex-shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Live Processing Pipeline Status Panel */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between">
          <div className="space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="h-5 w-5 text-indigo-400" />
              Pipeline Operations
            </h2>

            {!activeJob ? (
              <div className="text-center py-12 text-slate-500 space-y-4">
                <ShieldCheck className="h-12 w-12 mx-auto text-slate-700" />
                <p className="text-sm">Submit footage file to track and re-identify entities.</p>
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <span className="text-xs text-slate-400 font-semibold uppercase block">Job Registry ID</span>
                  <span className="text-xs font-mono text-indigo-400 block mt-1 truncate">{activeJob}</span>
                </div>

                <div>
                  <span className="text-xs text-slate-400 font-semibold uppercase block">Inference Status</span>
                  <div className="mt-2">
                    {jobStatus === 'PENDING' && (
                      <span className="px-3 py-1 bg-slate-800 border border-slate-700 text-slate-400 rounded-full text-xs font-semibold">
                        Queued for GPU/CPU Core
                      </span>
                    )}
                    {jobStatus === 'PROCESSING' && (
                      <span className="px-3 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-full text-xs font-semibold animate-pulse">
                        Object Tracking & Re-ID Active
                      </span>
                    )}
                    {jobStatus === 'COMPLETED' && (
                      <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-semibold flex items-center gap-1.5 w-fit">
                        <CheckCircle2 className="h-4 w-4" />
                        Inference Success
                      </span>
                    )}
                    {jobStatus === 'FAILED' && (
                      <span className="px-3 py-1 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-full text-xs font-semibold flex items-center gap-1.5 w-fit">
                        <AlertTriangle className="h-4 w-4" />
                        Inference Error
                      </span>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-semibold uppercase">Tracking progress</span>
                    <span className="font-bold text-slate-200">{Math.round(jobProgress)}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-300 ${
                        jobStatus === 'FAILED' ? 'bg-rose-500' : 'bg-indigo-500 animate-pulse'
                      }`}
                      style={{ width: `${jobProgress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {jobStatus === 'COMPLETED' && (
            <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs space-y-2">
              <p className="font-bold flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" />
                Pipeline Completed Successfully!
              </p>
              <p className="text-slate-400">All targets mapped and database indexes structured for Re-ID search queries.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
