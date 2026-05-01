"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { MapPinOff, ArrowLeft, Home } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans text-slate-200">
      
      {/* Background Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none" />

      {/* Main Glassy Container */}
      <motion.div 
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative z-10 max-w-lg w-full p-8 md:p-12 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-md shadow-2xl flex flex-col items-center text-center"
      >
        <div className="w-20 h-20 rounded-2xl bg-rose-500/10 flex items-center justify-center border border-rose-500/20 mb-6 shadow-inner">
          <MapPinOff size={40} className="text-rose-400" />
        </div>

        <h1 className="text-6xl font-bold text-white tracking-tighter mb-2">404</h1>
        <h2 className="text-xl font-medium text-slate-300 mb-4 tracking-wide uppercase">Destination Unknown</h2>
        
        <p className="text-slate-500 text-sm leading-relaxed mb-8 max-w-sm">
          The page you are looking for has either been moved, deleted, or never existed in the system directory.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
          <button 
            onClick={() => window.history.back()}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white/5 text-white font-medium text-sm hover:bg-white/10 transition-colors border border-white/10"
          >
            <ArrowLeft size={16} />
            Go Back
          </button>
          
          <Link href="/" className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-indigo-500 text-white font-medium text-sm hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-500/20">
            <Home size={16} />
            Return to Portal
          </Link>
        </div>
      </motion.div>

      {/* Footer Branding */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="absolute bottom-8 text-center"
      >
        <p className="text-[10px] text-slate-600 uppercase tracking-widest font-bold">
          Internship Learning Evaluation System
        </p>
      </motion.div>

    </div>
  );
}