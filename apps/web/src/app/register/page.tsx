"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.auth.register({ email, password, org_name: orgName });
      await api.auth.login({ email, password });
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center relative overflow-hidden">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-[0.03]">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="grid-reg" width="60" height="60" patternUnits="userSpaceOnUse">
              <path d="M 60 0 L 0 0 0 60" fill="none" stroke="currentColor" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid-reg)" />
        </svg>
      </div>

      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[hsl(var(--guardian-gradient-end))] rounded-full opacity-[0.04] blur-[120px]" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[hsl(var(--guardian-accent))] rounded-full opacity-[0.04] blur-[120px]" />

      <div className="relative z-10 w-full max-w-md px-4">
        <div className="text-center mb-8 animate-fade-in-up">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[hsl(var(--guardian-gradient-start))] to-[hsl(var(--guardian-gradient-end))] mb-4 shadow-lg shadow-[hsl(var(--guardian-accent-glow)/0.2)]">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Create Organization</h1>
          <p className="text-sm text-[hsl(var(--guardian-text-muted))] mt-1">Protect your digital assets</p>
        </div>

        <Card className="gradient-border animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-lg">Get Started</CardTitle>
            <CardDescription>Register your organization</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-lg bg-[hsl(var(--guardian-danger)/0.1)] border border-[hsl(var(--guardian-danger)/0.2)] p-3 text-sm text-[hsl(var(--guardian-danger))]">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="reg-org">Organization Name</Label>
                <Input
                  id="reg-org"
                  type="text"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  placeholder="e.g. Champions League FC"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reg-email">Email</Label>
                <Input
                  id="reg-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@yourorg.com"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reg-password">Password</Label>
                <Input
                  id="reg-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 8 characters"
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Creating...
                  </span>
                ) : (
                  "Create Account"
                )}
              </Button>
              <p className="text-center text-sm text-[hsl(var(--guardian-text-muted))]">
                Already have an account?{" "}
                <a href="/login" className="text-[hsl(var(--guardian-accent))] hover:underline font-medium">
                  Sign In
                </a>
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}