import React from 'react';
import { AlertTriangle, Clock, ArrowRight } from 'lucide-react';

/**
 * Alerts Component (Role 4 - UI/UX)
 * Urgent high-visibility flashing banner displayed upon detecting mule transactions > ₹50,000.
 */
const Alerts = ({ alert }) => {
  if (!alert) return null;

  return (
    <div className="bg-red-950/80 border-y border-red-500/50 px-6 py-2.5 flex items-center justify-between text-xs backdrop-blur animate-pulse select-none">
      <div className="flex items-center gap-3">
        <span className="p-1 bg-red-600 text-white rounded font-black tracking-wider flex items-center gap-1 text-[11px]">
          <AlertTriangle className="w-3.5 h-3.5" />
          ACTIVE FRAUD ALERT
        </span>
        <span className="text-red-200 font-mono">
          Case <strong className="text-white">{alert.case_id || 'CYB-2026-0098'}</strong>:
          Suspected Mule Account <strong className="text-white font-mono">{alert.mule_account || 'ACC-984321'}</strong>
        </span>
      </div>

      <div className="flex items-center gap-4 text-red-300 font-mono">
        <span className="flex items-center gap-1 bg-red-900/50 px-2 py-0.5 rounded border border-red-500/30">
          <Clock className="w-3.5 h-3.5 text-amber-400" />
          Predicted Cashout Window: <strong className="text-amber-400 font-bold ml-1">{alert.time_window || '25 - 40 Mins'}</strong>
        </span>
        <span className="text-slate-300 font-bold">
          Amount: <span className="text-emerald-400 font-mono font-bold">₹{(alert.amount || 75000).toLocaleString('en-IN')}</span>
        </span>
      </div>
    </div>
  );
};

export default Alerts;
