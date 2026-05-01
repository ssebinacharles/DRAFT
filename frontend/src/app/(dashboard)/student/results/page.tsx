"use client";

import React from "react";
import { 
  GraduationCap, 
  Award, 
  FileText, 
  Building2, 
  BookOpen, 
  CalendarCheck,
  ShieldAlert
} from "lucide-react";

import ApiListPage from "@/components/common/ApiListPage";
import { getFinalResults } from "@/api/finalResultsApi"; // Ensure this uses your @ alias

export default function StudentsResultsPage() {
  
  // Custom renderer for the Academic Scorecard
  const renderResultCard = (result: any) => {
    const isPublished = !!result.published_at;

    return (
      <div className="flex flex-col md:flex-row gap-8">
        
        {/* Left Side: The Final Grade Spotlight */}
        <div className="md:w-1/3 flex flex-col items-center justify-center p-8 rounded-3xl bg-indigo-500/5 border border-indigo-500/20 text-center relative overflow-hidden group">
          {/* Subtle background glow effect */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-indigo-500/20 blur-3xl rounded-full" />
          
          <GraduationCap size={32} className="text-indigo-400 mb-4 relative z-10" />
          <p className="text-slate-400 text-xs font-bold tracking-widest uppercase mb-2 relative z-10">
            Final Mark
          </p>
          <h2 className="text-6xl font-bold text-white tracking-tighter relative z-10">
            {result.final_mark !== null && result.final_mark !== undefined ? result.final_mark : "N/A"}
          </h2>
          
          <div className="mt-6 relative z-10">
            {isPublished ? (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] uppercase font-bold tracking-wider">
                <CalendarCheck size={12} />
                Official Result
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[10px] uppercase font-bold tracking-wider">
                <ShieldAlert size={12} />
                Pending Verification
              </span>
            )}
          </div>
        </div>

        {/* Right Side: Detailed Score Breakdown */}
        <div className="md:w-2/3 flex flex-col justify-center gap-4">
          <h3 className="text-lg font-medium text-white mb-2 border-b border-white/5 pb-4">
            Assessment Breakdown
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Weekly Logs */}
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
                  <FileText size={14} className="text-slate-400" />
                </div>
                <span className="text-sm text-slate-300">Weekly Logs</span>
              </div>
              <span className="text-white font-semibold">{result.weekly_logs_score ?? "-"}</span>
            </div>

            {/* Academic Evaluation */}
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
                  <Award size={14} className="text-slate-400" />
                </div>
                <span className="text-sm text-slate-300">Academic Eval</span>
              </div>
              <span className="text-white font-semibold">{result.supervisor_evaluation_score ?? "-"}</span>
            </div>

            {/* Workplace Assessment */}
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
                  <Building2 size={14} className="text-slate-400" />
                </div>
                <span className="text-sm text-slate-300">Workplace Score</span>
              </div>
              <span className="text-white font-semibold">{result.workplace_assessment_score ?? "-"}</span>
            </div>

            {/* Final Report */}
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center">
                  <BookOpen size={14} className="text-slate-400" />
                </div>
                <span className="text-sm text-slate-300">Final Report</span>
              </div>
              <span className="text-white font-semibold">{result.final_report_score ?? "-"}</span>
            </div>
          </div>
          
          {/* Publish Date Footer */}
          {isPublished && (
            <p className="text-xs text-slate-500 mt-4 text-right">
              Published on: {new Date(result.published_at).toLocaleDateString()}
            </p>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-4xl">
      <ApiListPage
        title="Academic Results"
        description="Your final evaluated scores across all internship grading criteria. Official results are published after the review board."
        fetchData={getFinalResults}
        emptyMessage="Your final results have not been calculated or published yet."
        renderItem={renderResultCard}
      />
    </div>
  );
}