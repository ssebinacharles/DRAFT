"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  FileCheck2, 
  UserPlus, 
  TrendingUp, 
  Bell,
  ArrowUpRight
} from 'lucide-react';

// Adjusted path to reach out of the app directory into components
// If you configured the Next.js '@' alias, you can use: import { GlassCard } from '@/components/ui/GlassCard';
// This tells Next.js to start looking directly from the 'src' folder
import { GlassCard } from "@/components/ui/GlassCard";

export default function AdminDashboardPage() {
  // Mock data for the analytical overview
  const metrics = [
    { label: "Total Students", value: "1,248", change: "+12%", icon: Users, color: "text-blue-400" },
    { label: "Pending Placements", value: "42", change: "Action Req.", icon: UserPlus, color: "text-amber-400" },
    { label: "Logs to Review", value: "156", change: "+48", icon: FileCheck2, color: "text-indigo-400" },
    { label: "Completion Rate", value: "88.4%", change: "+2.4%", icon: TrendingUp, color: "text-emerald-400" },
  ];

  const recentActivities = [
    { id: 1, user: "Alice Walker", action: "submitted Weekly Log 8", time: "12m ago" },
    { id: 2, user: "Admin Office", action: "approved Acme Corp Placement", time: "45m ago" },
    { id: 3, user: "Supervisor Smith", action: "added feedback for John Doe", time: "1h ago" },
  ];

  return (
    <div className="space-y-10">
      {/* --- WELCOME HEADER --- */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-light text-white tracking-tight">
            System <span className="font-semibold text-indigo-400">Intelligence</span>
          </h1>
          <p className="text-slate-500 mt-1 text-sm">Real-time administrative oversight and portal metrics.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="p-3 rounded-2xl bg-white/5 border border-white/10 text-slate-400 hover:text-white transition-all">
            <Bell size={20} />
          </button>
          <button className="px-6 py-3 rounded-2xl bg-indigo-500 text-white text-sm font-medium shadow-lg shadow-indigo-500/20 hover:bg-indigo-600 transition-all">
            Generate Export
          </button>
        </div>
      </div>

      {/* --- METRICS GRID --- */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard className="group hover:bg-white/[0.06] transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-2xl bg-white/5 ${item.color}`}>
                  <item.icon size={22} />
                </div>
                <div className="flex items-center text-[10px] font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-lg">
                  {item.change} <ArrowUpRight size={10} className="ml-1" />
                </div>
              </div>
              <p className="text-slate-500 text-xs uppercase tracking-widest font-medium">{item.label}</p>
              <h3 className="text-3xl font-bold text-white mt-1">{item.value}</h3>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* --- BOTTOM SECTIONS --- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Analytics Visualization Placeholder */}
        <GlassCard className="lg:col-span-2 min-h-[350px] flex items-center justify-center border-dashed border-white/5">
           <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="text-slate-600" />
              </div>
              <p className="text-slate-600 text-sm italic font-light">Placement Flow Distribution Chart Rendering...</p>
           </div>
        </GlassCard>

        {/* Recent Activity Feed */}
        <GlassCard className="lg:col-span-1">
          <div className="flex items-center justify-between mb-6">
            <h4 className="text-white font-medium">Activity Stream</h4>
            <span className="text-[10px] text-indigo-400 cursor-pointer hover:underline">View All</span>
          </div>
          <div className="space-y-6">
            {recentActivities.map((act) => (
              <div key={act.id} className="flex gap-4 relative">
                <div className="w-2 h-2 mt-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)]" />
                <div>
                  <p className="text-sm text-slate-300 leading-tight">
                    <span className="text-white font-medium">{act.user}</span> {act.action}
                  </p>
                  <p className="text-[10px] text-slate-500 mt-1 uppercase tracking-tighter">{act.time}</p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}