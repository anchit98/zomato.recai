"use client";

import { Star, Sparkles, ThumbsUp, ThumbsDown, Check } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

interface RecommendationCardProps {
  data: any; // Allow flexible data structure
  sessionId?: string;
}

export default function RecommendationCard({ data, sessionId = "user-123" }: RecommendationCardProps) {
  const [feedbackStatus, setFeedbackStatus] = useState<null | 'positive' | 'negative'>(null);
  
  // Normalize data for both live and history sources
  const restaurant_name = data.restaurant_name || "Unknown Restaurant";
  const cuisines = data.cuisines || "Various Cuisines";
  const location = data.location || "Bangalore";
  const rating = data.rating || 0;
  
  // Handle field name variations
  const cost = data.estimated_cost_for_two || data.estimated_cost || 0;
  const explanation = data.explanation || data.ai_explanation || "AI is fetching details...";

  const handleFeedback = async (isPositive: boolean) => {
    setFeedbackStatus(isPositive ? 'positive' : 'negative');
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${API_URL}/api/v1/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          restaurant_name: restaurant_name,
          is_positive: isPositive
        }),
      });
    } catch (err) {
      console.error("Failed to save feedback", err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rec-card"
    >
      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <h3 className="text-xl font-extrabold text-[var(--foreground)] tracking-tight">
            {restaurant_name}
          </h3>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2 py-0.5 bg-[var(--muted)] text-gray-600 dark:text-gray-400 rounded">
              {String(cuisines).split(",")[0]}
            </span>
            <span className="text-gray-300 dark:text-gray-700">•</span>
            <span className="text-xs font-medium text-gray-500 dark:text-gray-400">{location}</span>
          </div>
        </div>

        <div className="text-right flex flex-col items-end gap-1">
          <div className="rating-badge">
            <Star size={12} fill="currentColor" /> {rating}
          </div>
          <div className="mt-1">
            <p className="text-lg font-black text-[var(--foreground)] leading-none">₹{cost}</p>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">for two</p>
          </div>
        </div>
      </div>

      <div className="insight-box">
        <div className="mt-1 bg-[var(--accent)] p-1.5 rounded-lg">
          <Sparkles size={16} className="text-[#C5112E]" />
        </div>
        <div className="flex-1">
          <p className="text-[11px] font-black text-[var(--foreground)] uppercase tracking-widest mb-1 flex items-center gap-1">
            Why this was chosen:
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed font-medium">
            {explanation}
          </p>
        </div>
      </div>

      {/* Feedback Controls */}
      <div className="mt-4 pt-4 border-t border-[var(--card-border)] flex items-center justify-between">
        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Was this helpful?</span>
        <div className="flex items-center gap-2">
          <AnimatePresence mode="wait">
            {feedbackStatus === null ? (
              <motion.div 
                key="actions"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2"
              >
                <button 
                  onClick={() => handleFeedback(true)}
                  className="p-1.5 rounded-lg border border-[var(--card-border)] hover:bg-green-50 dark:hover:bg-green-950/20 hover:text-green-600 transition-colors"
                >
                  <ThumbsUp size={14} />
                </button>
                <button 
                  onClick={() => handleFeedback(false)}
                  className="p-1.5 rounded-lg border border-[var(--card-border)] hover:bg-red-50 dark:hover:bg-red-950/20 hover:text-[#C5112E] transition-colors"
                >
                  <ThumbsDown size={14} />
                </button>
              </motion.div>
            ) : (
              <motion.div 
                key="thank-you"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="flex items-center gap-1.5 text-green-600 dark:text-green-500 font-bold text-xs"
              >
                <Check size={14} /> Thanks!
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}
