"use client";

import { useState, useEffect, useRef } from "react";
import { Search, MapPin, Sparkles, Star, LucideIcon, ChevronDown, Check, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

const LOCATIONS = [
  "BTM", "Banashankari", "Banaswadi", "Bannerghatta Road", "Basavanagudi", 
  "Basaveshwara Nagar", "Bellandur", "Bommanahalli", "Brigade Road", 
  "Brookefield", "CV Raman Nagar", "Central Bangalore", "Church Street", 
  "City Market", "Commercial Street", "Cunningham Road", "Domlur", 
  "East Bangalore", "Ejipura", "Electronic City", "Frazer Town", 
  "HBR Layout", "HSR", "Hebbal", "Hennur", "Hosur Road", 
  "ITPL Main Road, Whitefield", "Indiranagar", "Infantry Road", "JP Nagar", 
  "Jalahalli", "Jayanagar", "Jeevan Bhima Nagar", "KR Puram", "Kaggadasapura", 
  "Kalyan Nagar", "Kammanahalli", "Kanakapura Road", "Kengeri", "Koramangala", 
  "Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 3rd Block", 
  "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 6th Block", 
  "Koramangala 7th Block", "Koramangala 8th Block", "Kumaraswamy Layout", 
  "Langford Town", "Lavelle Road", "MG Road", "Magadi Road", "Majestic", 
  "Malleshwaram", "Marathahalli", "Mysore Road", "Nagarbhavi", "Nagawara", 
  "New BEL Road", "North Bangalore", "Old Airport Road", "Old Madras Road", 
  "Peenya", "RT Nagar", "Race Course Road", "Rajajinagar", "Rajarajeshwari Nagar", 
  "Rammurthy Nagar", "Residency Road", "Richmond Road", "Sadashiv Nagar", 
  "Sahakara Nagar", "Sanjay Nagar", "Sankey Road", "Sarjapur Road", 
  "Seshadripuram", "Shanti Nagar", "Shivajinagar", "South Bangalore", 
  "St. Marks Road", "Thippasandra", "Ulsoor", "Uttarahalli", 
  "Varthur Main Road, Whitefield", "Vasanth Nagar", "Vijay Nagar", 
  "West Bangalore", "Whitefield", "Wilson Garden", "Yelahanka", "Yeshwantpur"
];

const QUICK_CUISINES = ["North Indian", "Italian", "Cafe", "Asian", "Desserts"];

interface FloatingInputProps {
  label: string;
  id: string;
  type?: string;
  value: string | number;
  onChange: (val: string) => void;
  placeholder?: string;
  icon?: LucideIcon;
  min?: string;
  required?: boolean;
}

const FloatingInput = ({ 
  label, 
  id, 
  type = "text", 
  value, 
  onChange, 
  placeholder, 
  icon: Icon,
  min,
  required 
}: FloatingInputProps) => {
  return (
    <div className="relative w-full group">
      {Icon && (
        <Icon 
          className="absolute left-4 top-[30px] -translate-y-1/2 text-gray-400 group-focus-within:text-red-500 transition-colors pointer-events-none z-10" 
          size={18} 
        />
      )}
      <input
        type={type}
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        min={min}
        required={required}
        placeholder=" "
        className={cn(
          "peer w-full bg-[var(--input-bg)] border border-[var(--card-border)] rounded-2xl px-4 pt-8 pb-3 text-[15px] font-medium focus:outline-none focus:ring-2 focus:ring-red-500/10 focus:border-red-500 transition-all text-[var(--foreground)] placeholder:opacity-0 focus:placeholder:opacity-100",
          "sm:px-4 sm:pt-8 sm:pb-3",
          Icon && "pl-12"
        )}
      />
      <label
        htmlFor={id}
        className={cn(
          "absolute transition-all duration-200 ease-out cursor-text pointer-events-none text-gray-500 dark:text-gray-400",
          "left-4 top-1/2 -translate-y-1/2 text-sm font-medium",
          Icon && "left-12",
          "peer-focus:top-2.5 peer-focus:translate-y-0 peer-focus:text-[10px] peer-focus:font-extrabold peer-focus:uppercase peer-focus:tracking-widest peer-focus:text-red-500/80 peer-focus:opacity-80",
          "not-placeholder-shown:top-2.5 not-placeholder-shown:translate-y-0 not-placeholder-shown:text-[10px] not-placeholder-shown:font-extrabold not-placeholder-shown:uppercase not-placeholder-shown:tracking-widest not-placeholder-shown:opacity-75",
          "peer-focus:left-4 not-placeholder-shown:left-4",
          Icon && "peer-focus:left-12 not-placeholder-shown:left-12"
        )}
      >
        {label}
      </label>
    </div>
  );
};

const LocationDropdown = ({ value, onChange }: { value: string, onChange: (val: string) => void }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredLocations = LOCATIONS.filter(loc => 
    loc.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative w-full group" ref={containerRef}>
      <MapPin 
        className={cn(
          "absolute left-4 top-[30px] -translate-y-1/2 transition-colors pointer-events-none z-10",
          isOpen ? "text-red-500" : "text-gray-400"
        )} 
        size={18} 
      />
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "w-full bg-[var(--input-bg)] border border-[var(--card-border)] rounded-2xl px-12 pt-8 pb-3 text-[15px] font-medium text-left focus:outline-none focus:ring-2 focus:ring-red-500/10 focus:border-red-500 transition-all",
          isOpen && "border-red-500"
        )}
      >
        {value || "Select Location"}
        <ChevronDown size={16} className={cn("absolute right-4 top-1/2 -translate-y-1/2 transition-transform", isOpen && "rotate-180")} />
      </button>
      
      <label className="absolute left-12 top-2.5 text-[10px] font-extrabold text-red-500/80 uppercase tracking-widest opacity-75">
        Location
      </label>

      {isOpen && (
        <div className="absolute top-[calc(100%+8px)] left-0 w-full bg-[var(--card)] border border-[var(--card-border)] rounded-2xl shadow-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          <div className="p-3 border-b border-[var(--card-border)] bg-[var(--card)] sticky top-0 z-10">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={14} />
              <input
                type="text"
                autoFocus
                placeholder="Search localities..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-[var(--input-bg)] border border-[var(--card-border)] rounded-xl pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-red-500/30 focus:border-red-500/50 transition-all"
              />
            </div>
          </div>

          <div className="max-h-[250px] overflow-y-auto custom-scrollbar p-2 space-y-1">
            {filteredLocations.length > 0 ? (
              filteredLocations.map((loc) => (
                <button
                  key={loc}
                  type="button"
                  onClick={() => {
                    onChange(loc);
                    setIsOpen(false);
                    setSearch("");
                  }}
                  className={cn(
                    "w-full px-4 py-3 text-sm text-left rounded-xl hover:bg-red-50 dark:hover:bg-red-950/20 transition-colors flex items-center justify-between",
                    value === loc ? "text-red-600 font-bold bg-red-50/50 dark:bg-red-950/10" : "text-[var(--foreground)]"
                  )}
                >
                  {loc}
                  {value === loc && <Check size={14} />}
                </button>
              ))
            ) : (
              <div className="px-4 py-8 text-center text-gray-500 text-sm italic">
                No localities found matching "{search}"
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [formData, setFormData] = useState({
    location: "Bellandur",
    budget: "",
    minimum_rating: 4.0,
    cuisine: "North Indian",
    additional_preferences: ""
  });
  const [isCustomCuisine, setIsCustomCuisine] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(formData);
  };

  const handleCuisineSelect = (c: string) => {
    setFormData({ ...formData, cuisine: c });
    setIsCustomCuisine(false);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="space-y-6">
        <LocationDropdown 
          value={formData.location}
          onChange={(val) => setFormData({ ...formData, location: val })}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <FloatingInput
            id="budget"
            label="Budget (Max INR)"
            type="number"
            min="0"
            value={formData.budget}
            onChange={(val) => setFormData({ ...formData, budget: val })}
            placeholder="e.g. 1500"
          />

          <div className="relative bg-[var(--input-bg)] border border-[var(--card-border)] rounded-2xl px-4 pt-8 pb-3 flex flex-col justify-end min-h-[64px]">
            <label className="absolute left-4 top-2.5 text-[10px] font-extrabold text-red-500/80 uppercase tracking-widest opacity-75">
              Minimum Rating
            </label>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setFormData({ ...formData, minimum_rating: star })}
                  className={cn(
                    "w-7 h-7 rounded-full flex items-center justify-center transition-all",
                    formData.minimum_rating >= star 
                      ? "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800" 
                      : "bg-[var(--muted)] text-gray-300 dark:text-gray-700 border border-[var(--card-border)]"
                  )}
                >
                  <Star size={12} fill={formData.minimum_rating >= star ? "currentColor" : "none"} />
                </button>
              ))}
              <span className="ml-2 text-xs font-bold text-gray-700 dark:text-gray-300">{formData.minimum_rating.toFixed(1)}+</span>
            </div>
          </div>
        </div>

        <div className="relative bg-[var(--input-bg)] border border-[var(--card-border)] rounded-2xl px-4 pt-8 pb-4 sm:pb-4">
          <label className="absolute left-4 top-2.5 text-[10px] font-extrabold text-red-500/80 uppercase tracking-widest opacity-75">
            Cuisines & Tags
          </label>
          <div className="flex flex-wrap gap-2">
            {QUICK_CUISINES.map((c) => (
              <span
                key={c}
                onClick={() => handleCuisineSelect(c)}
                className={cn(
                  "tag-pill",
                  formData.cuisine === c && !isCustomCuisine ? "tag-pill-active" : "tag-pill-inactive"
                )}
              >
                {c}
              </span>
            ))}
            
            {isCustomCuisine ? (
              <div className="flex items-center gap-2 animate-in slide-in-from-left-2 duration-200">
                <input
                  autoFocus
                  type="text"
                  value={formData.cuisine}
                  onChange={(e) => setFormData({ ...formData, cuisine: e.target.value })}
                  placeholder="Type any cuisine..."
                  className="bg-[var(--input-bg)] border border-red-200 dark:border-red-900 rounded-full px-4 py-1 text-xs font-bold text-red-600 outline-none focus:ring-2 focus:ring-red-500/20 min-w-[150px]"
                />
                <button 
                  type="button" 
                  onClick={() => setIsCustomCuisine(false)}
                  className="text-[10px] font-black text-gray-400 hover:text-gray-600 uppercase"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => {
                  setIsCustomCuisine(true);
                  setFormData({ ...formData, cuisine: "" });
                }}
                className={cn(
                  "tag-pill flex items-center gap-1",
                  isCustomCuisine ? "tag-pill-active" : "tag-pill-inactive"
                )}
              >
                <Plus size={10} /> {formData.cuisine && !QUICK_CUISINES.includes(formData.cuisine) ? formData.cuisine : "More"}
              </button>
            )}
          </div>
        </div>

        <div className="relative group">
          <textarea
            id="additional_preferences"
            value={formData.additional_preferences}
            onChange={(e) => setFormData({ ...formData, additional_preferences: e.target.value })}
            placeholder=" "
            className="peer w-full bg-[var(--input-bg)] border border-[var(--card-border)] rounded-2xl px-4 pt-9 pb-3 text-[15px] font-medium focus:outline-none focus:ring-2 focus:ring-red-500/10 focus:border-red-500 transition-all text-[var(--foreground)] min-h-[100px] sm:min-h-[140px] resize-none"
          />
          <label
            htmlFor="additional_preferences"
            className={cn(
              "absolute transition-all duration-200 ease-out cursor-text pointer-events-none text-gray-500 dark:text-gray-400",
              "left-4 top-6 text-sm font-medium",
              "peer-focus:top-2.5 peer-focus:text-[10px] peer-focus:font-extrabold peer-focus:uppercase peer-focus:tracking-widest peer-focus:text-red-500/80 peer-focus:opacity-80",
              "not-placeholder-shown:top-2.5 not-placeholder-shown:text-[10px] not-placeholder-shown:font-extrabold not-placeholder-shown:uppercase not-placeholder-shown:tracking-widest not-placeholder-shown:opacity-75"
            )}
          >
            Extra Preferences (Vibe, Dietary, etc.)
          </label>
        </div>

        <button type="submit" disabled={isLoading} className="btn-primary mt-4">
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          ) : (
            <>
              Get Recommendations <Sparkles size={18} />
            </>
          )}
        </button>
      </form>
    </div>
  );
}

interface SearchFormProps {
  onSearch: (data: any) => void;
  isLoading: boolean;
}
