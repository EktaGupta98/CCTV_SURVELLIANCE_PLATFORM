import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Shield,
  Camera,
  Film,
  Users,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Eye,
  Activity,
} from "lucide-react";
import { api } from "../services/api";

export default function Dashboard() {
  // Fetch stats and lists
  const {
    data: videos = [],
    isLoading: isLoadingVideos,
    refetch: refetchVideos,
  } = useQuery({
    queryKey: ["videos"],
    queryFn: api.getVideos,
    refetchInterval: 5000, // Poll every 5s to check processing status progress!
  });

  const { data: entities = [], isLoading: isLoadingEntities } = useQuery({
    queryKey: ["entities"],
    queryFn: () => api.getEntities(0, 12),
  });

  const { data: cameras = [] } = useQuery({
    queryKey: ["cameras"],
    queryFn: api.getCameras,
  });

  // Calculate high level numbers
  const totalCameras = cameras.length;
  const totalVideos = videos.length;
  const totalEntities = entities.length;

  const activeJobs = videos.filter(
    (v) => v.status === "PROCESSING" || v.status === "PENDING",
  ).length;
  const failedJobs = videos.filter((v) => v.status === "FAILED").length;
  const completedJobs = videos.filter((v) => v.status === "COMPLETED").length;

  return (
    <div className="space-y-8">
      {/* Title Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Security Command Operations
          </h1>
          <p className="text-slate-400 mt-2">
            Live CCTV video ingestion and computer vision Re-ID processing hub.
          </p>
        </div>
        <button
          onClick={() => refetchVideos()}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 rounded-lg text-sm text-slate-300 transition-all"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh Operations
        </button>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-semibold tracking-wider uppercase">
              Active Cameras
            </span>
            <p className="text-3xl font-bold mt-2 text-indigo-400">
              {totalCameras}
            </p>
          </div>
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
            <Camera className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-semibold tracking-wider uppercase">
              Ingested Streams
            </span>
            <p className="text-3xl font-bold mt-2 text-sky-400">
              {totalVideos}
            </p>
          </div>
          <div className="p-3 bg-sky-500/10 border border-sky-500/20 text-sky-400 rounded-xl">
            <Film className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-semibold tracking-wider uppercase">
              Tracked Entities
            </span>
            <p className="text-3xl font-bold mt-2 text-violet-400">
              {totalEntities}
            </p>
          </div>
          <div className="p-3 bg-violet-500/10 border border-violet-500/20 text-violet-400 rounded-xl">
            <Users className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-semibold tracking-wider uppercase">
              Active Jobs
            </span>
            <p
              className={`text-3xl font-bold mt-2 ${activeJobs > 0 ? "text-amber-400" : "text-emerald-400"}`}
            >
              {activeJobs}
            </p>
          </div>
          <div
            className={`p-3 rounded-xl border ${
              activeJobs > 0
                ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                : "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
            }`}
          >
            <Activity className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Video Ingestion Streams & Job Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Film className="h-5 w-5 text-indigo-400" />
              Footage Ingestion Pipeline
            </h2>
            <Link
              to="/upload"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
            >
              + Upload Video
            </Link>
          </div>

          {isLoadingVideos ? (
            <div className="py-8 flex justify-center items-center text-slate-500">
              <RefreshCw className="animate-spin h-6 w-6 mr-3" />
              Loading footage records...
            </div>
          ) : videos.length === 0 ? (
            <div className="py-12 border border-dashed border-slate-800 rounded-xl flex flex-col justify-center items-center text-slate-500 space-y-4">
              <Film className="h-10 w-10 text-slate-600" />
              <p className="text-sm">No CCTV videos ingested yet.</p>
              <Link
                to="/upload"
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs transition-colors"
              >
                Ingest First Stream
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                    <th className="py-3 px-4">Filename</th>
                    <th className="py-3 px-4">Recorded Time</th>
                    <th className="py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40 text-sm">
                  {videos.map((video) => (
                    <tr
                      key={video.id}
                      className="hover:bg-slate-900/30 transition-colors"
                    >
                      <td className="py-4 px-4 font-medium max-w-[200px] truncate">
                        {video.filename}
                      </td>
                      <td className="py-4 px-4 text-slate-400 text-xs">
                        {new Date(video.video_timestamp).toLocaleString()}
                      </td>
                      <td className="py-4 px-4">
                        {video.status === "COMPLETED" && (
                          <span className="inline-flex items-center gap-1 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            Completed
                          </span>
                        )}
                        {video.status === "PROCESSING" && (
                          <div className="w-36 space-y-1">
                            <span className="inline-flex items-center gap-1 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full">
                              <Activity className="h-3.5 w-3.5 animate-pulse" />
                              Processing
                            </span>
                            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                              <div
                                className="bg-indigo-500 h-full animate-pulse transition-all duration-500"
                                style={{ width: "60%" }}
                              ></div>
                            </div>
                          </div>
                        )}
                        {video.status === "PENDING" && (
                          <span className="inline-flex items-center gap-1 text-xs text-slate-400 bg-slate-800/40 border border-slate-700/50 px-2 py-0.5 rounded-full">
                            Queueing
                          </span>
                        )}
                        {video.status === "FAILED" && (
                          <span
                            className="inline-flex items-center gap-1 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-full"
                            title={video.error_message}
                          >
                            <AlertTriangle className="h-3.5 w-3.5" />
                            Failed
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Recent Tracked Entities */}
        <div className="glass-panel p-6 rounded-2xl space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Users className="h-5 w-5 text-violet-400" />
              Identified Targets
            </h2>
            <Link
              to="/search"
              className="text-xs text-violet-400 hover:text-violet-300 font-semibold transition-colors"
            >
              Search Portal
            </Link>
          </div>

          {isLoadingEntities ? (
            <div className="py-8 flex justify-center items-center text-slate-500">
              <RefreshCw className="animate-spin h-6 w-6 mr-3" />
              Scanning targets...
            </div>
          ) : entities.length === 0 ? (
            <div className="py-12 border border-dashed border-slate-800 rounded-xl flex flex-col justify-center items-center text-slate-500 space-y-4">
              <Users className="h-10 w-10 text-slate-600" />
              <p className="text-sm">No targets identified yet.</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
              {entities.map((entity) => (
                <div
                  key={entity.id}
                  className="glass-card p-4 rounded-xl flex items-center justify-between border border-slate-800 hover:border-slate-700 transition-all hover:translate-x-1"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`h-10 w-10 rounded-lg flex items-center justify-center font-bold text-xs ${
                        entity.class_name === "person"
                          ? "bg-violet-500/10 border border-violet-500/20 text-violet-400"
                          : "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                      }`}
                    >
                      {entity.class_name.substring(0, 4).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Target Entity ID</p>
                      <p className="text-sm font-bold font-mono text-slate-200">
                        {entity.id.substring(0, 8)}...
                      </p>
                    </div>
                  </div>
                  <Link
                    to={`/entity/${entity.id}`}
                    className="p-2 bg-slate-800 hover:bg-indigo-600 rounded-lg text-slate-400 hover:text-white transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
