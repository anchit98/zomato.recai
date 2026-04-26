"use client";

import { useState, useEffect } from "react";
import { Flame, AlertCircle, Coffee, ChevronLeft, Sun, Moon } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import SearchForm from "@/components/SearchForm";
import RecommendationCard from "@/components/RecommendationCard";
import HistorySidebar from "@/components/HistorySidebar";
import { cn } from "@/lib/utils";

const SESSION_ID = "user-123";

export default function Home() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const [hasSearched, setHasSearched] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  // Initialize theme and detect mobile
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedTheme = localStorage.getItem("theme");
      // Default to dark unless explicitly set to light
      if (savedTheme === "light") {
        setIsDarkMode(false);
      } else {
        setIsDarkMode(true);
      }

      // Mobile detection
      const checkMobile = () => setIsMobile(window.innerWidth < 640);
      checkMobile();
      window.addEventListener("resize", checkMobile);
      return () => window.removeEventListener("resize", checkMobile);
    }
  }, []);

  // Update localStorage and class on change
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDarkMode]);

  const handleSearch = async (formData: any) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    setRecommendations([]);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_URL}/api/v1/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          session_id: SESSION_ID,
          top_k: 5
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.message || "Failed to fetch recommendations");
      }

      setRecommendations(data.recommendations);
      setRefreshHistory(prev => prev + 1);
    } catch (err: any) {
      setError(err.message || "An error occurred. Is the backend running?");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] pb-20 transition-colors">
      {/* Navigation */}
      <nav className="sticky top-0 z-40 bg-[var(--background)]/80 backdrop-blur-md border-b border-[var(--card-border)]">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
              title="Toggle Dark Mode"
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>

          <div className="flex-1 flex justify-center">
            <div className="brand-title">
              <span className="brand-zomato">zomato</span>
              <span className="brand-rec">REC.Ai</span>
            </div>
          </div>

          <div className="flex items-center gap-2 md:gap-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors flex items-center gap-2"
              title="Trending Searches"
            >
              <Flame size={18} className="text-orange-500 dark:text-orange-400" />
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 pt-8 sm:pt-16">
        <AnimatePresence mode="wait">
          {!hasSearched ? (
            <motion.div
              key="discovery"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="space-y-8 sm:space-y-12"
            >
              {/* Hero */}
              <div className="text-center space-y-4">
                <h2 className="text-3xl sm:text-5xl md:text-6xl font-black tracking-tight leading-[1.1]">
                  Find your next meal with <span className="brand-zomato">zomato</span> <span className="text-gray-400">REC.Ai</span>
                </h2>
                <p className="text-gray-500 dark:text-gray-400 text-base sm:text-lg font-medium">
                  Tell us what you're craving, and we'll find the perfect spot.
                </p>
              </div>

              {/* Search Form */}
              <SearchForm onSearch={handleSearch} isLoading={isLoading} />
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-10"
            >
              {/* Results Header */}
              <div className="space-y-4 text-center">
                <button
                  onClick={() => setHasSearched(false)}
                  className="flex items-center gap-1 text-sm font-bold text-[#C5112E] hover:underline mx-auto"
                >
                  <ChevronLeft size={16} /> New Search
                </button>
                <div className="space-y-1">
                  <h2 className="text-4xl font-black tracking-tight">
                    Top <span className="brand-zomato">zomato</span> <span className="text-gray-400">REC.AI</span> for you
                  </h2>
                  <p className="text-gray-500 dark:text-gray-400 font-medium">
                    Based on your cravings and preferences, we found these spots.
                  </p>
                </div>
              </div>

              {/* Recommendation List */}
              <div className="space-y-6 max-w-4xl mx-auto">
                {isLoading ? (
                  [1, 2, 3].map(i => (
                    <div key={i} className="h-48 bg-[var(--card)] border border-[var(--card-border)] rounded-2xl animate-pulse" />
                  ))
                ) : error ? (
                  <div className="bg-red-50 dark:bg-red-950/20 border border-red-100 dark:border-red-900/50 p-8 rounded-2xl text-center space-y-4">
                    <AlertCircle className="mx-auto text-red-600" size={32} />
                    <p className="text-red-800 dark:text-red-200 font-bold">{error}</p>
                    <button onClick={() => setHasSearched(false)} className="text-red-600 dark:text-red-400 text-sm font-black underline">Try Again</button>
                  </div>
                ) : recommendations.length > 0 ? (
                  recommendations.map((rec, i) => (
                    <RecommendationCard key={i} data={rec} />
                  ))
                ) : (
                  <div className="text-center py-20 opacity-30">
                    <Coffee size={48} className="mx-auto mb-4" />
                    <p className="font-bold">No matches found. Try relaxing your filters.</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* History Sidebar Drawer */}
      <AnimatePresence>
        {isSidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsSidebarOpen(false)}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            />
            <motion.div
              initial={{ x: isMobile ? 0 : "100%", y: isMobile ? "100%" : 0 }}
              animate={{ x: 0, y: 0 }}
              exit={{ x: isMobile ? 0 : "100%", y: isMobile ? "100%" : 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className={cn(
                "fixed bg-[var(--card)] border-[var(--card-border)] z-50 p-6 shadow-2xl",
                isMobile
                  ? "bottom-0 left-0 w-full h-[80vh] border-t rounded-t-[32px]"
                  : "top-0 right-0 w-full max-w-sm h-full border-l"
              )}
            >
              {isMobile && (
                <div className="w-12 h-1.5 bg-gray-200 dark:bg-gray-800 rounded-full mx-auto mb-6 mt-[-12px]" />
              )}
              <HistorySidebar
                sessionId={SESSION_ID}
                onSelectHistory={(data) => {
                  setRecommendations(data.recommendations);
                  setHasSearched(true);
                  setIsSidebarOpen(false);
                }}
                refreshTrigger={refreshHistory}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
