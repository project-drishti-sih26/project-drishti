import React, { useState, useEffect } from 'react';
import { ShieldAlert, Radio, Clock, Activity, FileText } from 'lucide-react';

/**
 * Header Component (Role 4 - UI/UX)
 * Cyber command center status bar with I4C agency branding, live clock, and dispatch trigger.
 */
const Header = ({ onOpenDispatch = () => {}, isConnected = true, activeAlertCount = 1 }) => {
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-IN', { hour12: false }) + ' IST');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 px-6 bg-slate-950/90 border-b border-cyan-500/20 backdrop-blur flex items-center justify-between select-none">
      {/* Brand & Project Identity */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-red-950/40 border border-red-500/40 flex items-center justify-center">
          <ShieldAlert className="w-6 h-6 text-red-500 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold tracking-wider text-slate-100 font-mono">
              PROJECT DRISHTI
            </h1>
            <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-widest bg-cyan-950 text-cyan-400 border border-cyan-500/40 rounded">
              I4C RADAR
            </span>
          </div>
          <p className="text-xs text-slate-400">
            National Cybercrime Predictive Interception System
          </p>
        </div>
      </div>

      {/* Center Operational Status */}
      <div className="hidden md:flex items-center gap-6 text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="text-slate-400">STATUS:</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-ping' : 'bg-red-500'}`} />
            {isConnected ? 'LIVE FEED CONNECTED' : 'DISCONNECTED'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Radio className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">ACTIVE CASHOUTS:</span>
          <span className="text-red-400 font-bold bg-red-950/60 px-2 py-0.5 rounded border border-red-500/30">
            {activeAlertCount} CRITICAL
          </span>
        </div>

        <div className="flex items-center gap-2 text-slate-300">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{currentTime || '00:00:00 IST'}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenDispatch}
          className="flex items-center gap-2 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded-lg transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)] cursor-pointer"
        >
          <FileText className="w-4 h-4" />
          <span>POLICE DISPATCH PDF</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
