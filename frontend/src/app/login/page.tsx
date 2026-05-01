"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation"; // Next.js native router
import { motion } from "framer-motion";
import { 
  Hexagon, 
  User, 
  Lock, 
  ArrowRight, 
  AlertCircle 
} from "lucide-react";

// Using your path alias for the context
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const { login } = useAuth();
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(""); // Clear error when user types
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoggingIn(true);
    
    const { username } = formData;

    // Simulate network delay for the sleek UI feel
    setTimeout(() => {
      // Demo role logic – replace with real authentication later.
      let userRole: "STUDENT" | "SUPERVISOR" | "ADMINISTRATOR" | null = null;
      if (username.toLowerCase() === "student") userRole = "STUDENT";
      else if (username.toLowerCase() === "supervisor") userRole = "SUPERVISOR";
      else if (username.toLowerCase() === "admin") userRole = "ADMINISTRATOR";

      if (userRole) {
        // Set dummy user and navigate via Next.js router.
        login({ username, role: userRole });
        
        if (userRole === "STUDENT") router.push("/student/dashboard");
        else if (userRole === "SUPERVISOR") router.push("/supervisor/dashboard");
        else if (userRole === "ADMINISTRATOR") router.push("/admin/dashboard");
      } else {
        setError("Invalid credentials. Try 'student', 'supervisor', or 'admin'.");
        setIsLoggingIn(false);
      }
    }, 800);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans">
      
      {/* Background Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Brand Header */}
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30 mb-4 shadow-[0_0_30px_rgba(99,102,241,0.2)]">
            <Hexagon size={32} className="text-indigo-400" />
          </div>
          <h1 className="text-3xl font-light text-white tracking-tight">
            Welcome to <span className="font-semibold text-indigo-400">ILES</span>
          </h1>
          <p className="text-slate-500 mt-2 text-sm">
            Internship Learning Evaluation System
          </p>
        </div>

        {/* Login Card */}
        <div className="p-8 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-md shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            
            {/* Error Message Box */}
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }} 
                animate={{ opacity: 1, height: "auto" }} 
                className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center gap-3 text-rose-400 text-sm"
              >
                <AlertCircle size={16} className="shrink-0" />
                <p>{error}</p>
              </motion.div>
            )}

            {/* Username Input */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 ml-1">
                Username
              </label>
              <div className="relative">
                <User size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  name="username"
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all"
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <div className="flex items-center justify-between mb-2 ml-1 mr-1">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Password
                </label>
                <a href="#" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
                  Forgot?
                </a>
              </div>
              <div className="relative">
                <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="password"
                  name="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button 
              type="submit" 
              disabled={isLoggingIn}
              className="w-full flex items-center justify-center gap-2 py-3.5 mt-4 rounded-xl bg-indigo-500 text-white font-medium hover:bg-indigo-600 transition-all shadow-lg shadow-indigo-500/25 disabled:opacity-70 disabled:cursor-not-allowed group"
            >
              {isLoggingIn ? "Authenticating..." : "Sign In"}
              {!isLoggingIn && <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />}
            </button>
          </form>

          {/* Dev Hint */}
          <div className="mt-8 pt-6 border-t border-white/5 text-center">
            <p className="text-xs text-slate-500">
              Demo Access: <span className="text-slate-300">student</span> | <span className="text-slate-300">supervisor</span> | <span className="text-slate-300">admin</span>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}