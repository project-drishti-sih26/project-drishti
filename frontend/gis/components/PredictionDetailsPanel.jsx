import React from 'react';

/**
 * PredictionDetailsPanel Component (Role 3 - GIS Radar)
 * Project Drishti - Tactical Target Analysis HUD
 * 
 * Displays in-depth predictive intelligence for the currently selected cashout target:
 * - Target Name, Type, Address & Ranking
 * - Risk Probability & Threat Level
 * - Expected Cash-Out Withdrawal Window (ETA)
 * - "Why This Location?" dynamic ML explainability reasons / SHAP factors
 */
export const PredictionDetailsPanel = ({
  selectedTarget = null,
  activeAlert = null,
  onFlyTo = null
}) => {
  if (!selectedTarget) {
    return (
      <div className="bg-slate-950/90 backdrop-blur-md border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-slate-600"></span>
          <span>SELECT A PREDICTED TARGET ON THE RADAR</span>
        </div>
      </div>
    );
  }

  const rank = selectedTarget.rank || 1;
  // Every `||` default in this block used to manufacture a plausible-looking
  // number when the real one was missing: an 80% risk score, a "20-40 mins"
  // window, a "15 mins" ETA, and three generic sentences dressed as model
  // reasoning. On a dispatch panel that is not a graceful degradation, it is a
  // fabricated prediction. Missing data now reads as missing.
  const scorePercent = selectedTarget.scorePercent
    ?? (typeof selectedTarget.riskScore === 'number' && selectedTarget.hasRealScore !== false
      ? Math.round(selectedTarget.riskScore * 100)
      : null);
  const tier = String(selectedTarget.riskTier || '').toUpperCase();
  const type = selectedTarget.type || 'ATM';
  // The interception window belongs to the case, not to a single ATM.
  const withdrawalWindow = selectedTarget.expectedWindow || activeAlert?.withdrawalWindow || null;
  const travelTime = selectedTarget.travelTime || null;

  // Real SHAP attributions for this target; alert-level reasons as a second
  // choice. No invented third option.
  const rawExplanations = selectedTarget.explanations
    || selectedTarget.reasons
    || (selectedTarget.explanation ? [selectedTarget.explanation] : null)
    || activeAlert?.explanation
    || [];
  const explanations = (Array.isArray(rawExplanations) ? rawExplanations : [rawExplanations])
    .filter((r) => typeof r === 'string' && r.trim().length > 0);


  // Tactical badge styling
  let typeBadge = { label: 'ATM', bg: 'bg-red-500/20 text-red-400 border-red-500/40' };
  if (type.toLowerCase().includes('branch')) {
    typeBadge = { label: 'BANK BRANCH', bg: 'bg-blue-500/20 text-blue-400 border-blue-500/40' };
  } else if (type.toLowerCase().includes('bc') || type.toLowerCase().includes('point')) {
    typeBadge = { label: 'BC POINT', bg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' };
  }

  return (
    <div className="w-full max-w-sm bg-slate-950/95 backdrop-blur-md border border-cyan-500/40 rounded-xl p-4 shadow-2xl shadow-cyan-950/40 text-slate-200 font-sans space-y-3.5">
      {/* Header / Target Identifier */}
      <div className="flex items-start justify-between gap-2 pb-2.5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`px-2 py-0.5 rounded text-xs font-mono font-bold uppercase tracking-wide border ${
                rank === 1
                  ? 'bg-red-500/30 text-red-400 border-red-500/60 shadow-[0_0_8px_rgba(239,68,68,0.4)]'
                  : rank <= 3
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
                  : 'bg-slate-800 text-cyan-300 border-cyan-500/40'
              }`}
            >
              RANK #{rank}
            </span>
            <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded border ${typeBadge.bg}`}>
              {typeBadge.label}
            </span>
          </div>
          <h4 className="font-bold text-sm text-white leading-tight">
            {selectedTarget.name || 'Predicted Target Node'}
          </h4>
          {selectedTarget.address && (
            <p className="text-xs text-slate-400 mt-0.5 leading-snug">
              📍 {selectedTarget.address}
            </p>
          )}
        </div>

        {/* Risk Percentage Box */}
        <div className="flex-shrink-0 text-right bg-slate-900/80 px-2.5 py-1 rounded-lg border border-slate-700">
          <div className={`text-base font-black font-mono leading-none ${
            tier === 'CRITICAL' ? 'text-red-400'
              : tier === 'HIGH' ? 'text-amber-400'
              : tier === 'MEDIUM' ? 'text-yellow-300'
              : 'text-emerald-400'
          }`}>
            {scorePercent !== null ? `${scorePercent}%` : '—'}
          </div>
          <div className="text-xs font-mono text-slate-400 uppercase tracking-tight mt-0.5">
            {tier ? `${tier} risk` : 'Cash-out prob.'}
          </div>
        </div>
      </div>

      {/* Spatio-Temporal Metrics Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
        <div className="bg-slate-900/70 p-2 rounded-lg border border-slate-800">
          <span className="text-xs text-slate-400 uppercase block">Expected Cash-Out</span>
          <span className="font-bold text-cyan-300 text-xs mt-0.5 block">
            {withdrawalWindow ? `⏱ ${withdrawalWindow}` : <span className="text-slate-500">not predicted</span>}
          </span>
        </div>
        <div className="bg-slate-900/70 p-2 rounded-lg border border-slate-800">
          <span className="text-xs text-slate-400 uppercase block">Estimated Travel ETA</span>
          <span className="font-bold text-amber-300 text-xs mt-0.5 block">
            {travelTime ? `🚗 ~${travelTime}` : <span className="text-slate-500">unavailable</span>}
          </span>
        </div>
      </div>

      {/* "Why This Location?" ML Reasoning Section */}
      <div className="space-y-1.5 pt-1">
        <div className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase tracking-wider text-cyan-400">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
          <span>Why This Location?</span>
        </div>
        <ul className="space-y-1 text-xs text-slate-300 font-sans leading-snug">
          {explanations.length > 0 ? explanations.map((reason, idx) => (
            <li key={idx} className="flex items-start gap-1.5 bg-slate-900/40 p-1.5 rounded border border-slate-800/80">
              <span className="text-cyan-400 text-xs mt-[-1px] font-mono">▸</span>
              <span>{reason}</span>
            </li>
          )) : (
            <li className="text-slate-500 italic p-1.5">
              No attribution available for this target.
            </li>
          )}
        </ul>
      </div>

      {/* FlyTo Quick Action Button */}
      {onFlyTo && selectedTarget.latitude && selectedTarget.longitude && (
        <button
          type="button"
          onClick={() => onFlyTo(selectedTarget)}
          className="w-full py-1.5 px-3 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 hover:text-white border border-cyan-500/50 text-xs font-mono font-semibold transition-all duration-150 flex items-center justify-center gap-1.5 shadow-sm"
        >
          <span>🎯 Focus Radar on Node</span>
        </button>
      )}
    </div>
  );
};

export default PredictionDetailsPanel;
