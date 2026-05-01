"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  Users, 
  FileSignature, 
  ClipboardCheck, 
  Activity, 
  Loader2, 
  AlertCircle,
  ArrowRight
} from "lucide-react";

import { GlassCard } from "@/components/ui/GlassCard";

// Future API imports (Placeholders for now)
// import { getAssignedStudents } from "@/api/supervisorApi";
// import { getPendingLogs } from "@/api/weeklyLogsApi";

interface SupervisorStats {
  totalStudents: number;
  pendingLogs: number;
  completedEvaluations: number;
}

export default function SupervisorDashboardPage() {
  const [stats, setStats] = useState<SupervisorStats>({
    totalStudents: 0,
    pendingLogs: 0,
    completedEvaluations: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Simulating API Fetch for the UI build phase
    const fetchDashboardData = async () => {
      try {
        // In the future, this will be: 
        // const [students, logs] = await Promise.all([getAssignedStudents(), getPendingLogs()]);
        
        setTimeout(() => {
          setStats({
            totalStudents: 12, // Mock data
            pendingLogs: 5,    // Mock data
            completedEvaluations: 4,
          });
          setLoading(false);
        }, 800);

      } catch (err: any) {
        setError(err.message || "Failed to load dashboard data.");
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const statCards = [
    { 
      title: "Assigned Students", 
      value: stats.totalStudents, 
      icon: Users, 
      color: "text-blue-400", 
      bg: "bg-blue-500/10",
      border: "hover:border-blue-500/30"
    },
    { 
      title: "Logs Awaiting Review", 
      value: stats.pendingLogs, 
      icon: FileSignature, 
      color: "text-amber-400", 
      bg: "bg-amber-500/10",
      border: "hover:border-amber-500/30"
    },
    { 
      title: "Completed Evaluations", 
      value: stats.completedEvaluations, 
      icon: ClipboardCheck, 
      color: "text-emerald-400", 
      bg: "bg-emerald-500/10",
      border: "hover:border-emerald-500/30"
    }
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-slate-400 font-light tracking-widest text-xs uppercase">Loading Supervisor Profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 rounded-3xl bg-rose-500/5 border border-rose-500/20 backdrop-blur-md max-w-2xl">
        <div className="flex items-center gap-3 text-rose-400 mb-2">
          <AlertCircle size={20} />
          <h3 className="font-semibold">Sync Error</h3>
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
          Supervisor <span className="font-semibold text-indigo-400">Overview</span>
        </h1>
        <p className="text-slate-500 mt-1 text-sm">Monitor your assigned students and pending reviews.</p>
      </div>

      {/* METRICS GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard className={`group transition-all duration-300 ${card.border} cursor-default h-full`}>
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-2xl ${card.bg} ${card.color} border border-white/5`}>
                  <card.icon size={22} />
                </div>
                {card.title === "Logs Awaiting Review" && card.value > 0 && (
                  <span className="flex h-3 w-3 relative mt-2 mr-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
                  </span>
                )}
              </div>
              <h3 className="text-4xl font-bold text-white tracking-tight">{card.value < 10 ? `0${card.value}` : card.value}</h3>
              <p className="text-slate-500 text-xs uppercase tracking-widest font-medium mt-2">{card.title}</p>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* QUICK ACTIONS */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ delay: 0.3 }}
      >
        <GlassCard className="flex flex-col md:flex-row items-center justify-between gap-6 border-dashed border-white/10 bg-indigo-500/5 hover:bg-indigo-500/10 transition-colors">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center">
              <Activity className="text-indigo-400" />
            </div>
            <div>
              <h4 className="text-white font-medium">Pending Approvals</h4>
              <p className="text-sm text-slate-400">You have {stats.pendingLogs} logbooks requiring your signature.</p>
            </div>
          </div>
          <button className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-500 text-white font-medium text-sm hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-500/20 whitespace-nowrap w-full md:w-auto justify-center">
            Review Logbooks <ArrowRight size={16} />
          </button>
        </GlassCard>
      </motion.div>
    </div>
  );
}