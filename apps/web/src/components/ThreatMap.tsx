"use client";

import { useEffect, useState } from "react";

interface ThreatData {
  id: string;
  asset_title: string;
  platform: string;
  confidence: number;
  origin_lon: number;
  origin_lat: number;
  detected_lon: number;
  detected_lat: number;
  status: string;
}

interface ThreatMapProps {
  threats: ThreatData[];
}

export function ThreatMap({ threats }: ThreatMapProps) {
  const [activeThreat, setActiveThreat] = useState<ThreatData | null>(null);

  const getSeverityColor = (confidence: number, status: string) => {
    if (status === "confirmed") return "#ef4444";
    if (status === "suspected") return confidence > 0.8 ? "#f97316" : "#3b82f6";
    return "#9ca3af";
  };

  const platformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "youtube":
        return "▶";
      case "vimeo":
        return "◉";
      case "custom":
        return "◈";
      default:
        return "●";
    }
  };

  return (
    <div className="relative w-full h-[400px] bg-slate-900 rounded-lg overflow-hidden">
      <div className="absolute inset-0 opacity-20">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-slate-700" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🗺️</div>
          <p className="text-slate-400 text-sm">Threat Distribution Map</p>
          <p className="text-slate-500 text-xs mt-1">
            {threats.length === 0 ? "No active threats" : `${threats.length} threats detected`}
          </p>
        </div>
      </div>

      {threats.map((threat, index) => {
        const x = 50 + (threat.detected_lon / 180) * 40;
        const y = 50 - (threat.detected_lat / 90) * 40;

        return (
          <div
            key={threat.id}
            className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 hover:scale-125"
            style={{
              left: `${x}%`,
              top: `${y}%`,
            }}
            onClick={() => setActiveThreat(threat)}
          >
            <div
              className="w-4 h-4 rounded-full animate-pulse"
              style={{ backgroundColor: getSeverityColor(threat.confidence, threat.status) }}
            />
            <div className="absolute -top-1 -right-1 text-xs">{platformIcon(threat.platform)}</div>
          </div>
        );
      })}

      {activeThreat && (
        <div className="absolute bottom-4 left-4 right-4 bg-slate-800 rounded-lg p-4 text-white">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold">{activeThreat.asset_title}</h3>
              <p className="text-sm text-slate-400">{activeThreat.platform}</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold" style={{ color: getSeverityColor(activeThreat.confidence, activeThreat.status) }}>
                {Math.round(activeThreat.confidence * 100)}%
              </div>
              <p className="text-xs text-slate-400">confidence</p>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-700 text-xs text-slate-500">
            {activeThreat.discovered_url || "Detection in progress..."}
          </div>
          <button
            onClick={() => setActiveThreat(null)}
            className="absolute top-2 right-2 text-slate-400 hover:text-white"
          >
            ×
          </button>
        </div>
      )}

      <div className="absolute bottom-4 right-4 flex gap-2 text-xs">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500" /> Confirmed
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-orange-500" /> Suspected
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-blue-500" /> Monitored
        </span>
      </div>
    </div>
  );
}