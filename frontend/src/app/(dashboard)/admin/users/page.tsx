"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Users, 
  GraduationCap, 
  Briefcase, 
  ShieldCheck, 
  Search, 
  Loader2, 
  AlertCircle,
  Mail
} from "lucide-react";

// Assuming these are your API calls located in src/api/usersApi.js
import {
  getUsers,
  getStudents,
  getSupervisors,
  getAdministrators,
} from "@/api/usersApi"; // Note: Using the '@' alias if configured, or '../../../../../api/usersApi'

export default function AdminUsersPage() {
  const [data, setData] = useState({
    users: [],
    students: [],
    supervisors: [],
    administrators: [],
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("students");

  const normalize = (response: any) => {
    if (Array.isArray(response)) return response;
    if (response && Array.isArray(response.results)) return response.results;
    return [];
  };

  useEffect(() => {
    let isMounted = true;

    // Fetch all directories simultaneously 
    Promise.all([
      getUsers(),
      getStudents(),
      getSupervisors(),
      getAdministrators(),
    ])
      .then(([users, students, supervisors, administrators]) => {
        if (isMounted) {
          setData({
            users: normalize(users),
            students: normalize(students),
            supervisors: normalize(supervisors),
            administrators: normalize(administrators),
          });
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Failed to load user directories.");
          setLoading(false);
        }
      });

    return () => { isMounted = false; };
  }, []);

  const tabs = [
    { id: "students", label: "Students", icon: GraduationCap, count: data.students.length },
    { id: "supervisors", label: "Supervisors", icon: Briefcase, count: data.supervisors.length },
    { id: "administrators", label: "Administrators", icon: ShieldCheck, count: data.administrators.length },
    { id: "users", label: "All Accounts", icon: Users, count: data.users.length },
  ];

  // --- LOADING STATE ---
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-slate-400 font-light tracking-widest text-xs uppercase">Loading Directory...</p>
      </div>
    );
  }

  // --- ERROR STATE ---
  if (error) {
    return (
      <div className="p-8 rounded-3xl bg-rose-500/5 border border-rose-500/20 backdrop-blur-md">
        <div className="flex items-center gap-3 text-rose-400 mb-2">
          <AlertCircle size={20} />
          <h3 className="font-semibold">Directory Sync Error</h3>
        </div>
        <p className="text-slate-400 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* HEADER & SEARCH */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-light text-white tracking-tight">
            User <span className="font-semibold text-indigo-400">Directory</span>
          </h1>
          <p className="text-slate-500 mt-1 text-sm">Manage system access, roles, and profiles.</p>
        </div>

        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search users..." 
            className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all"
          />
        </div>
      </div>

      {/* GLASSY TABS */}
      <div className="flex overflow-x-auto p-1 bg-white/[0.02] border border-white/5 rounded-2xl gap-1 hide-scrollbar">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap
                ${isActive 
                  ? "bg-white/10 text-white shadow-lg" 
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"}`}
            >
              <tab.icon size={16} className={isActive ? "text-indigo-400" : ""} />
              {tab.label}
              <span className={`ml-2 px-2 py-0.5 rounded-md text-[10px] ${isActive ? "bg-indigo-500/20 text-indigo-300" : "bg-white/5"}`}>
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* DYNAMIC CONTENT GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AnimatePresence mode="popLayout">
          
          {/* RENDER STUDENTS */}
          {activeTab === "students" && data.students.map((student: any, i) => (
            <motion.div key={student.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }} className="p-5 rounded-2xl bg-white/[0.03] border border-white/10 hover:border-emerald-500/30 transition-colors">
              <div className="flex justify-between items-start mb-3">
                <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                  <GraduationCap className="text-emerald-400" size={18} />
                </div>
                <span className="text-[10px] uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-md border border-emerald-500/20">
                  {student.course || "Course N/A"}
                </span>
              </div>
              <h3 className="text-white font-medium">{student.registration_number}</h3>
              <p className="text-slate-500 text-xs mt-1">{student.department || "Unassigned Dept"}</p>
            </motion.div>
          ))}

          {/* RENDER SUPERVISORS */}
          {activeTab === "supervisors" && data.supervisors.map((sup: any, i) => (
            <motion.div key={sup.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }} className="p-5 rounded-2xl bg-white/[0.03] border border-white/10 hover:border-blue-500/30 transition-colors">
              <div className="flex justify-between items-start mb-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                  <Briefcase className="text-blue-400" size={18} />
                </div>
                <span className="text-[10px] uppercase tracking-wider text-blue-400 bg-blue-500/10 px-2 py-1 rounded-md border border-blue-500/20">
                  {sup.supervisor_type || "Type N/A"}
                </span>
              </div>
              <h3 className="text-white font-medium">{sup.user?.username || "Unnamed Supervisor"}</h3>
              <p className="text-slate-500 text-xs mt-1">{sup.organization_name || "Academic Faculty"}</p>
            </motion.div>
          ))}

          {/* RENDER ADMINISTRATORS */}
          {activeTab === "administrators" && data.administrators.map((admin: any, i) => (
            <motion.div key={admin.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }} className="p-5 rounded-2xl bg-white/[0.03] border border-white/10 hover:border-indigo-500/30 transition-colors">
              <div className="flex justify-between items-start mb-3">
                <div className="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
                  <ShieldCheck className="text-indigo-400" size={18} />
                </div>
                <span className="text-[10px] uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded-md border border-indigo-500/20">
                  System Admin
                </span>
              </div>
              <h3 className="text-white font-medium">{admin.user?.username || "Administrator"}</h3>
              <p className="text-slate-500 text-xs mt-1">{admin.office_name || "Main Office"}</p>
            </motion.div>
          ))}

          {/* RENDER ALL USERS (RAW DATA) */}
          {activeTab === "users" && data.users.map((user: any, i) => (
            <motion.div key={user.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }} className="p-5 rounded-2xl bg-white/[0.01] border border-white/5 flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center border border-white/10 shrink-0">
                <span className="text-xs text-slate-400">{user.username?.charAt(0).toUpperCase()}</span>
              </div>
              <div className="overflow-hidden">
                <h3 className="text-white font-medium text-sm truncate">{user.username}</h3>
                <p className="text-slate-500 text-xs truncate flex items-center gap-1 mt-0.5">
                  <Mail size={10} /> {user.email}
                </p>
              </div>
            </motion.div>
          ))}

        </AnimatePresence>
      </div>

      {/* EMPTY STATE */}
      {data[activeTab as keyof typeof data]?.length === 0 && (
        <div className="py-20 text-center rounded-3xl bg-white/[0.02] border border-white/5">
          <Users className="w-12 h-12 text-slate-700 mx-auto mb-4" />
          <p className="text-slate-500 italic">No records found for {activeTab}.</p>
        </div>
      )}
    </div>
  );
}