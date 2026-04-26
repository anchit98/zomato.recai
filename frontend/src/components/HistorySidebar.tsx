"use client";

import { useEffect, useState } from "react";
import { Flame, Clock, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface HistorySidebarProps {
  sessionId: string;
  onSelectHistory: (data: any) => void;
  refreshTrigger: number;
}

export default function HistorySidebar({ sessionId, onSelectHistory, refreshTrigger }: HistorySidebarProps) {
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function fetchHistory() {
      setIsLoading(true);
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${API_URL}/api/v1/recent-searches`);
        if (res.ok) {
          const data = await res.json();
          // Safety Guard: Ensure data is an array
          setHistory(Array.isArray(data) ? data : []);
        } else {
          setHistory([]);
        }
      } catch (err) {
        console.error("Failed to fetch history", err);
        setHistory([]);
      } finally {
        setIsLoading(false);
      }
    }
    fetchHistory();
  }, [sessionId, refreshTrigger]);

  return (
    <div className="flex flex-col h-full space-y-6">
      <div className="flex items-center gap-2 border-b border-[var(--card-border)] pb-4">
        <Flame size={18} className="text-orange-500" />
        <h2 className="text-lg font-black text-[var(--foreground)] tracking-tight">Trending Searches</h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
        {isLoading && history.length === 0 ? (
          [1, 2, 3].map((i) => (
            <div key={i} className="h-20 w-full bg-[var(--input-bg)] rounded-xl animate-pulse" />
          ))
        ) : history.length === 0 ? (
          <div className="text-center py-10 px-4">
            <Clock size={32} className="mx-auto text-gray-300 dark:text-gray-700 mb-3" />
            <p className="text-xs font-bold text-gray-400">No community searches yet.</p>
          </div>
        ) : (
          history.map((item) => (
            <button
              key={item.id}
              onClick={() => onSelectHistory(item)}
              className="w-full text-left bg-[var(--input-bg)] border border-[var(--card-border)] p-4 rounded-xl hover:border-[#C5112E]/30 hover:bg-red-50/5 dark:hover:bg-red-950/10 transition-all group"
            >
              <div className="flex justify-between items-start mb-1">
                <span className="text-[10px] font-black text-[#C5112E] uppercase tracking-widest">
                  {item.created_at 
                    ? new Date(item.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })
                    : 'Recent'
                  }
                </span>
                <ChevronRight size={14} className="text-gray-300 group-hover:text-[#C5112E] transition-colors" />
              </div>
              <p className="text-sm font-extrabold text-[var(--foreground)] truncate">
                {String(item.location || "Unknown").split(",")[0]}
              </p>
              <p className="text-[11px] font-medium text-gray-500 italic">
                {item.cuisine || "Any Cuisine"} • ₹{item.budget || "Any"}
              </p>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
