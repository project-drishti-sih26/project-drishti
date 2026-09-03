import React from 'react';
import { Shield, AlertCircle, TrendingUp, DollarSign, Database } from 'lucide-react';
import FeedbackActions from './FeedbackActions';

/**
 * SidebarLeft Component (Role 4 - UI/UX)
 * Displays case metadata, active suspects, transaction metrics, and human-in-the-loop action buttons.
 */
const SidebarLeft = ({
  caseData = {
    case_id: 'CYB-2026-00491',
    victim_account: 'SBIN-0019284',
    mule_account: 'HDFC-8839201',
    compromised_amount: 85000,
    timestamp: '21:42:10 IST',
    risk_level: 'CRITICAL (0.94)'
  },
  onFeedback = () => {}
}) => {
  return (
    <aside className="w-80 h-full flex flex-col gap-4 p-4 bg-slate-950/90 border-r border-slate-800/80 overflow-y-auto font-sans">
      {/* Case Dossier Card */}
      <div className="bg-slate-900/90 border border-cyan-500/30 rounded-xl p-4 shadow-md">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              CASE DOSSIER
            </h2>
          </div>
          <span className="text-[11px] font-mono font-bold text-red-400 bg-red-950 px-2 py-0.5 rounded border border-red-500/30">
            {caseData.risk_level || 'CRITICAL'}
          </span>
        </div>

        <div className="mt-3 space-y-2.5 text-xs">
          <div>
            <span className="text-slate-400 font-mono text-[11px] block">CASE REFERENCE:</span>
            <span className="font-mono font-bold text-cyan-300">{caseData.case_id}</span>
          </div>

          <div>
            <span className="text-slate-400 font-mono text-[11px] block">VICTIM ACCOUNT:</span>
            <span className="font-mono text-slate-200">{caseData.victim_account}</span>
          </div>

          <div>
            <span className="text-slate-400 font-mono text-[11px] block">MULE CASH-OUT VEHICLE:</span>
            <span className="font-mono text-red-400 font-semibold">{caseData.mule_account}</span>
          </div>

          <div>
            <span className="text-slate-400 font-mono text-[11px] block">SIPHONED SUM:</span>
            <span className="font-mono text-base font-extrabold text-emerald-400">
              ₹{Number(caseData.compromised_amount).toLocaleString('en-IN')}
            </span>
          </div>

          <div>
            <span className="text-slate-400 font-mono text-[11px] block">DETECTION TIME:</span>
            <span className="font-mono text-slate-300">{caseData.timestamp}</span>
          </div>
        </div>
      </div>

      {/* Model Trigger Heuristics */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
        <h3 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <TrendingUp className="w-3.5 h-3.5 text-amber-400" />
          TRIGGER HEURISTICS
        </h3>
        <ul className="text-[11px] space-y-1.5 text-slate-400">
          <li className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Amount &gt; ₹50,000 threshold passed</span>
          </li>
          <li className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Mule network topology match (&gt;0.88)</span>
          </li>
          <li className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Fast cashout velocity profile</span>
          </li>
        </ul>
      </div>

      {/* Human-In-The-Loop Action Buttons */}
      <div className="mt-auto">
        <FeedbackActions onFeedback={onFeedback} />
      </div>
    </aside>
  );
};

export default SidebarLeft;
