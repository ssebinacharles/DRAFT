"use client";

import React from "react";
import { 
  CalendarDays, 
  CheckCircle2, 
  Clock, 
  FileEdit, 
  ClipboardList,
  MessageSquare,
  Award
} from "lucide-react";

import ApiListPage from "@/components/common/ApiListPage";
// Ensure this API file exists in your src/api folder
import { getEvaluations } from "@/api/evaluationsApi"; 

export default function SupervisorEvaluationsPage() {
  
  // Custom renderer for the Evaluation Card
  const renderEvaluationCard = (evaluation: any) => {
    
    // Helper to color-code the status badge
    const getStatusConfig = (status: string) => {
      switch (status?.toLowerCase()) {
        case "completed":
        case "submitted":
          return { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", icon: CheckCircle2 };
        case "pending":
        case "in progress":
          return { color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", icon: Clock };
        case "draft":
          return { color: "text-slate-400", bg: "bg-white/5", border: "border-white/10", icon: FileEdit };
        default:
          return { color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20", icon: ClipboardList };
      }
    };

    const statusConfig = getStatusConfig(evaluation.status);
    const StatusIcon = statusConfig.icon;

    const formatDate = (dateString: string) => {
      if (!dateString) return "Not submitted yet";
      return new Date(dateString).toLocaleDateString();
    };

    return (
      <div className="flex flex-col gap-5 p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all">
        
        {/* Header: Evaluation Type & Status */}
        <div className="flex justify-between items-start border-b border-white/5 pb-4">
          <h3 className="text-lg font-medium text-white m-0">
            {evaluation.evaluation_type || "Unknown Evaluation"}
          </h3>
          <span className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider border ${statusConfig.bg} ${statusConfig.color} ${statusConfig.border}`}>
            <StatusIcon size={14} />
            {evaluation.status || "Unknown"}
          </span>
        </div>

        {/* Metrics Section */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/[0.02] rounded-xl p-4 border border-white/5">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1 flex items-center gap-1.5">
              <Award size={12} /> Total Score
            </p>
            <p className="text-3xl font-bold text-white">
              {evaluation.total_score ?? "-"}
            </p>
          </div>
          <div className="bg-indigo-500/5 rounded-xl p-4 border border-indigo-500/10">
            <p className="text-[10px] text-indigo-400 uppercase tracking-widest font-semibold mb-1 flex items-center gap-1.5">
              <Award size={12} /> Weighted Score
            </p>
            <p className="text-3xl font-bold text-indigo-300">
              {evaluation.weighted_score ?? "-"}
            </p>
          </div>
        </div>

        {/* Remarks Section */}
        <div>
          <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider flex items-center gap-1.5">
            <MessageSquare size={14} /> Remarks
          </p>
          <div className="text-slate-300 text-sm bg-white/[0.01] p-4 rounded-xl border border-white/5">
            {evaluation.remarks ? (
              <p className="whitespace-pre-wrap leading-relaxed">{evaluation.remarks}</p>
            ) : (
              <span className="italic text-slate-500">No remarks provided for this evaluation.</span>
            )}
          </div>
        </div>

        {/* Footer: Submission Date */}
        <div className="flex justify-end items-center text-xs text-slate-500 mt-1 pt-4 border-t border-white/5">
          <div className="flex items-center gap-1.5">
            <CalendarDays size={14} />
            <span>Submitted: {formatDate(evaluation.submitted_at)}</span>
          </div>
        </div>
        
      </div>
    );
  };

  return (
    <div className="max-w-4xl">
      <ApiListPage
        title="Internship Evaluations"
        description="Review detailed evaluations, scores, and remarks for the internship program."
        fetchData={getEvaluations}
        emptyMessage="No evaluations found yet. Check back later!"
        renderItem={renderEvaluationCard}
      />
    </div>
  );
}