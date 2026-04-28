"use client";

import { useState } from "react";

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
  discovered_url?: string;
}

interface ThreatMapProps {
  threats: ThreatData[];
}

// Convert lat/lon to SVG coordinates (simple equirectangular projection)
function geoToSvg(lat: number, lon: number, width: number, height: number) {
  const x = ((lon + 180) / 360) * width;
  const y = ((90 - lat) / 180) * height;
  return { x, y };
}

// Generate a curved arc path between two points
function arcPath(x1: number, y1: number, x2: number, y2: number) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const curvature = dist * 0.3;
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2 - curvature;
  return `M ${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}`;
}

const getSeverityColor = (confidence: number, status: string) => {
  if (status === "confirmed") return "hsl(var(--guardian-danger))";
  if (confidence > 0.8) return "hsl(var(--guardian-warning))";
  return "hsl(var(--guardian-accent))";
};

// Simplified world map continents as SVG paths (equirectangular projection)
const WORLD_PATHS = [
  // North America
  "M 50 80 L 60 65 L 80 55 L 110 55 L 130 60 L 140 75 L 145 95 L 130 110 L 115 115 L 100 120 L 90 130 L 80 125 L 65 105 L 55 95 Z",
  // South America
  "M 115 135 L 125 130 L 140 135 L 145 160 L 140 185 L 130 200 L 120 210 L 115 195 L 110 175 L 108 155 Z",
  // Europe
  "M 195 55 L 210 50 L 225 52 L 230 60 L 225 70 L 220 75 L 210 78 L 200 72 L 195 65 Z",
  // Africa
  "M 195 85 L 210 80 L 225 85 L 235 100 L 230 120 L 225 140 L 215 155 L 205 150 L 195 135 L 190 115 L 192 100 Z",
  // Asia
  "M 230 45 L 250 35 L 280 40 L 310 45 L 330 55 L 340 70 L 335 85 L 320 90 L 300 95 L 280 90 L 260 80 L 245 70 L 235 60 Z",
  // Australia
  "M 310 150 L 330 145 L 345 150 L 350 160 L 340 170 L 325 175 L 310 165 Z",
];

const SVG_W = 400;
const SVG_H = 230;

export function ThreatMap({ threats }: ThreatMapProps) {
  const [active, setActive] = useState<ThreatData | null>(null);

  return (
    <div className="relative w-full rounded-lg overflow-hidden bg-[hsl(var(--guardian-bg-secondary))]">
      <svg
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        className="w-full"
        style={{ minHeight: 320 }}
      >
        {/* Background grid */}
        <defs>
          <pattern id="map-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path
              d="M 20 0 L 0 0 0 20"
              fill="none"
              stroke="hsl(var(--guardian-border))"
              strokeWidth="0.15"
              opacity="0.4"
            />
          </pattern>
          {/* Glow filter for threat nodes */}
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect width={SVG_W} height={SVG_H} fill="url(#map-grid)" />

        {/* Continents */}
        {WORLD_PATHS.map((d, i) => (
          <path
            key={i}
            d={d}
            fill="hsl(var(--guardian-bg-hover))"
            stroke="hsl(var(--guardian-border))"
            strokeWidth="0.5"
            opacity="0.6"
          />
        ))}

        {/* Origin marker (HQ) */}
        {threats.length > 0 && (() => {
          const hq = geoToSvg(threats[0].origin_lat, threats[0].origin_lon, SVG_W, SVG_H);
          return (
            <g>
              <circle cx={hq.x} cy={hq.y} r="4" fill="hsl(var(--guardian-success))" opacity="0.8" />
              <circle cx={hq.x} cy={hq.y} r="7" fill="none" stroke="hsl(var(--guardian-success))" strokeWidth="0.5" opacity="0.4" />
              <text x={hq.x + 8} y={hq.y + 3} fontSize="5" fill="hsl(var(--guardian-success))" fontWeight="600">
                HQ
              </text>
            </g>
          );
        })()}

        {/* Animated arcs + threat nodes */}
        {threats.map((threat, idx) => {
          const origin = geoToSvg(threat.origin_lat, threat.origin_lon, SVG_W, SVG_H);
          const target = geoToSvg(threat.detected_lat, threat.detected_lon, SVG_W, SVG_H);
          const color = getSeverityColor(threat.confidence, threat.status);
          const isActive = active?.id === threat.id;

          return (
            <g key={threat.id}>
              {/* Arc line */}
              <path
                d={arcPath(origin.x, origin.y, target.x, target.y)}
                fill="none"
                stroke={color}
                strokeWidth={isActive ? "1.2" : "0.6"}
                opacity={isActive ? 0.9 : 0.35}
                className="animated-arc"
              />

              {/* Threat node */}
              <g
                style={{ cursor: "pointer" }}
                onClick={() => setActive(isActive ? null : threat)}
              >
                {/* Pulse ring */}
                <circle
                  cx={target.x}
                  cy={target.y}
                  r={isActive ? 8 : 5}
                  fill={color}
                  opacity="0.15"
                >
                  <animate
                    attributeName="r"
                    values={isActive ? "8;14;8" : "5;9;5"}
                    dur="2s"
                    repeatCount="indefinite"
                  />
                  <animate
                    attributeName="opacity"
                    values="0.15;0;0.15"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>

                {/* Core dot */}
                <circle
                  cx={target.x}
                  cy={target.y}
                  r={isActive ? 3.5 : 2.5}
                  fill={color}
                  filter="url(#glow)"
                />
              </g>
            </g>
          );
        })}

        {/* Empty state */}
        {threats.length === 0 && (
          <text
            x={SVG_W / 2}
            y={SVG_H / 2}
            textAnchor="middle"
            fontSize="8"
            fill="hsl(var(--guardian-text-muted))"
          >
            No active threats detected
          </text>
        )}
      </svg>

      {/* Active threat info panel */}
      {active && (
        <div className="absolute bottom-3 left-3 right-3 glass-card p-4 animate-fade-in-up">
          <div className="flex justify-between items-start">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold truncate">{active.asset_title}</h3>
              <p className="text-xs text-[hsl(var(--guardian-text-muted))] mt-0.5">{active.platform}</p>
              {active.discovered_url && (
                <p className="text-[10px] text-[hsl(var(--guardian-text-muted))] truncate mt-1">
                  {active.discovered_url}
                </p>
              )}
            </div>
            <div className="text-right ml-4">
              <div
                className="text-xl font-bold"
                style={{ color: getSeverityColor(active.confidence, active.status) }}
              >
                {Math.round(active.confidence * 100)}%
              </div>
              <p className="text-[10px] text-[hsl(var(--guardian-text-muted))]">confidence</p>
            </div>
            <button
              onClick={() => setActive(null)}
              className="ml-2 text-[hsl(var(--guardian-text-muted))] hover:text-[hsl(var(--guardian-text-primary))] transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-3 right-3 flex gap-3 text-[10px] text-[hsl(var(--guardian-text-muted))]">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full" style={{ background: "hsl(var(--guardian-danger))" }} />
          Confirmed
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full" style={{ background: "hsl(var(--guardian-warning))" }} />
          Suspected
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full" style={{ background: "hsl(var(--guardian-accent))" }} />
          Monitored
        </span>
      </div>
    </div>
  );
}