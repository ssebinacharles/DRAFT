"use client";

import React from "react";
import { 
  CalendarDays, 
  CheckCircle2, 
  XCircle, 
  Send,
  FileEdit,
  Target,
  Lightbulb,
  ClipboardList
} from "lucide-react";

import ApiListPage from "@/components/common/ApiListPage";
import { getWeeklyLogs } from "@/api/weeklyLogsApi"; // Ensure this uses your @ alias

export default function StudentsWeeklyLogsPage() {
  
  // Intelligent Status Formatter for Logbooks
  const getStatusConfig = (status: string) => {
    const s = status?.toUpperCase() || "DRAFT";
    if (s === "APPROVED" || s === "REVIEWED") 
      return { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", icon: CheckCircle2, label: "Reviewed" };
    if (s === "REJECTED" || s === "NEEDS_REVISION") 
      return { color: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/20", icon: XCircle, label: "Needs Revision" };
    if (s === "SUBMITTED") 
      return { color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20", icon: Send, label: "Submitted" };
    
    // Default: DRAFT
    return { color: "text-slate-400", bg: "bg-white/5", border: "border-white/10", icon: FileEdit, label: "Draft" };
  };

  // Structured Report Card for each Weekly Log
  const renderLogCard = (log: any) => {
    const statusConfig = getStatusConfig(log.status);
    const StatusIcon = statusConfig.icon;

    return (
      <div className="flex flex-col gap-6">
        
        {/* --- Header: Week Number, Title, & Status --- */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-5">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 flex flex-col items-center justify-center border border-indigo-500/20 shrink-0">
              <span className="text-[10px] uppercase tracking-widest text-indigo-400 font-bold">Week</span>
              <span className="text-xl font-bold text-white leading-none mt-0.5">{log.week_number || "-"}</span>
            </div>
            <div>
              <h2 className="text-xl font-medium text-white">
                {log.title || `Logbook Entry - Week ${log.week_number}`}
              </h2>
              {log.submitted_at && (
                <p className="text-slate-500 text-xs mt-1 flex items-center gap-1.5">
                  <CalendarDays size={12} />
                  Submitted: {new Date(log.submitted_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>

          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-bold tracking-wider uppercase whitespace-nowrap ${statusConfig.bg} ${statusConfig.color} ${statusConfig.border}`}>
            <StatusIcon size={14} />
            {statusConfig.label}
          </div>
        </div>

        {/* --- Body: The Text Content Grid --- */}
        <div className="space-y-4">
          
          {/* Activities Block */}
          <div className="p-4 rounded-2xl bg-white/[0.01] border border-white/5 hover:bg-white/[0.02] transition-colors">
            <div className="flex items-center gap-2 text-indigo-400 mb-2">
              <ClipboardList size={16} />
              <h3 className="text-sm font-semibold uppercase tracking-wider">Key Activities</h3>
            </div>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
              {log.activities || "No activities recorded for this week."}
            </p>
          </div>

          {/* Challenges & Lessons (Split on large screens, stacked on mobile) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Challenges */}
            <div className="p-4 rounded-2xl bg-rose-500/5 border border-rose-500/10">
              <div className="flex items-center gap-2 text-rose-400 mb-2">
                <Target size={16} />
                <h3 className="text-sm font-semibold uppercase tracking-wider">Challenges Faced</h3>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                {log.challenges || "No challenges recorded."}
              </p>
            </div>

            {/* Lessons Learned */}
            <div className="p-4 rounded-2xl bg-amber-500/5 border border-amber-500/10">
              <div className="flex items-center gap-2 text-amber-400 mb-2">
                <Lightbulb size={16} />
                <h3 className="text-sm font-semibold uppercase tracking-wider">Lessons Learned</h3>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                {log.lessons_learned || "No lessons recorded."}
              </p>
            </div>
          </div>

        </div>
      </div>
    );
  };

  return (
    <div className="max-w-5xl">
      <ApiListPage
        title="Weekly Logbook"
        description="Review your submitted weekly activities, challenges, and insights. Your academic supervisor will evaluate these records."
        fetchData={getWeeklyLogs}
        emptyMessage="You haven't created any weekly logs yet."
        renderItem={renderLogCard}
      />
    </div>
  );
}