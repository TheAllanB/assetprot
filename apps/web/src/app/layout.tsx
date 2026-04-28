import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GUARDIAN — AI-Powered Digital Asset Protection",
  description:
    "Enterprise-grade content protection platform using multimodal AI fingerprinting, autonomous detection agents, and automated DMCA enforcement for sports media rights holders.",
  keywords: ["content protection", "DMCA", "AI fingerprinting", "piracy detection", "sports media"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
