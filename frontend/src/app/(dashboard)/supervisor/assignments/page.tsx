"use client";

import React from "react";
import ApiListPage from "@/components/common/ApiListPage"; // Adjust path if needed
import { useAuth } from "@/context/AuthContext"; // Adjust path if needed

// 1. We tell TypeScript exactly what a Supervisor Assignment looks like
interface AssignmentData {
  id: string;
  assignment_role: string;
  is_active: boolean;
  placement: {
    start_date: string;
    end_date: string;
    status: string;
    student: {
      registration_number: string;
      user: {
        username: string;
        first_name: string;
        last_name: string;
      };
    };
    company: {
      company_name: string;
      location: string;
    };
  };
}

export default function SupervisorAssignmentsPage() {
  const { user } = useAuth();

  // 2. The function that fetches the data from Django
  const fetchAssignments = async () => {
    // Replace this with your actual API call using axios or fetch!
    const response = await fetch("http://localhost:8000/api/issues/supervisor-assignments/", {
      headers: {
        "Authorization": `Token ${localStorage.getItem("authToken")}` // Adjust based on your auth
      }
    });
    if (!response.ok) throw new Error("Failed to fetch assignments");
    return response.json();
  };

  // 3. The card renderer you deleted, completely fixed and typed!
  const renderAssignmentCard = (item: AssignmentData) => {
    // Helper to safely format dates
    const formatDate = (dateString: string | undefined) => {
      if (!dateString) return "N/A";
      return new Date(dateString).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    };

    return (
      <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 hover:bg-white/[0.04] transition-colors">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-semibold text-white">
              {item.placement?.company?.company_name || "Unknown Company"}
            </h3>
            <p className="text-slate-400 text-sm mt-1">
              Student: <span className="text-slate-300">{item.placement?.student?.user?.first_name} {item.placement?.student?.user?.last_name}</span> ({item.placement?.student?.registration_number})
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium tracking-wide ${item.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
            {item.is_active ? "ACTIVE" : "INACTIVE"}
          </span>
        </div>
        
        <div className="grid grid-cols-2 gap-4 text-sm mt-4 pt-4 border-t border-white/5">
          <div>
            <span className="block text-[10px] uppercase tracking-wider text-slate-500 mb-1">Assignment Role</span>
            <span className="text-indigo-400 font-medium">{item.assignment_role}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase tracking-wider text-slate-500 mb-1">Placement Duration</span>
            <span className="text-slate-400">
              {formatDate(item.placement?.start_date)} - {formatDate(item.placement?.end_date)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  // 4. Pass everything into the ApiListPage
  return (
    <ApiListPage<AssignmentData>
      title="My Student Assignments"
      description={`Welcome back, ${user?.username}. Here are the students you are currently supervising.`}
      fetchData={fetchAssignments}
      renderItem={renderAssignmentCard}
      emptyMessage="You have not been assigned to supervise any students yet."
    />
  );
}