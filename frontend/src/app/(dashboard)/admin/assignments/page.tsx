"use client";

import React from 'react';
import { UserPlus, ShieldCheck, Building2, UserCog } from 'lucide-react';
import ApiListPage from '@/components/common/ApiListPage';

// Assuming you will create this API file soon, or already have it:
import { getApprovedPlacements } from '@/api/placementsApi';

export default function AdminAssignmentsPage() {
  
  // Custom renderer for each placement "Assignment Card"
  const renderAssignmentCard = (placement: any) => (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 shrink-0">
          <UserCog className="text-indigo-400" size={24} />
        </div>
        <div>
          <h3 className="text-white font-medium">{placement.student_name || "Unregistered Student"}</h3>
          <p className="text-slate-500 text-xs tracking-wide uppercase mt-0.5">
            {placement.registration_number || "REG-PENDING"} • {placement.company_name}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {/* Academic Supervisor Status */}
        <div className={`px-4 py-2 rounded-xl border text-xs flex items-center gap-2 transition-all ${
          placement.academic_supervisor 
          ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400' 
          : 'bg-white/5 border-white/10 text-slate-500'
        }`}>
          <ShieldCheck size={14} />
          {placement.academic_supervisor ? `Academic: ${placement.academic_supervisor}` : 'Academic Unassigned'}
        </div>

        {/* Workplace Supervisor Status */}
        <div className={`px-4 py-2 rounded-xl border text-xs flex items-center gap-2 transition-all ${
          placement.workplace_supervisor 
          ? 'bg-blue-500/5 border-blue-500/20 text-blue-400' 
          : 'bg-white/5 border-white/10 text-slate-500'
        }`}>
          <Building2 size={14} />
          {placement.workplace_supervisor ? `Workplace: ${placement.workplace_supervisor}` : 'Workplace Unassigned'}
        </div>

        {/* Assignment Action Button */}
        <button className="ml-2 p-2 rounded-xl bg-indigo-500/80 hover:bg-indigo-500 text-white transition-all shadow-lg shadow-indigo-500/20">
          <UserPlus size={18} />
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <ApiListPage
          title="Supervisor Assignments"
          description="Manage and audit the linkage between students and their respective Academic and Workplace mentors."
          fetchData={getApprovedPlacements}
          renderItem={renderAssignmentCard}
          emptyMessage="No approved placements require assignment at this time."
        />
      </div>
    </div>
  );
}