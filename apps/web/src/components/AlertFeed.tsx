"use client";

import { useState } from "react";
import type { Violation } from "@/lib/types";
import { Badge } from "@/components/ui/badge";

interface AlertFeedProps {
  violations: Violation[];
}

export function AlertFeed({ violations }: AlertFeedProps) {
  if (violations.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="w-10 h-10 rounded-full bg-[hsl(var(--guardian-bg-hover))] flex items-center justify-center mx-auto mb-3">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-text-muted))" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
        </div>
        <p className="text-xs text-[hsl(var(--guardian-text-muted))]">No alerts yet</p>
      </div>
    );
  }

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  const severityIcon = (confidence: number, status: string) => {
    if (status === "confirmed") {
      return (
        <div className="w-7 h-7 rounded-full bg-[hsl(var(--guardian-danger)/0.15)] flex items-center justify-center flex-shrink-0">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-danger))" strokeWidth="2.5">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </div>
      );
    }
    if (confidence > 0.8) {
      return (
        <div className="w-7 h-7 rounded-full bg-[hsl(var(--guardian-warning)/0.15)] flex items-center justify-center flex-shrink-0">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-warning))" strokeWidth="2.5">
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
      );
    }
    return (
      <div className="w-7 h-7 rounded-full bg-[hsl(var(--guardian-accent)/0.15)] flex items-center justify-center flex-shrink-0">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-accent))" strokeWidth="2.5">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
    );
  };

  return (
    <div className="space-y-2 max-h-[340px] overflow-y-auto pr-1">
      {violations.map((v, idx) => (
        <div
          key={v.id}
          className="alert-entry flex items-start gap-3 p-3 rounded-lg bg-[hsl(var(--guardian-bg-secondary)/0.5)] hover:bg-[hsl(var(--guardian-bg-hover))] transition-colors"
          style={{ animationDelay: `${idx * 0.05}s` }}
        >
          {severityIcon(v.confidence, v.status)}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs font-semibold truncate">{v.platform}</p>
              <span className="text-[10px] text-[hsl(var(--guardian-text-muted))] whitespace-nowrap">
                {timeAgo(v.detected_at)}
              </span>
            </div>
            <p className="text-[11px] text-[hsl(var(--guardian-text-muted))] truncate mt-0.5">
              {v.discovered_url}
            </p>
            <div className="flex items-center gap-2 mt-1.5">
              <div className="confidence-bar flex-1">
                <div
                  className="confidence-bar-fill"
                  style={{
                    width: `${v.confidence * 100}%`,
                    background:
                      v.confidence > 0.8
                        ? "hsl(var(--guardian-danger))"
                        : v.confidence > 0.6
                        ? "hsl(var(--guardian-warning))"
                        : "hsl(var(--guardian-accent))",
                  }}
                />
              </div>
              <span className="text-[10px] font-semibold text-[hsl(var(--guardian-text-muted))]">
                {(v.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
