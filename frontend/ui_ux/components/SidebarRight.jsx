import React, { useState } from 'react';

/**
 * SidebarRight Component (Role 4 - UI/UX)
 * Right Panel:
 * - Estimated Withdrawal Timeframe countdown
 * - ATM Locations (Ranked by Proximity)
 * - Case Actions (Text-only clean buttons)
 */
const SidebarRight = ({
  countdown = '10:56',
  onFeedback = () => {},
  selectedAtmId = 'ATM-091',
  onSelectAtm = () => {},
  predictedAtms = [
    {
      id: 'ATM-091',
      rank: 1,
      name: 'SBI Kiosk #091',
      location: 'Block B, Inner Circle, Connaught Place',
      distance: '1.8 km',
      eta: '11 min',
      probability: '89%',
      cctv_status: 'Active (3 Cameras)',
      notes: 'Identified recurring withdrawal node for reported beneficiary syndicate.'
    },
    {
      id: 'ATM-142',
      rank: 2,
      name: 'HDFC ATM',
      location: 'Statesman House, Barakhamba Road',
      distance: '2.4 km',
      eta: '17 min',
      probability: '82%',
      cctv_status: 'Active (Bank Guard)',
      notes: 'Located on transit corridor towards New Delhi Railway Station.'
    },
    {
      id: 'ATM-033',
      rank: 3,
      name: 'ICICI Bank ATM',
      location: 'Janpath Market Lane',
      distance: '3.1 km',
      eta: '22 min',
      probability: '76%',
      cctv_status: 'Active (Market Feed)',
      notes: 'Pedestrian market access point.'
    },
    {
      id: 'ATM-089',
      rank: 4,
      name: 'PNB ATM',
      location: 'Antriksh Bhawan, Kasturba Gandhi Marg',
      distance: '3.8 km',
      eta: '29 min',
      probability: '68%',
      cctv_status: 'Active (Building Security)',
      notes: 'Verified unoccupied during last patrol check at 22:30 IST.'
    },
    {
      id: 'ATM-052',
      rank: 5,
      name: 'Axis Bank ATM',
      location: 'Outer Circle, Near Shankar Market',
      distance: '4.2 km',
      eta: '34 min',
      probability: '59%',
      cctv_status: 'Maintenance Offline',
      notes: 'Secondary node based on cell tower perimeter coverage.'
    }
  ]
}) => {
  const [expandedAtmId, setExpandedAtmId] = useState('ATM-091');
  const [isMuleFrozen, setIsMuleFrozen] = useState(false);

  const toggleExpand = (atm) => {
    setExpandedAtmId(expandedAtmId === atm.id ? null : atm.id);
    onSelectAtm(atm);
  };

  const handleFreeze = () => {
    setIsMuleFrozen(true);
    onFeedback('freeze_mule');
  };

  return (
    <aside className="w-full flex flex-col gap-5">
      {/* 1. TIMEFRAME COUNTDOWN */}
      <div className="bg-white rounded-sm border border-slate-200 p-4 text-center">
        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
          Estimated Withdrawal Timeframe
        </span>
        <div className="mt-1.5 text-3xl font-bold font-mono text-rose-700">
          {countdown}
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Proximity estimate based on last cell-tower registration.
        </p>
      </div>

      {/* 2. ATM LOCATIONS */}
      <div className="bg-white rounded-sm border border-slate-200 p-3.5 space-y-2.5">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">
            ATM Locations
          </h3>
          <span className="text-[11px] text-slate-400">Ranked by Proximity</span>
        </div>

        <div className="space-y-2">
          {predictedAtms.map((atm) => {
            const isExpanded = expandedAtmId === atm.id;
            const isSelected = selectedAtmId === atm.id;

            return (
              <div
                key={atm.id}
                onClick={() => toggleExpand(atm)}
                className={`p-2.5 rounded-sm border transition-colors cursor-pointer ${
                  isSelected
                    ? 'border-slate-400 bg-slate-100/70 border-l-4 border-l-slate-900'
                    : 'border-slate-200 hover:bg-slate-50 border-l-4 border-l-transparent'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`w-4 h-4 rounded-sm flex items-center justify-center font-bold text-[10px] ${
                      atm.rank === 1 ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-slate-100 text-slate-700 border border-slate-200'
                    }`}>
                      {atm.rank}
                    </span>
                    <div>
                      <div className="text-xs font-bold text-slate-900">{atm.name}</div>
                      <div className="text-[11px] text-slate-500 truncate max-w-[140px]">{atm.location}</div>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-900 block font-mono">{atm.probability}</span>
                    <span className="text-[10px] text-slate-500">{atm.distance} ({atm.eta})</span>
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-600 space-y-1">
                    <div><strong className="text-slate-800">Case Note:</strong> {atm.notes}</div>
                    <div className="text-[11px] text-slate-500">CCTV: {atm.cctv_status}</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. CASE ACTIONS (TEXT-ONLY) */}
      <div className="bg-white rounded-sm border border-slate-200 p-3.5 space-y-2.5">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block pb-1 border-b border-slate-100">
          Case Actions
        </span>

        <div className="space-y-2 pt-1">
          {/* Primary Action */}
          <button
            onClick={handleFreeze}
            disabled={isMuleFrozen}
            className={`w-full py-2 px-3 font-semibold text-xs rounded-sm transition-colors cursor-pointer ${
              isMuleFrozen
                ? 'bg-slate-100 text-slate-400 border border-slate-200'
                : 'bg-rose-700 hover:bg-rose-800 text-white'
            }`}
          >
            {isMuleFrozen ? 'Debit Restriction Requested' : 'Freeze Mule Account'}
          </button>

          {/* Secondary Action */}
          <button
            onClick={() => onFeedback('intercepted')}
            className="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-sm transition-colors cursor-pointer"
          >
            Mark Case Resolved
          </button>
        </div>
      </div>
    </aside>
  );
};

export default SidebarRight;
