import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ZOMATO REC.AI | Your Personal Food Scout",
  description: "Find the perfect restaurant vibe in Bangalore using advanced LLM ranking and real-time filtering.",
  keywords: ["Zomato", "Bangalore", "Restaurant Recommendation", "AI", "LLM", "VibeCheck"],
  authors: [{ name: "Antigravity AI" }],
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light" suppressHydrationWarning>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
