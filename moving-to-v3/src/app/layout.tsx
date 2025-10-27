import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Moving.to - Find Your Perfect City | 32,496 Cities Worldwide",
  description: "Discover comprehensive guides for 32,496 cities across 195+ countries. Compare cost of living, explore neighborhoods, find jobs, and plan your perfect move with AI-powered recommendations.",
  keywords: ["moving", "relocation", "cities", "cost of living", "expat", "international move"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
