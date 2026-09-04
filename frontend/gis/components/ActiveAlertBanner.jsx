import React from 'react';

/**
 * ActiveAlertBanner Component (Role 3 - GIS Radar)
 * Project Drishti - Tactical Live Incident Alert HUD
 * 
 * Renders the top-level incident banner when a high-risk cashout alert is active.
 * Shows Alert ID, Defrauded Amount, Mule Account, and a 1-click Focus action.
 */
export const ActiveAlertBanner = ({
  activeAlert = null,
  onFocusPrimeTarget = () => {}
}) => {
  if (!activeAlert) return null;

  const alertId = activeAlert.alertId || activeAlert.alert_id || 'ALT-2026-LIVE';
  const amount = activeAlert.defraudedAmount || activeAlert.defrauded_amount || '₹ 1,85,000';
  const muleAcc = activeAlert.muleAccount || activeAlert.mule_account || 'XXXX-8821 (SBI)';
  // `?? 0.94` invented a 94% confidence for any alert whose score did not
  // resolve — and the badge below said "CRITICAL" unconditionally, so a LOW
  // alert still read "CRITICAL CASH-OUT RISK (94%)". Both come from the model
  // now, or are not shown.
  const riskScore = activeAlert.riskScore ?? activeAlert.risk_score ?? null;
  const scorePercent = typeof riskScore === 'number' && !isNaN(riskScore)
    ? Math.round(riskScore * 100) : null;
  const topTier = String(
    activeAlert.targets?.[0]?.riskTier || activeAlert.riskTier || ''
  ).toUpperCase();
  const withdrawalWindow = activeAlert.withdrawalWindow || (
    activeAlert.withdrawal_window?.min && activeAlert.withdrawal_window?.max
      ? `${activeAlert.withdrawal_window.min}–${activeAlert.withdrawal_window.max} mins`
      : null
  );
  const degraded = activeAlert.degraded === true;

  const tierStyle = degraded
    ? 'bg-rose-600 text-white border-rose-300 font-bold'
    : topTier === 'CRITICAL' ? 'bg-red-500/20 text-red-300 border-red-500/40'
    : topTier === 'HIGH' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
    : topTier === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-200 border-yellow-500/40'
    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';

  return (
    <div className={`w-full bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl flex flex-wrap items-center justify-between gap-3 text-slate-100 font-sans ${
      degraded ? 'border-rose-500 shadow-rose-950/40' : 'border-red-500/40 shadow-red-950/30'
    }`}>
      {/* Left: Tactical Badge & Alert Info */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-red-600 text-white font-mono font-black text-sm shadow-md shadow-red-600/50 flex-shrink-0 animate-pulse">
          🚨
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono font-bold text-xs text-red-400 uppercase tracking-wide">
              {alertId}
            </span>
            <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border font-bold ${tierStyle}`}>
              {degraded
                ? 'DEGRADED — HEURISTIC, NOT A PREDICTION'
                : `${topTier || 'CASH-OUT'} RISK${scorePercent !== null ? ` (${scorePercent}%)` : ''}`}
            </span>
          </div>
          <p className="text-xs text-slate-300 truncate mt-0.5">
            Defrauded: <span className="text-white font-bold font-mono">{amount}</span> • Mule: <span className="text-cyan-300 font-mono">{muleAcc}</span>
          </p>
        </div>
      </div>

      {/* Right: Withdrawal Window & Action Button */}
      <div className="flex items-center gap-2.5 flex-shrink-0">
        <div className="hidden sm:block text-right font-mono text-[11px] pr-2 border-r border-slate-800">
          <span className="text-slate-400 block text-[9px] uppercase">Window</span>
          <span className="text-amber-300 font-bold">
            {withdrawalWindow || <span className="text-slate-500">not predicted</span>}
          </span>
        </div>

        <button
          type="button"
          onClick={onFocusPrimeTarget}
          className="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-mono font-bold text-xs transition-all duration-150 shadow-md shadow-red-900/50 flex items-center gap-1.5 active:scale-95"
        >
          <span>🎯 Focus #1 Target</span>
        </button>
      </div>
    </div>
  );
};

export default ActiveAlertBanner;
