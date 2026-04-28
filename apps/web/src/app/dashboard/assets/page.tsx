"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { Asset } from "@/lib/types";

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const limit = 20;

  useEffect(() => {
    setLoading(true);
    api.assets
      .list(offset, limit)
      .then((res) => {
        setAssets(res.data);
        setTotal(res.meta.total);
      })
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

  const statusIcon = (status: string) => {
    switch (status) {
      case "protected":
        return (
          <div className="w-9 h-9 rounded-lg bg-[hsl(var(--guardian-success)/0.12)] flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-success))" strokeWidth="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <polyline points="9 12 11 14 15 10" />
            </svg>
          </div>
        );
      case "fingerprinting":
        return (
          <div className="w-9 h-9 rounded-lg bg-[hsl(var(--guardian-accent)/0.12)] flex items-center justify-center">
            <svg className="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-accent))" strokeWidth="2.5">
              <path d="M21 12a9 9 0 11-6.219-8.56" />
            </svg>
          </div>
        );
      case "failed":
        return (
          <div className="w-9 h-9 rounded-lg bg-[hsl(var(--guardian-danger)/0.12)] flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-danger))" strokeWidth="2.5">
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-9 h-9 rounded-lg bg-[hsl(var(--guardian-bg-hover))] flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-text-muted))" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between animate-fade-in-up">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Protected Assets</h1>
          <p className="text-sm text-[hsl(var(--guardian-text-muted))] mt-1">
            {total} asset{total !== 1 ? "s" : ""} registered
          </p>
        </div>
        <Link href="/dashboard/upload">
          <Button>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mr-2">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Upload Asset
          </Button>
        </Link>
      </div>

      {assets.length === 0 ? (
        <Card className="animate-fade-in-up">
          <CardContent className="py-16">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-[hsl(var(--guardian-bg-hover))] flex items-center justify-center mx-auto mb-4">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-text-muted))" strokeWidth="1.5">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <p className="text-sm text-[hsl(var(--guardian-text-muted))]">
                No assets yet. Upload your first asset to get started.
              </p>
              <Link href="/dashboard/upload">
                <Button className="mt-4" size="sm">Upload Your First Asset</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="space-y-2 animate-fade-in-up" style={{ animationDelay: "0.05s" }}>
            {assets.map((asset, idx) => (
              <div
                key={asset.id}
                className="flex items-center gap-4 p-4 rounded-xl bg-[hsl(var(--guardian-bg-card)/0.6)] border border-[hsl(var(--guardian-border)/0.4)] hover:border-[hsl(var(--guardian-border-hover))] hover:bg-[hsl(var(--guardian-bg-hover)/0.4)] transition-all duration-200"
              >
                {statusIcon(asset.status)}
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">{asset.title}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-[hsl(var(--guardian-text-muted))]">
                      {asset.content_type === "video" ? "🎬" : asset.content_type === "audio" ? "🎵" : "🖼️"} {asset.content_type}
                    </span>
                    <span className="text-xs text-[hsl(var(--guardian-text-muted))]">
                      {new Date(asset.created_at).toLocaleDateString()}
                    </span>
                    {asset.territories.length > 0 && (
                      <span className="text-xs text-[hsl(var(--guardian-text-muted))]">
                        📍 {asset.territories.join(", ")}
                      </span>
                    )}
                  </div>
                </div>
                <Badge
                  variant={
                    asset.status === "protected" ? "success" :
                    asset.status === "failed" ? "destructive" :
                    asset.status === "fingerprinting" ? "info" :
                    "secondary"
                  }
                >
                  {asset.status}
                </Badge>
              </div>
            ))}
          </div>

          {total > limit && (
            <div className="flex items-center justify-between animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
              <p className="text-xs text-[hsl(var(--guardian-text-muted))]">
                Showing {offset + 1}–{Math.min(offset + assets.length, total)} of {total}
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}>
                  Previous
                </Button>
                <Button variant="outline" size="sm" disabled={offset + limit >= total} onClick={() => setOffset(offset + limit)}>
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}