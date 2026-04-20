import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GUARDIAN",
  description: "AI-native digital asset protection for sports media",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
