import React, { useState } from 'react';

/**
 * MapLegend Component (Role 3 - GIS Radar)
 * Project Drishti - Tactical Map Legend
 * 
 * Displays visual indicators for marker types, priority tiers, and H3 hexagonal zones.
 */
export const MapLegend = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-slate-950/90 backdrop-blur-md border border-cyan-500/30 rounded-xl p-2.5 shadow-xl text-xs font-mono text-slate-300">
      <div 
        className="flex items-center justify-between cursor-pointer select-none gap-3"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          <span className="font-bold text-cyan-300 tracking-wider uppercase text-[11px]">
            Map Legend
          </span>
        </div>
        <button 
          type="button" 
          className="text-slate-400 hover:text-white text-[10px] px-1 bg-slate-800 rounded"
        >
          {isExpanded ? '▲ HIDE' : '▼ SHOW'}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-2.5 pt-2 border-t border-slate-800 space-y-2 text-[10px]">
          {/* Target Types */}
          <div>
            <span className="text-slate-400 font-semibold uppercase tracking-wider block mb-1">
              Target Types
            </span>
            <div className="grid grid-cols-3 gap-1">
              <span className="px-1.5 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/40 text-center">
                ATM
              </span>
              <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/40 text-center">
                Branch
              </span>
              <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-center">
                BC Point
              </span>
            </div>
          </div>

          {/* Priority Levels */}
          <div>
            <span className="text-slate-400 font-semibold uppercase tracking-wider block mb-1">
              Threat Ranking
            </span>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-600 border border-white flex-shrink-0 animate-ping" />
                <span className="text-red-400 font-bold">#1 Critical Cashout Target</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-500 flex-shrink-0" />
                <span className="text-amber-400">#2–#3 High Risk Corridors</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-slate-700 border border-cyan-400 flex-shrink-0" />
                <span className="text-cyan-400">#4+ Secondary Monitored Nodes</span>
              </div>
            </div>
          </div>

          {/* H3 Risk Bins */}
          <div>
            <span className="text-slate-400 font-semibold uppercase tracking-wider block mb-1">
              H3 Spatial Risk Hexagons
            </span>
            <div className="flex items-center justify-between gap-1">
              <span className="px-1 py-0.5 rounded bg-red-500/30 text-red-400 border border-red-500/60 text-[9px]">
                Critical
              </span>
              <span className="px-1 py-0.5 rounded bg-amber-500/30 text-amber-400 border border-amber-500/60 text-[9px]">
                High
              </span>
              <span className="px-1 py-0.5 rounded bg-yellow-500/30 text-yellow-400 border border-yellow-500/60 text-[9px]">
                Medium
              </span>
              <span className="px-1 py-0.5 rounded bg-emerald-500/30 text-emerald-400 border border-emerald-500/60 text-[9px]">
                Low
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapLegend;
