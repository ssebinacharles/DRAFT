"use client";

import React from "react";
import { 
  Building2, 
  Calendar, 
  Briefcase, 
  CheckCircle2, 
  XCircle, 
  Clock,
  AlertOctagon
} from "lucide-react";

import ApiListPage from "@/components/common/ApiListPage";
import { getPlacements } from "@/api/placementsApi"; // Ensure this uses your @ alias

export default function StudentPlacementPage() {
  
  // Helper function to color-code the status badge
  const getStatusConfig = (status: string) => {
    const s = status?.toUpperCase() || "PENDING";
    if (s === "APPROVED") return { color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", icon: CheckCircle2 };
    if (s === "REJECTED") return { color: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/20", icon: XCircle };
    return { color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", icon: Clock };
  };

  // The upgraded Glassy Card for each placement
  const renderPlacementCard = (placement: any) => {
    const statusConfig = getStatusConfig(placement.status);
    const StatusIcon = statusConfig.icon;

    return (
      <div className="flex flex-col gap-6">
        {/* Top Row: Company & Status */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-white/5 pb-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center border border-white/10 shrink-0">
              <Building2 className="text-slate-400" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-medium text-white">
                {placement.company?.company_name || "Company Details Pending"}
              </h2>
              <p className="text-slate-400 text-sm mt-1 flex items-center gap-2">
                <Briefcase size={14} /> 
                {placement.org_department || "Department not specified"}
              </p>
            </div>
          </div>
          
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-bold tracking-wider uppercase ${statusConfig.bg} ${statusConfig.color} ${statusConfig.border}`}>
            <StatusIcon size={14} />
            {placement.status || "PENDING"}
          </div>
        </div>

        {/* Middle Row: Dates & Details */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/5">
            <Calendar className="text-indigo-400" size={18} />
            <div>
              <p className="text-slate-500 text-[10px] uppercase tracking-widest">Start Date</p>
              <p className="text-white font-medium">{placement.start_date || "TBD"}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/5">
            <Calendar className="text-indigo-400" size={18} />
            <div>
              <p className="text-slate-500 text-[10px] uppercase tracking-widest">End Date</p>
              <p className="text-white font-medium">{placement.end_date || "TBD"}</p>
            </div>
          </div>
        </div>

        {/* Bottom Row: Rejection Reason (Only shows if rejected) */}
        {placement.status?.toUpperCase() === "REJECTED" && placement.rejection_reason && (
          <div className="mt-2 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-3">
            <AlertOctagon className="text-rose-400 shrink-0 mt-0.5" size={18} />
            <div>
              <p className="text-rose-400 text-xs font-bold uppercase tracking-wider mb-1">Reason for Rejection</p>
              <p className="text-slate-300 text-sm">{placement.rejection_reason}</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <ApiListPage
      title="My Placements"
      description="Track the status of your internship applications and current organizational assignments."
      fetchData={getPlacements}
      emptyMessage="You have not submitted any placement records yet."
      renderItem={renderPlacementCard}
    />
  );
}