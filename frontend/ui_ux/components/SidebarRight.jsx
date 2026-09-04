import React, { useState } from 'react';

/**
 * SidebarRight Component
 * Minimal Right Panel:
 * - Estimated Withdrawal Timeframe countdown
 * - ATM Locations (Ranked by Proximity)
 * - Plain Case Actions
 */
const SidebarRight = ({
  countdown = '10:56',
  onFeedback = () => {},
  selectedAtmId = 'ATM-091',
  onSelectAtm = () => {},
  caseData = {
    victim_name: 'R. K. Sharma',
    mule_bank: 'HDFC Bank (Noida Sector 18 Branch)',
    mule_account: 'HDFC •••• 9201',
    predicted_atm: 'SBI Kiosk #091, Inner Circle Block-B, CP',
    assigned_patrol: 'PCR Unit 12 (Central Division)',
    crime_vector: 'Unauthorized APK Screen Share',
    debit_time: '22:41 IST',
    status: 'Active'
  },
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

  // Timeline milestones derived from the active case
  const getTimelineEvents = (c) => {
    const baseTime = c.debit_time || '22:41 IST';
    const match = baseTime.match(/(\d{1,2}):(\d{2})/);
    let h = 22, m = 41;
    if (match) { h = parseInt(match[1], 10); m = parseInt(match[2], 10); }
    const fmt = (addMins) => {
      const totalM = h * 60 + m + addMins;
      const newH = Math.floor((totalM % (24 * 60)) / 60);
      const newM = totalM % 60;
      return `${String(newH).padStart(2, '0')}:${String(newM).padStart(2, '0')} IST`;
    };
    return [
      { time: fmt(0),  title: 'Complaint Registered',        desc: `Victim ${c.victim_name || 'Citizen'} reported unauthorized debit via 1930 / I4C portal.`, status: 'done' },
      { time: fmt(2),  title: 'Mule Account Flagged',         desc: `Beneficiary account identified at ${c.mule_bank || 'Bank'} (${c.mule_account || 'Mule Acc'}).`, status: 'done' },
      { time: fmt(3),  title: 'Withdrawal Location Predicted',desc: `Case analysis flagged ${c.predicted_atm?.split(',')[0] || 'Target ATM'} as priority node (Confidence 89%).`, status: 'done' },
      { time: fmt(4),  title: 'Field Patrol Dispatched',      desc: `Intercept coordinates routed to ${c.assigned_patrol || 'PCR Unit 12'}.`, status: 'done' },
      { time: fmt(7),  title: 'Section 91 Notice Prepared',   desc: `Compliance order pre-generated for nodal bank officer.`, status: 'done' },
      {
        time: c.status === 'Resolved' ? fmt(34) : 'Active',
        title: c.status === 'Resolved' ? 'Case Resolved' : 'Interception In Progress',
        desc: c.status === 'Resolved'
          ? 'Funds restrained at beneficiary branch; debit restriction enforced.'
          : 'Awaiting field patrol verification and bank debit restriction confirmation.',
        status: c.status === 'Resolved' ? 'done' : 'active'
      }
    ];
  };
  const timelineEvents = getTimelineEvents(caseData);

  const toggleExpand = (atm) => {
    setExpandedAtmId(expandedAtmId === atm.id ? null : atm.id);
    onSelectAtm(atm);
  };

  const handleFreeze = () => {
    setIsMuleFrozen(true);
    onFeedback('freeze_mule');
  };

  return (
    <aside className="w-full flex flex-col gap-4">
      {/* 1. ATM LOCATIONS */}
      <div className="bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-2">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <h3 className="font-medium text-slate-900 text-xs uppercase">
            ATM Locations
          </h3>
          <span className="text-[11px] text-slate-400 font-normal">Ranked by proximity</span>
        </div>

        <div className="space-y-1.5">
          {predictedAtms.map((atm) => {
            const isExpanded = expandedAtmId === atm.id;
            const isSelected = selectedAtmId === atm.id;

            return (
              <div
                key={atm.id}
                onClick={() => toggleExpand(atm)}
                className={`p-2 rounded-[4px] border transition-colors cursor-pointer ${
                  isSelected
                    ? 'border-slate-300 bg-slate-100/80 border-l-2 border-l-slate-900'
                    : 'border-slate-200 hover:bg-slate-50 border-l-2 border-l-transparent'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-[3px] flex items-center justify-center font-mono font-medium text-[10px] bg-slate-100 text-slate-700 border border-slate-200">
                      {atm.rank}
                    </span>
                    <div>
                      <div className="text-xs font-medium text-slate-900">{atm.name}</div>
                      <div className="text-[11px] text-slate-500 font-normal truncate max-w-[140px]">{atm.location}</div>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-medium text-slate-900 block font-mono">{atm.probability}</span>
                    <span className="text-[10px] text-slate-400 font-normal">{atm.distance} ({atm.eta})</span>
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-600 font-normal space-y-1">
                    <div><span className="font-medium text-slate-800">Note:</span> {atm.notes}</div>
                    <div className="text-[11px] text-slate-500">CCTV: {atm.cctv_status}</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. CASE ACTIONS */}
      <div className="bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-2">
        <span className="text-xs font-medium text-slate-900 uppercase block pb-1 border-b border-slate-100">
          Case Actions
        </span>

        <div className="space-y-1.5 pt-0.5">
          <button
            onClick={handleFreeze}
            disabled={isMuleFrozen}
            className={`w-full py-1.5 px-3 font-medium text-xs rounded-[3px] transition-colors cursor-pointer ${
              isMuleFrozen
                ? 'bg-slate-100 text-slate-400 border border-slate-200'
                : 'bg-rose-700 hover:bg-rose-800 text-white'
            }`}
          >
            {isMuleFrozen ? 'Debit Restriction Requested' : 'Freeze Mule Account'}
          </button>

          <button
            onClick={() => onFeedback('intercepted')}
            className="w-full py-1.5 px-3 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-[3px] transition-colors cursor-pointer"
          >
            Mark Case Resolved
          </button>
        </div>
      </div>
      {/* 3. CASE TIMELINE */}
      <div className="bg-white rounded-[4px] border border-slate-200 p-3.5 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <h3 className="text-xs font-medium text-slate-900 uppercase">Case Timeline</h3>
            <p className="text-[11px] text-slate-400 font-normal mt-0.5">Operational milestones &amp; audit log</p>
          </div>
          <span className="text-[11px] font-mono font-medium px-1.5 py-0.5 rounded-[3px] bg-emerald-50 text-emerald-700 border border-emerald-200">
            Live
          </span>
        </div>

        <div className="relative pl-4 space-y-3 before:absolute before:left-1.5 before:top-2 before:bottom-2 before:w-px before:bg-slate-200">
          {timelineEvents.map((evt, idx) => (
            <div key={idx} className="relative text-xs">
              <div
                className={`absolute -left-4 top-1 w-2 h-2 rounded-full ring-2 ring-white ${
                  evt.status === 'done' ? 'bg-slate-900' : 'bg-rose-600 animate-pulse'
                }`}
              />
              <div className="flex items-baseline justify-between gap-2">
                <span className="font-medium text-slate-900">{evt.title}</span>
                <span className="text-[10px] font-mono text-slate-400 shrink-0">{evt.time}</span>
              </div>
              <p className="text-[11px] text-slate-600 font-normal mt-0.5 leading-relaxed">{evt.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default SidebarRight;
