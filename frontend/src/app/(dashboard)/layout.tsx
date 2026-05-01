"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  LayoutDashboard, 
  Briefcase, 
  FileText, 
  GraduationCap,
  Users,
  UserPlus,
  BarChart,
  ClipboardCheck,
  MessageSquare,
  LogOut,
  Hexagon,
  Loader2 // <-- Added a loading icon
} from "lucide-react";

// Import your auth hook
import { useAuth } from "@/context/AuthContext";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  
  // Pull user data and loading state from context
  const { user, logout, isLoading } = useAuth();

  // Extract the current portal from the URL (e.g., "/admin/dashboard" -> "admin")
  const currentPathSegment = pathname?.split("/")[1] || "student";

  // --- SECURITY CHECK (PROTECTED ROUTE LOGIC) ---
  useEffect(() => {
    // If we are still loading the user from localStorage, do nothing yet
    if (isLoading) return;

    // 1. If there is no user logged in, kick them to the login page
    if (!user) {
      router.push("/login");
      return;
    }

    // 2. Role-Based Access Control (RBAC)
    // Ensure the user's role matches the portal they are trying to access
    const isStudentTryingToAccessStudent = user.role === "STUDENT" && currentPathSegment === "student";
    const isSupervisorTryingToAccessSupervisor = user.role === "SUPERVISOR" && currentPathSegment === "supervisor";
    const isAdminTryingToAccessAdmin = user.role === "ADMINISTRATOR" && currentPathSegment === "admin";

    if (!isStudentTryingToAccessStudent && !isSupervisorTryingToAccessSupervisor && !isAdminTryingToAccessAdmin) {
      // If they are logged in but trying to access a URL they don't have permission for,
      // route them back to their correct dashboard.
      if (user.role === "STUDENT") router.push("/student/dashboard");
      if (user.role === "SUPERVISOR") router.push("/supervisor/dashboard");
      if (user.role === "ADMINISTRATOR") router.push("/admin/dashboard");
    }
  }, [user, isLoading, currentPathSegment, router]);


  // --- DYNAMIC NAVIGATION MENUS ---
  const navigationConfig = {
    student: [
      { name: "Overview", href: "/student/dashboard", icon: LayoutDashboard },
      { name: "My Placements", href: "/student/placements", icon: Briefcase },
      { name: "Weekly Logs", href: "/student/logs", icon: FileText },
      { name: "Final Results", href: "/student/results", icon: GraduationCap },
    ],
    admin: [
      { name: "Intelligence", href: "/admin/dashboard", icon: LayoutDashboard },
      { name: "User Directory", href: "/admin/users", icon: Users },
      { name: "Assignments", href: "/admin/assignments", icon: UserPlus },
      { name: "Placements", href: "/admin/placements", icon: Briefcase },
      { name: "Reports", href: "/admin/reports", icon: BarChart },
    ],
    supervisor: [
      { name: "Overview", href: "/supervisor/dashboard", icon: LayoutDashboard },
      { name: "My Assignments", href: "/supervisor/assignments", icon: Users },
      { name: "Evaluations", href: "/supervisor/evaluations", icon: ClipboardCheck },
      { name: "Logbook Feedback", href: "/supervisor/feedback", icon: MessageSquare },
    ],
  };

  const activeMenu = navigationConfig[currentPathSegment as keyof typeof navigationConfig] || navigationConfig.student;

  // --- LOADING STATE ---
  // Prevent flashing the dashboard UI before the security check is complete
  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mb-4" />
        <p className="text-slate-400 font-light tracking-widest text-xs uppercase">Verifying Credentials...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-indigo-500/30">
      
      {/* --- GLASSY SIDEBAR --- */}
      <aside className="w-72 flex-shrink-0 border-r border-white/5 bg-white/[0.01] flex flex-col hidden md:flex">
        
        {/* Brand Header */}
        <div className="h-20 flex items-center px-8 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
              <Hexagon size={18} className="text-indigo-400" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-widest uppercase">I.L.E.S.</h1>
              <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">Evaluation System</p>
            </div>
          </div>
        </div>

        {/* Dynamic Navigation Links */}
        <nav className="flex-1 px-4 py-8 space-y-2">
          <p className="px-4 text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-4">
            {currentPathSegment} Portal
          </p>
          
          {activeMenu.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link 
                key={item.name} 
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group
                  ${isActive 
                    ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" 
                    : "text-slate-400 border border-transparent hover:bg-white/[0.03] hover:text-slate-200"
                  }`}
              >
                <Icon size={18} className={isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-300 transition-colors"} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User Profile / Logout Area */}
        <div className="p-4 border-t border-white/5">
          {/* Added the logout function to this button! */}
          <button 
            onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-medium text-rose-400/80 hover:bg-rose-500/10 hover:text-rose-400 border border-transparent hover:border-rose-500/20 transition-all"
          >
            <LogOut size={18} />
            Secure Logout
          </button>
        </div>
      </aside>

      {/* --- MAIN CONTENT AREA --- */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-20 border-b border-white/5 bg-white/[0.01] flex items-center justify-between px-8 shrink-0">
          <div className="md:hidden flex items-center gap-3">
             <Hexagon size={24} className="text-indigo-400" />
             <h2 className="font-bold text-white tracking-widest uppercase">I.L.E.S.</h2>
          </div>
          <div className="hidden md:block">
             <p className="text-sm text-slate-400">Welcome, <span className="text-white font-medium">{user.username}</span></p>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-8 hide-scrollbar relative">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none" />
          <div className="relative z-10">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}