import React from 'react';
import { Crosshair, Navigation, HelpCircle, Flame, Clock } from 'lucide-react';

/**
 * SidebarRight Component (Role 4 - UI/UX)
 * Renders the ranked Top-5 ATM cashout predictions, countdown window, and SHAP explainability cards.
 */
const SidebarRight = ({
  predictedAtms = [
    {
      id: 'ATM-091',
      name: 'SBI ATM, Block B, Connaught Place',
      rank: 1,
      score: 0.94,
      travel_time: '18 mins',
      distance_km: 2.3,
      shap_reasons: 'High historical mule cashouts + 2.3km proximity to last known IP'
    },
    {
      id: 'ATM-142',
      name: 'HDFC ATM, Barakhamba Road',
      rank: 2,
      score: 0.81,
      travel_time: '24 mins',
      distance_km: 3.1,
      shap_reasons: 'Frequent evening cashout cluster + Low surveillance density'
    },
    {
      id: 'ATM-033',
      name: 'ICICI Bank BC Point, Janpath',
      rank: 3,
      score: 0.74,
      travel_time: '29 mins',
      distance_km: 3.9,
      shap_reasons: 'Correlated secondary withdrawal point'
    }
  ],
  selectedAtmId = null,
  onSelectAtm = () => {},
  countdown = '22:15'
}) => {
  return (
    <aside className="w-88 h-full flex flex-col gap-4 p-4 bg-slate-950/90 border-l border-slate-800/80 overflow-y-auto">
      {/* Time Window Countdown Card */}
      <div className="bg-gradient-to-br from-red-950/60 to-slate-900 border border-red-500/40 rounded-xl p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold tracking-wider text-red-400 flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-red-400 animate-spin" />
            INTERCEPTION WINDOW
          </span>
          <span className="text-[10px] font-mono bg-red-900/60 text-red-300 px-2 py-0.5 rounded border border-red-500/40">
            KAPLAN-MEIER
          </span>
        </div>
        <div className="mt-2 text-center">
          <span className="font-mono text-3xl font-black text-amber-400 tracking-wider">
            {countdown}
          </span>
          <p className="text-[11px] text-slate-400 mt-1">
            Estimated withdrawal in <strong className="text-white">18–35 mins</strong>
          </p>
        </div>
      </div>

      {/* Top-5 Predictions List Header */}
      <div className="flex items-center justify-between px-1">
        <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
          <Crosshair className="w-4 h-4 text-cyan-400" />
          RANKED CASHOUT ATMS (LTR)
        </h2>
        <span className="text-[10px] text-slate-400 font-mono">TOP 5</span>
      </div>

      {/* Ranked Cards */}
      <div className="space-y-3">
        {predictedAtms.map((atm) => {
          const isRankOne = atm.rank === 1;
          const isSelected = selectedAtmId === atm.id;

          return (
            <div
              key={atm.id}
              onClick={() => onSelectAtm(atm)}
              className={`p-3 rounded-xl border transition-all cursor-pointer select-none ${
                isSelected
                  ? 'bg-slate-800/90 border-cyan-400 ring-1 ring-cyan-400/50'
                  : isRankOne
                  ? 'bg-red-950/30 hover:bg-red-950/50 border-red-500/40'
                  : 'bg-slate-900/80 hover:bg-slate-800/80 border-slate-800'
              }`}
            >
              {/* Card Header: Rank + Confidence */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-6 h-6 flex items-center justify-center rounded-md font-mono text-xs font-bold ${
                      isRankOne
                        ? 'bg-red-600 text-white shadow-md shadow-red-500/50'
                        : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}
                  >
                    #{atm.rank}
                  </span>
                  <span className="text-xs font-semibold text-slate-200">
                    {atm.name}
                  </span>
                </div>
                <span className="text-[10px] font-mono font-bold text-emerald-400">
                  {((atm.score || 0.8) * 100).toFixed(0)}%
                </span>
              </div>

              {/* Distance & Travel Time */}
              <div className="flex items-center gap-3 mt-2 text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <Navigation className="w-3 h-3 text-cyan-400" />
                  {atm.distance_km} km
                </span>
                <span>•</span>
                <span>ETA ~{atm.travel_time}</span>
              </div>

              {/* SHAP Explainability Badge */}
              <div className="mt-2.5 p-2 rounded bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300">
                <div className="flex items-center gap-1 text-amber-400 text-[10px] font-mono font-semibold mb-1">
                  <Flame className="w-3 h-3" />
                  <span>SHAP AI REASONING:</span>
                </div>
                <p className="leading-snug text-slate-400">
                  {atm.shap_reasons || 'Top spatial candidate based on network movement.'}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
};

export default SidebarRight;
