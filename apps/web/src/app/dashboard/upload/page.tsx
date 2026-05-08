"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";

const STEPS = ["Upload", "Fingerprinting", "Vector Storage", "Protected"];

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [contentType, setContentType] = useState("image");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [taskStatus, setTaskStatus] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) {
      setFile(dropped);
      if (!title) setTitle(dropped.name.replace(/\.[^/.]+$/, ""));
      // Auto-detect content type
      if (dropped.type.startsWith("video/")) setContentType("video");
      else if (dropped.type.startsWith("audio/")) setContentType("audio");
      else setContentType("image");
    }
  }, [title]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      if (!title) setTitle(selected.name.replace(/\.[^/.]+$/, ""));
      if (selected.type.startsWith("video/")) setContentType("video");
      else if (selected.type.startsWith("audio/")) setContentType("audio");
      else setContentType("image");
    }
  };

  const handleUpload = async () => {
    if (!file || !title) { setError("Please select a file and provide a title"); return; }
    setError(""); setLoading(true); setCurrentStep(0);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("title", title);
      formData.append("content_type", contentType);
      formData.append("territories", JSON.stringify(["global"]));
      const res = await api.assets.upload(formData);
      setTaskId(res.data.task_id);
      setCurrentStep(1);
      pollTaskStatus(res.data.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setLoading(false);
    }
  };

  const pollTaskStatus = async (tid: string) => {
    const poll = async () => {
      try {
        const res = await api.tasks.getStatus(tid);
        setTaskStatus(res.data.status);
        if (res.data.status === "success" || res.data.status === "complete") {
          setCurrentStep(3); setLoading(false);
          setTimeout(() => router.push("/dashboard/assets"), 1500);
        } else if (res.data.status === "failure" || res.data.status === "failed") {
          setCurrentStep(0); setLoading(false); setError("Fingerprinting failed");
        } else {
          setCurrentStep((prev) => Math.min(prev + 1, 2));
          setTimeout(poll, 2000);
        }
      } catch { setTimeout(poll, 2000); }
    };
    poll();
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes/1024).toFixed(1)} KB`;
    return `${(bytes/1048576).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="animate-fade-in-up">
        <h1 className="text-2xl font-bold tracking-tight">Upload Asset</h1>
        <p className="text-sm text-[hsl(var(--guardian-text-muted))] mt-1">Protect your content with GUARDIAN</p>
      </div>

      <Card className="animate-fade-in-up" style={{animationDelay:"0.05s"}}>
        <CardHeader>
          <CardTitle>Asset Details</CardTitle>
          <CardDescription>Upload images, videos, or audio files for fingerprinting</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {error && (
            <div className="rounded-lg bg-[hsl(var(--guardian-danger)/0.1)] border border-[hsl(var(--guardian-danger)/0.2)] p-3 text-sm text-[hsl(var(--guardian-danger))]">
              {error}
            </div>
          )}

          {/* Drag and drop zone */}
          <div
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer ${
              dragActive
                ? "border-[hsl(var(--guardian-accent))] bg-[hsl(var(--guardian-accent)/0.05)]"
                : file
                ? "border-[hsl(var(--guardian-success)/0.5)] bg-[hsl(var(--guardian-success)/0.03)]"
                : "border-[hsl(var(--guardian-border))] hover:border-[hsl(var(--guardian-border-hover))] hover:bg-[hsl(var(--guardian-bg-hover)/0.3)]"
            }`}
            onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input ref={fileInputRef} type="file" accept="image/*,video/*,audio/*" onChange={handleFileChange} className="hidden" />
            {file ? (
              <div className="space-y-2">
                <div className="w-12 h-12 rounded-xl bg-[hsl(var(--guardian-success)/0.12)] flex items-center justify-center mx-auto">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-success))" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <p className="text-sm font-medium">{file.name}</p>
                <p className="text-xs text-[hsl(var(--guardian-text-muted))]">{formatSize(file.size)}</p>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="w-12 h-12 rounded-xl bg-[hsl(var(--guardian-bg-hover))] flex items-center justify-center mx-auto">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="hsl(var(--guardian-text-muted))" strokeWidth="1.5">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
                <p className="text-sm text-[hsl(var(--guardian-text-secondary))]">
                  <span className="text-[hsl(var(--guardian-accent))] font-medium">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-[hsl(var(--guardian-text-muted))]">Images, videos, or audio files</p>
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="upload-title">Title</Label>
            <Input id="upload-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Enter asset title" />
          </div>

          <div className="space-y-2">
            <Label>Content Type</Label>
            <div className="flex gap-2">
              {[{v:"image",l:"🖼️ Image"},{v:"video",l:"🎬 Video"},{v:"audio",l:"🎵 Audio"}].map((t) => (
                <button key={t.v} type="button"
                  className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium border transition-all ${
                    contentType === t.v
                      ? "border-[hsl(var(--guardian-accent))] bg-[hsl(var(--guardian-accent)/0.1)] text-[hsl(var(--guardian-accent))]"
                      : "border-[hsl(var(--guardian-border))] text-[hsl(var(--guardian-text-muted))] hover:bg-[hsl(var(--guardian-bg-hover))]"
                  }`}
                  onClick={() => setContentType(t.v)}
                >{t.l}</button>
              ))}
            </div>
          </div>

          {/* Progress steps */}
          {taskId && (
            <div className="p-4 rounded-xl bg-[hsl(var(--guardian-bg-secondary))] border border-[hsl(var(--guardian-border)/0.4)]">
              <div className="flex items-center justify-between mb-3">
                {STEPS.map((step, i) => (
                  <div key={step} className="flex items-center gap-1.5">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all ${
                      i < currentStep ? "bg-[hsl(var(--guardian-success))] text-white"
                      : i === currentStep ? "bg-[hsl(var(--guardian-accent))] text-white animate-pulse"
                      : "bg-[hsl(var(--guardian-bg-hover))] text-[hsl(var(--guardian-text-muted))]"
                    }`}>
                      {i < currentStep ? "✓" : i+1}
                    </div>
                    <span className={`text-[10px] font-medium ${i <= currentStep ? "text-[hsl(var(--guardian-text-primary))]" : "text-[hsl(var(--guardian-text-muted))]"}`}>
                      {step}
                    </span>
                    {i < STEPS.length - 1 && <div className={`w-4 h-px mx-1 ${i < currentStep ? "bg-[hsl(var(--guardian-success))]" : "bg-[hsl(var(--guardian-border))]"}`} />}
                  </div>
                ))}
              </div>
              <p className="text-xs text-[hsl(var(--guardian-text-muted))]">
                {currentStep === 3 ? "Asset protected! Redirecting..." : `Processing: ${STEPS[currentStep]}...`}
              </p>
            </div>
          )}

          <Button onClick={handleUpload} disabled={loading || !file || !title} className="w-full">
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Processing...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
                Upload & Protect
              </span>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}