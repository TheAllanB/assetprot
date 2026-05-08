"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { Violation } from "@/lib/types";

export default function ViolationsPage() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const limit = 20;

  useEffect(() => {
    setLoading(true);
    api.violations.list(offset, limit)
      .then((res) => { setViolations(res.data); setTotal(res.meta.total); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [offset]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <svg className="animate-spin h-8 w-8 text-[hsl(var(--guardian-accent))]" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    );
  }

  const badgeVar = (s: string) => {
    const m: Record<string, "destructive"|"success"|"warning"|"info"|"secondary"> = {
      confirmed:"destructive", dmca_sent:"success", suspected:"warning", requires_human_review:"info"
    };
    return m[s] || "secondary";
  };

  const sevColor = (v: Violation) =>
    v.status === "confirmed" ? "hsl(var(--guardian-danger))"
    : v.confidence > 0.8 ? "hsl(var(--guardian-warning))"
    : "hsl(var(--guardian-accent))";

  return (
    <div className="space-y-6">
      <div className="animate-fade-in-up">
        <h1 className="text-2xl font-bold tracking-tight">Violations</h1>
        <p className="text-sm text-[hsl(var(--guardian-text-muted))] mt-1">{total} detected</p>
      </div>

      {violations.length === 0 ? (
        <Card><CardContent className="py-16 text-center">
          <p className="text-sm text-[hsl(var(--guardian-text-muted))]">No violations detected.</p>
        </CardContent></Card>
      ) : (
        <>
          <div className="space-y-2 animate-fade-in-up" style={{animationDelay:"0.05s"}}>
            {violations.map((v) => (
              <div key={v.id} className="p-4 rounded-xl bg-[hsl(var(--guardian-bg-card)/0.6)] border border-[hsl(var(--guardian-border)/0.4)] hover:border-[hsl(var(--guardian-border-hover))] transition-all">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{background: `color-mix(in srgb, ${sevColor(v)} 12%, transparent)`}}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={sevColor(v)} strokeWidth="2.5">
                        <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-semibold">{v.platform}</span>
                        {v.infringement_type && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-[hsl(var(--guardian-bg-hover))] text-[hsl(var(--guardian-text-muted))]">
                            {v.infringement_type.replace("_"," ")}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[hsl(var(--guardian-text-muted))] truncate max-w-[400px]">{v.discovered_url}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-[10px] text-[hsl(var(--guardian-text-muted))]">
                          {new Date(v.detected_at).toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"})}
                        </span>
                        {v.estimated_reach && <span className="text-[10px] text-[hsl(var(--guardian-text-muted))]">~{v.estimated_reach.toLocaleString()} reach</span>}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    <Badge variant={badgeVar(v.status)}>{v.status}</Badge>
                    <div className="flex items-center gap-2">
                      <div className="w-16 confidence-bar">
                        <div className="confidence-bar-fill" style={{width:`${v.confidence*100}%`,background:sevColor(v)}}/>
                      </div>
                      <span className="text-xs font-semibold tabular-nums w-10 text-right">{(v.confidence*100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {total > limit && (
            <div className="flex items-center justify-between">
              <p className="text-xs text-[hsl(var(--guardian-text-muted))]">
                {offset+1}–{Math.min(offset+violations.length,total)} of {total}
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={offset===0} onClick={()=>setOffset(Math.max(0,offset-limit))}>Previous</Button>
                <Button variant="outline" size="sm" disabled={offset+limit>=total} onClick={()=>setOffset(offset+limit)}>Next</Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}