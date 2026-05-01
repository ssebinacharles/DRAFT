"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  Building2, 
  Briefcase, 
  FileText, 
  GraduationCap, 
  Loader2, 
  AlertCircle,
  ArrowRight
} from "lucide-react";

// Using your configured path alias
import { GlassCard } from "@/components/ui/GlassCard";

// API Imports (Ensure these files exist in your src/api/ folder)
import { getCompanies } from "@/api/companiesApi";
import { getPlacements } from "@/api/placementsApi";
import { getWeeklyLogs } from "@/api/weeklyLogsApi";
import { getFinalResults } from "@/api/finalResultsApi";

// TypeScript interfaces for state
interface DashboardStats {
  companies: number;
  placements: number;
  weeklyLogs: number;
  results: number;
}

const getCount = (data: any) => {
  if (Array.isArray(data)) return data.length;
  if (data && Array.isArray(data.results)) return data.results.length;
  return 0;
};

export default function StudentDashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    companies: 0,
    placements: 0,
    weeklyLogs: 0,
    results: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    Promise.all([
      getCompanies(),
      getPlacements(),
      getWeeklyLogs(),
      getFinalResults(),
    ])
      .then(([companies, placements, weeklyLogs, results]) => {
        if (isMounted) {
          setStats({
            companies: getCount(companies),
            placements: getCount(placements),
            weeklyLogs: getCount(weeklyLogs),
            results: getCount(results),
          });
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Failed to sync dashboard data.");
          setLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, []);

  // --- UI Configuration for Stat Cards ---
  const statCards = [
    { 
      title: "Available Companies", 
      value: stats.companies, 
      icon: Building2, 
      color: "text-blue-400", 
      bg: "bg-blue-500/10",
      border: "hover:border-blue-500/30"
    },
    { 
      title: "My Placements", 
      value: stats.placements, 
      icon: Briefcase, 
      color: "text-emerald-400", 
      bg: "bg-emerald-500/10",
      border: "hover:border-emerald-500/30"
    },
    { 
      title: "Weekly Logs", 
      value: stats.weeklyLogs, 
      icon: FileText, 
      color: "text-amber-400", 
      bg: "bg-amber-500/10",
      border: "hover:border-amber-500/30"
    },
    { 
      title: "Final Results", 
      value: stats.results, 
      icon: GraduationCap, 
      color: "text-indigo-400", 
      bg: "bg-indigo-500/10",
      border: "hover:border-indigo-500/30"
    },
  ];

  // --- LOADING STATE ---
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-slate-400 font-light tracking-widest text-xs uppercase">Syncing Data...</p>
      </div>
    );
  }

  // --- ERROR STATE ---
  if (error) {
    return (
      <div className="p-8 rounded-3xl bg-rose-500/5 border border-rose-500/20 backdrop-blur-md max-w-2xl">
        <div className="flex items-center gap-3 text-rose-400 mb-2">
          <AlertCircle size={20} />
          <h3 className="font-semibold">Connection Error</h3>
        </div>
        <p className="text-slate-400 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      {/* HEADER */}
      <div>
        <h1 className="text-3xl font-light text-white tracking-tight">
          Internship <span className="font-semibold text-indigo-400">Overview</span>
        </h1>
        <p className="text-slate-500 mt-1 text-sm">Monitor your placement status and academic progress.</p>
      </div>

      {/* METRICS GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard className={`group transition-all duration-300 ${card.border} cursor-default`}>
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-2xl ${card.bg} ${card.color} border border-white/5`}>
                  <card.icon size={22} />
                </div>
              </div>
              <h3 className="text-4xl font-bold text-white tracking-tight">{card.value < 10 ? `0${card.value}` : card.value}</h3>
              <p className="text-slate-500 text-xs uppercase tracking-widest font-medium mt-2">{card.title}</p>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* QUICK ACTIONS / NEXT STEPS WIDGET */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ delay: 0.4 }}
      >
        <GlassCard className="flex flex-col md:flex-row items-center justify-between gap-6 border-dashed border-white/10 bg-indigo-500/5 hover:bg-indigo-500/10 transition-colors">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center">
              <FileText className="text-indigo-400" />
            </div>
            <div>
              <h4 className="text-white font-medium">Submit Your Weekly Log</h4>
              <p className="text-sm text-slate-400">Keep your academic supervisor updated on your progress.</p>
            </div>
          </div>
          <button className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-500 text-white font-medium text-sm hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-500/20 whitespace-nowrap w-full md:w-auto justify-center">
            Draft New Log <ArrowRight size={16} />
          </button>
        </GlassCard>
      </motion.div>
    </div>
  );
}