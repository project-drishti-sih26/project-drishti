import React from 'react';

/**
 * TopTargetsPanel Component (Role 3 - GIS Radar)
 * Project Drishti - Tactical Predicted Targets Panel
 * 
 * Lists ranked cashout prediction targets (ATMs, Bank Branches, BC Points)
 * with instant `flyTo` navigation when an investigator clicks on a row.
 */
export const TopTargetsPanel = ({
  targets = [],
  selectedTargetId = null,
  onTargetSelect = () => {}
}) => {
  if (!targets || targets.length === 0) {
    return (
      <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/60 rounded-xl p-4 text-xs text-slate-400 font-mono">
        NO TARGETS IDENTIFIED
      </div>
    );
  }

  // Type badge color resolver
  const getTypeBadge = (type = '') => {
    const t = type.toLowerCase();
    if (t.includes('branch')) {
      return { label: 'BRANCH', bg: 'bg-blue-500/20 text-blue-400 border-blue-500/40' };
    }
    if (t.includes('bc') || t.includes('point')) {
      return { label: 'BC POINT', bg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' };
    }
    return { label: 'ATM', bg: 'bg-red-500/20 text-red-400 border-red-500/40' };
  };

  // Risk percentage color resolver
  const getRiskColor = (score) => {
    const s = Number(score) || 0;
    if (s >= 0.85) return 'text-red-400 font-bold';
    if (s >= 0.70) return 'text-amber-400 font-bold';
    return 'text-cyan-400';
  };

  return (
    <div className="w-full max-w-sm bg-slate-950/90 backdrop-blur-md border border-cyan-500/30 rounded-xl p-3.5 shadow-2xl shadow-cyan-950/40">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-2.5 mb-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <h3 className="text-xs font-mono font-bold tracking-wider text-cyan-300 uppercase">
            Top Predicted Targets
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
          {targets.length} LOCATIONS
        </span>
      </div>

      {/* Target Items List */}
      <div className="space-y-1.5 max-h-[320px] overflow-y-auto pr-1 custom-scrollbar">
        {targets.map((target, idx) => {
          const rank = target.rank || idx + 1;
          const isSelected = selectedTargetId === target.id;
          const badge = getTypeBadge(target.type);
          const scorePercent = Math.round((target.riskScore || target.score || 0) * 100);

          return (
            <button
              key={target.id || idx}
              type="button"
              onClick={() => onTargetSelect(target)}
              className={`w-full text-left p-2 rounded-lg border transition-all duration-150 flex items-center justify-between gap-2 ${
                isSelected
                  ? 'bg-cyan-950/70 border-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.3)] ring-1 ring-cyan-400'
                  : 'bg-slate-900/60 hover:bg-slate-800/80 border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Left Rank & Name */}
              <div className="flex items-center gap-2.5 min-w-0">
                {/* Rank Badge */}
                <div
                  className={`flex-shrink-0 w-6 h-6 rounded-md flex items-center justify-center font-mono font-bold text-xs ${
                    rank === 1
                      ? 'bg-red-600 text-white shadow-md shadow-red-600/40'
                      : rank <= 3
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  #{rank}
                </div>

                {/* Name & Type */}
                <div className="min-w-0">
                  <div className="text-xs font-semibold text-slate-200 truncate group-hover:text-white">
                    {target.name || `Location ${rank}`}
                  </div>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${badge.bg}`}
                    >
                      {badge.label}
                    </span>
                    {target.travelTime && (
                      <span className="text-[10px] text-slate-400 font-mono">
                        ⏱ {target.travelTime}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Right: Risk Probability */}
              <div className="text-right flex-shrink-0">
                <div className={`text-xs font-mono ${getRiskColor(target.riskScore || target.score)}`}>
                  {scorePercent}%
                </div>
                <div className="text-[9px] font-mono text-slate-500 uppercase">
                  Risk
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default TopTargetsPanel;
