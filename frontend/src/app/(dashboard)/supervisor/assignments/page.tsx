"use client";

import React from "react";
import { 
  CalendarDays, 
  UserCog, 
  CheckCircle2, 
  XCircle,
  ShieldCheck
} from "lucide-react";

import ApiListPage from "@/components/common/ApiListPage";
// Ensure this API file exists in your src/api folder
import { getSupervisorAssignments } from "@/api/supervisorAssignmentsApi"; 

export default function SupervisorAssignmentsPage() {
  
  // Custom renderer for the Assignment Card
  const renderAssignmentCard = (assignment: any) => {
    // Helper to safely format dates
    const formatDate = (dateString: string) => {
      if (!dateString) return "Date not available";
      return new Date(dateString).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    };

    // Safely get the supervisor's name
    const supervisorName = assignment.supervisor?.user?.username || "Unassigned";
    const initial = supervisorName.charAt(0).toUpperCase();

    return (
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 p-5 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] hover:border-white/10 transition-all group">
        
        {/* Left side: Avatar, Supervisor Info & Role */}
        <div className="flex items-center gap-4">
          {/* Glassy Avatar Circle */}
          <div className="w-12 h-12 flex-shrink-0 bg-indigo-500/10 text-indigo-400 rounded-full flex items-center justify-center font-bold text-lg border border-indigo-500/20 group-hover:scale-105 transition-transform">
            {initial}
          </div>

          <div>
            <h3 className="text-lg font-medium text-white m-0 flex items-center gap-2">
              {supervisorName}
            </h3>
            <p className="text-sm text-slate-400 mt-1 flex items-center gap-1.5">
              <ShieldCheck size={14} className="text-indigo-400" />
              Role: <span className="text-slate-300">{assignment.assignment_role || "Standard Supervisor"}</span>
            </p>
          </div>
        </div>

        {/* Right side: Status Badge and Date */}
        <div className="flex flex-col items-start sm:items-end gap-3 mt-2 sm:mt-0">
          
          {/* Active/Inactive Status Badge */}
          {assignment.is_active ? (
            <span className="flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 text-[10px] uppercase tracking-widest font-bold px-3 py-1.5 rounded-xl border border-emerald-500/20">
              <CheckCircle2 size={14} /> Active
            </span>
          ) : (
            <span className="flex items-center gap-1.5 bg-white/5 text-slate-400 text-[10px] uppercase tracking-widest font-bold px-3 py-1.5 rounded-xl border border-white/10">
              <XCircle size={14} /> Inactive
            </span>
          )}

          {/* Formatted Date */}
          <div className="text-xs text-slate-500 flex items-center gap-1.5">
            <CalendarDays size={14} className="text-slate-600" />
            <span>Assigned: {formatDate(assignment.assigned_at)}</span>
          </div>
        </div>

      </div>
    );
  };

  return (
    <div className="max-w-5xl">
      <ApiListPage
        title="My Assignments"
        description="View your active and past student oversight assignments for current internship placements."
        fetchData={getSupervisorAssignments}
        emptyMessage="You have no active supervisor assignments at this time."
        renderItem={renderAssignmentCard}
      />
    </div>
  );
}