import React from 'react';
import { ArrowRight, UserCheck, ShieldOff, Building2, Banknote } from 'lucide-react';

/**
 * CaseFlow Component (Role 4 - UI/UX)
 * Visual money trail showing Victim Account -> Compromised Amount -> Mule Cascade -> Predicted ATM.
 */
const CaseFlow = ({
  victim = 'VICTIM-AC-1029',
  mule = 'MULE-AC-9941',
  amount = 75000,
  predictedAtm = 'SBI ATM #092 (Connaught Place)'
}) => {
  return (
    <div className="bg-slate-900/80 border border-cyan-500/20 rounded-xl p-4 shadow-lg backdrop-blur">
      <h3 className="text-xs font-mono text-cyan-400 font-semibold tracking-wider uppercase mb-3 flex items-center gap-2">
        <Banknote className="w-4 h-4 text-cyan-400" />
        Transaction Velocity & Money Trail
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-2 items-center text-xs font-mono">
        {/* Node 1: Victim */}
        <div className="bg-slate-950/80 border border-slate-800 p-2.5 rounded-lg">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <UserCheck className="w-3 h-3 text-emerald-400" />
            <span>ORIGIN VICTIM</span>
          </div>
          <div className="font-semibold text-slate-200 truncate">{victim}</div>
          <div className="text-[10px] text-emerald-400 font-bold mt-1">-₹{amount.toLocaleString('en-IN')}</div>
        </div>

        {/* Node 2: Cascade */}
        <div className="bg-slate-950/80 border border-red-900/50 p-2.5 rounded-lg">
          <div className="flex items-center gap-1.5 text-red-400 text-[10px] mb-1">
            <ShieldOff className="w-3 h-3 text-red-400" />
            <span>PRIMARY MULE</span>
          </div>
          <div className="font-semibold text-red-300 truncate">{mule}</div>
          <div className="text-[10px] text-red-400 font-bold mt-1">Status: Flagged Tier-1</div>
        </div>

        {/* Node 3: Amount In Transit */}
        <div className="bg-slate-950/80 border border-amber-500/30 p-2.5 rounded-lg">
          <div className="text-[10px] text-amber-400 mb-1">IN TRANSIT / TIME</div>
          <div className="text-sm font-bold text-amber-300">₹{amount.toLocaleString('en-IN')}</div>
          <div className="text-[10px] text-slate-400 mt-1">Velocity: Fast Drain</div>
        </div>

        {/* Node 4: Target ATM */}
        <div className="bg-slate-950/80 border border-cyan-500/40 p-2.5 rounded-lg">
          <div className="flex items-center gap-1.5 text-cyan-400 text-[10px] mb-1">
            <Building2 className="w-3 h-3 text-cyan-400" />
            <span>PREDICTED CASHOUT</span>
          </div>
          <div className="font-semibold text-cyan-300 truncate">{predictedAtm}</div>
          <div className="text-[10px] text-cyan-400 font-bold mt-1">Interception Target</div>
        </div>
      </div>
    </div>
  );
};

export default CaseFlow;
