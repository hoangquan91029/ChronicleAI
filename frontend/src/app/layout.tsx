import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChronicleAI — Historical Research & Video Production Platform",
  description: "Transform historical source documents into fact-checked educational video scripts and 2D minimalist animation storyboards.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
