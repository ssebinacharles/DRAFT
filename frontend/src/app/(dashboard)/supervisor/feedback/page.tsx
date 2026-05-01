"use client";

import React from "react";
import { 
  UserCircle, 
  CalendarDays, 
  CheckCircle2, 
  AlertCircle, 
  XCircle,
  MessageSquareQuote,
  Clock
} from "lucide-react";

import ApiListPage from "@/components/common/ApiListPage";
// Ensure this API file exists in your src/api folder
import { getFeedback } from "@/api/feedbackApi"; 

export default function SupervisorFeedbackPage() {
  
  // Custom renderer for the Feedback Card
  const renderFeedbackCard = (feedback: any) => {
    
    // Dynamic Status Colors
    const getDecisionConfig = (decision: string) => {
      switch (decision?.toLowerCase()) {
        case "approved":
          return { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", icon: CheckCircle2 };
        case "needs revision":
          return { color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", icon: AlertCircle };
        case "rejected":
          return { color: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/20", icon: XCircle };
        default:
          return { color: "text-slate-400", bg: "bg-white/5", border: "border-white/10", icon: Clock };
      }
    };

    const decisionConfig = getDecisionConfig(feedback.decision);
    const DecisionIcon = decisionConfig.icon;

    return (
      <div className="flex flex-col gap-4 p-5 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all">
        
        {/* Header Section: Decision & Latest Badge */}
        <div className="flex justify-between items-start border-b border-white/5 pb-4">
          <span className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider border ${decisionConfig.bg} ${decisionConfig.color} ${decisionConfig.border}`}>
            <DecisionIcon size={14} />
            {feedback.decision || "Pending Review"}
          </span>
          
          {feedback.is_latest && (
            <span className="bg-indigo-500/20 text-indigo-300 text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-md border border-indigo-500/30">
              Latest Update
            </span>
          )}
        </div>

        {/* Body Section: The actual feedback comment */}
        <div className="py-2">
          <div className="flex items-start gap-3">
            <MessageSquareQuote size={18} className="text-indigo-400 shrink-0 mt-0.5" />
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
              {feedback.comment || <span className="italic text-slate-500">No additional comments provided.</span>}
            </p>
          </div>
        </div>

        {/* Footer Section: Metadata */}
        <div className="flex justify-between items-center text-xs text-slate-500 border-t border-white/5 pt-4 mt-2">
          <div className="flex items-center gap-2">
            <UserCircle size={16} className="text-slate-400" />
            <span className="font-medium text-slate-300">
              {feedback.supervisor?.user?.username || "Unassigned Supervisor"}
            </span>
          </div>
          
          {feedback.created_at && (
            <div className="flex items-center gap-1.5">
              <CalendarDays size={14} />
              <span>{new Date(feedback.created_at).toLocaleDateString()}</span>
            </div>
          )}
        </div>
        
      </div>
    );
  };

  return (
    <div className="max-w-4xl">
      <ApiListPage
        title="Logbook Feedback"
        description="Review decisions and official commentary provided on weekly student logs."
        fetchData={getFeedback}
        emptyMessage="No feedback records found yet."
        renderItem={renderFeedbackCard}
      />
    </div>
  );
}