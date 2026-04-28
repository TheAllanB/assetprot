"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ThreatMap } from "@/components/ThreatMap";
import { AlertFeed } from "@/components/AlertFeed";
import { api } from "@/lib/api";
import type { Asset, Violation } from "@/lib/types";

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

export default function DashboardPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.assets.list(0, 10), api.violations.list(0, 10)])
      .then(([assetsRes, violationsRes]) => {
        setAssets(assetsRes.data);
        setViolations(violationsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const threats: ThreatData[] = violations.map((v, i) => ({
    id: v.id,
    asset_title: assets.find((a) => a.id === v.asset_id)?.title || "Unknown Asset",
    platform: v.platform,
    confidence: v.confidence,
    origin_lon: -0.13,
    origin_lat: 51.51,
    detected_lon: -122.4 + Math.random() * 60,
    detected_lat: 25 + Math.random() * 30,
    status: v.status,
    discovered_url: v.discovered_url,
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-3">
          <svg className="animate-spin h-8 w-8 text-[hsl(var(--guardian-accent))]" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-sm text-[hsl(var(--guardian-text-muted))]">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const protectedCount = assets.filter((a) => a.status === "protected").length;
  const confirmedViolations = violations.filter((v) => v.status === "confirmed").length;
  const totalReach = violations.reduce((sum, v) => sum + (v.estimated_reach || 0), 0);

  const stats = [
    {
      label: "Total Assets",
      value: assets.length,
      subtext: `${protectedCount} protected`,
      colorClass: "stat-card-blue",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-accent))" strokeWidth="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      ),
    },
    {
      label: "Active Violations",
      value: violations.length,
      subtext: `${confirmedViolations} confirmed`,
      colorClass: "stat-card-red",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-danger))" strokeWidth="2">
          <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      ),
    },
    {
      label: "Estimated Reach",
      value: totalReach > 1000 ? `${(totalReach / 1000).toFixed(0)}K` : totalReach.toString(),
      subtext: "Potential exposure",
      colorClass: "stat-card-orange",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-warning))" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      ),
    },
    {
      label: "Protection Rate",
      value: assets.length > 0 ? `${Math.round((protectedCount / assets.length) * 100)}%` : "—",
      subtext: "Assets secured",
      colorClass: "stat-card-green",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-success))" strokeWidth="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in-up">
        <h1 className="text-2xl font-bold tracking-tight">Command Center</h1>
        <p className="text-sm text-[hsl(var(--guardian-text-muted))] mt-1">Real-time asset protection monitoring</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-4 animate-fade-in-up" style={{ animationDelay: "0.05s" }}>
        {stats.map((stat) => (
          <div key={stat.label} className={`stat-card ${stat.colorClass}`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-[hsl(var(--guardian-text-muted))] uppercase tracking-wider">
                {stat.label}
              </span>
              {stat.icon}
            </div>
            <div className="text-3xl font-bold tracking-tight">{stat.value}</div>
            <p className="text-xs text-[hsl(var(--guardian-text-muted))] mt-1">{stat.subtext}</p>
          </div>
        ))}
      </div>

      {/* Threat Map */}
      <Card className="animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Global Threat Map</CardTitle>
              <p className="text-xs text-[hsl(var(--guardian-text-muted))] mt-1">Live violation tracking across platforms</p>
            </div>
            <Badge variant="info">{threats.length} active</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <ThreatMap threats={threats} />
        </CardContent>
      </Card>

      {/* Two columns: Recent activity */}
      <div className="grid gap-4 lg:grid-cols-5 animate-fade-in-up" style={{ animationDelay: "0.15s" }}>
        {/* Recent Assets (3 cols) */}
        <Card className="lg:col-span-3">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle>Recent Assets</CardTitle>
              <a href="/dashboard/assets" className="text-xs text-[hsl(var(--guardian-accent))] hover:underline">
                View all →
              </a>
            </div>
          </CardHeader>
          <CardContent>
            {assets.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-sm text-[hsl(var(--guardian-text-muted))]">No assets yet. Upload your first asset.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {assets.slice(0, 6).map((asset) => (
                  <div
                    key={asset.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-[hsl(var(--guardian-bg-secondary)/0.5)] hover:bg-[hsl(var(--guardian-bg-hover))] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-md bg-[hsl(var(--guardian-bg-hover))] flex items-center justify-center text-xs">
                        {asset.content_type === "video" ? "🎬" : asset.content_type === "audio" ? "🎵" : "🖼️"}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{asset.title}</p>
                        <p className="text-xs text-[hsl(var(--guardian-text-muted))]">
                          {asset.content_type} • {new Date(asset.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={
                        asset.status === "protected"
                          ? "success"
                          : asset.status === "failed"
                          ? "destructive"
                          : asset.status === "fingerprinting"
                          ? "info"
                          : "secondary"
                      }
                    >
                      {asset.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Alert Feed (2 cols) */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle>Live Alerts</CardTitle>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[hsl(var(--guardian-danger))] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[hsl(var(--guardian-danger))]"></span>
              </span>
            </div>
          </CardHeader>
          <CardContent>
            <AlertFeed violations={violations} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}