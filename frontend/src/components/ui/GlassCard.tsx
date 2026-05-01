import React from 'react';

// Notice this is a Named Export (export const), so you must import it with { GlassCard }
export const GlassCard = ({ 
  children, 
  className = "" 
}: { 
  children: React.ReactNode; 
  className?: string; 
}) => {
  return (
    <div className={`bg-white/[0.03] backdrop-blur-md border border-white/10 rounded-3xl p-6 shadow-xl ${className}`}>
      {children}
    </div>
  );
};