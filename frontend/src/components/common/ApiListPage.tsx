"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Loader2, 
  AlertCircle, 
  Terminal, 
  FileJson 
} from "lucide-react";

// 1. We make the props accept a Generic Type <T>
interface ApiListPageProps<T> {
  title: string;
  description?: string;
  fetchData: () => Promise<unknown>; // Use unknown instead of any
  renderItem?: (item: T) => React.ReactNode;
  emptyMessage?: string;
}

// 2. We use Generics and Record<string, unknown> to avoid 'any'
function normalizeData<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  
  if (data !== null && typeof data === "object") {
    const obj = data as Record<string, unknown>;
    // Check if it's a paginated Django response
    if (Array.isArray(obj.results)) {
      return obj.results as T[];
    }
    // Otherwise, wrap the single object in an array
    return [data] as T[];
  }
  
  return [];
}

// 3. Define the component as a Generic (T extends an object that might have an id)
export default function ApiListPage<T extends { id?: string | number }>({
  title,
  description,
  fetchData,
  renderItem,
  emptyMessage = "No records found yet.",
}: ApiListPageProps<T>) {
  
  // Update state to use the Generic type T and 'unknown'
  const [items, setItems] = useState<T[]>([]);
  const [rawData, setRawData] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showDebug, setShowDebug] = useState(false);

  useEffect(() => {
    let isMounted = true;
    
    // 4. Renamed to loadData so it doesn't overwrite the fetchData prop!
    const loadData = async () => {
      setLoading(true);
      setError("");
      try {
        // Actually call the API prop passed into the component
        const response = await fetchData();
        
        // Only update state if the component is still on the screen
        if (isMounted) {
          setRawData(response);
          setItems(normalizeData<T>(response));
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError("Failed to fetch data.");
          console.error("API Error:", err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false; // Cleanup to prevent memory leaks
    };
  }, [fetchData]);

  // --- 1. GLOBAL LOADING STATE ---
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-slate-400 font-light tracking-widest text-xs uppercase">
          Fetching Database Records...
        </p>
      </div>
    );
  }

  // --- 2. GLOBAL ERROR STATE ---
  if (error) {
    return (
      <div className="p-8 rounded-3xl bg-rose-500/5 border border-rose-500/20 backdrop-blur-md max-w-2xl">
        <div className="flex items-center gap-3 text-rose-400 mb-2">
          <AlertCircle size={20} />
          <h3 className="font-semibold">Data Synchronization Failed</h3>
        </div>
        <p className="text-slate-400 text-sm">{error}</p>
      </div>
    );
  }

  // --- 3. MAIN UI RENDER ---
  return (
    <div className="space-y-8 pb-12">
      
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-light text-white tracking-tight">{title}</h1>
        {description && (
          <p className="text-slate-500 mt-2 text-sm max-w-2xl leading-relaxed">
            {description}
          </p>
        )}
      </div>

      {/* Dynamic List Content */}
      {items.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-white/[0.01] border border-white/5 border-dashed">
          <p className="text-slate-500 text-sm">{emptyMessage}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item, index) => (
            <motion.div
              key={item.id || index}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05, ease: "easeOut" }}
            >
              {renderItem ? (
                renderItem(item)
              ) : (
                // Fallback UI if the developer forgets to pass a renderItem function
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 overflow-x-auto text-xs text-slate-400 font-mono">
                  <pre>{JSON.stringify(item, null, 2)}</pre>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}

      {/* --- DEVELOPER DEBUG PANEL --- */}
      <div className="pt-10 border-t border-white/5">
        <button 
          onClick={() => setShowDebug(!showDebug)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all text-xs font-medium uppercase tracking-wider border border-white/5"
        >
          <Terminal size={14} />
          {showDebug ? "Close Terminal" : "View Raw API Response"}
        </button>

        <AnimatePresence>
          {showDebug && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden mt-4"
            >
              <div className="p-5 rounded-2xl bg-black/50 border border-indigo-500/20 shadow-inner overflow-x-auto backdrop-blur-md">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-white/10 text-indigo-400">
                  <FileJson size={14} />
                  <span className="text-[10px] uppercase tracking-widest font-bold">JSON Payload</span>
                </div>
                <pre className="text-xs text-emerald-400/80 font-mono leading-relaxed">
                  {JSON.stringify(rawData, null, 2)}
                </pre>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

    </div>
  );
}